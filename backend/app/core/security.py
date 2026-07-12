from datetime import datetime, timedelta, timezone
from typing import Any, Optional
import bcrypt
import jwt

from app.core.config import settings

# Password Security Functions


def hash_password(password: str) -> str:
    """Hashes a plain-text password using bcrypt.

    Args:
        password: Plain text password to hash.

    Returns:
        The hashed password as a string.
    """
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies a plain-text password against a hashed bcrypt password.

    Args:
        plain_password: The user's input password.
        hashed_password: The stored hashed password from the database.

    Returns:
        True if the password matches, False otherwise.
    """
    try:
        return bcrypt.checkpw(
            plain_password.encode("utf-8"),
            hashed_password.encode("utf-8"),
        )
    except Exception:
        return False


# JWT Token Security Functions


def create_access_token(
    subject: str | Any, expires_delta: Optional[timedelta] = None
) -> str:
    """Generates a signed JWT access token.

    Args:
        subject: The unique identifier (usually email) to store in the token.
        expires_delta: Optional custom lifetime duration.

    Returns:
        Encoded JWT token as a string.
    """
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )

    to_encode = {
        "exp": expire,
        "sub": str(subject),
        "iat": datetime.now(timezone.utc),
    }
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )
    return encoded_jwt


def decode_access_token(token: str) -> Optional[str]:
    """Decodes and validates a JWT access token.

    Args:
        token: The raw access token string.

    Returns:
        The subject (email) stored in the token if valid, or None if expired/invalid.
    """
    try:
        decoded_token = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )
        return decoded_token.get("sub")
    except (jwt.PyJWTError, KeyError):
        return None
