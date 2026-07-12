from __future__ import annotations

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Seat(Base):
    """Represents an individual seat record for a venue layout."""

    __tablename__ = "seats"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    venue_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("venues.id"), nullable=False
    )
    seat_category_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("seat_categories.id"), nullable=True
    )
    row_label: Mapped[str] = mapped_column(String(10), nullable=False)
    seat_number: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(String(30), default="available", nullable=False)

    seat_category: Mapped["SeatCategory"] = relationship(
        "SeatCategory", back_populates="seats"
    )
