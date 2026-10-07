"""The database model for application users."""

from enum import Enum

from sqlalchemy import Column, DateTime, Integer, String, func
from sqlalchemy.orm import relationship, validates

from app.db.base import Base


class UserRole(str, Enum):
    """The only roles a user is allowed to have."""

    USER = "user"
    ADMIN = "admin"


class User(Base):
    """A person who can sign in and use the ticket system."""

    # This is the table name that will appear in SQLite.
    __tablename__ = "users"

    # primary_key=True makes each user's ID unique.
    id = Column(Integer, primary_key=True)

    # A name can contain up to 120 characters and cannot be empty/NULL.
    full_name = Column(String(120), nullable=False)

    # unique=True prevents two accounts from using the same email address.
    # NOCASE makes SQLite compare emails without caring about letter case.
    email = Column(
        String(320, collation="NOCASE"),
        nullable=False,
        unique=True,
    )

    # Only a secure hash is stored. The original password is never stored.
    password_hash = Column(String(255), nullable=False)

    # Every new account is a normal user unless an admin script says otherwise.
    role = Column(
        String(5),
        nullable=False,
        default=UserRole.USER.value,
        server_default=UserRole.USER.value,
    )

    # The database automatically records when the user was created.
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    # These relationships let us use user.tickets and user.comments in Python.
    tickets = relationship(
        "Ticket",
        back_populates="owner",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    comments = relationship(
        "Comment",
        back_populates="author",
        passive_deletes=True,
    )

    @validates("email")
    def normalize_email(self, _key, value):
        """Turn ' USER@Example.com ' into 'user@example.com' before saving."""

        return value.strip().lower()
