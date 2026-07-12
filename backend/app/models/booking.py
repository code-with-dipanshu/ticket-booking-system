from __future__ import annotations

from datetime import datetime
from typing import List

from sqlalchemy import DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Booking(Base):
    """Represents a customer booking against an event."""

    __tablename__ = "bookings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    event_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("events.id"), nullable=False
    )
    customer_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=False
    )
    status: Mapped[str] = mapped_column(String(30), default="confirmed", nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    event: Mapped["Event"] = relationship("Event", back_populates="bookings")
    customer: Mapped["User"] = relationship("User", back_populates="bookings")
    booking_seats: Mapped[List["BookingSeat"]] = relationship(
        "BookingSeat",
        back_populates="booking",
        cascade="all, delete-orphan",
    )
