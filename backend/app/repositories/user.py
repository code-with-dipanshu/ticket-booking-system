from typing import Optional
from sqlalchemy.orm import Session

from app.models.user import User


class UserRepository:
    """Repository for handling database operations on the User model."""

    def __init__(self, db: Session):
        """Initializes the repository with a database session.

        Args:
            db: Active SQLAlchemy database session.
        """
        self.db = db

    def get_by_email(self, email: str) -> Optional[User]:
        """Finds a user by their email address.

        Args:
            email: Email to search for.

        Returns:
            The User object if found, otherwise None.
        """
        return self.db.query(User).filter(User.email == email).first()

    def get_by_id(self, id: int) -> Optional[User]:
        """Finds a user by their primary key ID.

        Args:
            id: The user's ID.

        Returns:
            The User object if found, otherwise None.
        """
        return self.db.query(User).filter(User.id == id).first()

    def create(self, user: User) -> User:
        """Persists a new user in the database.

        Args:
            user: The User model instance to create.

        Returns:
            The created User instance.
        """
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user
