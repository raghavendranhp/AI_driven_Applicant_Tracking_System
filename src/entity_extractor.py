import os
import json
import requests
import warnings
from dotenv import load_dotenv
from groq import Groq

load_dotenv()
groq_client = Groq()

#suppress any potential warnings from external libraries
warnings.filterwarnings("ignore")

def load_prompt_file(filepath: str, **kwargs) -> str:
    """
    reads a text file containing a prompt template and injects dynamic variables.
    
    args:
        filepath (str): relative path to the prompt text file.
        **kwargs: dynamic variables to inject into the prompt template.
        
    returns:
        str: the formatted prompt string.
    """
    #build the absolute path to ensure it works from any execution directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    full_path = os.path.join(current_dir, filepath)
    
    try:
        #open and read the prompt template
        with open(full_path, 'r', encoding='utf-8') as file:
            prompt_template = file.read()
            
        #inject variables like resume_text into the template
        if kwargs:
            for k, v in kwargs.items():
                prompt_template = prompt_template.replace(f"{{{k}}}", str(v))
        return prompt_template
        
    except Exception as e:
        #return an error string if file is missing or unreadable
        return f"error loading prompt: {str(e)}"

def extract_entities(resume_text: str) -> dict:
    """
    sends the raw resume text to a local ollama instance running llama3 
    to extract structured json data (name, skills, experience).
    
    args:
        resume_text (str): the raw text extracted from a pdf or docx file.
        
    returns:
        dict: a dictionary containing the extracted entities or default empty values on failure.
    """
    #default fallback dictionary in case of api failure or parsing errors
    fallback_response = {"name": "unknown", "skills": [], "experience": 0}
    
    #validate input text
    if not resume_text or not isinstance(resume_text, str):
        return fallback_response

    #load the detailed system and user prompts from the text files
    system_prompt = load_prompt_file("prompts/system/extractor_system.txt")
    user_prompt = load_prompt_file("prompts/user/extractor_user.txt", resume_text=resume_text)
    
    #check if prompt loading failed
    if "error loading prompt" in system_prompt or "error loading prompt" in user_prompt:
        print("error: prompt files not found. please ensure the folder structure is correct.")
        return fallback_response

    # LOCAL OLLAMA IMPLEMENTATION
    # payload = {
    #     "model": "tinyllama",
    #     "format": "json",
    #     "stream": False,
    #     "messages": [
    #         {"role": "system", "content": system_prompt},
    #         {"role": "user", "content": user_prompt}
    #     ],
    #     "options": {
    #         "temperature": 0.1
    #     }
    # }
    # ollama_url = "http://localhost:11434/api/chat"
    # try:
    #     response = requests.post(ollama_url, json=payload, timeout=120)
    #     response.raise_for_status()
    #     response_data = response.json()
    #     message_content = response_data.get("message", {}).get("content", "{}")
    #     
    #     #parse the string content returned by local model
    #     extracted_json = json.loads(message_content)
    #     
    #     #ensure the required keys exist
    #     if "name" not in extracted_json:
    #         extracted_json["name"] = fallback_response["name"]
    #     if "skills" not in extracted_json:
    #         extracted_json["skills"] = fallback_response["skills"]
    #     if "experience" not in extracted_json:
    #         extracted_json["experience"] = fallback_response["experience"]
    #         
    #     return extracted_json
    # except Exception as e:
    #     print(f"error from ollama: {str(e)}")
    #     return fallback_response

    # GROQ API IMPLEMENTATION 
    try:
        completion = groq_client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.1,
            response_format={"type": "json_object"}
        )
        message_content = completion.choices[0].message.content
       
        extracted_json = json.loads(message_content)
        if "name" not in extracted_json:
            extracted_json["name"] = fallback_response["name"]
        if "skills" not in extracted_json:
            extracted_json["skills"] = fallback_response["skills"]
        if "experience" not in extracted_json:
            extracted_json["experience"] = fallback_response["experience"]
           
        return extracted_json
       
    except Exception as e:
        print(f"unexpected error during extraction: {str(e)}")
        return fallback_response