"""Database connection and session setup for the FastAPI application."""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings


# The engine manages connections to the database.
engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False},
)

# SessionLocal creates the sessions used to read and write database data.
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


def get_db():
    """Give one database session to a request, then close it afterward."""

    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
