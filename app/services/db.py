# app/services/db.py
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

Base = declarative_base()

_engine = None
_SessionLocal = None


def get_database_url():
    env = os.getenv("APP_ENV", "development")

    if env == "test":
        return os.getenv("TEST_DATABASE_URL")

    return os.getenv("SUPABASE_DB_URL")


def init_db():
    global _engine, _SessionLocal

    if _engine is not None:
        return _engine, _SessionLocal

    db_url = get_database_url()

    if os.getenv("PYTEST_CURRENT_TEST") and "test" not in db_url:
        raise RuntimeError("❌ Pytest running on non-test database")

    _engine = create_engine(
        db_url,
        echo=False,
        pool_pre_ping=True,
    )
    _SessionLocal = sessionmaker(
        bind=_engine,
        autocommit=False,
        autoflush=False,
    )

    return _engine, _SessionLocal


def get_engine():
    if _engine is None:
        raise RuntimeError("DB not initialized. Call init_db() first.")
    return _engine

def get_session():
    if _SessionLocal is None:
        raise RuntimeError("DB not initialized. Call init_db() first.")
    session = _SessionLocal()
    print(f"[DB] Session opened {id(session)}")
    return session