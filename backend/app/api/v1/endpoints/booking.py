from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import get_booking_service, get_current_user
from app.models.user import User
from app.schemas.booking import BookingCreate, BookingOut
from app.services.booking import BookingService

router = APIRouter()


@router.post("", response_model=BookingOut, status_code=status.HTTP_201_CREATED)
def create_booking(
    data: BookingCreate,
    current_user: User = Depends(get_current_user),
    booking_service: BookingService = Depends(get_booking_service),
):
    """Create a booking for a customer. The caller must be authenticated."""
    if current_user.role.name.lower() != "customer":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to perform this action",
        )

    try:
        booking = booking_service.create_booking(data, customer_id=current_user.id)
    except ValueError as exc:
        if "currently on hold" in str(exc).lower():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=str(exc),
            ) from exc
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    return booking


@router.post("/{booking_id}/cancel", response_model=BookingOut)
def cancel_booking(
    booking_id: int,
    current_user: User = Depends(get_current_user),
    booking_service: BookingService = Depends(get_booking_service),
):
    """Cancel a customer booking and release its seat hold state."""
    if current_user.role.name.lower() != "customer":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to perform this action",
        )

    try:
        booking = booking_service.cancel_booking(booking_id, customer_id=current_user.id)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    return booking
