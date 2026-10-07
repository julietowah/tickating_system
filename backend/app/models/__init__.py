"""Import all models so SQLAlchemy and Alembic can discover them."""

from app.models.comment import Comment
from app.models.ticket import Ticket, TicketPriority, TicketStatus
from app.models.user import User, UserRole

__all__ = [
    "Comment",
    "Ticket",
    "TicketPriority",
    "TicketStatus",
    "User",
    "UserRole",
]
