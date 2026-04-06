import os
import sys

# Add the project directory to sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_dir = os.path.dirname(current_dir)
sys.path.append(project_dir)

from src.document_parser import parse_document
from src.entity_extractor import extract_entities

def test_entity_extractor():
    print("--- Testing Entity Extractor (with Ollama Gemma:2b) ---")
    
    # Selecting one valid resume to extract its text
    test_resume = os.path.join(project_dir, "data", "raw_resumes", "resume_aarush_seth.docx")
    
    if not os.path.exists(test_resume):
        print(f"[-] Cannot test entity extractor: Test file not found at {test_resume}")
        return

    print(f"[+] Loading text from {test_resume}")
    raw_text = parse_document(test_resume)
    
    print("[+] Extracted text length: ", len(raw_text))
    print("[+] Submitting text to Entity Extractor (Sending prompt to Gemma)...")
    
    # Sending to the extractor
    extracted_data = extract_entities(raw_text)
    
    print("\n--- Extraction Results ---")
    print(f"Name:       {extracted_data.get('name')}")
    print(f"Experience: {extracted_data.get('experience')} years")
    print(f"Skills:     {', '.join(extracted_data.get('skills', []))}")
    
if __name__ == "__main__":
    test_entity_extractor()
