from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import get_current_user, get_event_service
from app.models.user import User
from app.schemas.event import EventCreate, EventOut
from app.services.event import EventService

router = APIRouter()


@router.post("", response_model=EventOut, status_code=status.HTTP_201_CREATED)
def create_event(
    data: EventCreate,
    current_user: User = Depends(get_current_user),
    event_service: EventService = Depends(get_event_service),
):
    """Create a new event. Only organizer users may create events."""
    if current_user.role.name.lower() != "organizer":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to perform this action",
        )

    try:
        event = event_service.create_event(data, organizer_id=current_user.id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    return event


@router.get("", response_model=list[EventOut])
def list_events(
    current_user: User = Depends(get_current_user),
    event_service: EventService = Depends(get_event_service),
):
    """List all events. Admin access is required."""
    if current_user.role.name.lower() != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to perform this action",
        )

    return event_service.list_events()
