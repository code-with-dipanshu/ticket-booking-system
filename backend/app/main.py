import logging
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.api.v1.endpoints import auth as auth_router
from app.api.v1.endpoints import test_auth as test_auth_router
from app.core.config import settings
from app.core.exceptions import (
    AuthenticationRequiredException,
    InvalidCredentialsException,
    PermissionDeniedException,
    RoleNotFoundException,
    UserAlreadyExistsException,
)
from app.db.base import Base
from app.db.database import engine, SessionLocal
from app.db.session import get_db
from app.models.role import Role  # noqa: F401 - registers Role with Base.metadata
from app.models.user import User  # noqa: F401 - registers User with Base.metadata

logger = logging.getLogger(__name__)


def seed_roles() -> None:
    """Seeds the default roles into the database if they don't exist."""
    default_roles = [
        {"name": "admin", "description": "System administrator with full access"},
        {"name": "organizer", "description": "Event organizer who creates and manages events"},
        {"name": "customer", "description": "Customer who browses and books tickets"},
    ]
    db = SessionLocal()
    try:
        for role_data in default_roles:
            existing = db.query(Role).filter(Role.name == role_data["name"]).first()
            if not existing:
                db.add(Role(**role_data))
                logger.info(f"Seeded role: {role_data['name']}")
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(f"Error seeding roles: {e}")
        raise
    finally:
        db.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown lifecycle handler."""
    # Startup: Create tables and seed roles
    logger.info("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    logger.info("Seeding default roles...")
    seed_roles()
    logger.info("Application startup complete.")
    yield
    # Shutdown
    logger.info("Application shutdown.")


app = FastAPI(
    title="Ticket Booking System API",
    description="Backend API for the Ticket Booking System",
    version="1.0.0",
    lifespan=lifespan,
)

# --- Global Exception Handlers ---


@app.exception_handler(UserAlreadyExistsException)
async def user_already_exists_handler(request: Request, exc: UserAlreadyExistsException):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": exc.message},
    )


@app.exception_handler(InvalidCredentialsException)
async def invalid_credentials_handler(request: Request, exc: InvalidCredentialsException):
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={"detail": exc.message},
    )


@app.exception_handler(RoleNotFoundException)
async def role_not_found_handler(request: Request, exc: RoleNotFoundException):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": exc.message},
    )


@app.exception_handler(PermissionDeniedException)
async def permission_denied_handler(request: Request, exc: PermissionDeniedException):
    return JSONResponse(
        status_code=status.HTTP_403_FORBIDDEN,
        content={"detail": exc.message},
    )


@app.exception_handler(AuthenticationRequiredException)
async def auth_required_handler(request: Request, exc: AuthenticationRequiredException):
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={"detail": exc.message},
    )


# --- Include Routers ---

app.include_router(
    auth_router.router,
    prefix=f"{settings.API_V1_STR}/auth",
    tags=["Authentication"],
)

app.include_router(
    test_auth_router.router,
    prefix=f"{settings.API_V1_STR}/test-auth",
    tags=["Test Authentication"],
)


# --- Core Endpoints ---


@app.get("/")
def root():
    return {"message": "Welcome to Ticket Booking System 🚀"}


@app.get("/health")
def health(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database connection failed: {str(e)}",
        )