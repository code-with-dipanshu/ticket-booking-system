"""Tests for the Event Management milestone."""


def _create_admin_headers(client, email: str = "admin@event.com"):
    register_response = client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": "secret123",
            "full_name": "Event Admin",
            "role_name": "admin",
        },
    )
    assert register_response.status_code == 201

    login_response = client.post(
        "/api/v1/auth/login",
        data={"username": email, "password": "secret123"},
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def _create_organizer_headers(client, email: str = "organizer@event.com"):
    register_response = client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": "secret123",
            "full_name": "Event Organizer",
            "role_name": "organizer",
        },
    )
    assert register_response.status_code == 201

    login_response = client.post(
        "/api/v1/auth/login",
        data={"username": email, "password": "secret123"},
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def _create_customer_headers(client, email: str = "customer@event.com"):
    register_response = client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": "secret123",
            "full_name": "Event Customer",
            "role_name": "customer",
        },
    )
    assert register_response.status_code == 201

    login_response = client.post(
        "/api/v1/auth/login",
        data={"username": email, "password": "secret123"},
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


class TestEventManagement:
    def test_organizer_can_create_event(self, client):
        admin_headers = _create_admin_headers(client)
        venue_response = client.post(
            "/api/v1/venues",
            headers=admin_headers,
            json={
                "name": "Event Arena",
                "city": "Mumbai",
                "address": "Lower Parel",
                "capacity": 1000,
                "description": "Venue for events",
            },
        )
        assert venue_response.status_code == 201
        venue_id = venue_response.json()["id"]

        organizer_headers = _create_organizer_headers(client)
        response = client.post(
            "/api/v1/events",
            headers=organizer_headers,
            json={
                "title": "Sunset Live",
                "description": "Live concert event",
                "venue_id": venue_id,
                "start_time": "2026-08-01T18:00:00",
                "end_time": "2026-08-01T22:00:00",
                "status": "draft",
                "organizer_id": 1,
            },
        )

        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Sunset Live"
        assert data["venue_id"] == venue_id

    def test_customer_cannot_create_event(self, client):
        customer_headers = _create_customer_headers(client)
        response = client.post(
            "/api/v1/events",
            headers=customer_headers,
            json={
                "title": "Forbidden Event",
                "description": "Should fail",
                "venue_id": 1,
                "start_time": "2026-08-01T18:00:00",
                "end_time": "2026-08-01T22:00:00",
                "status": "draft",
                "organizer_id": 1,
            },
        )

        assert response.status_code == 403

    def test_admin_can_list_events(self, client):
        admin_headers = _create_admin_headers(client)
        venue_response = client.post(
            "/api/v1/venues",
            headers=admin_headers,
            json={
                "name": "Event List Arena",
                "city": "Pune",
                "address": "Shivaji Nagar",
                "capacity": 700,
                "description": "Another venue",
            },
        )
        assert venue_response.status_code == 201
        venue_id = venue_response.json()["id"]

        organizer_headers = _create_organizer_headers(client)
        create_response = client.post(
            "/api/v1/events",
            headers=organizer_headers,
            json={
                "title": "Tech Fest",
                "description": "Technology convention",
                "venue_id": venue_id,
                "start_time": "2026-08-15T10:00:00",
                "end_time": "2026-08-15T18:00:00",
                "status": "draft",
                "organizer_id": 1,
            },
        )
        assert create_response.status_code == 201

        list_response = client.get("/api/v1/events", headers=admin_headers)
        assert list_response.status_code == 200
        data = list_response.json()
        assert isinstance(data, list)
        assert any(item["title"] == "Tech Fest" for item in data)
