"""Database operations for support tickets."""

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.ticket import Ticket, TicketPriority, TicketStatus
from app.models.user import User, UserRole
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


def list_tickets(
    db: Session,
    current_user: User,
    page: int,
    page_size: int,
    ticket_status: TicketStatus | None = None,
    priority: TicketPriority | None = None,
) -> tuple[list[Ticket], int]:
    """Return one visible, filtered page of tickets and its total count."""

    filters = []

    # Normal users can only see their own tickets; admins can see every ticket.
    if current_user.role != UserRole.ADMIN.value:
        filters.append(Ticket.owner_id == current_user.id)

    if ticket_status is not None:
        filters.append(Ticket.status == ticket_status.value)

    if priority is not None:
        filters.append(Ticket.priority == priority.value)

    total = db.scalar(
        select(func.count()).select_from(Ticket).where(*filters)
    )
    tickets = db.scalars(
        select(Ticket)
        .where(*filters)
        .order_by(Ticket.created_at.desc(), Ticket.id.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    ).all()

    return list(tickets), total or 0
