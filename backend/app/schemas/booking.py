from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class BookingCreate(BaseModel):
    """Schema for creating a booking."""

    event_id: int = Field(..., gt=0)
    seat_category_id: int = Field(..., gt=0)
    quantity: int = Field(..., gt=0)


class BookingOut(BaseModel):
    """Schema for booking responses."""

    id: int
    event_id: int
    customer_id: int
    status: str
    quantity: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
