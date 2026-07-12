from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm

from app.api.deps import get_auth_service, get_current_user
from app.models.user import User
from app.schemas.user import Token, UserLogin, UserOut, UserRegister
from app.services.auth import AuthService

router = APIRouter()


@router.post(
    "/register", response_model=UserOut, status_code=status.HTTP_201_CREATED
)
def register(
    data: UserRegister, auth_service: AuthService = Depends(get_auth_service)
) -> UserOut:
    """Registers a new user and returns their profile details (excluding password)."""
    user = auth_service.register_user(data)
    return UserOut(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        role_name=user.role.name,
        is_active=user.is_active,
        created_at=user.created_at,
    )


@router.post("/login", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    auth_service: AuthService = Depends(get_auth_service),
) -> Token:
    """Authenticates credentials and returns a JWT access token."""
    login_data = UserLogin(
        email=form_data.username, password=form_data.password
    )
    return auth_service.authenticate_user(login_data)


@router.get("/me", response_model=UserOut)
def read_current_user(
    current_user: User = Depends(get_current_user),
) -> UserOut:
    """Returns the profile details of the authenticated caller."""
    return UserOut(
        id=current_user.id,
        email=current_user.email,
        full_name=current_user.full_name,
        role_name=current_user.role.name,
        is_active=current_user.is_active,
        created_at=current_user.created_at,
    )
