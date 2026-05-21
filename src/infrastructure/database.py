from __future__ import annotations
from __future__ import annotations
from __future__ import annotations
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, UniqueConstraint
from sqlalchemy.orm import declarative_base, sessionmaker
import datetime

import os

DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///jobs.db")

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


class JobEntry(Base):
    __tablename__ = "jobs"

    id = Column(String, primary_key=True, index=True)
    task = Column(Text, nullable=False)
    status = Column(String, index=True, nullable=False)
    result = Column(Text, nullable=True)

    priority = Column(String, default="normal", nullable=False)
    model_used = Column(String, nullable=True)
    tokens_used = Column(Integer, default=0, nullable=False)
    latency_ms = Column(Integer, default=0, nullable=False)
    agent_trace = Column(Text, nullable=True)
    skills_absorbed = Column(Text, nullable=True)
    threat_score = Column(Integer, default=0, nullable=False)

    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    error = Column(Text, nullable=True)


class RepoProvenanceEntry(Base):
    __tablename__ = "repo_provenance"
    __table_args__ = (UniqueConstraint("repo_url", name="uq_repo_provenance_repo_url"),)

    id = Column(String, primary_key=True, index=True)
    repo_url = Column(Text, nullable=False, index=True)
    pinned_sha = Column(String, nullable=False)
    ingest_timestamp = Column(DateTime, nullable=False, default=datetime.datetime.utcnow)
    discovered_skills = Column(Text, nullable=False, default="[]")
    validation_status = Column(String, nullable=False, default="unknown")
    policy_decision = Column(String, nullable=False, default="deny")
    policy_reason = Column(String, nullable=False, default="unspecified")


Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
