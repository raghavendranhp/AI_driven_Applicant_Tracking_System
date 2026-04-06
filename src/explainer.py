import os
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
    #this current file is in 'src', so current_dir is 'src'
    current_dir = os.path.dirname(os.path.abspath(__file__))
    full_path = os.path.join(current_dir, filepath)
    
    try:
        #open and read the prompt template
        with open(full_path, 'r', encoding='utf-8') as file:
            prompt_template = file.read()
            
        #inject variables into the template
        if kwargs:
            for k, v in kwargs.items():
                prompt_template = prompt_template.replace(f"{{{k}}}", str(v))
        return prompt_template
        
    except Exception as e:
        #return an error string if file is missing or unreadable
        return f"error loading prompt: {str(e)}"

def generate_explanation(
    candidate_name: str, 
    candidate_skills: list, 
    candidate_experience: float, 
    jd_skills: list, 
    jd_experience: float, 
    match_score: float
) -> str:
    """
    sends candidate and job description data to a local ollama instance running llama3
    to generate a single-sentence explanation of why the candidate received their score.
    
    args:
        candidate_name (str): name of the candidate.
        candidate_skills (list): list of skills extracted from the resume.
        candidate_experience (float): years of experience extracted from the resume.
        jd_skills (list): list of required skills from the job description.
        jd_experience (float): required years of experience.
        match_score (float): the final calculated match score (0 to 100).
        
    returns:
        str: a single sentence explaining the score, or a fallback string on error.
    """
    #convert lists to comma-separated strings for the prompt
    cand_skills_str = ", ".join(candidate_skills) if candidate_skills else "none found"
    jd_skills_str = ", ".join(jd_skills) if jd_skills else "none specified"
    
    #load the detailed system and user prompts from the text files
    system_prompt = load_prompt_file("prompts/system/explainer_system.txt")
    user_prompt = load_prompt_file(
        "prompts/user/explainer_user.txt", 
        candidate_name=candidate_name,
        candidate_skills=cand_skills_str,
        candidate_experience=candidate_experience,
        jd_skills=jd_skills_str,
        jd_experience=jd_experience,
        match_score=match_score
    )
    
    #check if prompt loading failed
    if "error loading prompt" in system_prompt or "error loading prompt" in user_prompt:
        return "explanation unavailable due to missing prompt files."

    # LOCAL OLLAMA IMPLEMENTATION
    # payload = {
    #     "model": "gemma:2b",
    #     "stream": False,
    #     "messages": [
    #         {"role": "system", "content": system_prompt},
    #         {"role": "user", "content": user_prompt}
    #     ],
    #     "options": {
    #         "temperature": 0.2
    #     }
    # }
    # ollama_url = "http://localhost:11434/api/chat"
    # try:
    #     response = requests.post(ollama_url, json=payload, timeout=60)
    #     response.raise_for_status()
    #     response_data = response.json()
    #     message_content = response_data.get("message", {}).get("content", "")
    #     cleaned_explanation = message_content.strip().strip('"').strip("'")
    #     return cleaned_explanation
    # except Exception as e:
    #      print(f"error from ollama: {str(e)}")
    #      return f"scored {match_score}% based on alignment of skills and experience."

    # --- GROQ API IMPLEMENTATION (ACTIVE) ---
    try:
        completion = groq_client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.2
        )
        message_content = completion.choices[0].message.content
        cleaned_explanation = message_content.strip().strip('"').strip("'")
        return cleaned_explanation
    except Exception as e:
        print(f"unexpected error during explanation generation: {str(e)}")
        return f"scored {match_score}% based on alignment of skills and experience."