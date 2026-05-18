from fastapi import FastAPI, BackgroundTasks, HTTPException, Depends, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import uuid
import logging
import asyncio
from sqlalchemy.orm import Session

from src.infrastructure.database import get_db, SessionLocal, JobEntry
from src.application.workflows import workflow
from src.domain.skills import skill_manager

logger = logging.getLogger("EnterpriseAPI")

app = FastAPI(title="OmniAgent DDD API", version="2.0.0")

class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

# Setup static files for frontend UI
import os
os.makedirs("src/presentation/static/css", exist_ok=True)
app.mount("/static", StaticFiles(directory="src/presentation/static"), name="static")

class JobRequest(BaseModel):
    task: str

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

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
            asyncio.run(manager.broadcast(f"Job {job_id} status updated to processing"))
        except Exception:
            pass

        try:
            plan, code, review = workflow.process_task(task)
            job.status = "completed"
            job.result = f"Plan: {plan[:50]}... Code: {code[:50]}..."
            try:
                asyncio.run(manager.broadcast(f"Job {job_id} status updated to completed"))
            except Exception:
                pass
        except Exception as e:
            logger.error(f"Job {job_id} failed: {e}")
            job.status = "failed"
            job.result = str(e)
            try:
                asyncio.run(manager.broadcast(f"Job {job_id} status updated to failed: {e}"))
            except Exception:
                pass

        db.commit()
    finally:
        db.close()

@app.get("/", response_class=HTMLResponse)
async def serve_dashboard():
    with open("src/presentation/templates/index.html", "r") as f:
        return f.read()
