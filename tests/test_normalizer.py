import os
import sys

# Add the project directory to sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_dir = os.path.dirname(current_dir)
sys.path.append(project_dir)

from src.skill_normalizer import normalize_skills, clean_skill_string

def test_skill_normalizer():
    print("--- Testing Skill Normalizer ---")
    
    raw_skills = [
        " React.js ", 
        "ML", 
        " machine   learning", 
        "Node.js", 
        "(Python)", 
        "JS", 
        "AWS",
        "aws",
        "C++!"
    ]
    
    print("[+] Input Raw Skills:")
    print(raw_skills)
    
    print("\n[+] Testing clean_skill_string...")
    for s in raw_skills:
        print(f"    '{s}' -> '{clean_skill_string(s)}'")
        
    print("\n[+] Testing normalize_skills (Deduplication + Synonym expansion)...")
    normalized = normalize_skills(raw_skills)
    print(f"-> Normalized Skills: {normalized}")
    print("\n--- Skill Normalizer Tests Completed ---")

if __name__ == "__main__":
    test_skill_normalizer()
