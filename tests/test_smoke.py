# tests/test_smoke.py
from sqlalchemy import text

def test_pytest_works():
    assert 1 + 1 == 2

def test_sqlite_in_memory(db):
    result = db.execute(text("SELECT 1")).scalar()
    assert result == 1