import os
import glob
import requests
import json

#Point to your local FastAPI server
url = "http://localhost:8000/match"

print("[+] Initializing payload...")
#Job Description
files = [
    ('jd_file', ('jd.docx', open('data/job_descriptions/jd.docx', 'rb')))
]

#utomatically grab every single resume in the directory
resume_paths = glob.glob('data/raw_resumes/*')
file_handles = []

for resume_path in resume_paths:
    if os.path.isfile(resume_path):
        filename = os.path.basename(resume_path)
        f_handle = open(resume_path, 'rb')
        file_handles.append(f_handle)
        files.append(('resume_files', (filename, f_handle)))

print(f"[+] Sending request to FastAPI with JD and {len(file_handles)} resumes...")
print("    (This may take a minute or two as it processes each candidate via the local LLM)")

response = requests.post(url, files=files)

print("\n--- Final API Response ---")
print(json.dumps(response.json(), indent=2))

#Cleanup open file handles
for f in file_handles:
    f.close()
