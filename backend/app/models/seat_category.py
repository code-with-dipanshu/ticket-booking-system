from __future__ import annotations

from datetime import datetime
from typing import List

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class SeatCategory(Base):
    """Represents a category of seats for a venue such as VIP, Premium, Standard."""

    __tablename__ = "seat_categories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    price_multiplier: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)
    venue_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("venues.id"), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    venue: Mapped["Venue"] = relationship("Venue", back_populates="seat_categories")
    seats: Mapped[List["Seat"]] = relationship(
        "Seat",
        back_populates="seat_category",
        cascade="all, delete-orphan",
    )
