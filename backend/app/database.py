import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# SQLite file next to backend/ (repo-relative, portable: local, Docker, HF Spaces)
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "app.db")
# Legacy absolute path on the original dev machine — only used if it exists
ALT_PATH = "/home/pandeyps/Prefix/rictrlab/backend/app.db"
# Env override wins (e.g. DATABASE_FILE=/data/app.db on HF persistent storage)
DB_FILE = os.environ.get("DATABASE_FILE") or (ALT_PATH if os.path.exists(ALT_PATH) else DB_PATH)
# Ensure directory exists
os.makedirs(os.path.dirname(DB_FILE) or ".", exist_ok=True)

# Full URL override also supported (e.g. external Postgres)
SQLITE_URL = os.environ.get("DATABASE_URL", f"sqlite:///{DB_FILE}")

# Echo False for production
engine = create_engine(
    SQLITE_URL, connect_args={"check_same_thread": False}, echo=False
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    # Import models to register tables before create_all
    from app.models import Submission  # noqa: F401
    Base.metadata.create_all(bind=engine)
