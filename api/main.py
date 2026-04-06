import os
import sys
import shutil
import warnings
from typing import List, Dict, Any
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse

#suppress any potential warnings from external libraries to keep logs clean
warnings.filterwarnings("ignore")

#add the parent directory to sys.path so we can seamlessly import from the src folder
#this ensures uvicorn works whether run from the project root or the api folder
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

#import the core engine modules built in the src directory
from src.document_parser import parse_document
from src.entity_extractor import extract_entities
from src.skill_normalizer import normalize_skills
from src.matcher import calculate_skill_match_score
from src.ranker import calculate_experience_match, calculate_keyword_match, calculate_final_score, rank_candidates
from src.explainer import generate_explanation

#initialize the fastapi application
app = FastAPI(
    title="ai recruitment engine api",
    description="core api for parsing resumes, matching candidates, and generating ai insights.",
    version="1.0.0"
)

#define the temporary storage path for uploaded files during api processing
TEMP_DIR = os.path.join(parent_dir, "data", "temp_uploads")
os.makedirs(TEMP_DIR, exist_ok=True)

def save_uploaded_file(upload_file: UploadFile) -> str:
    """
    saves a fastapi uploadfile to a local temporary directory so it can be 
    processed by the file-path based document parser.
    
    args:
        upload_file (UploadFile): the file uploaded via the api endpoint.
        
    returns:
        str: the absolute path to the temporarily saved file.
    """
    file_path = os.path.join(TEMP_DIR, upload_file.filename)
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(upload_file.file, buffer)
        return file_path
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"failed to save file {upload_file.filename}: {str(e)}")

@app.get("/")
def health_check() -> Dict[str, str]:
    """
    simple health check endpoint to verify the api is running successfully.
    """
    return {"status": "success", "message": "ai recruitment engine api is operational."}

@app.post("/extract")
async def extract_resume_data(file: UploadFile = File(...)) -> JSONResponse:
    """
    endpoint for task: parsing a single resume and extracting structured json.
    
    args:
        file (UploadFile): a pdf or docx resume file.
        
    returns:
        JSONResponse: the extracted json data containing name, skills, and experience.
    """
    #validate file extension
    if not file.filename.lower().endswith(('.pdf', '.docx')):
        raise HTTPException(status_code=400, detail="only .pdf and .docx files are supported.")
        
    #save the file locally
    file_path = save_uploaded_file(file)
    
    #step 1: parse the document to get raw text
    raw_text = parse_document(file_path)
    if raw_text.startswith("error"):
        raise HTTPException(status_code=500, detail=raw_text)
        
    #step 2: extract entities using the local ollama model
    extracted_data = extract_entities(raw_text)
    
    #clean up the temporary file to save disk space
    if os.path.exists(file_path):
        os.remove(file_path)
        
    return JSONResponse(content=extracted_data)

@app.post("/match")
async def match_candidates(
    jd_file: UploadFile = File(...),
    resume_files: List[UploadFile] = File(...)
) -> JSONResponse:
    """
    endpoint for task: matching multiple resumes against a job description,
    scoring them, ranking them, and generating ai explanations.
    
    args:
        jd_file (UploadFile): the job description file (.pdf or .docx).
        resume_files (List[UploadFile]): a list of candidate resume files.
        
    returns:
        JSONResponse: a sorted list of matched candidates with scores and reasons.
    """
    #process the job description
    jd_path = save_uploaded_file(jd_file)
    jd_text = parse_document(jd_path)
    
    #we use the same entity extractor to pull required skills and experience from the jd
    jd_data = extract_entities(jd_text)
    jd_skills_normalized = normalize_skills(jd_data.get("skills", []))
    jd_experience = float(jd_data.get("experience", 0))
    
    os.remove(jd_path)
    
    #process all uploaded resumes
    results = []
    
    for resume_file in resume_files:
        res_path = save_uploaded_file(resume_file)
        res_text = parse_document(res_path)
        res_data = extract_entities(res_text)
        os.remove(res_path)
        
        #normalize candidate skills
        candidate_skills = res_data.get("skills", [])
        res_skills_normalized = normalize_skills(candidate_skills)
        candidate_experience = float(res_data.get("experience", 0))
        candidate_name = res_data.get("name", "unknown")
        
        #calculate individual matching metrics
        skill_score = calculate_skill_match_score(jd_skills_normalized, res_skills_normalized)
        exp_score = calculate_experience_match(jd_experience, candidate_experience)
        keyword_score = calculate_keyword_match(jd_skills_normalized, res_skills_normalized)
        
        #calculate final weighted score
        final_score = calculate_final_score(skill_score, exp_score, keyword_score)
        
        #compile the candidate's result payload without reason yet
        results.append({
            "candidate": candidate_name,
            "score": final_score,
            "reason": None, # will be generated only for top 5 later
            "details": {
                "skills": candidate_skills,
                "experience": candidate_experience
            }
        })
        
    #rank the candidates from highest score to lowest
    ranked_results = rank_candidates(results)
    
    #take only the top 5 candidates as per the mvp requirement
    top_candidates = ranked_results[:5]
    
    #now generate ai explanation ONLY for the top 5 candidates to save massive LLM time
    for candidate in top_candidates:
        candidate["reason"] = generate_explanation(
            candidate_name=candidate["candidate"],
            candidate_skills=candidate["details"]["skills"],
            candidate_experience=candidate["details"]["experience"],
            jd_skills=jd_data.get("skills", []),
            jd_experience=jd_experience,
            match_score=candidate["score"]
        )
    
    return JSONResponse(content={"matches": top_candidates})