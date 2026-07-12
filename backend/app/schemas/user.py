from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class UserRegister(BaseModel):
    """Schema for registering a new user."""

    email: str = Field(..., description="Unique email address of the user")
    password: str = Field(
        ..., min_length=6, description="Password (minimum 6 characters)"
    )
    full_name: str = Field(..., min_length=1, description="Full name of the user")
    role_name: str = Field(
        ..., description="Desired role (e.g., 'customer', 'organizer')"
    )


class UserLogin(BaseModel):
    """Schema for logging in an existing user."""

    email: str = Field(..., description="Email address")
    password: str = Field(..., description="Password")


class Token(BaseModel):
    """Schema for JWT authentication token response."""

    access_token: str
    token_type: str = "bearer"


class UserOut(BaseModel):
    """Schema for user details returned in API responses."""

    id: int
    email: str
    full_name: str
    role_name: str
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
