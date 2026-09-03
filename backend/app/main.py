import os
import json
import logging
import time
from typing import Optional, List

from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import torch

from sqlalchemy.orm import Session

# Internal imports
from app.database import get_db, init_db, SessionLocal, engine
from app.models import Submission
from app.problems import load_problems, get_problem, list_problems
from app import judge

# Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)
logger = logging.getLogger(__name__)

# FastAPI app
app = FastAPI(
    title="RictrLab API",
    description="CPU-only PyTorch execution platform",
    version="0.1.0",
)

# CORS: allow localhost:3000 and 3001, plus all for dev
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
    ],
    allow_origin_regex=".*",  # allow all for dev as required
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Startup events
@app.on_event("startup")
async def startup_event():
    logger.info("Starting RictrLab backend...")
    # Init DB
    try:
        init_db()
        logger.info("Database initialized")
    except Exception as e:
        logger.exception(f"DB init failed: {e}")

    # Load problems
    try:
        problems = load_problems(force_reload=True)
        logger.info(f"Loaded {len(problems)} problems")
        for slug, prob in problems.items():
            logger.info(f"  - {prob.id}: {slug} -> {prob.title} ({prob.difficulty})")
    except Exception as e:
        logger.exception(f"Problem load failed: {e}")

    # Log torch info
    try:
        logger.info(f"Torch version: {torch.__version__}, threads: {torch.get_num_threads()}, deterministic: torch deterministic available")
        # Ensure CPU settings
        torch.set_num_threads(2)
        try:
            torch.use_deterministic_algorithms(True)
        except Exception:
            pass
    except Exception as e:
        logger.warning(f"Torch config failed: {e}")

# --- Pydantic Schemas for API ---
class SubmitRequest(BaseModel):
    slug: str
    code: str

class TestResultSchema(BaseModel):
    name: str
    passed: bool
    error: str = ""

class SubmitResponse(BaseModel):
    passed: int
    total: int
    results: List[TestResultSchema]
    stdout: str
    latency_ms: int
    error: Optional[str] = None

class ProblemShortOut(BaseModel):
    id: int
    slug: str
    title: str
    difficulty: str
    category: str
    description_short: str

class ProblemDetailOut(ProblemShortOut):
    prompt_md: str
    starter_code: str
    function_name: str

class HealthOut(BaseModel):
    status: str
    torch_version: str
    problems_loaded: int
    cpu_threads: int

# --- Endpoints ---

@app.get("/api/health", response_model=HealthOut, tags=["health"])
async def health():
    problems = list_problems()
    try:
        cpu_threads = torch.get_num_threads()
        torch_version = torch.__version__
    except Exception:
        cpu_threads = 0
        torch_version = "unknown"
    return {
        "status": "ok",
        "torch_version": torch_version,
        "problems_loaded": len(problems),
        "cpu_threads": cpu_threads,
    }

@app.get("/api/problems", response_model=List[ProblemShortOut], tags=["problems"])
async def get_problems():
    probs = list_problems()
    return [p.to_short_dict() for p in probs]

@app.get("/api/problems/{slug}", response_model=ProblemDetailOut, tags=["problems"])
async def get_problem_detail(slug: str):
    prob = get_problem(slug)
    if not prob:
        raise HTTPException(status_code=404, detail=f"Problem '{slug}' not found")
    return prob.to_detail_dict()

@app.post("/api/submit", response_model=SubmitResponse, tags=["judge"])
async def submit_code(payload: SubmitRequest, db: Session = Depends(get_db)):
    slug = payload.slug.strip()
    code = payload.code

    if not slug:
        raise HTTPException(status_code=400, detail="slug is required")
    if not code or not code.strip():
        raise HTTPException(status_code=400, detail="code is required and cannot be empty")

    prob = get_problem(slug)
    if not prob:
        raise HTTPException(status_code=404, detail=f"Problem '{slug}' not found")

    logger.info(f"Submission received for {slug}, code length {len(code)}")

    # Evaluate via judge (sync but fast; runs in subprocess with timeout)
    # We run judge.evaluate which is blocking; for FastAPI we can just call it (it's CPU + subprocess).
    # For better async, could run in thread pool, but simple is fine.
    start = time.time()
    try:
        result = judge.evaluate(slug, code, timeout=5)
    except Exception as e:
        logger.exception(f"Judge crashed for {slug}: {e}")
        raise HTTPException(status_code=500, detail=f"Judge error: {e}")

    latency_ms = result.get("latency_ms", int((time.time() - start) * 1000))
    passed = result.get("passed", 0)
    total = result.get("total", 0)
    results = result.get("results", [])
    stdout = result.get("stdout", "")
    error = result.get("error")

    # Normalize results for response
    normalized_results = []
    for r in results:
        normalized_results.append({
            "name": r.get("name", "test"),
            "passed": bool(r.get("passed", False)),
            "error": r.get("error", "")
        })

    # Persist submission
    try:
        submission = Submission(
            slug=slug,
            code=code,
            passed=passed,
            total=total,
            results_json=json.dumps(normalized_results),
            stdout=stdout or "",
            latency_ms=latency_ms,
        )
        db.add(submission)
        db.commit()
        db.refresh(submission)
        logger.info(f"Submission saved id={submission.id} for {slug}: {passed}/{total} in {latency_ms}ms")
    except Exception as e:
        logger.exception(f"Failed to save submission: {e}")
        # Don't fail the request if DB save fails; still return result
        db.rollback()

    return {
        "passed": passed,
        "total": total,
        "results": normalized_results,
        "stdout": stdout or "",
        "latency_ms": latency_ms,
        "error": error,
    }

@app.get("/api/submissions", tags=["submissions"])
async def list_submissions(
    slug: Optional[str] = Query(None, description="Filter by problem slug"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    query = db.query(Submission).order_by(Submission.created_at.desc())
    if slug:
        query = query.filter(Submission.slug == slug)
    total_count = query.count()
    items = query.offset(offset).limit(limit).all()

    output = []
    for s in items:
        try:
            results = json.loads(s.results_json) if s.results_json else []
        except Exception:
            results = []
        output.append({
            "id": s.id,
            "slug": s.slug,
            "passed": s.passed,
            "total": s.total,
            "results": results,
            "stdout": s.stdout,
            "latency_ms": s.latency_ms,
            "created_at": s.created_at.isoformat() if s.created_at else None,
        })

    return {"total": total_count, "items": output, "limit": limit, "offset": offset}

# Root for convenience
@app.get("/", tags=["root"])
async def root():
    return {
        "name": "RictrLab API",
        "version": "0.1.0",
        "docs": "/docs",
        "health": "/api/health",
        "problems": "/api/problems",
    }

# Entry point for `python -m app.main`
if __name__ == "__main__":
    import uvicorn
    # Ensure we use app.main:app when run via python -m
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=False)
