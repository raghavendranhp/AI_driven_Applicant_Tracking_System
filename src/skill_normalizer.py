import re

#default dictionary for common skill abbreviations to speed up matching
COMMON_SYNONYMS = {
    "js": "javascript",
    "ml": "machine learning",
    "dl": "deep learning",
    "nlp": "natural language processing",
    "cv": "computer vision",
    "aws": "amazon web services",
    "gcp": "google cloud platform",
    "k8s": "kubernetes",
    "tf": "tensorflow",
    "py": "python",
    "react": "reactjs",
    "react.js": "reactjs",
    "node": "nodejs",
    "node.js": "nodejs"
}

def clean_skill_string(skill: str) -> str:
    """
    cleans a single skill string by converting to lowercase, 
    removing extra spaces, and stripping special characters.
    
    args:
        skill (str): the raw skill string.
        
    returns:
        str: the cleaned skill string.
    """
    if not skill or not isinstance(skill, str):
        return ""
        
    #convert to lowercase and strip leading/trailing spaces
    cleaned = skill.lower().strip()
    
    #remove unwanted special characters like brackets or bullet points
    cleaned = re.sub(r'[^a-z0-9\s\.\+]', '', cleaned)
    
    #remove extra internal spaces
    cleaned = re.sub(r'\s+', ' ', cleaned)
    
    return cleaned.strip()

def normalize_skills(skills_list: list) -> list:
    """
    takes a list of extracted raw skills, cleans them, 
    and resolves common abbreviations using a predefined dictionary.
    this ensures the semantic matcher in the next step is highly accurate.
    
    args:
        skills_list (list): list of raw skill strings extracted from a resume or jd.
        
    returns:
        list: a list of normalized skill strings without duplicates.
    """
    if not skills_list or not isinstance(skills_list, list):
        return []
        
    #use a set to automatically remove duplicates during normalization
    normalized_set = set()
    
    for raw_skill in skills_list:
        #clean the raw string
        cleaned_skill = clean_skill_string(raw_skill)
        
        #skip empty strings that might occur after cleaning
        if not cleaned_skill:
            continue
            
        #check if the cleaned skill matches a known abbreviation
        final_skill = COMMON_SYNONYMS.get(cleaned_skill, cleaned_skill)
        
        normalized_set.add(final_skill)
        
    #return as a sorted list for consistent processing in the matcher pipeline
    return sorted(list(normalized_set))