from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.venue import Venue


class VenueRepository:
    """Repository for handling database operations on venues."""

    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, venue_id: int) -> Optional[Venue]:
        return self.db.query(Venue).filter(Venue.id == venue_id).first()

    def get_by_name(self, name: str) -> Optional[Venue]:
        return self.db.query(Venue).filter(Venue.name == name).first()

    def list_all(self) -> List[Venue]:
        return self.db.query(Venue).order_by(Venue.created_at.desc()).all()

    def create(self, venue: Venue) -> Venue:
        self.db.add(venue)
        self.db.commit()
        self.db.refresh(venue)
        return venue
