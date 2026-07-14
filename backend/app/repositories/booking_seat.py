from typing import Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.booking import Booking
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

    def get_confirmed_quantity_for_event_category(
        self, event_id: int, seat_category_id: int
    ) -> int:
        subtotal = (
            self.db.query(func.coalesce(func.sum(BookingSeat.quantity), 0))
            .join(Booking, BookingSeat.booking_id == Booking.id)
            .filter(
                Booking.event_id == event_id,
                BookingSeat.seat_category_id == seat_category_id,
                Booking.status == "confirmed",
            )
            .scalar()
        )
        return int(subtotal or 0)

    def update(self, booking_seat: BookingSeat) -> BookingSeat:
        self.db.add(booking_seat)
        self.db.commit()
        self.db.refresh(booking_seat)
        return booking_seat
