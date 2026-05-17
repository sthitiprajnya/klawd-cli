from fastapi import FastAPI, BackgroundTasks, HTTPException, Depends
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import uuid
import logging
from sqlalchemy.orm import Session

from src.infrastructure.database import get_db, SessionLocal, JobEntry
from src.application.workflows import workflow
from src.domain.skills import skill_manager

logger = logging.getLogger("EnterpriseAPI")

app = FastAPI(title="OmniAgent DDD API", version="2.0.0")

# Setup static files for frontend UI
import os
os.makedirs("src/presentation/static/css", exist_ok=True)
app.mount("/static", StaticFiles(directory="src/presentation/static"), name="static")

class JobRequest(BaseModel):
    task: str

@app.post("/api/v1/jobs")
async def create_job(request: JobRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    job_id = str(uuid.uuid4())
    job = JobEntry(id=job_id, task=request.task, status="pending")
    db.add(job)
    db.commit()

    background_tasks.add_task(execute_job, job_id, request.task)
    return {"job_id": job_id, "status": "pending"}

@app.get("/api/v1/jobs")
async def list_jobs(db: Session = Depends(get_db)):
    jobs = db.query(JobEntry).order_by(JobEntry.created_at.desc()).limit(20).all()
    return {j.id: {"task": j.task, "status": j.status} for j in jobs}

@app.get("/api/v1/skills")
async def get_skills():
    return {"skills": skill_manager.list_skills()}

def execute_job(job_id: str, task: str):
    db = SessionLocal()
    try:
        job = db.query(JobEntry).filter(JobEntry.id == job_id).first()
        if not job: return

        job.status = "processing"
        db.commit()

        try:
            plan, code, review = workflow.process_task(task)
            job.status = "completed"
            job.result = f"Plan: {plan[:50]}... Code: {code[:50]}..."
        except Exception as e:
            logger.error(f"Job {job_id} failed: {e}")
            job.status = "failed"
            job.result = str(e)

        db.commit()
    finally:
        db.close()

@app.get("/", response_class=HTMLResponse)
async def serve_dashboard():
    with open("src/presentation/templates/index.html", "r") as f:
        return f.read()
