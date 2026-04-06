import os
import sys

# Add the project directory to sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_dir = os.path.dirname(current_dir)
sys.path.append(project_dir)

from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)

def test_api():
    print("--- Testing FastAPI Endpoints ---")
    
    #Test Health Endpoint
    print("\n[+] 1. Testing GET / (Health Check)")
    response = client.get("/")
    if response.status_code == 200:
        print("    Success! Response:", response.json())
    else:
        print("    Failed with status:", response.status_code)
        
    #Test Extract Endpoint
    print("\n[+] 2. Testing POST /extract")
    resume_path = os.path.join(project_dir, "data", "raw_resumes", "resume_aarush_seth.docx")
    
    if os.path.exists(resume_path):
        with open(resume_path, "rb") as f:
            #Send file request
            response = client.post(
                "/extract", 
                files={"file": ("resume_aarush_seth.docx", f, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")}
            )
            
        if response.status_code == 200:
            print("    Success! Extracted JSON Response:")
            print("   ", response.json())
        else:
            print("    Failed with status:", response.status_code)
            print("    Response:", response.text)
    else:
        print("    [-] Skipped: Could not find resume to test upload.")
        
    print("\n--- API Tests Completed ---")

if __name__ == "__main__":
    test_api()
