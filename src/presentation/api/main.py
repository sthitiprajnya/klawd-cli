import asyncio
import datetime
import logging
import os
import uuid
from contextlib import asynccontextmanager
from typing import Literal

from fastapi import (
    BackgroundTasks,
    Depends,
    FastAPI,
    HTTPException,
    Query,
    WebSocket,
    WebSocketDisconnect,
)
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.orm import Session

from src.application.workflows import workflow
from src.domain.skills import skill_manager
from src.infrastructure.database import JobEntry, SessionLocal, get_db
from src.infrastructure.memory.agent_memory import agent_memory
from src.infrastructure.provenance import repo_provenance_store
from src.infrastructure.security.execution_adapter import (
    execution_adapter,
)

logger = logging.getLogger("EnterpriseAPI")

@asynccontextmanager
async def lifespan(app: FastAPI):
    execution_adapter.startup_validate()
    yield

app = FastAPI(title="OmniAgent DDD API", version="2.0.0", lifespan=lifespan)
JobStatus = Literal["queued", "running", "completed", "failed", "completed_partial"]


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

def _broadcast_sync(message: dict) -> None:
    """Fire-and-forget broadcast from a sync thread."""
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            asyncio.run_coroutine_threadsafe(manager.broadcast(message), loop)
        else:
            loop.run_until_complete(manager.broadcast(message))
    except Exception:
        pass  # Broadcast failure must never crash a job


def _workflow_transition_sink(event: dict):
    try:
        _broadcast_sync(event)
    except Exception:
        pass





# Setup static files for frontend UI

os.makedirs("src/presentation/static/css", exist_ok=True)
app.mount("/static", StaticFiles(directory="src/presentation/static"), name="static")


class JobRequest(BaseModel):
    task: str = Field(min_length=1)
    priority: str = Field(default="normal")
    tags: list[str] = Field(default_factory=list)


class JobTelemetry(BaseModel):
    model_used: str | None
    tokens_used: int
    latency_ms: int
    threat_score: int


class JobResponse(BaseModel):
    job_id: str
    task: str
    status: JobStatus
    priority: str
    result: str | None
    error: str | None
    created_at: datetime.datetime | None
    started_at: datetime.datetime | None
    completed_at: datetime.datetime | None
    telemetry: JobTelemetry


class JobCreateResponse(BaseModel):
    job: JobResponse


class JobListResponse(BaseModel):
    jobs: list[JobResponse]
    total: int
    limit: int
    offset: int


class HealthResponse(BaseModel):
    status: str
    services: dict[str, str]


class MemorySearchResponse(BaseModel):
    query: str
    results: list[str]


class SkillsResponse(BaseModel):
    skills: list[str]


class RepoProvenanceResponse(BaseModel):
    repo_url: str
    pinned_sha: str
    ingest_timestamp: datetime.datetime
    discovered_skills: list[dict[str, str]]
    validation_status: str
    policy_decision: str
    policy_reason: str


class RepoProvenanceListResponse(BaseModel):
    records: list[RepoProvenanceResponse]


class JobUpdateFrame(BaseModel):
    type: Literal["job_update"]
    job_id: str
    status: JobStatus
    error: str | None = None
    telemetry: JobTelemetry | None = None


class DeadLetterRequest(BaseModel):
    task: str
    reason: str
    attempts: int
    timestamp: str


def _to_job_response(job: JobEntry) -> JobResponse:
    return JobResponse(
        job_id=job.id,
        task=job.task,
        status=job.status,
        priority=job.priority,
        result=job.result,
        error=job.error,
        created_at=job.created_at,
        started_at=job.started_at,
        completed_at=job.completed_at,
        telemetry=JobTelemetry(
            model_used=job.model_used,
            tokens_used=job.tokens_used or 0,
            latency_ms=job.latency_ms or 0,
            threat_score=job.threat_score or 0,
        ),
    )


@app.websocket("/ws/jobs")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)


