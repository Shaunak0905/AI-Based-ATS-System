from fastapi import FastAPI, HTTPException, UploadFile, File
import shutil
import os
from pydantic import BaseModel

from app.ingestion.resume_parser import parse_resume
from app.ingestion.jd_parser import parse_jd

from app.extraction.resume_extractor import extract_resume_info
from app.extraction.jd_extractor import extract_jd_info

from app.matchings.scorer import score_candidate
from app.explain.explanation import generate_explanation

from app.database import init_db , get_connection
import json

app = FastAPI(title="LLM based ATS System")

init_db()

class MatchRequest(BaseModel):
    resume_id: int
    jd_id: int

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

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO resumes (data) VALUES (?)",
        (json.dumps(extracted),)
    )

    resume_id = cursor.lastrowid
    conn.commit()
    conn.close()

    return {
        "resume_id": resume_id,
        "status": "stored"
    }



# Job Description Upload
@app.post("/upload-jd")
async def upload_jd(file: UploadFile = File(...)):
    file_path = save_upload(file, "data/job_descriptions")

    raw_text = parse_jd(file_path)
    extracted = extract_jd_info(raw_text)

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO job_descriptions (data) VALUES (?)",
        (json.dumps(extracted),)
    )

    jd_id = cursor.lastrowid
    conn.commit()
    conn.close()

    return {
        "jd_id": jd_id,
        "status": "stored"
    }



#Matching
@app.post("/match")
def match_by_id(payload: MatchRequest):
    resume_id = payload.resume_id
    jd_id = payload.jd_id

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT data FROM resumes WHERE id=?", (resume_id,))
    resume_row = cursor.fetchone()

    cursor.execute("SELECT data FROM job_descriptions WHERE id=?", (jd_id,))
    jd_row = cursor.fetchone()

    conn.close()

    if not resume_row or not jd_row:
        raise HTTPException(status_code=404, detail="Resume or JD not found")

    resume = json.loads(resume_row[0])
    jd = json.loads(jd_row[0])

    score = score_candidate(resume, jd)
    explanation = generate_explanation(score, resume, jd)

    return {
        "resume_id": resume_id,
        "jd_id": jd_id,
        "score": score,
        "explanation": explanation
    }
