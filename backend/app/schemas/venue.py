from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class VenueCreate(BaseModel):
    """Schema for creating a new venue."""

    name: str = Field(..., min_length=1, max_length=150)
    city: str = Field(..., min_length=1, max_length=100)
    address: str = Field(..., min_length=1, max_length=255)
    capacity: int = Field(..., gt=0)
    description: str | None = None


class VenueOut(BaseModel):
    """Schema for returning venue information."""

    id: int
    name: str
    city: str
    address: str
    capacity: int
    description: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SeatCategoryCreate(BaseModel):
    """Schema for creating a seat category for a venue."""

    name: str = Field(..., min_length=1, max_length=100)
    description: str | None = None
    price_multiplier: float = Field(default=1.0, ge=0)


class SeatCategoryOut(BaseModel):
    """Schema for returning a seat category."""

    id: int
    name: str
    description: str | None = None
    price_multiplier: float
    venue_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
