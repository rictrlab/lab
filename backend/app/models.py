from sqlalchemy import Column, Integer, String, Text, Float, DateTime, Boolean
from sqlalchemy.sql import func
from app.database import Base
from pydantic import BaseModel
from typing import List, Optional, Any
from datetime import datetime

class Submission(Base):
    __tablename__ = "submissions"

    id = Column(Integer, primary_key=True, index=True)
    slug = Column(String, index=True, nullable=False)
    code = Column(Text, nullable=False)
    passed = Column(Integer, nullable=False)  # number passed
    total = Column(Integer, nullable=False)
    results_json = Column(Text, nullable=True)  # JSON string of results
    stdout = Column(Text, nullable=True)
    latency_ms = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

# Pydantic schemas

class ProblemShort(BaseModel):
    id: int
    slug: str
    title: str
    difficulty: str
    category: str
    description_short: str

class ProblemDetail(ProblemShort):
    prompt_md: str
    starter_code: str
    function_name: str

class TestResult(BaseModel):
    name: str
    passed: bool
    error: str = ""

class SubmitRequest(BaseModel):
    slug: str
    code: str

class SubmitResponse(BaseModel):
    passed: int
    total: int
    results: List[TestResult]
    stdout: str
    latency_ms: int
    error: Optional[str] = None

class SubmissionOut(BaseModel):
    id: int
    slug: str
    passed: int
    total: int
    stdout: Optional[str]
    latency_ms: Optional[int]
    created_at: Optional[datetime]

    class Config:
        from_attributes = True

class HealthResponse(BaseModel):
    status: str
    torch_version: str
    problems_loaded: int
