"""Tests for centralized authorization dependencies."""

import pytest
from fastapi import HTTPException

from app.dependencies.permissions import get_editable_ticket, require_admin
from app.models.ticket import TicketStatus
from app.models.user import User, UserRole
from app.schemas.ticket import TicketCreate
from app.services.tickets import create_ticket


def make_user(db_session, name: str, email: str, role: UserRole) -> User:
    """Create a user for an authorization scenario."""

    user = User(
        full_name=name,
        email=email,
        password_hash="not-used-in-this-test",
        role=role.value,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


def make_ticket(db_session, owner: User):
    """Create an open ticket owned by the supplied user."""

    return create_ticket(
        db_session,
        TicketCreate(
            title="Authorization test ticket",
            description="This ticket is used to test authorization rules.",
        ),
        owner,
    )


def test_require_admin_accepts_administrator(db_session):
    admin = make_user(
        db_session,
        "System Admin",
        "admin@example.com",
        UserRole.ADMIN,
    )

    assert require_admin(current_user=admin) is admin


def test_require_admin_rejects_normal_user(db_session):
    user = make_user(
        db_session,
        "Ada Okafor",
        "ada@example.com",
        UserRole.USER,
    )

    with pytest.raises(HTTPException) as error:
        require_admin(current_user=user)

    assert error.value.status_code == 403
    assert error.value.detail == "Administrator access required"


def test_owner_can_edit_unresolved_ticket(db_session):
    owner = make_user(
        db_session,
        "Ada Okafor",
        "ada@example.com",
        UserRole.USER,
    )
    ticket = make_ticket(db_session, owner)

    editable_ticket = get_editable_ticket(
        ticket_id=ticket.id,
        current_user=owner,
        db=db_session,
    )

    assert editable_ticket.id == ticket.id


def test_owner_cannot_edit_resolved_ticket(db_session):
    owner = make_user(
        db_session,
        "Ada Okafor",
        "ada@example.com",
        UserRole.USER,
    )
    ticket = make_ticket(db_session, owner)
    ticket.status = TicketStatus.RESOLVED.value
    db_session.commit()

    with pytest.raises(HTTPException) as error:
        get_editable_ticket(
            ticket_id=ticket.id,
            current_user=owner,
            db=db_session,
        )

    assert error.value.status_code == 403
    assert error.value.detail == "Resolved tickets cannot be edited"


def test_admin_can_edit_resolved_ticket(db_session):
    owner = make_user(
        db_session,
        "Ada Okafor",
        "ada@example.com",
        UserRole.USER,
    )
    admin = make_user(
        db_session,
        "System Admin",
        "admin@example.com",
        UserRole.ADMIN,
    )
    ticket = make_ticket(db_session, owner)
    ticket.status = TicketStatus.RESOLVED.value
    db_session.commit()

    editable_ticket = get_editable_ticket(
        ticket_id=ticket.id,
        current_user=admin,
        db=db_session,
    )

    assert editable_ticket.id == ticket.id


def test_normal_user_cannot_edit_another_users_ticket(db_session):
    owner = make_user(
        db_session,
        "Ada Okafor",
        "ada@example.com",
        UserRole.USER,
    )
    other_user = make_user(
        db_session,
        "Ben Ali",
        "ben@example.com",
        UserRole.USER,
    )
    ticket = make_ticket(db_session, owner)

    with pytest.raises(HTTPException) as error:
        get_editable_ticket(
            ticket_id=ticket.id,
            current_user=other_user,
            db=db_session,
        )

    assert error.value.status_code == 404
    assert error.value.detail == "Ticket not found"
