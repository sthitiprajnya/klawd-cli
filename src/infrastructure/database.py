from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
import datetime

DATABASE_URL = "sqlite:///mempalace_mock.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class MemoryEntry(Base):
    __tablename__ = "memory_entries"

    id = Column(Integer, primary_key=True, index=True)
    task = Column(Text, index=True)
    result = Column(Text)
    feedback = Column(Text)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

class JobEntry(Base):
    __tablename__ = "jobs"

    id = Column(String, primary_key=True, index=True)
    task = Column(Text)
    status = Column(String, index=True)
    result = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
