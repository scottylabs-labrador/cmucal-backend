# tests/conftest.py
import itertools
import os
import sys
import pytest

# Add project root to python path so imports work
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import create_app
from app.services.db import Base, engine, SessionLocal
from app.models.models import User, Organization
from app.models.admin import create_admin


# ---------- Flask App ----------
@pytest.fixture(scope="session")
def app():
    os.environ["APP_ENV"] = "test"
    app = create_app()
    app.config["TESTING"] = True
    yield app


@pytest.fixture
def client(app):
    return app.test_client()


# ---------- Database ----------
@pytest.fixture
def db(app):
    from app.models import models  # ensure models are registered

    Base.metadata.create_all(bind=engine)
    session = SessionLocal()

    try:
        yield session
    finally:
        session.rollback()
        session.close()
        Base.metadata.drop_all(bind=engine)


# ---------- ID COUNTERS ----------
_user_counter = itertools.count(1)
_org_counter = itertools.count(1)


# ---------- FACTORY FIXTURES ----------
@pytest.fixture
def user_factory(db):
    def create_user(**kwargs):
        user_id = kwargs.pop("id", next(_user_counter))
        user = User(
            id=user_id,
            email=kwargs.pop("email", f"user{user_id}@test.com"),
            clerk_id=kwargs.pop("clerk_id", f"clerk_user_{user_id}"),
            **kwargs,
        )
        db.add(user)
        db.commit()
        return user

    return create_user


@pytest.fixture
def org_factory(db):
    def create_org(**kwargs):
        org_id = kwargs.pop("id", next(_org_counter))
        org = Organization(
            id=org_id,
            name=kwargs.pop("name", f"Org {org_id}"),
            **kwargs,
        )
        db.add(org)
        db.commit()
        return org

    return create_org


@pytest.fixture
def admin_factory(db):
    def create_admin_factory(*, user, org, role="admin", category_id=None):
        return create_admin(
            db,
            org_id=org.id,
            user_id=user.id,
            role=role,
            category_id=category_id,
        )

    return create_admin_factory
