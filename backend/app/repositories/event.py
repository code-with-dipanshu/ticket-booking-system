from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.event import Event


class EventRepository:
    """Repository for handling database operations on events."""

    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, event_id: int) -> Optional[Event]:
        return self.db.query(Event).filter(Event.id == event_id).first()

    def list_all(self) -> List[Event]:
        return self.db.query(Event).order_by(Event.created_at.desc()).all()

    def create(self, event: Event) -> Event:
        self.db.add(event)
        self.db.commit()
        self.db.refresh(event)
        return event
