import logging
from sqlalchemy import text

from app.db.database import engine

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("verify_db")


def verify_connection():
    logger.info("Attempting to connect to PostgreSQL database...")
    try:
        # Connect to the engine and run a test query
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            logger.info("Database connection successful!")
            logger.info(f"Test query result (SELECT 1): {result.scalar()}")
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        raise e


if __name__ == "__main__":
    verify_connection()
