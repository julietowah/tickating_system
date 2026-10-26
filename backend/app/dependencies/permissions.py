"""Reusable ticket authorization dependencies."""

from fastapi import Depends, HTTPException, Path, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.dependencies.auth import get_current_user
from app.models.ticket import Ticket, TicketStatus
from app.models.user import User, UserRole


def require_admin(
    current_user: User = Depends(get_current_user),
) -> User:
    """Allow only authenticated administrators to continue."""

    if current_user.role != UserRole.ADMIN.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Administrator access required",
        )

    return current_user


def get_visible_ticket(
    ticket_id: int = Path(ge=1),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Ticket:
    """Load a ticket if the current user is allowed to see it."""

    ticket = db.get(Ticket, ticket_id)

    if ticket is None or (
        current_user.role != UserRole.ADMIN.value
        and ticket.owner_id != current_user.id
    ):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found",
        )

    return ticket


def get_editable_ticket(
    ticket_id: int = Path(ge=1),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Ticket:
    """Load a ticket whose content the current user may edit."""

    # This first applies the owner-or-administrator visibility rule.
    ticket = get_visible_ticket(
        ticket_id=ticket_id,
        current_user=current_user,
        db=db,
    )

    if (
        current_user.role != UserRole.ADMIN.value
        and ticket.status == TicketStatus.RESOLVED.value
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Resolved tickets cannot be edited",
        )

    return ticket
