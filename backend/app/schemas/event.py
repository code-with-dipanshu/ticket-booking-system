from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class EventCreate(BaseModel):
    """Schema for creating an event."""

    title: str = Field(..., min_length=1, max_length=150)
    description: str | None = None
    venue_id: int = Field(..., gt=0)
    organizer_id: int = Field(..., gt=0)
    start_time: datetime
    end_time: datetime
    status: str = Field(default="draft", max_length=30)


class EventOut(BaseModel):
    """Schema for returning event information."""

    id: int
    title: str
    description: str | None = None
    venue_id: int
    organizer_id: int
    start_time: datetime
    end_time: datetime
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
