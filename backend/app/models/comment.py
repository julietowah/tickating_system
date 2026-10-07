"""The database model for comments added to tickets."""

from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    Text,
    func,
)
from sqlalchemy.orm import relationship

from app.db.base import Base


class Comment(Base):
    """A message written by a user on a ticket."""

    __tablename__ = "comments"

    id = Column(Integer, primary_key=True)

    # This links the comment to the ticket it belongs to.
    ticket_id = Column(
        Integer,
        ForeignKey("tickets.id", ondelete="CASCADE"),
        nullable=False,
    )

    # This links the comment to the user who wrote it.
    author_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )

    body = Column(Text, nullable=False)
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    # These relationships provide comment.ticket and comment.author in Python.
    ticket = relationship("Ticket", back_populates="comments")
    author = relationship("User", back_populates="comments")
