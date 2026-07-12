from app.core.exceptions import (
    InvalidCredentialsException,
    RoleNotFoundException,
    UserAlreadyExistsException,
)
from app.core.security import create_access_token, hash_password, verify_password
from app.models.user import User
from app.repositories.role import RoleRepository
from app.repositories.user import UserRepository
from app.schemas.user import Token, UserLogin, UserRegister


class AuthService:
    """Service layer handling user authentication and registration business logic."""

    def __init__(self, user_repo: UserRepository, role_repo: RoleRepository):
        """Initializes the AuthService with user and role repositories.

        Args:
            user_repo: UserRepository instance.
            role_repo: RoleRepository instance.
        """
        self.user_repo = user_repo
        self.role_repo = role_repo

    def register_user(self, data: UserRegister) -> User:
        """Registers a new user in the system.

        Args:
            data: Registration details.

        Returns:
            The created User model.

        Raises:
            UserAlreadyExistsException: If the email is already in use.
            RoleNotFoundException: If the requested role doesn't exist.
        """
        # Ensure email uniqueness
        existing_user = self.user_repo.get_by_email(data.email)
        if existing_user:
            raise UserAlreadyExistsException(
                f"Email '{data.email}' is already registered."
            )

        # Resolve role
        role = self.role_repo.get_by_name(data.role_name.lower())
        if not role:
            raise RoleNotFoundException(
                f"Role '{data.role_name}' does not exist."
            )

        # Create user
        hashed_pw = hash_password(data.password)
        new_user = User(
            email=data.email,
            hashed_password=hashed_pw,
            full_name=data.full_name,
            role_id=role.id,
            is_active=True,
        )

        return self.user_repo.create(new_user)

    def authenticate_user(self, data: UserLogin) -> Token:
        """Authenticates a user and generates a access token.

        Args:
            data: Login credentials.

        Returns:
            A Token schema containing the JWT.

        Raises:
            InvalidCredentialsException: If email/password is incorrect.
        """
        user = self.user_repo.get_by_email(data.email)
        if not user:
            raise InvalidCredentialsException("Invalid email or password.")

        if not verify_password(data.password, user.hashed_password):
            raise InvalidCredentialsException("Invalid email or password.")

        # Generate token (store email as subject)
        access_token = create_access_token(subject=user.email)
        return Token(access_token=access_token, token_type="bearer")
