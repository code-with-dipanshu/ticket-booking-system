import logging
from contextlib import asynccontextmanager
from datetime import datetime, timedelta, timezone

from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.api.v1.endpoints import auth as auth_router
from app.api.v1.endpoints import booking as booking_router
from app.api.v1.endpoints import event as event_router
from app.api.v1.endpoints import test_auth as test_auth_router
from app.api.v1.endpoints import venue as venue_router
from app.core.config import settings
from app.core.exceptions import (
    AuthenticationRequiredException,
    InvalidCredentialsException,
    PermissionDeniedException,
    RoleNotFoundException,
    UserAlreadyExistsException,
)
from app.core.security import hash_password
from app.db.base import Base
from app.db.database import engine, SessionLocal
from app.db.session import get_db
from app.models.booking import Booking  # noqa: F401 - registers Booking with Base.metadata
from app.models.booking_seat import BookingSeat  # noqa: F401 - registers BookingSeat with Base.metadata
from app.models.event import Event  # noqa: F401 - registers Event with Base.metadata
from app.models.event_price import EventPrice  # noqa: F401 - registers EventPrice with Base.metadata
from app.models.role import Role  # noqa: F401 - registers Role with Base.metadata
from app.models.seat import Seat  # noqa: F401 - registers Seat with Base.metadata
from app.models.seat_category import SeatCategory  # noqa: F401 - registers SeatCategory with Base.metadata
from app.models.user import User  # noqa: F401 - registers User with Base.metadata
from app.models.venue import Venue  # noqa: F401 - registers Venue with Base.metadata

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


def seed_demo_content(db: Session | None = None) -> None:
    """Seed sample users, venue, seat categories, and events for easy customer testing."""
    should_close = db is None
    db = db or SessionLocal()

    try:
        admin_role = db.query(Role).filter(Role.name == "admin").first()
        organizer_role = db.query(Role).filter(Role.name == "organizer").first()
        customer_role = db.query(Role).filter(Role.name == "customer").first()

        if not admin_role or not organizer_role or not customer_role:
            raise RuntimeError("Default roles are not available; seed_roles() must run first.")

        demo_users = [
            {
                "email": "admin@booking.com",
                "password": "secret123",
                "full_name": "Demo Admin",
                "role_id": admin_role.id,
            },
            {
                "email": "organizer@booking.com",
                "password": "secret123",
                "full_name": "Demo Organizer",
                "role_id": organizer_role.id,
            },
            {
                "email": "customer@booking.com",
                "password": "secret123",
                "full_name": "Demo Customer",
                "role_id": customer_role.id,
            },
        ]

        for user_data in demo_users:
            existing_user = db.query(User).filter(User.email == user_data["email"]).first()
            if not existing_user:
                db.add(
                    User(
                        email=user_data["email"],
                        hashed_password=hash_password(user_data["password"]),
                        full_name=user_data["full_name"],
                        role_id=user_data["role_id"],
                        is_active=True,
                    )
                )

        venue = db.query(Venue).filter(Venue.name == "Grand Arena").first()
        if not venue:
            venue = Venue(
                name="Grand Arena",
                city="Mumbai",
                address="Marine Drive",
                capacity=1200,
                description="Premium concert venue for live events",
            )
            db.add(venue)
            db.flush()

        vip_category = db.query(SeatCategory).filter(SeatCategory.name == "VIP").first()
        if not vip_category:
            vip_category = SeatCategory(
                name="VIP",
                description="Premium lounge seating",
                price_multiplier=2.0,
                venue_id=venue.id,
            )
            db.add(vip_category)
            db.flush()

        standard_category = (
            db.query(SeatCategory).filter(SeatCategory.name == "Standard").first()
        )
        if not standard_category:
            standard_category = SeatCategory(
                name="Standard",
                description="General admission seating",
                price_multiplier=1.0,
                venue_id=venue.id,
            )
            db.add(standard_category)
            db.flush()

        organizer_user = db.query(User).filter(User.email == "organizer@booking.com").first()
        if organizer_user is None:
            raise RuntimeError("Organizer demo user was not created.")

        event_titles = ["Sunset Live", "Neon Nights"]
        for title in event_titles:
            existing_event = db.query(Event).filter(Event.title == title).first()
            if not existing_event:
                start_time = datetime.now(timezone.utc) + timedelta(days=14)
                end_time = start_time + timedelta(hours=3)
                db.add(
                    Event(
                        title=title,
                        description=(
                            "A premium live performance with reserved and general admission seating."
                            if title == "Sunset Live"
                            else "An electrifying night of music and immersive stage visuals."
                        ),
                        venue_id=venue.id,
                        organizer_id=organizer_user.id,
                        start_time=start_time,
                        end_time=end_time,
                        status="published",
                    )
                )

        db.commit()
        logger.info("Seeded demo content for customer testing.")
    except Exception as exc:
        db.rollback()
        logger.error(f"Error seeding demo content: {exc}")
        raise
    finally:
        if should_close:
            db.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown lifecycle handler."""
    # Startup: Create tables and seed roles
    logger.info("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    logger.info("Seeding default roles...")
    seed_roles()
    logger.info("Seeding demo content...")
    seed_demo_content()
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

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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

app.include_router(
    venue_router.router,
    prefix=f"{settings.API_V1_STR}/venues",
    tags=["Venue Management"],
)

app.include_router(
    event_router.router,
    prefix=f"{settings.API_V1_STR}/events",
    tags=["Event Management"],
)

app.include_router(
    booking_router.router,
    prefix=f"{settings.API_V1_STR}/bookings",
    tags=["Booking Management"],
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