import os
import sys

#Add the project directory to sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_dir = os.path.dirname(current_dir)
sys.path.append(project_dir)

from src.explainer import generate_explanation

def test_explainer():
    print("--- Testing AI Explainer (with Ollama Gemma:2b) ---")
    
    cand_name = "Jane Doe"
    cand_skills = ["python", "pandas", "machine learning"]
    cand_exp = 4.0
    
    jd_skills = ["python", "deep learning", "aws"]
    jd_exp = 5.0
    
    match_score = 75.50
    
    print(f"\n[+] Input Data for {cand_name}:")
    print(f"    Candidate Skills: {cand_skills} | Exp: {cand_exp}y")
    print(f"    JD Skills:        {jd_skills} | Exp: {jd_exp}y")
    print(f"    Calculated Match Score: {match_score}")
    
    print("\n[+] Submitting to Explainer (Generating 1-sentence logic via Gemma)...")
    
    explanation = generate_explanation(
        candidate_name=cand_name,
        candidate_skills=cand_skills,
        candidate_experience=cand_exp,
        jd_skills=jd_skills,
        jd_experience=jd_exp,
        match_score=match_score
    )
    
    print(f"\n-> Explainer Output: \n\"{explanation}\"")
    print("\n--- Explainer Tests Completed ---")

if __name__ == "__main__":
    test_explainer()
