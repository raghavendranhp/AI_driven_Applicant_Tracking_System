import os
import sys

#Append parent dir so src can be imported
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__))))

from src.document_parser import parse_document
from src.entity_extractor import extract_entities
from src.skill_normalizer import normalize_skills
from src.matcher import calculate_skill_match_score
from src.ranker import calculate_experience_match, calculate_keyword_match, calculate_final_score
from src.explainer import generate_explanation

jd_path = r"data\job_descriptions\jd.docx"
res_path = r"data\raw_resumes\resume_divya_mitter.pdf"

print("1. Processing Job Description...")
jd_text = parse_document(jd_path)
jd_data = extract_entities(jd_text)
jd_skills = normalize_skills(jd_data.get("skills", []))
jd_exp = float(jd_data.get("experience", 0))

print(f"JD Skills: {jd_skills}")
print(f"JD Experience: {jd_exp}")

print("\n2. Processing Resume...")
res_text = parse_document(res_path)
res_data = extract_entities(res_text)
candidate_name = res_data.get("name", "unknown")
raw_cand_skills = res_data.get("skills", [])
cand_skills = normalize_skills(raw_cand_skills)
cand_exp = float(res_data.get("experience", 0))

print(f"Candidate Name: {candidate_name}")
print(f"Candidate Skills: {cand_skills}")
print(f"Candidate Experience: {cand_exp}")

print("\n3. Calculating Scores...")
skill_score = calculate_skill_match_score(jd_skills, cand_skills)
exp_score = calculate_experience_match(jd_exp, cand_exp)
keyword_score = calculate_keyword_match(jd_skills, cand_skills)
final_score = calculate_final_score(skill_score, exp_score, keyword_score)

print(f"Skill Score: {skill_score}")
print(f"Exp Score: {exp_score}")
print(f"Keyword Score: {keyword_score}")
print(f"FINAL SCORE: {final_score}")

print("\n4. Generating AI Insight...")
reason = generate_explanation(
    candidate_name, raw_cand_skills, cand_exp, 
    jd_data.get("skills", []), jd_exp, final_score
)

print(f"AI Insight: {reason}")
print("\n[SUCCESS] Pipeline runs without errors.")
