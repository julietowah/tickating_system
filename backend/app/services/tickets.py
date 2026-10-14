"""Database operations for support tickets."""

from sqlalchemy.orm import Session

from app.models.ticket import Ticket
from app.models.user import User
from app.schemas.ticket import TicketCreate


def create_ticket(
    db: Session,
    ticket_data: TicketCreate,
    owner: User,
) -> Ticket:
    """Create a new open ticket belonging to the authenticated user."""

    ticket = Ticket(
        title=ticket_data.title,
        description=ticket_data.description,
        priority=ticket_data.priority.value,
        owner_id=owner.id,
    )
    db.add(ticket)
    db.commit()
    db.refresh(ticket)

    return ticket
