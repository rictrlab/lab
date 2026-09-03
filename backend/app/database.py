import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# SQLite file at backend/app.db (as required)
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "app.db")
# Also support absolute path requested
ALT_PATH = "/home/pandeyps/Prefix/rictrlab/backend/app.db"
# Ensure directory exists
os.makedirs(os.path.dirname(ALT_PATH), exist_ok=True)

# Use ALT_PATH as canonical
SQLITE_URL = f"sqlite:///{ALT_PATH}"

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
