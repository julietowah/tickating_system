"""The database model for comments added to tickets."""

from sqlalchemy import (
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Text,
    func,
)
from sqlalchemy.orm import relationship

from app.db.base import Base


class Comment(Base):
    """A message written by a user on a ticket."""

    __tablename__ = "comments"

    __table_args__ = (
        # trim removes spaces before checking that the comment is not empty.
        CheckConstraint(
            "length(trim(body)) > 0",
            name="ck_comments_body_not_blank",
        ),
        # These indexes make finding comments by ticket or author faster.
        Index("ix_comments_ticket_id", "ticket_id"),
        Index("ix_comments_author_id", "author_id"),
    )

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
