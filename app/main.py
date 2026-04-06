import os
import sys
import warnings
import pandas as pd
import streamlit as st
from streamlit_option_menu import option_menu

#suppress warnings to keep the ui clean
warnings.filterwarnings("ignore")

#add the parent directory to sys.path so we can import from the src folder
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

#import core engine modules from src
from src.document_parser import parse_document
from src.entity_extractor import extract_entities
from src.skill_normalizer import normalize_skills
from src.matcher import calculate_skill_match_score
from src.ranker import calculate_experience_match, calculate_keyword_match, calculate_final_score, rank_candidates
from src.explainer import generate_explanation

#configure the streamlit page properties
st.set_page_config(
    page_title="ai recruitment engine",
    layout="wide",
    initial_sidebar_state="collapsed"
)

#define temporary storage for streamlit file uploads
temp_dir = os.path.join(parent_dir, "data", "temp_uploads")
os.makedirs(temp_dir, exist_ok=True)

def save_temp_file(uploaded_file) -> str:
    """
    saves a streamlit uploaded file object to a local temporary directory
    so it can be processed by the file-path based document parser.
    
    args:
        uploaded_file: the file object uploaded via streamlit.
        
    returns:
        str: the absolute path to the temporarily saved file.
    """
    file_path = os.path.join(temp_dir, uploaded_file.name)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return file_path

def cleanup_temp_file(file_path: str):
    """
    removes a temporary file from the disk.
    
    args:
        file_path (str): the path of the file to remove.
    """
    if os.path.exists(file_path):
        os.remove(file_path)

#create the horizontal navigation menu
selected_tab = option_menu(
    menu_title=None,
    options=["single resume analysis", "batch resume ranking"],
    icons=["", ""],
    orientation="horizontal",
    default_index=0
)

if selected_tab == "single resume analysis":
    st.header("single resume analysis")
    st.write("upload a job description and a single resume to see a detailed match breakdown.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        jd_file = st.file_uploader("upload job description (.pdf or .docx)", type=["pdf", "docx"], key="jd_single")
        
    with col2:
        resume_file = st.file_uploader("upload candidate resume (.pdf or .docx)", type=["pdf", "docx"], key="res_single")
        
    if st.button("analyze match"):
        if jd_file and resume_file:
            with st.spinner("extracting entities and calculating scores..."):
                #process job description
                jd_path = save_temp_file(jd_file)
                jd_text = parse_document(jd_path)
                jd_data = extract_entities(jd_text)
                jd_skills = normalize_skills(jd_data.get("skills", []))
                jd_exp = float(jd_data.get("experience", 0))
                cleanup_temp_file(jd_path)
                
                #process resume
                res_path = save_temp_file(resume_file)
                res_text = parse_document(res_path)
                res_data = extract_entities(res_text)
                candidate_name = res_data.get("name", "unknown")
                raw_cand_skills = res_data.get("skills", [])
                cand_skills = normalize_skills(raw_cand_skills)
                cand_exp = float(res_data.get("experience", 0))
                cleanup_temp_file(res_path)
                
                #calculate scores
                skill_score = calculate_skill_match_score(jd_skills, cand_skills)
                exp_score = calculate_experience_match(jd_exp, cand_exp)
                keyword_score = calculate_keyword_match(jd_skills, cand_skills)
                final_score = calculate_final_score(skill_score, exp_score, keyword_score)
                
                #generate ai insight
                reason = generate_explanation(
                    candidate_name, raw_cand_skills, cand_exp, 
                    jd_data.get("skills", []), jd_exp, final_score
                )
                
                #display results
                st.subheader(f"results for {candidate_name}")
                
                #use columns to display metrics clearly
                metric_col1, metric_col2, metric_col3 = st.columns(3)
                metric_col1.metric("final match score", f"{final_score}/100")
                metric_col2.metric("experience found", f"{cand_exp} years")
                metric_col3.metric("skills matched", f"{int(skill_score * 100)}%")
                
                st.info(f"**ai insight:** {reason}")
                
                with st.expander("view extracted data details"):
                    st.json({
                        "job_requirements": {
                            "skills": jd_skills,
                            "experience": jd_exp
                        },
                        "candidate_profile": {
                            "name": candidate_name,
                            "skills": cand_skills,
                            "experience": cand_exp
                        }
                    })
        else:
            st.warning("please upload both a job description and a resume to proceed.")

elif selected_tab == "batch resume ranking":
    st.header("batch resume ranking")
    st.write("paste a job description and upload multiple resumes to rank top candidates.")
    
    jd_text_input = st.text_area("paste job description text here", height=200)
    uploaded_resumes = st.file_uploader("upload multiple resumes (.pdf or .docx)", type=["pdf", "docx"], accept_multiple_files=True)
    
    if st.button("rank candidates"):
        if jd_text_input and uploaded_resumes:
            with st.spinner(f"processing job description and {len(uploaded_resumes)} resumes..."):
                #process job description from pasted text
                jd_data = extract_entities(jd_text_input)
                jd_skills = normalize_skills(jd_data.get("skills", []))
                jd_exp = float(jd_data.get("experience", 0))
                
                results_list = []
                
                #process each uploaded resume
                for res_file in uploaded_resumes:
                    res_path = save_temp_file(res_file)
                    res_text = parse_document(res_path)
                    res_data = extract_entities(res_text)
                    cleanup_temp_file(res_path)
                    
                    candidate_name = res_data.get("name", "unknown")
                    raw_cand_skills = res_data.get("skills", [])
                    cand_skills = normalize_skills(raw_cand_skills)
                    cand_exp = float(res_data.get("experience", 0))
                    
                    #calculate scores
                    skill_score = calculate_skill_match_score(jd_skills, cand_skills)
                    exp_score = calculate_experience_match(jd_exp, cand_exp)
                    keyword_score = calculate_keyword_match(jd_skills, cand_skills)
                    final_score = calculate_final_score(skill_score, exp_score, keyword_score)
                    
                    #generate ai insight
                    reason = generate_explanation(
                        candidate_name, raw_cand_skills, cand_exp, 
                        jd_data.get("skills", []), jd_exp, final_score
                    )
                    
                    #append to results list
                    results_list.append({
                        "candidate name": candidate_name,
                        "score": final_score,
                        "experience (yrs)": cand_exp,
                        "ai insight": reason
                    })
                    
                #rank the candidates
                ranked_results = sorted(results_list, key=lambda x: x["score"], reverse=True)
                
                #convert to pandas dataframe for clean display
                df = pd.DataFrame(ranked_results)
                
                st.subheader("ranked candidate results")
                st.dataframe(df, use_container_width=True)
                
        else:
            st.warning("please paste a job description and upload at least one resume.")