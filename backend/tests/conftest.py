"""Shared test setup using an isolated in-memory database."""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import app.models  # noqa: F401 - register all tables with Base.metadata
from app.db.base import Base


@pytest.fixture
def db_session():
    """Provide a database session backed by a fresh in-memory database."""

    engine = create_engine("sqlite://")
    TestingSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine,
    )
    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()
    yield db
    db.close()
    Base.metadata.drop_all(bind=engine)
    engine.dispose()
