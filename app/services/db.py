# app/services/db.py
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Base class for models
Base = declarative_base()

engine = None
SessionLocal = None

if not os.getenv("ALEMBIC_RUNNING"):
    DATABASE_URL = os.getenv("SUPABASE_DB_URL")
    # Create SQLAlchemy engine
    engine = create_engine(DATABASE_URL, echo=False, pool_pre_ping=True)
    # Session maker for DB sessions
    SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


