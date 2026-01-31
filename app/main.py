from fastapi import FastAPI, UploadFile, File
import shutil
import os

from app.ingestion.resume_parser import parse_resume
from app.ingestion.jd_parser import parse_jd

from app.extraction.resume_extractor import extract_resume_info
from app.extraction.jd_extractor import extract_jd_info

from app.matchings.scorer import score_candidate
from app.explain.explanation import generate_explanation

from app.database import init_db   

app = FastAPI(title="LLM based ATS System")


# Save uploaded file
def save_upload(file: UploadFile, folder: str) -> str:
    os.makedirs(folder, exist_ok=True)
    file_path = os.path.join(folder, file.filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return file_path


# Health Checkup
@app.get("/")
def root():
    return {"status": "ATS server running"}


#Resume Upload
@app.post("/upload-resume")
async def upload_resume(file: UploadFile = File(...)):
    file_path = save_upload(file, "data/resumes")

    raw_text = parse_resume(file_path)
    extracted = extract_resume_info(raw_text)

    return {
        "filename": file.filename,
        "resume_data": extracted
    }


# Job Description Upload
@app.post("/upload-jd")
async def upload_jd(file: UploadFile = File(...)):
    file_path = save_upload(file, "data/job_descriptions")

    raw_text = parse_jd(file_path)
    extracted = extract_jd_info(raw_text)

    return {
        "filename": file.filename,
        "job_description": extracted
    }


#Matching
@app.post("/match")
def match_resume_to_jd(resume: dict, jd: dict):
    score = score_candidate(resume, jd)
    explanation = generate_explanation(score, resume, jd)

    return {
        "score": score,
        "explanation": explanation
    }
