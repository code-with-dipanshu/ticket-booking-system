"""Tests for the Authentication endpoints (register, login, me, RBAC)."""


def _register_user(client, email="user@test.com", password="secret123",
                   full_name="Test User", role_name="customer"):
    """Helper to register a user via the API."""
    return client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": password,
            "full_name": full_name,
            "role_name": role_name,
        },
    )


def _login_user(client, email="user@test.com", password="secret123"):
    """Helper to login and return the access token."""
    response = client.post(
        "/api/v1/auth/login",
        data={"username": email, "password": password},
    )
    return response


def _get_auth_header(client, email="user@test.com", password="secret123"):
    """Helper to register, login, and return the Authorization header."""
    resp = _login_user(client, email, password)
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


# --- Registration Tests ---


class TestRegistration:

    def test_register_success(self, client):
        response = _register_user(client)
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "user@test.com"
        assert data["full_name"] == "Test User"
        assert data["role_name"] == "customer"
        assert data["is_active"] is True
        assert "id" in data

    def test_register_duplicate_email(self, client):
        _register_user(client)
        response = _register_user(client)
        assert response.status_code == 400
        assert "already registered" in response.json()["detail"]

    def test_register_invalid_role(self, client):
        response = _register_user(client, role_name="superadmin")
        assert response.status_code == 400
        assert "does not exist" in response.json()["detail"]

    def test_register_short_password(self, client):
        response = _register_user(client, password="123")
        assert response.status_code == 422  # Pydantic validation error


# --- Login Tests ---


class TestLogin:

    def test_login_success(self, client):
        _register_user(client)
        response = _login_user(client)
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_login_wrong_password(self, client):
        _register_user(client)
        response = _login_user(client, password="wrongpassword")
        assert response.status_code == 401
        assert "Invalid" in response.json()["detail"]

    def test_login_nonexistent_user(self, client):
        response = _login_user(client, email="nobody@test.com")
        assert response.status_code == 401
        assert "Invalid" in response.json()["detail"]


# --- /auth/me Tests ---


class TestCurrentUser:

    def test_me_success(self, client):
        _register_user(client)
        headers = _get_auth_header(client)
        response = client.get("/api/v1/auth/me", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "user@test.com"
        assert data["role_name"] == "customer"

    def test_me_no_token(self, client):
        response = client.get("/api/v1/auth/me")
        assert response.status_code == 401

    def test_me_invalid_token(self, client):
        headers = {"Authorization": "Bearer invalidtoken123"}
        response = client.get("/api/v1/auth/me", headers=headers)
        assert response.status_code == 401


# --- RBAC Tests ---


class TestRBAC:

    def test_customer_accesses_customer_endpoint(self, client):
        _register_user(client, role_name="customer")
        headers = _get_auth_header(client)
        response = client.get("/api/v1/test-auth/customer-only", headers=headers)
        assert response.status_code == 200

    def test_customer_blocked_from_admin_endpoint(self, client):
        _register_user(client, role_name="customer")
        headers = _get_auth_header(client)
        response = client.get("/api/v1/test-auth/admin-only", headers=headers)
        assert response.status_code == 403

    def test_admin_accesses_admin_endpoint(self, client):
        _register_user(client, email="admin@test.com", role_name="admin")
        headers = _get_auth_header(client, email="admin@test.com")
        response = client.get("/api/v1/test-auth/admin-only", headers=headers)
        assert response.status_code == 200

    def test_organizer_blocked_from_admin_endpoint(self, client):
        _register_user(client, email="org@test.com", role_name="organizer")
        headers = _get_auth_header(client, email="org@test.com")
        response = client.get("/api/v1/test-auth/admin-only", headers=headers)
        assert response.status_code == 403

    def test_organizer_accesses_organizer_endpoint(self, client):
        _register_user(client, email="org@test.com", role_name="organizer")
        headers = _get_auth_header(client, email="org@test.com")
        response = client.get("/api/v1/test-auth/organizer-only", headers=headers)
        assert response.status_code == 200
