from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import RoleChecker, get_current_user, get_venue_service
from app.models.user import User
from app.schemas.venue import SeatCategoryCreate, SeatCategoryOut, VenueCreate, VenueOut
from app.services.venue import VenueService

router = APIRouter()


@router.post("", response_model=VenueOut, status_code=status.HTTP_201_CREATED)
def create_venue(
    data: VenueCreate,
    current_user: User = Depends(get_current_user),
    venue_service: VenueService = Depends(get_venue_service),
):
    """Create a new venue. Only admin users may perform this action."""
    if current_user.role.name.lower() != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to perform this action",
        )

    try:
        venue = venue_service.create_venue(data)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    return venue


@router.get("", response_model=list[VenueOut])
def list_venues(
    venue_service: VenueService = Depends(get_venue_service),
):
    """List all venues so customers and organizers can browse the catalog."""
    return venue_service.list_venues()


@router.post(
    "/{venue_id}/seat-categories",
    response_model=SeatCategoryOut,
    status_code=status.HTTP_201_CREATED,
)
def create_seat_category(
    venue_id: int,
    data: SeatCategoryCreate,
    current_user: User = Depends(get_current_user),
    venue_service: VenueService = Depends(get_venue_service),
):
    """Create a seat category under a venue. Only admin users may perform this action."""
    if current_user.role.name.lower() != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to perform this action",
        )

    try:
        seat_category = venue_service.add_seat_category(venue_id, data)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    return seat_category
