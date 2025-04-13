# app/database.py
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

load_dotenv()  # Loads variables from .env into environment (if you use local .env)

# Load from environment or fallback defaults
DATABASE_URL = os.getenv("DATABASE_URL")
DB_POOL_SIZE = int(os.getenv("DB_POOL_SIZE", 10))       # default = 10 connections
DB_MAX_OVERFLOW = int(os.getenv("DB_MAX_OVERFLOW", 5))  # default = 5 extra
DB_POOL_TIMEOUT = int(os.getenv("DB_POOL_TIMEOUT", 30)) # default = 30 seconds

if not DATABASE_URL:
    raise ValueError("No DATABASE_URL set for SQLAlchemy database.")

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,          # check stale connections
    pool_size=DB_POOL_SIZE,      # number of persistent connections
    max_overflow=DB_MAX_OVERFLOW,# extra connections above pool_size
    pool_timeout=DB_POOL_TIMEOUT # seconds to wait before giving up on a connection
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    """FastAPI dependency that provides a sqlalchemy session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
