"""Tests for the Booking and seat-hold milestone."""

import time

from app.core.redis import SeatHoldStore


def _create_admin_headers(client, email: str = "admin@booking.com"):
    register_response = client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": "secret123",
            "full_name": "Booking Admin",
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


def _create_organizer_headers(client, email: str = "organizer@booking.com"):
    register_response = client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": "secret123",
            "full_name": "Booking Organizer",
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


def _create_customer_headers(client, email: str = "customer@booking.com"):
    register_response = client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": "secret123",
            "full_name": "Booking Customer",
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


class TestBookingManagement:
    def test_customer_can_create_booking(self, client):
        admin_headers = _create_admin_headers(client)
        venue_response = client.post(
            "/api/v1/venues",
            headers=admin_headers,
            json={
                "name": "Booking Arena",
                "city": "Mumbai",
                "address": "Dadar",
                "capacity": 500,
                "description": "Booking venue",
            },
        )
        assert venue_response.status_code == 201
        venue_id = venue_response.json()["id"]

        seat_category_response = client.post(
            f"/api/v1/venues/{venue_id}/seat-categories",
            headers=admin_headers,
            json={
                "name": "VIP",
                "description": "Premium seat",
                "price_multiplier": 2.0,
            },
        )
        assert seat_category_response.status_code == 201
        seat_category_id = seat_category_response.json()["id"]

        organizer_headers = _create_organizer_headers(client)
        event_response = client.post(
            "/api/v1/events",
            headers=organizer_headers,
            json={
                "title": "Booking Night",
                "description": "Concert",
                "venue_id": venue_id,
                "organizer_id": 1,
                "start_time": "2026-09-01T18:00:00",
                "end_time": "2026-09-01T22:00:00",
                "status": "published",
            },
        )
        assert event_response.status_code == 201
        event_id = event_response.json()["id"]

        customer_headers = _create_customer_headers(client)
        response = client.post(
            "/api/v1/bookings",
            headers=customer_headers,
            json={
                "event_id": event_id,
                "seat_category_id": seat_category_id,
                "quantity": 1,
            },
        )

        assert response.status_code == 201
        data = response.json()
        assert data["status"] == "confirmed"
        assert data["quantity"] == 1

    def test_customer_cannot_overbook_available_inventory(self, client):
        admin_headers = _create_admin_headers(client)
        venue_response = client.post(
            "/api/v1/venues",
            headers=admin_headers,
            json={
                "name": "Inventory Arena",
                "city": "Chennai",
                "address": "Guindy",
                "capacity": 400,
                "description": "Inventory venue",
            },
        )
        assert venue_response.status_code == 201
        venue_id = venue_response.json()["id"]

        seat_category_response = client.post(
            f"/api/v1/venues/{venue_id}/seat-categories",
            headers=admin_headers,
            json={
                "name": "Standard",
                "description": "Standard seat",
                "price_multiplier": 1.0,
            },
        )
        assert seat_category_response.status_code == 201
        seat_category_id = seat_category_response.json()["id"]

        organizer_headers = _create_organizer_headers(client, email="other-organizer@booking.com")
        event_response = client.post(
            "/api/v1/events",
            headers=organizer_headers,
            json={
                "title": "Inventory Night",
                "description": "Another concert",
                "venue_id": venue_id,
                "organizer_id": 1,
                "start_time": "2026-09-02T18:00:00",
                "end_time": "2026-09-02T22:00:00",
                "status": "published",
            },
        )
        assert event_response.status_code == 201
        event_id = event_response.json()["id"]

        customer_headers = _create_customer_headers(client, email="first-customer@booking.com")
        first_response = client.post(
            "/api/v1/bookings",
            headers=customer_headers,
            json={
                "event_id": event_id,
                "seat_category_id": seat_category_id,
                "quantity": 5,
            },
        )
        assert first_response.status_code == 201

        second_customer_headers = _create_customer_headers(
            client, email="second-customer@booking.com"
        )
        second_response = client.post(
            "/api/v1/bookings",
            headers=second_customer_headers,
            json={
                "event_id": event_id,
                "seat_category_id": seat_category_id,
                "quantity": 5,
            },
        )

        assert second_response.status_code == 409

    def test_seat_hold_ttl_expires(self):
        hold_store = SeatHoldStore()
        hold_store.hold(key="event:1:seat_category:1", value="customer-1", ttl_seconds=1)

        assert hold_store.is_held("event:1:seat_category:1") is True

        time.sleep(1.2)

        assert hold_store.is_held("event:1:seat_category:1") is False
