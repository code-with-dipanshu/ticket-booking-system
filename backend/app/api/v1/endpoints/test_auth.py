from fastapi import APIRouter, Depends

from app.api.deps import RoleChecker
from app.models.user import User

router = APIRouter()


@router.get("/admin-only")
def admin_only_endpoint(
    current_user: User = Depends(RoleChecker(["admin"])),
):
    """Access restricted to users with the 'admin' role."""
    return {
        "message": f"Hello Admin {current_user.full_name}! Access granted."
    }


@router.get("/organizer-only")
def organizer_only_endpoint(
    current_user: User = Depends(RoleChecker(["organizer", "admin"])),
):
    """Access restricted to users with 'organizer' or 'admin' roles."""
    return {
        "message": f"Hello Organizer/Admin {current_user.full_name}! Access granted."
    }


@router.get("/customer-only")
def customer_only_endpoint(
    current_user: User = Depends(RoleChecker(["customer", "admin"])),
):
    """Access restricted to users with 'customer' or 'admin' roles."""
    return {
        "message": f"Hello Customer/Admin {current_user.full_name}! Access granted."
    }
