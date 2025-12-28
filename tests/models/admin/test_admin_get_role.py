# tests/models/admin/test_admin_get_role.py
from app.models.admin import get_role

# ---------- NO ROLES ----------
def test_get_role_no_admin_entries(db, user_factory):
    user = user_factory()

    is_manager, is_admin, role_orgs = get_role(db, user_id=user.id)

    assert is_manager is False
    assert is_admin is False
    assert role_orgs == []


# ---------- ADMIN ONLY ----------
def test_get_role_admin_only(db, user_factory, org_factory, admin_factory):
    user = user_factory()
    org = org_factory()

    admin_factory(user=user, org=org, role="admin")

    is_manager, is_admin, role_orgs = get_role(db, user_id=user.id)

    assert is_manager is False
    assert is_admin is True
    assert role_orgs == [("admin", org.id)]


# ---------- MANAGER ONLY ----------
def test_get_role_manager_only(db, user_factory, org_factory, admin_factory):
    user = user_factory()
    org = org_factory()

    admin_factory(user=user, org=org, role="manager")

    is_manager, is_admin, role_orgs = get_role(db, user_id=user.id)

    assert is_manager is True
    assert is_admin is False
    assert role_orgs == [("manager", org.id)]


# ---------- MULTIPLE ROLES ----------
def test_get_role_multiple_roles(db, user_factory, org_factory, admin_factory):
    user = user_factory()
    org1 = org_factory()
    org2 = org_factory()

    admin_factory(user=user, org=org1, role="admin")
    admin_factory(user=user, org=org2, role="manager")

    is_manager, is_admin, role_orgs = get_role(db, user_id=user.id)

    assert is_manager is True
    assert is_admin is True
    assert set(role_orgs) == {
        ("admin", org1.id),
        ("manager", org2.id),
    }
