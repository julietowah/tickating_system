"""The database model for support tickets."""

from enum import Enum

from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.orm import relationship

from app.db.base import Base


class TicketPriority(str, Enum):
    """The priority choices accepted by the application."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class TicketStatus(str, Enum):
    """The stages a ticket can move through."""

    OPEN = "open"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"


class Ticket(Base):
    """A support request created by a user."""

    __tablename__ = "tickets"

    id = Column(Integer, primary_key=True)
    title = Column(String(120), nullable=False)
    description = Column(Text, nullable=False)

    # A new ticket uses medium priority if the user does not choose one.
    priority = Column(
        String(6),
        nullable=False,
        default=TicketPriority.MEDIUM.value,
        server_default=TicketPriority.MEDIUM.value,
    )

    # All new tickets begin in the open state.
    status = Column(
        String(11),
        nullable=False,
        default=TicketStatus.OPEN.value,
        server_default=TicketStatus.OPEN.value,
    )

    # This foreign key connects each ticket to one user in the users table.
    owner_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )

    # The database sets created_at. SQLAlchemy refreshes updated_at after edits.
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    # ticket.owner returns the User who created this ticket.
    owner = relationship("User", back_populates="tickets")

    # ticket.comments returns its comments from oldest to newest.
    comments = relationship(
        "Comment",
        back_populates="ticket",
        cascade="all, delete-orphan",
        passive_deletes=True,
        order_by="Comment.created_at",
    )
