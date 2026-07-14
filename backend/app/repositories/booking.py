from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.booking import Booking


class BookingRepository:
    """Repository for handling database operations on bookings."""

    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, booking_id: int) -> Optional[Booking]:
        return self.db.query(Booking).filter(Booking.id == booking_id).first()

    def list_for_customer(self, customer_id: int) -> List[Booking]:
        return (
            self.db.query(Booking)
            .filter(Booking.customer_id == customer_id)
            .order_by(Booking.created_at.desc())
            .all()
        )

    def create(self, booking: Booking) -> Booking:
        self.db.add(booking)
        self.db.commit()
        self.db.refresh(booking)
        return booking

    def update(self, booking: Booking) -> Booking:
        self.db.add(booking)
        self.db.commit()
        self.db.refresh(booking)
        return booking
