from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import uuid
import logging
from typing import Dict, Any

from omni_agent.utils.logging_config import setup_enterprise_logging
from omni_agent.main import OmniAgentWorker
from omni_agent.utils.skill_manager import skill_manager
from omni_agent.utils.memory import agent_memory

logger = logging.getLogger("EnterpriseAPI")

app = FastAPI(
    title="OmniAgent Enterprise",
    description="Autonomous software engineering capabilities via REST API.",
    version="1.0.0"
)

# Enterprise mock job store
job_store: Dict[str, Dict[str, Any]] = {}
worker = OmniAgentWorker()

class JobRequest(BaseModel):
    task: str

class JobResponse(BaseModel):
    job_id: str
    status: str

@app.post("/api/v1/jobs", response_model=JobResponse)
async def create_job(request: JobRequest, background_tasks: BackgroundTasks):
    job_id = str(uuid.uuid4())
    job_store[job_id] = {"status": "pending", "task": request.task, "result": None}

    background_tasks.add_task(execute_job, job_id, request.task)
    logger.info(f"Job {job_id} queued: {request.task[:50]}...")
    return JobResponse(job_id=job_id, status="pending")

@app.get("/api/v1/jobs")
async def list_jobs() -> Dict[str, Any]:
    return job_store

@app.get("/api/v1/jobs/{job_id}")
async def get_job_status(job_id: str) -> Dict[str, Any]:
    job = job_store.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job

@app.get("/api/v1/skills")
async def get_skills() -> Dict[str, Any]:
    return {"skills": skill_manager.list_skills()}

@app.get("/api/v1/memory")
async def get_memory() -> Dict[str, Any]:
    lessons = agent_memory.retrieve_lessons("")
    return {"memory_context": lessons}

def execute_job(job_id: str, task: str) -> None:
    job_store[job_id]["status"] = "processing"
    try:
        if "github.com" in task.lower() or "absorb" in task.lower():
            success = worker.process_absorption(task)
            if success:
                job_store[job_id]["status"] = "completed"
                job_store[job_id]["result"] = "Absorption successful."
            else:
                job_store[job_id]["status"] = "failed"
                job_store[job_id]["result"] = "Absorption validation failed."
        else:
            plan, code, final_review = worker.process_task(task)
            job_store[job_id]["status"] = "completed"
            job_store[job_id]["result"] = {
                "plan": plan,
                "code": code,
                "review": final_review
            }
        logger.info(f"Job {job_id} successfully completed.")
    except Exception as e:
        logger.error(f"Job {job_id} failed: {e}")
        job_store[job_id]["status"] = "failed"
        job_store[job_id]["result"] = str(e)

@app.get("/", response_class=HTMLResponse)
async def serve_dashboard():
    with open("omni_agent/api/static/index.html", "r") as f:
        return HTMLResponse(content=f.read())
