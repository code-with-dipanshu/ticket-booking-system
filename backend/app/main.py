from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.db.session import get_db

app = FastAPI(
    title="Ticket Booking System API",
    description="Backend API for the Ticket Booking System",
    version="1.0.0",
)


@app.get("/")
def root():
    return {"message": "Welcome to Ticket Booking System 🚀"}


@app.get("/health")
def health(db: Session = Depends(get_db)):
    try:
        # Run a simple query to verify the db is alive
        db.execute(text("SELECT 1"))
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database connection failed: {str(e)}",
        )