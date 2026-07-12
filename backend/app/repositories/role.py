from typing import Optional
from sqlalchemy.orm import Session

from app.models.role import Role


class RoleRepository:
    """Repository for handling database operations on the Role model."""

    def __init__(self, db: Session):
        """Initializes the repository with a database session.

        Args:
            db: Active SQLAlchemy database session.
        """
        self.db = db

    def get_by_name(self, name: str) -> Optional[Role]:
        """Finds a role by its unique name.

        Args:
            name: Name of the role (e.g., 'admin', 'customer').

        Returns:
            The Role object if found, otherwise None.
        """
        return self.db.query(Role).filter(Role.name == name).first()

    def create(self, role: Role) -> Role:
        """Persists a new role in the database.

        Args:
            role: The Role model instance to create.

        Returns:
            The created Role instance with populated DB fields.
        """
        self.db.add(role)
        self.db.commit()
        self.db.refresh(role)
        return role
