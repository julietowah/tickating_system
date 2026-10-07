"""Database connection and session setup for the FastAPI application."""

import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


# Load values from the .env file into the environment.
load_dotenv()

# Use DATABASE_URL from .env, or use this SQLite database by default.
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./service_desk.db")

# The engine manages connections to the database.
engine = create_engine(
    DATABASE_URL,
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
