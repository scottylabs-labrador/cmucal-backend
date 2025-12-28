# app/services/db.py
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Base class for models
Base = declarative_base()

engine = None
SessionLocal = None

def get_database_url():
    """
    Decide which DB to use based on environment.
    """
    env = os.getenv("APP_ENV", "development")

    if env == "test":
        # SQLite in-memory DB for pytest
        return "sqlite+pysqlite:///:memory:"

    # Default: Supabase / production / dev DB
    return os.getenv("SUPABASE_DB_URL")

if not os.getenv("ALEMBIC_RUNNING"):
    DATABASE_URL = get_database_url()
    # Create SQLAlchemy engine
    engine = create_engine(DATABASE_URL, echo=False, pool_pre_ping=True)
    # Session maker for DB sessions
    SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


