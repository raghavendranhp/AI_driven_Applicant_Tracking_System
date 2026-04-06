import warnings

#suppress any potential warnings during math operations
warnings.filterwarnings("ignore")

def calculate_experience_match(required_exp: float, candidate_exp: float) -> float:
    """
    calculates how well the candidate's experience matches the job requirement.
    
    args:
        required_exp (float): years of experience required by the job description.
        candidate_exp (float): total years of experience extracted from the resume.
        
    returns:
        float: a score between 0.0 and 1.0 representing the experience match.
    """
    #if the job requires no experience, it is a perfect match by default
    if required_exp <= 0:
        return 1.0
        
    #if candidate has more or equal experience, perfect match
    if candidate_exp >= required_exp:
        return 1.0
        
    #otherwise, calculate the percentage of required experience met
    return candidate_exp / required_exp

def calculate_keyword_match(jd_skills: list, resume_skills: list) -> float:
    """
    calculates an exact keyword intersection score. unlike semantic matching,
    this ensures that explicit, hard-requirement keywords are respected.
    
    args:
        jd_skills (list): list of normalized skills from the jd.
        resume_skills (list): list of normalized skills from the resume.
        
    returns:
        float: a score between 0.0 and 1.0 representing exact keyword overlap.
    """
    #if there are no required keywords, score is perfect
    if not jd_skills:
        return 1.0
        
    #if candidate has no skills, score is zero
    if not resume_skills:
        return 0.0
        
    #convert lists to sets for fast intersection math
    jd_set = set(jd_skills)
    resume_set = set(resume_skills)
    
    #calculate how many required skills are explicitly present in the resume
    matches = len(jd_set.intersection(resume_set))
    
    #return the ratio of matches to total required skills
    return matches / len(jd_set)

def calculate_final_score(semantic_skill_score: float, exp_score: float, keyword_score: float) -> float:
    """
    applies the weighted ranking formula to calculate the final candidate score.
    formula: score = (0.5 * skill match) + (0.3 * experience match) + (0.2 * keyword similarity)
    
    args:
        semantic_skill_score (float): score from sentence-transformers (0.0 to 1.0).
        exp_score (float): score from experience calculation (0.0 to 1.0).
        keyword_score (float): score from exact keyword intersection (0.0 to 1.0).
        
    returns:
        float: the final weighted score on a 0 to 100 scale.
    """
    #apply weights as per the explicit instructions in the original task
    weighted_score = (0.5 * semantic_skill_score) + (0.3 * exp_score) + (0.2 * keyword_score)
    
    #convert to a 100-point scale and round to 2 decimal places for clean ui presentation
    return round(weighted_score * 100, 2)

def rank_candidates(candidates_data: list) -> list:
    """
    sorts a list of candidate dictionaries based on their final calculated score
    in descending order (highest score first).
    
    args:
        candidates_data (list): a list of dictionaries, where each dict must contain
                                at least a 'score' key with a numeric value.
                                
    returns:
        list: the sorted list of candidates.
    """
    #sort the list using the 'score' key, descending
    return sorted(candidates_data, key=lambda x: x.get("score", 0), reverse=True)