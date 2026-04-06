import os
import sys

# Add the project directory to sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_dir = os.path.dirname(current_dir)
sys.path.append(project_dir)

from src.ranker import calculate_experience_match, calculate_keyword_match, calculate_final_score, rank_candidates

def test_ranker():
    print("--- Testing Ranker & Scoring Formula ---")
    
    print("\n[+] Testing Experience Match")
    print(f"Req: 5, Cand: 6 -> Score: {calculate_experience_match(5, 6)}")
    print(f"Req: 5, Cand: 3 -> Score: {calculate_experience_match(5, 3)}")
    
    print("\n[+] Testing Keyword Match")
    jd = ["python", "aws", "docker"]
    res = ["python", "docker", "kubernetes"]
    print(f"JD: {jd}, Resume: {res} -> Keyword Match Score: {calculate_keyword_match(jd, res)}")
    
    print("\n[+] Testing Final Scoring Formula")
    # Using arbitrary sub-scores
    score = calculate_final_score(semantic_skill_score=0.8, exp_score=0.6, keyword_score=0.66)
    print(f"Semantic: 0.8, Exp: 0.6, Keyword: 0.66 -> Final Score (out of 100): {score}")
    
    print("\n[+] Testing Candidate Ranking")
    candidates = [
        {"name": "Alice", "score": 75.5},
        {"name": "Bob", "score": 92.0},
        {"name": "Charlie", "score": 60.0}
    ]
    ranked = rank_candidates(candidates)
    print("Unranked:", [c["name"] for c in candidates])
    print("Ranked:  ", [c["name"] for c in ranked])
    
    print("\n--- Ranker Tests Completed ---")

if __name__ == "__main__":
    test_ranker()
