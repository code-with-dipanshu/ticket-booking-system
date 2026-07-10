from fastapi import FastAPI

app = FastAPI(
    title="Ticket Booking System API",
    description="Backend API for the Ticket Booking System",
    version="1.0.0",
)


@app.get("/")
def root():
    return {
        "message": "Welcome to Ticket Booking System 🚀"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }