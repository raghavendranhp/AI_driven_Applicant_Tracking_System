import numpy as np
import warnings
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

#suppress warnings from huggingface and sentence transformers to keep console clean
warnings.filterwarnings("ignore")

#load the tiny, fast model globally so it only loads into memory once per session
MODEL_NAME = "all-MiniLM-L6-v2"
model = SentenceTransformer(MODEL_NAME)

def get_embeddings(text_list: list) -> np.ndarray:
    """
    converts a list of text strings into mathematical vectors (embeddings)
    using the pre-trained sentence-transformers model.
    
    args:
        text_list (list): a list of strings (e.g., normalized skills).
        
    returns:
        np.ndarray: an array of vectors representing the semantic meaning of the text.
    """
    #return empty array if input is invalid or empty to prevent model errors
    if not text_list or not isinstance(text_list, list):
        return np.array([])
        
    #encode the list of strings into a numpy array of floats
    return model.encode(text_list)

def calculate_skill_match_score(jd_skills: list, resume_skills: list) -> float:
    """
    calculates the semantic similarity between job description skills and candidate skills.
    it compares every jd skill against every resume skill using cosine similarity, 
    finds the best match for each requirement, and averages the results.
    
    args:
        jd_skills (list): list of normalized skills required by the job description.
        resume_skills (list): list of normalized skills possessed by the candidate.
        
    returns:
        float: a score between 0.0 and 1.0 representing the overall skill match percentage.
    """
    #if the job description requires no skills, it is a perfect match by default
    if not jd_skills:
        return 1.0
        
    #if candidate has no skills but the jd requires them, the score is absolute zero
    if not resume_skills:
        return 0.0
        
    #convert both lists of text skills into high-dimensional semantic vectors
    jd_embeddings = get_embeddings(jd_skills)
    resume_embeddings = get_embeddings(resume_skills)
    
    #calculate the cosine similarity matrix between jd and resume skills
    similarity_matrix = cosine_similarity(jd_embeddings, resume_embeddings)
    
    #for each required jd skill (row), find the highest matching candidate skill score
    best_matches = np.max(similarity_matrix, axis=1)
    
    #average the best matches to get the final overall skill score
    final_score = np.clip(np.mean(best_matches), 0.0, 1.0)
    
    return float(final_score)