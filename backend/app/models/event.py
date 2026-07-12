from __future__ import annotations

from datetime import datetime
from typing import List

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Event(Base):
    """Represents an event hosted at a venue by an organizer."""

    __tablename__ = "events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(150), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    venue_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("venues.id"), nullable=False
    )
    organizer_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=False
    )
    start_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    end_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    status: Mapped[str] = mapped_column(String(30), default="draft", nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    venue: Mapped["Venue"] = relationship("Venue", back_populates="events")
    organizer: Mapped["User"] = relationship("User", back_populates="organized_events")
    event_prices: Mapped[List["EventPrice"]] = relationship(
        "EventPrice",
        back_populates="event",
        cascade="all, delete-orphan",
    )
    bookings: Mapped[List["Booking"]] = relationship(
        "Booking",
        back_populates="event",
        cascade="all, delete-orphan",
    )
