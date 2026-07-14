from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.seat_category import SeatCategory


class SeatCategoryRepository:
    """Repository for handling database operations on seat categories."""

    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, seat_category_id: int) -> Optional[SeatCategory]:
        return (
            self.db.query(SeatCategory)
            .filter(SeatCategory.id == seat_category_id)
            .first()
        )

    def list_for_venue(self, venue_id: int) -> List[SeatCategory]:
        return (
            self.db.query(SeatCategory)
            .filter(SeatCategory.venue_id == venue_id)
            .order_by(SeatCategory.id.asc())
            .all()
        )

    def create(self, seat_category: SeatCategory) -> SeatCategory:
        self.db.add(seat_category)
        self.db.commit()
        self.db.refresh(seat_category)
        return seat_category
