import pytest
from app.models.admin import create_admin

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
