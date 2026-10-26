"""Endpoints for creating and managing support tickets."""

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.dependencies.auth import get_current_user
from app.dependencies.permissions import get_visible_ticket
from app.models.ticket import Ticket, TicketPriority, TicketStatus
from app.models.user import User
from app.schemas.ticket import TicketCreate, TicketListResponse, TicketResponse
from app.services.tickets import (
    create_ticket as create_ticket_service,
    list_tickets as list_tickets_service,
)


router = APIRouter(prefix="/tickets", tags=["Tickets"])


@router.post(
    "",
    response_model=TicketResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_ticket(
    ticket_data: TicketCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a ticket owned by the authenticated user."""

    return create_ticket_service(db, ticket_data, current_user)


@router.get("", response_model=TicketListResponse)
def list_tickets(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    ticket_status: TicketStatus | None = Query(default=None, alias="status"),
    priority: TicketPriority | None = Query(default=None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Return a filtered page of tickets visible to the current user."""

    items, total = list_tickets_service(
        db=db,
        current_user=current_user,
        page=page,
        page_size=page_size,
        ticket_status=ticket_status,
        priority=priority,
    )

    return TicketListResponse(
        items=items,
        page=page,
        page_size=page_size,
        total=total,
    )


@router.get("/{ticket_id}", response_model=TicketResponse)
def retrieve_ticket(ticket: Ticket = Depends(get_visible_ticket)):
    """Return one ticket visible to the authenticated user."""

    return ticket
