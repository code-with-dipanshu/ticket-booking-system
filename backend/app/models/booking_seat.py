from __future__ import annotations

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class BookingSeat(Base):
    """Maps a booking to the seat category and seat quantity it consumes."""

    __tablename__ = "booking_seats"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    booking_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("bookings.id"), nullable=False
    )
    seat_category_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("seat_categories.id"), nullable=False
    )
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(String(30), default="confirmed", nullable=False)

    booking: Mapped["Booking"] = relationship("Booking", back_populates="booking_seats")
