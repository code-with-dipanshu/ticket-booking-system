from app.core.redis import SeatHoldStore
from app.models.booking import Booking
from app.models.booking_seat import BookingSeat
from app.repositories.booking import BookingRepository
from app.repositories.booking_seat import BookingSeatRepository
from app.repositories.event import EventRepository
from app.repositories.seat_category import SeatCategoryRepository
from app.repositories.user import UserRepository


class BookingService:
    """Business logic for customer booking creation and seat-hold validation."""

    def __init__(
        self,
        booking_repo: BookingRepository,
        booking_seat_repo: BookingSeatRepository,
        event_repo: EventRepository,
        seat_category_repo: SeatCategoryRepository,
        user_repo: UserRepository,
        hold_store: SeatHoldStore,
    ):
        self.booking_repo = booking_repo
        self.booking_seat_repo = booking_seat_repo
        self.event_repo = event_repo
        self.seat_category_repo = seat_category_repo
        self.user_repo = user_repo
        self.hold_store = hold_store

    def create_booking(self, data, customer_id: int) -> Booking:
        event = self.event_repo.get_by_id(data.event_id)
        if not event:
            raise ValueError(f"Event with id {data.event_id} not found.")

        customer = self.user_repo.get_by_id(customer_id)
        if not customer:
            raise ValueError(f"Customer with id {customer_id} not found.")

        seat_category = self.seat_category_repo.get_by_id(data.seat_category_id)
        if not seat_category:
            raise ValueError(
                f"Seat category with id {data.seat_category_id} not found."
            )

        hold_key = f"event:{event.id}:seat_category:{seat_category.id}"
        has_hold = self.hold_store.is_held(hold_key)
        if has_hold:
            raise ValueError("Seat inventory is currently on hold.")

        if not self.hold_store.hold(hold_key, str(customer_id), ttl_seconds=60):
            raise ValueError("Seat inventory is currently on hold.")

        booking = Booking(
            event_id=event.id,
            customer_id=customer.id,
            status="confirmed",
            quantity=data.quantity,
        )
        created_booking = self.booking_repo.create(booking)

        booking_seat = BookingSeat(
            booking_id=created_booking.id,
            seat_category_id=seat_category.id,
            quantity=data.quantity,
            status="confirmed",
        )
        self.booking_seat_repo.create(booking_seat)

        return created_booking
