from fastapi import FastAPI, BackgroundTasks, Depends, WebSocket, WebSocketDisconnect, Query, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
import uuid
import logging
import asyncio
import datetime
from sqlalchemy.orm import Session
from sqlalchemy import text

from src.infrastructure.database import get_db, SessionLocal, JobEntry
from src.application.workflows import workflow
from src.domain.skills import skill_manager
from src.infrastructure.memory.agent_memory import agent_memory
from src.infrastructure.security.execution_adapter import execution_adapter, PolicyRejectionError

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

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            await connection.send_json(message)

manager = ConnectionManager()

@app.on_event("startup")
async def startup_policy_validation():
    execution_adapter.startup_validate()


# Setup static files for frontend UI
import os
os.makedirs("src/presentation/static/css", exist_ok=True)
app.mount("/static", StaticFiles(directory="src/presentation/static"), name="static")

class JobRequest(BaseModel):
    task: str
    priority: str = Field(default="normal")
    tags: list[str] = Field(default_factory=list)


class JobCreateResponse(BaseModel):
    job_id: str
    status: str
    queue_position: int
    queue_depth: int
    priority: str
    tags: list[str]


class JobStatusResponse(BaseModel):
    job_id: str
    task: str
    status: str
    result: str | None
    priority: str
    tags: list[str]
    created_at: datetime.datetime | None

@app.websocket("/ws/jobs")
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
    task_with_meta = f"{request.task}\n[priority={request.priority};tags={','.join(request.tags)}]"
    job = JobEntry(id=job_id, task=task_with_meta, status="pending")
    db.add(job)
    db.commit()

    pending_jobs = db.query(JobEntry).filter(JobEntry.status == "pending").count()
    background_tasks.add_task(execute_job, job_id, request.task)
    return JobCreateResponse(
        job_id=job_id,
        status="pending",
        queue_position=pending_jobs,
        queue_depth=pending_jobs,
        priority=request.priority,
        tags=request.tags,
    )


@app.get("/api/v1/jobs/{job_id}")
async def get_job(job_id: str, db: Session = Depends(get_db)):
    job = db.query(JobEntry).filter(JobEntry.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return JobStatusResponse(
        job_id=job.id,
        task=job.task,
        status=job.status,
        result=job.result,
        priority="normal",
        tags=[],
        created_at=job.created_at,
    )

@app.get("/api/v1/jobs")
async def list_jobs(limit: int = Query(default=20, ge=1, le=200), offset: int = Query(default=0, ge=0), db: Session = Depends(get_db)):
    total = db.query(JobEntry).count()
    jobs = db.query(JobEntry).order_by(JobEntry.created_at.desc()).offset(offset).limit(limit).all()
    return {
        "jobs": [
            {"job_id": j.id, "task": j.task, "status": j.status, "result": j.result, "created_at": j.created_at}
            for j in jobs
        ],
        "total": total,
        "limit": limit,
        "offset": offset,
    }


@app.get("/api/v1/health")
async def health(db: Session = Depends(get_db)):
    db.execute(text("SELECT 1"))
    memory_status = "up"
    try:
        agent_memory.retrieve_lessons("health-check")
    except Exception:
        memory_status = "degraded"
    nemo = execution_adapter.health()
    return {"status": "ok", "services": {"api": "up", "database": "up", "memory": memory_status, "nemoclaw": nemo.status}, "nemoclaw_reason": nemo.reason}


@app.get("/api/v1/memory/search")
async def memory_search(q: str):
    return {"query": q, "results": agent_memory.retrieve_lessons(q)}

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
            asyncio.run(manager.broadcast({"type": "job_update", "job_id": job_id, "status": "processing"}))
        except Exception:
            pass

        try:
            plan, code, review = workflow.process_task(task)
            job.status = "completed"
            job.result = f"Plan: {plan[:50]}... Code: {code[:50]}..."
            try:
                asyncio.run(manager.broadcast({"type": "job_update", "job_id": job_id, "status": "completed"}))
            except Exception:
                pass
        except Exception as e:
            logger.error(f"Job {job_id} failed: {e}")
            job.status = "failed"
            job.result = str(e)
            try:
                asyncio.run(manager.broadcast({"type": "job_update", "job_id": job_id, "status": "failed", "error": str(e)}))
            except Exception:
                pass

        db.commit()
    finally:
        db.close()

@app.get("/", response_class=HTMLResponse)
async def serve_dashboard():
    with open("src/presentation/templates/index.html", "r") as f:
        return f.read()
