import datetime
import json
import uuid
from dataclasses import dataclass

from sqlalchemy.orm import Session

from src.infrastructure.database import RepoProvenanceEntry


@dataclass
class ProvenanceRecord:
    repo_url: str
    pinned_sha: str
    ingest_timestamp: datetime.datetime
    discovered_skills: list[dict[str, str]]
    validation_status: str
    policy_decision: str
    policy_reason: str


class RepoProvenanceStore:
    def write_record_atomic(self, db: Session, record: ProvenanceRecord) -> None:
        with db.begin():
            existing = db.query(RepoProvenanceEntry).filter(RepoProvenanceEntry.repo_url == record.repo_url).first()
            payload = {
                "pinned_sha": record.pinned_sha,
                "ingest_timestamp": record.ingest_timestamp,
                "discovered_skills": json.dumps(record.discovered_skills),
                "validation_status": record.validation_status,
                "policy_decision": record.policy_decision,
                "policy_reason": record.policy_reason,
            }
            if existing:
                for key, value in payload.items():
                    setattr(existing, key, value)
            else:
                db.add(
                    RepoProvenanceEntry(
                        id=str(uuid.uuid4()),
                        repo_url=record.repo_url,
                        **payload,
                    )
                )

    def list_records(self, db: Session) -> list[ProvenanceRecord]:
        rows = db.query(RepoProvenanceEntry).order_by(RepoProvenanceEntry.ingest_timestamp.desc()).all()
        return [
            ProvenanceRecord(
                repo_url=r.repo_url,
                pinned_sha=r.pinned_sha,
                ingest_timestamp=r.ingest_timestamp,
                discovered_skills=json.loads(r.discovered_skills or "[]"),
                validation_status=r.validation_status,
                policy_decision=r.policy_decision,
                policy_reason=r.policy_reason,
            )
            for r in rows
        ]


repo_provenance_store = RepoProvenanceStore()
