"""The database model for support tickets."""

from enum import Enum

from sqlalchemy import (
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Index,
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

    # These rules protect the database even if validation is accidentally skipped.
    __table_args__ = (
        CheckConstraint(
            "length(title) BETWEEN 5 AND 120",
            name="ck_tickets_title_length",
        ),
        CheckConstraint(
            "length(description) >= 20",
            name="ck_tickets_description_length",
        ),
        CheckConstraint(
            "priority IN ('low', 'medium', 'high')",
            name="ck_tickets_priority_values",
        ),
        CheckConstraint(
            "status IN ('open', 'in_progress', 'resolved')",
            name="ck_tickets_status_values",
        ),
        # Indexes make common ticket searches faster.
        Index("ix_tickets_owner_id", "owner_id"),
        Index("ix_tickets_status", "status"),
        Index("ix_tickets_priority", "priority"),
    )

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
