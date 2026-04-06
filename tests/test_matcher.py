import os
import sys

# Add the project directory to sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_dir = os.path.dirname(current_dir)
sys.path.append(project_dir)

from src.matcher import calculate_skill_match_score

def test_matcher():
    print("--- Testing Semantic Skill Matcher ---")
    
    #Exact Match Test
    jd_skills_1 = ["python", "machine learning", "docker"]
    resume_skills_1 = ["python", "machine learning", "docker"]
    
    #Semantic Variation Test (Different words, similar meaning)
    jd_skills_2 = ["natural language processing", "frontend development", "gcp"]
    resume_skills_2 = ["nlp", "reactjs", "google cloud platform"]
    
    #Weak Match Test
    jd_skills_3 = ["data engineering", "sql", "airflow"]
    resume_skills_3 = ["html", "css", "javascript"]
    
    print("\nTest 1 (Exact Match):")
    score1 = calculate_skill_match_score(jd_skills_1, resume_skills_1)
    print(f"JD: {jd_skills_1}\nResume: {resume_skills_1}\nScore: {score1:.2f}\n")
    
    print("Test 2 (Semantic Variation):")
    score2 = calculate_skill_match_score(jd_skills_2, resume_skills_2)
    print(f"JD: {jd_skills_2}\nResume: {resume_skills_2}\nScore: {score2:.2f}\n")
    
    print("Test 3 (Weak Match):")
    score3 = calculate_skill_match_score(jd_skills_3, resume_skills_3)
    print(f"JD: {jd_skills_3}\nResume: {resume_skills_3}\nScore: {score3:.2f}\n")

    print("--- Matcher Tests Completed ---")

if __name__ == "__main__":
    test_matcher()
