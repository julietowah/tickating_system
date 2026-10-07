"""The common base class used by all database models."""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """SQLAlchemy uses this class to collect our table information."""

    pass
