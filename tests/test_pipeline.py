import os
import sys

# Add the project directory to sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_dir = os.path.dirname(current_dir)
sys.path.append(project_dir)

from src.document_parser import parse_document
from src.entity_extractor import extract_entities
from src.skill_normalizer import normalize_skills
from src.matcher import calculate_skill_match_score
from src.ranker import calculate_experience_match, calculate_keyword_match, calculate_final_score
from src.explainer import generate_explanation

def run_end_to_end_test():
    print("--- Testing Full E2E Pipeline ---")
    
    #Define paths
    jd_path = os.path.join(project_dir, "data", "job_descriptions", "jd.docx")
    resume_path = os.path.join(project_dir, "data", "raw_resumes", "resume_aarush_seth.docx")
    
    if not os.path.exists(jd_path) or not os.path.exists(resume_path):
        print("[-] Files missing. Ensure jd.docx and resume_aarush_seth.docx exist.")
        return

    #Parse and Extract JD
    print("\n[+] 1. Processing Job Description...")
    jd_text = parse_document(jd_path)
    jd_data = extract_entities(jd_text)
    jd_skills = normalize_skills(jd_data.get("skills", []))
    jd_exp = float(jd_data.get("experience", 0))
    print(f"    Target Exp: {jd_exp}y | Target Skills: {len(jd_skills)} extracted")
    print(f"    Normalized JD Skills: {jd_skills}")

    #Parse and Extract Resume
    print("\n[+] 2. Processing Candidate Resume...")
    res_text = parse_document(resume_path)
    res_data = extract_entities(res_text)
    candidate_name = res_data.get("name", "Unknown")
    raw_cand_skills = res_data.get("skills", [])
    cand_skills = normalize_skills(raw_cand_skills)
    cand_exp = float(res_data.get("experience", 0))
    print(f"    Candidate: {candidate_name}")
    print(f"    Cand Exp: {cand_exp}y | Cand Skills: {len(cand_skills)} extracted")
    print(f"    Normalized Cand Skills: {cand_skills}")

    #Calculate Scores
    print("\n[+] 3. Calculating Match Scores...")
    skill_score = calculate_skill_match_score(jd_skills, cand_skills)
    exp_score = calculate_experience_match(jd_exp, cand_exp)
    keyword_score = calculate_keyword_match(jd_skills, cand_skills)
    final_score = calculate_final_score(skill_score, exp_score, keyword_score)
    print(f"    Semantic Skill Score: {skill_score:.2f}")
    print(f"    Experience Score:     {exp_score:.2f}")
    print(f"    Keyword Score:        {keyword_score:.2f}")
    print(f"    Final Match Score:    {final_score} / 100")

    #Generate Explanation
    print("\n[+] 4. Generating AI Explanation (via Gemma:2b)...")
    reason = generate_explanation(
        candidate_name=candidate_name,
        candidate_skills=raw_cand_skills,
        candidate_experience=cand_exp,
        jd_skills=jd_data.get("skills", []),
        jd_experience=jd_exp,
        match_score=final_score
    )
    
    print("\n================ FINAL REPORT ================")
    print(f"Candidate: {candidate_name}")
    print(f"Match Score: {final_score}")
    print(f"AI Insight: \"{reason}\"")
    print("==============================================")

if __name__ == "__main__":
    run_end_to_end_test()
