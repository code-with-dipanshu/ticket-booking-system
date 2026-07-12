from app.models.seat_category import SeatCategory
from app.models.venue import Venue
from app.repositories.seat_category import SeatCategoryRepository
from app.repositories.venue import VenueRepository


class VenueService:
    """Business logic for venue management operations."""

    def __init__(
        self,
        venue_repo: VenueRepository,
        seat_category_repo: SeatCategoryRepository,
    ):
        self.venue_repo = venue_repo
        self.seat_category_repo = seat_category_repo

    def create_venue(self, data) -> Venue:
        existing = self.venue_repo.get_by_name(data.name)
        if existing:
            raise ValueError(f"Venue '{data.name}' already exists.")

        venue = Venue(
            name=data.name,
            city=data.city,
            address=data.address,
            capacity=data.capacity,
            description=data.description,
        )
        return self.venue_repo.create(venue)

    def list_venues(self):
        return self.venue_repo.list_all()

    def add_seat_category(self, venue_id: int, data) -> SeatCategory:
        venue = self.venue_repo.get_by_id(venue_id)
        if not venue:
            raise ValueError(f"Venue with id {venue_id} not found.")

        seat_category = SeatCategory(
            name=data.name,
            description=data.description,
            price_multiplier=data.price_multiplier,
            venue_id=venue.id,
        )

        created_seat_category = self.seat_category_repo.create(seat_category)
        return created_seat_category
