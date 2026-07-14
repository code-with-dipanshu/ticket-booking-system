from datetime import datetime

from app.models.event import Event
from app.repositories.event import EventRepository
from app.repositories.user import UserRepository
from app.repositories.venue import VenueRepository


class EventService:
    """Business logic for event management operations."""

    def __init__(
        self,
        event_repo: EventRepository,
        venue_repo: VenueRepository,
        user_repo: UserRepository,
    ):
        self.event_repo = event_repo
        self.venue_repo = venue_repo
        self.user_repo = user_repo

    def create_event(self, data, organizer_id: int) -> Event:
        if data.start_time >= data.end_time:
            raise ValueError("Event end time must be after start time.")

        venue = self.venue_repo.get_by_id(data.venue_id)
        if not venue:
            raise ValueError(f"Venue with id {data.venue_id} not found.")

        organizer = self.user_repo.get_by_id(organizer_id)
        if not organizer:
            raise ValueError(f"Organizer with id {organizer_id} not found.")

        if organizer.role.name.lower() not in {"organizer", "admin"}:
            raise ValueError("Only organizer and admin users can create events.")

        event = Event(
            title=data.title,
            description=data.description,
            venue_id=data.venue_id,
            organizer_id=organizer.id,
            start_time=data.start_time,
            end_time=data.end_time,
            status=data.status,
        )
        return self.event_repo.create(event)

    def list_events(self):
        return self.event_repo.list_all()
