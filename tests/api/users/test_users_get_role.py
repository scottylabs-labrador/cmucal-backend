from unittest.mock import MagicMock


# ---------- SUCCESS CASE ----------
def test_get_role_success(client, mocker):
    # Mock a user returned from get_user_by_clerk_id
    mock_user = MagicMock()
    mock_user.id = 42

    # Patch dependencies where they are imported
    mocker.patch("app.api.users.get_user_by_clerk_id", return_value=mock_user)

    mocker.patch(
        "app.api.users.get_role",
        return_value=(True, False, [("admin", 1), ("manager", 2)]),
    )

    # Call endpoint
    resp = client.get(
        "/api/users/get_role", headers={"Clerk-User-Id": "clerk_test_123"}
    )

    # Assertions
    assert resp.status_code == 200

    data = resp.get_json()
    assert data["is_manager"] is True
    assert data["is_admin"] is False
    assert data["roles"] == [
        {"role": "admin", "org_id": 1},
        {"role": "manager", "org_id": 2},
    ]


# ---------- MISSING HEADER ----------
def test_get_role_missing_clerk_id(client):
    resp = client.get("/api/users/get_role")

    assert resp.status_code == 400
    assert "Missing clerk_id" in resp.get_json()["error"]


# ---------- USER NOT FOUND ----------
def test_get_role_user_not_found(client, mocker):
    mocker.patch("app.api.users.get_user_by_clerk_id", return_value=None)

    resp = client.get("/api/users/get_role", headers={"Clerk-User-Id": "clerk_missing"})

    assert resp.status_code == 404
    assert "User not found" in resp.get_json()["error"]


# ---------- INTERNAL ERROR ----------
def test_get_role_internal_error(client, mocker):
    mocker.patch(
        "app.api.users.get_user_by_clerk_id", side_effect=Exception("DB exploded")
    )

    resp = client.get("/api/users/get_role", headers={"Clerk-User-Id": "clerk_test"})

    assert resp.status_code == 500
    assert "DB exploded" in resp.get_json()["error"]
