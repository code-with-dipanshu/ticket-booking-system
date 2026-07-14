import hashlib
import base64
import io
import qrcode
from PIL import Image

from app.core.redis import SeatHoldStore
from app.models.booking import Booking
from app.models.booking_seat import BookingSeat
from app.repositories.booking import BookingRepository
from app.repositories.booking_seat import BookingSeatRepository
from app.repositories.event import EventRepository
from app.repositories.seat_category import SeatCategoryRepository
from app.repositories.user import UserRepository
from app.repositories.venue import VenueRepository


class BookingService:
    """Business logic for customer booking creation and seat-hold validation."""

    HOLD_TTL_SECONDS = 60

    @staticmethod
    def _build_ticket_code(booking_id: int, event_id: int) -> str:
        return f"TICKET-{booking_id:06d}-{event_id:04d}"

    @staticmethod
    def _build_qr_code(payload: str) -> str:
        # Use qrcode to generate a PNG image for better browser compatibility.
        qr = qrcode.QRCode(version=2, box_size=6, border=2)
        qr.add_data(payload)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")

        # Normalize to a PIL Image and resize to 180x180 for consistency
        if hasattr(img, "get_image"):
            pil_img = img.get_image()
        elif isinstance(img, Image.Image):
            pil_img = img
        else:
            try:
                pil_img = Image.fromarray(getattr(img, "_img", img))
            except Exception:
                pil_img = Image.new("RGB", (180, 180), "white")

        png_img = pil_img.convert("RGB").resize((180, 180), Image.Resampling.NEAREST)

        buf = io.BytesIO()
        png_img.save(buf, format="PNG")
        b64 = base64.b64encode(buf.getvalue()).decode("ascii")
        return f"data:image/png;base64,{b64}"

    def __init__(
        self,
        booking_repo: BookingRepository,
        booking_seat_repo: BookingSeatRepository,
        event_repo: EventRepository,
        seat_category_repo: SeatCategoryRepository,
        user_repo: UserRepository,
        venue_repo: VenueRepository,
        hold_store: SeatHoldStore,
    ):
        self.booking_repo = booking_repo
        self.booking_seat_repo = booking_seat_repo
        self.event_repo = event_repo
        self.seat_category_repo = seat_category_repo
        self.user_repo = user_repo
        self.venue_repo = venue_repo
        self.hold_store = hold_store

    def get_seat_map(self, event_id: int) -> dict:
        event = self.event_repo.get_by_id(event_id)
        if not event:
            raise ValueError(f"Event with id {event_id} not found.")

        venue = self.venue_repo.get_by_id(event.venue_id)
        if not venue:
            raise ValueError(f"Venue with id {event.venue_id} not found.")

        seat_categories = self.seat_category_repo.list_for_venue(venue.id)
        seat_group = []
        for seat_category in seat_categories:
            confirmed_quantity = (
                self.booking_seat_repo.get_confirmed_quantity_for_event_category(
                    event.id,
                    seat_category.id,
                )
            )
            available = max(0, venue.capacity - confirmed_quantity)
            seat_group.append(
                {
                    "seat_category_id": seat_category.id,
                    "name": seat_category.name,
                    "description": seat_category.description,
                    "price_multiplier": seat_category.price_multiplier,
                    "available": available,
                    "hold_ttl_seconds": self.HOLD_TTL_SECONDS,
                }
            )

        layout_rows = []
        for row_index in range(5):
            row_label = chr(ord("A") + row_index)
            seat_labels = [f"{row_label}{seat_number}" for seat_number in range(1, 6)]
            layout_rows.append({"label": row_label, "seats": seat_labels})

        return {
            "event_id": event.id,
            "venue_id": venue.id,
            "available": sum(category["available"] for category in seat_group),
            "hold_ttl_seconds": self.HOLD_TTL_SECONDS,
            "seat_categories": seat_group,
            "layout": {
                "stage_label": "STAGE",
                "rows": layout_rows,
            },
        }

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

        venue = self.venue_repo.get_by_id(event.venue_id)
        if not venue:
            raise ValueError(f"Venue with id {event.venue_id} not found.")

        confirmed_quantity = (
            self.booking_seat_repo.get_confirmed_quantity_for_event_category(
                event.id,
                seat_category.id,
            )
        )
        if confirmed_quantity + data.quantity > venue.capacity:
            raise ValueError("Seat category has insufficient inventory available.")

        hold_key = f"event:{event.id}:seat_category:{seat_category.id}"
        has_hold = self.hold_store.is_held(hold_key)
        if has_hold:
            raise ValueError("Seat inventory is currently on hold.")

        if not self.hold_store.hold(
            hold_key,
            str(customer_id),
            ttl_seconds=self.HOLD_TTL_SECONDS,
        ):
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
        ticket_reference = f"TICKET-{created_booking.id:06d}"
        ticket_code = self._build_ticket_code(created_booking.id, event.id)
        qr_payload = f"booking:{created_booking.id}:{ticket_code}"
        created_booking.ticket_reference = ticket_reference
        created_booking.ticket_code = ticket_code
        created_booking.qr_payload = qr_payload
        created_booking.qr_code = self._build_qr_code(qr_payload)
        return created_booking

    def cancel_booking(self, booking_id: int, customer_id: int) -> Booking:
        booking = self.booking_repo.get_by_id(booking_id)
        if not booking:
            raise ValueError(f"Booking with id {booking_id} not found.")

        if booking.customer_id != customer_id:
            raise ValueError("You do not have permission to cancel this booking.")

        booking.status = "cancelled"
        self.booking_repo.update(booking)

        for booking_seat in booking.booking_seats:
            booking_seat.status = "cancelled"
            self.booking_seat_repo.update(booking_seat)
            hold_key = (
                f"event:{booking.event_id}:seat_category:{booking_seat.seat_category_id}"
            )
            self.hold_store.release(hold_key)

        return booking
