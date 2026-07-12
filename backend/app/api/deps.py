from typing import Generator, List
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import decode_access_token
from app.db.session import get_db
from app.models.user import User
from app.repositories.role import RoleRepository
from app.repositories.seat_category import SeatCategoryRepository
from app.repositories.user import UserRepository
from app.repositories.venue import VenueRepository
from app.services.auth import AuthService
from app.services.venue import VenueService

# Extract the Bearer token from the Authorization header.
# Point to our auth login endpoint to enable interactive Swagger authorization.
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/login"
)


# Dependency factories for DB and Repository injection


def get_user_repository(db: Session = Depends(get_db)) -> UserRepository:
    """Dependency that creates a UserRepository instance."""
    return UserRepository(db)


def get_role_repository(db: Session = Depends(get_db)) -> RoleRepository:
    """Dependency that creates a RoleRepository instance."""
    return RoleRepository(db)


def get_venue_repository(db: Session = Depends(get_db)) -> VenueRepository:
    """Dependency that creates a VenueRepository instance."""
    return VenueRepository(db)


def get_seat_category_repository(
    db: Session = Depends(get_db),
) -> SeatCategoryRepository:
    """Dependency that creates a SeatCategoryRepository instance."""
    return SeatCategoryRepository(db)


def get_auth_service(
    user_repo: UserRepository = Depends(get_user_repository),
    role_repo: RoleRepository = Depends(get_role_repository),
) -> AuthService:
    """Dependency that creates an AuthService instance."""
    return AuthService(user_repo, role_repo)


def get_venue_service(
    venue_repo: VenueRepository = Depends(get_venue_repository),
    seat_category_repo: SeatCategoryRepository = Depends(get_seat_category_repository),
) -> VenueService:
    """Dependency that creates a VenueService instance."""
    return VenueService(venue_repo, seat_category_repo)


# User Authentication and Authorization dependencies


def get_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme),
    user_repo: UserRepository = Depends(get_user_repository),
) -> User:
    """Extracts the current user from the JWT.

    Args:
        db: DB session.
        token: Extracted Bearer token.
        user_repo: User repository.

    Returns:
        The authenticated User instance.

    Raises:
        HTTPException: If token is invalid or user doesn't exist.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    email = decode_access_token(token)
    if email is None:
        raise credentials_exception

    user = user_repo.get_by_email(email)
    if user is None:
        raise credentials_exception

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user profile",
        )

    return user


class RoleChecker:
    """Role verification dependency for enforcing RBAC permissions on endpoints."""

    def __init__(self, allowed_roles: List[str]):
        """Initializes the checker with a list of authorized roles.

        Args:
            allowed_roles: List of string names for allowed roles (e.g. ['admin']).
        """
        self.allowed_roles = [role.lower() for role in allowed_roles]

    def __call__(self, current_user: User = Depends(get_current_user)) -> User:
        """Executes the authorization check.

        Args:
            current_user: The authenticated User model.

        Returns:
            The authenticated User if authorized.

        Raises:
            HTTPException: 403 Forbidden if user's role is not authorized.
        """
        if current_user.role.name.lower() not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to perform this action",
            )
        return current_user
