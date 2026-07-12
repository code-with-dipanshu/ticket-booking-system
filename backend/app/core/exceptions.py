class BookingSystemException(Exception):
    """Base exception for all domain-specific errors in the Ticket Booking System."""

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


class UserAlreadyExistsException(BookingSystemException):
    """Raised when trying to register an email that already exists."""

    pass


class InvalidCredentialsException(BookingSystemException):
    """Raised when password verification fails or email is not found during login."""

    pass


class RoleNotFoundException(BookingSystemException):
    """Raised when assigning or querying a role that does not exist in the database."""

    pass


class PermissionDeniedException(BookingSystemException):
    """Raised when a user lacks the necessary role permissions for an operation."""

    pass


class AuthenticationRequiredException(BookingSystemException):
    """Raised when an operation requires a valid token but none is provided or valid."""

    pass
