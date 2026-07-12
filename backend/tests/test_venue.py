"""Tests for the Venue Management milestone."""


def _create_admin_headers(client, email: str = "admin@venue.com"):
    register_response = client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": "secret123",
            "full_name": "Venue Admin",
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


def _create_customer_headers(client, email: str = "customer@venue.com"):
    register_response = client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": "secret123",
            "full_name": "Venue Customer",
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


class TestVenueManagement:
    def test_admin_can_create_venue(self, client):
        headers = _create_admin_headers(client)
        response = client.post(
            "/api/v1/venues",
            headers=headers,
            json={
                "name": "Grand Arena",
                "city": "Mumbai",
                "address": "Marine Drive",
                "capacity": 1200,
                "description": "Premium concert venue",
            },
        )

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Grand Arena"
        assert data["capacity"] == 1200
        assert data["city"] == "Mumbai"

    def test_customer_cannot_create_venue(self, client):
        headers = _create_customer_headers(client)
        response = client.post(
            "/api/v1/venues",
            headers=headers,
            json={
                "name": "Restricted Arena",
                "city": "Mumbai",
                "address": "Bandra",
                "capacity": 500,
                "description": "Should fail",
            },
        )

        assert response.status_code == 403

    def test_admin_can_list_venues(self, client):
        headers = _create_admin_headers(client)
        create_response = client.post(
            "/api/v1/venues",
            headers=headers,
            json={
                "name": "Sky Hall",
                "city": "Delhi",
                "address": "Connaught Place",
                "capacity": 800,
                "description": "Central event space",
            },
        )
        assert create_response.status_code == 201

        list_response = client.get("/api/v1/venues", headers=headers)
        assert list_response.status_code == 200
        data = list_response.json()
        assert isinstance(data, list)
        assert any(item["name"] == "Sky Hall" for item in data)

    def test_admin_can_create_seat_category_for_venue(self, client):
        headers = _create_admin_headers(client)
        venue_response = client.post(
            "/api/v1/venues",
            headers=headers,
            json={
                "name": "Seat Category Arena",
                "city": "Bengaluru",
                "address": "Koramangala",
                "capacity": 900,
                "description": "Venue for seat layout testing",
            },
        )
        assert venue_response.status_code == 201
        venue_id = venue_response.json()["id"]

        seat_category_response = client.post(
            f"/api/v1/venues/{venue_id}/seat-categories",
            headers=headers,
            json={
                "name": "VIP",
                "description": "Premium seating",
                "price_multiplier": 2.0,
            },
        )

        assert seat_category_response.status_code == 201
        data = seat_category_response.json()
        assert data["name"] == "VIP"
        assert data["venue_id"] == venue_id
