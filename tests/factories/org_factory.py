import pytest
from app.models.models import Organization

@pytest.fixture
def org_factory(db):
    def create_org(**kwargs):
        org = Organization(
            name=kwargs.pop("name", "Test Org"),
            **kwargs,
        )
        db.add(org)
        db.commit()
        return org
    return create_org
