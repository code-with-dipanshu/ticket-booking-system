from typing import Optional

from sqlalchemy.orm import Session

from app.models.booking_seat import BookingSeat


class BookingSeatRepository:
    """Repository for handling booking-seat association rows."""

    def __init__(self, db: Session):
        self.db = db

    def create(self, booking_seat: BookingSeat) -> BookingSeat:
        self.db.add(booking_seat)
        self.db.commit()
        self.db.refresh(booking_seat)
        return booking_seat
