from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class BookingCreate(BaseModel):
    """Schema for creating a booking."""

    event_id: int = Field(..., gt=0)
    seat_category_id: int = Field(..., gt=0)
    quantity: int = Field(..., gt=0)


class SeatCategoryAvailabilityOut(BaseModel):
    """Availability snapshot for an event seat category."""

    seat_category_id: int
    name: str
    description: str | None = None
    price_multiplier: float
    available: int
    hold_ttl_seconds: int


class SeatLayoutRowOut(BaseModel):
    """A row within the venue layout used by the customer-facing seat map."""

    label: str
    seats: list[str]


class SeatLayoutOut(BaseModel):
    """A simplified venue layout for the seat-map experience."""

    stage_label: str
    rows: list[SeatLayoutRowOut]


class SeatMapOut(BaseModel):
    """Response shape for a visual seat map and booking availability."""

    event_id: int
    venue_id: int
    available: int
    hold_ttl_seconds: int
    seat_categories: list[SeatCategoryAvailabilityOut]
    layout: SeatLayoutOut

    model_config = ConfigDict(from_attributes=True)


class BookingOut(BaseModel):
    """Schema for booking responses."""

    id: int
    event_id: int
    customer_id: int
    status: str
    quantity: int
    created_at: datetime
    updated_at: datetime
    ticket_reference: str | None = None
    ticket_code: str | None = None
    qr_payload: str | None = None
    qr_code: str | None = None

    model_config = ConfigDict(from_attributes=True)