@app.post("/api/v1/jobs", response_model=JobCreateResponse)
async def create_job(request: JobRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    job_id = str(uuid.uuid4())
    job = JobEntry(id=job_id, task=request.task, status="queued", priority=request.priority)
    db.add(job)
    db.commit()
    db.refresh(job)
    background_tasks.add_task(execute_job, job_id, request.task)
    return JobCreateResponse(job=_to_job_response(job))


@app.get("/api/v1/jobs/{job_id}", response_model=JobResponse)
async def get_job(job_id: str, db: Session = Depends(get_db)):
    job = db.query(JobEntry).filter(JobEntry.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return _to_job_response(job)


@app.get("/api/v1/jobs", response_model=JobListResponse)
async def list_jobs(limit: int = Query(default=20, ge=1, le=200), offset: int = Query(default=0, ge=0), db: Session = Depends(get_db)):
    total = db.query(JobEntry).count()
    jobs = db.query(JobEntry).order_by(JobEntry.created_at.desc()).offset(offset).limit(limit).all()
    return JobListResponse(jobs=[_to_job_response(j) for j in jobs], total=total, limit=limit, offset=offset)


@app.get("/api/v1/health", response_model=HealthResponse)
async def health(db: Session = Depends(get_db)):
    db.execute(text("SELECT 1"))
    memory_status = "up"
    try:
        agent_memory.retrieve_lessons("health-check")
    except Exception:
        memory_status = "degraded"
    # nemo = execution_adapter.health()
    return HealthResponse(status="ok", services={"api": "up", "database": "up", "memory": memory_status})


@app.get("/api/v1/memory/search", response_model=MemorySearchResponse)
async def memory_search(q: str):
    return MemorySearchResponse(query=q, results=agent_memory.retrieve_lessons(q))


@app.get("/api/v1/skills", response_model=SkillsResponse)
async def get_skills():
    return SkillsResponse(skills=skill_manager.list_skills())


@app.get("/api/v1/skills/provenance", response_model=RepoProvenanceListResponse)
async def get_skills_provenance(db: Session = Depends(get_db)):
    records = repo_provenance_store.list_records(db)
    return RepoProvenanceListResponse(records=[RepoProvenanceResponse(**r.__dict__) for r in records])


@app.post("/api/v1/dead-letter", status_code=202)
async def dead_letter(request: DeadLetterRequest):
    logger.critical(
        "DEAD LETTER: task=%s reason=%s attempts=%d timestamp=%s",
        request.task, request.reason, request.attempts, request.timestamp,
    )
    # Future: persist to a dead_letter_queue table
    return {"status": "accepted", "message": "Task moved to dead-letter queue"}


def execute_job(job_id: str, task: str):
    db = SessionLocal()
    try:
        job = db.query(JobEntry).filter(JobEntry.id == job_id).first()
        if not job:
            return
        job.status = "running"
        job.started_at = datetime.datetime.utcnow()
        db.commit()

        try:
            _broadcast_sync({"type": "job_update", "job_id": job_id, "status": "running"})
        except Exception:
            pass

        try:
            plan, code, feedback = workflow.process_task(task)
            job.status = "completed"
            job.result = f"Plan: {str(plan)[:200]}\n\nCode: {str(code)[:500]}"
            job.completed_at = datetime.datetime.utcnow()
            db.commit()
            try:
                _broadcast_sync({"type": "job_update", "job_id": job_id, "status": "completed"})
            except Exception:
                pass
        except Exception as e:
            logger.error("Job %s failed: %s", job_id, e)
            job.status = "failed"
            job.error = str(e)
            job.completed_at = datetime.datetime.utcnow()
            db.commit()
            try:
                _broadcast_sync({"type": "job_update", "job_id": job_id, "status": "failed", "error": str(e)})
            except Exception:
                pass
    finally:
        db.close()


@app.get("/", response_class=HTMLResponse)
async def serve_dashboard():
    with open("src/presentation/templates/index.html", "r") as f:
        return f.read()
