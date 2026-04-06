import os
import sys

# Add the project directory to sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_dir = os.path.dirname(current_dir)
sys.path.append(project_dir)

from src.document_parser import parse_document

def test_document_parser():
    print("--- Testing Document Parser ---")
    
    #Test PDF Resume
    pdf_resume = os.path.join(project_dir, "data", "raw_resumes", "resume_barkha_pant.pdf")
    if os.path.exists(pdf_resume):
        print(f"\n[+] Parsing PDF Resume: {pdf_resume}")
        parsed_text = parse_document(pdf_resume)
        print("-> Extracted text preview (first 200 chars):")
        print(parsed_text[:200].replace('\n', ' '))
    else:
        print(f"\n[-] Skipped PDF Resume test: File not found at {pdf_resume}")

    #Test DOCX Resume
    docx_resume = os.path.join(project_dir, "data", "raw_resumes", "resume_aarush_seth.docx")
    if os.path.exists(docx_resume):
        print(f"\n[+] Parsing DOCX Resume: {docx_resume}")
        parsed_text = parse_document(docx_resume)
        print("-> Extracted text preview (first 200 chars):")
        print(parsed_text[:200].replace('\n', ' '))
    else:
        print(f"\n[-] Skipped DOCX Resume test: File not found at {docx_resume}")

    #Test DOCX Job Description
    jd_docx = os.path.join(project_dir, "data", "job_descriptions", "jd.docx")
    if os.path.exists(jd_docx):
        print(f"\n[+] Parsing DOCX Job Description: {jd_docx}")
        parsed_text = parse_document(jd_docx)
        print("-> Extracted text preview (first 200 chars):")
        print(parsed_text[:200].replace('\n', ' '))
    else:
        print(f"\n[-] Skipped DOCX JD test: File not found at {jd_docx}")

    print("\n--- Document Parser Tests Completed ---")

if __name__ == "__main__":
    test_document_parser()
