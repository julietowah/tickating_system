"""Tests for ticket creation."""

import os

os.environ.setdefault("SECRET_KEY", "test-secret-key")

import pytest
from pydantic import ValidationError

from app.main import app
from app.models.ticket import TicketPriority, TicketStatus
from app.models.user import User, UserRole
from app.schemas.ticket import TicketCreate
from app.services.tickets import create_ticket, list_tickets


def make_user(db_session) -> User:
    """Insert the ticket owner needed by the foreign-key relationship."""

    user = User(
        full_name="Ada Okafor",
        email="ada@example.com",
        password_hash="not-used-in-this-test",
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


def make_named_user(db_session, name: str, email: str, role: str) -> User:
    """Insert a user with the requested role for visibility tests."""

    user = User(
        full_name=name,
        email=email,
        password_hash="not-used-in-this-test",
        role=role,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


def test_create_ticket_assigns_owner_and_open_status(db_session):
    owner = make_user(db_session)
    ticket_data = TicketCreate(
        title="Cannot access student portal",
        description="The portal rejects my correct login credentials.",
        priority="high",
    )

    ticket = create_ticket(db_session, ticket_data, owner)

    assert ticket.id is not None
    assert ticket.owner_id == owner.id
    assert ticket.title == ticket_data.title
    assert ticket.priority == "high"
    assert ticket.status == TicketStatus.OPEN.value


def test_ticket_create_schema_rejects_invalid_input():
    with pytest.raises(ValidationError):
        TicketCreate(
            title="Bad",
            description="Too short",
            priority="urgent",
        )


def test_post_tickets_uses_current_user_dependency():
    operation = app.openapi()["paths"]["/tickets"]["post"]

    assert operation["security"] == [{"HTTPBearer": []}]
    assert "201" in operation["responses"]


def test_normal_user_lists_only_own_tickets(db_session):
    ada = make_named_user(
        db_session, "Ada Okafor", "ada@example.com", UserRole.USER.value
    )
    ben = make_named_user(
        db_session, "Ben Ali", "ben@example.com", UserRole.USER.value
    )
    create_ticket(
        db_session,
        TicketCreate(
            title="Ada ticket one",
            description="This ticket belongs only to Ada Okafor.",
            priority="high",
        ),
        ada,
    )
    create_ticket(
        db_session,
        TicketCreate(
            title="Ben ticket one",
            description="This ticket belongs only to Ben Ali.",
            priority="low",
        ),
        ben,
    )

    items, total = list_tickets(db_session, ada, page=1, page_size=20)

    assert total == 1
    assert len(items) == 1
    assert items[0].owner_id == ada.id


def test_admin_lists_all_tickets(db_session):
    ada = make_named_user(
        db_session, "Ada Okafor", "ada@example.com", UserRole.USER.value
    )
    admin = make_named_user(
        db_session, "System Admin", "admin@example.com", UserRole.ADMIN.value
    )
    create_ticket(
        db_session,
        TicketCreate(
            title="First visible ticket",
            description="This ticket should be visible to the administrator.",
        ),
        ada,
    )
    create_ticket(
        db_session,
        TicketCreate(
            title="Second visible ticket",
            description="This ticket should also be visible to the administrator.",
        ),
        admin,
    )

    items, total = list_tickets(db_session, admin, page=1, page_size=20)

    assert total == 2
    assert len(items) == 2


def test_list_tickets_filters_before_paginating(db_session):
    owner = make_user(db_session)
    for number in range(3):
        create_ticket(
            db_session,
            TicketCreate(
                title=f"High priority ticket {number}",
                description="This is a high priority ticket used for pagination.",
                priority="high",
            ),
            owner,
        )
    create_ticket(
        db_session,
        TicketCreate(
            title="Low priority ticket",
            description="This low priority ticket must be excluded by filtering.",
            priority="low",
        ),
        owner,
    )

    items, total = list_tickets(
        db_session,
        owner,
        page=2,
        page_size=2,
        ticket_status=TicketStatus.OPEN,
        priority=TicketPriority.HIGH,
    )

    assert total == 3
    assert len(items) == 1
    assert items[0].priority == TicketPriority.HIGH.value


def test_get_tickets_contract_requires_auth_and_has_filters():
    operation = app.openapi()["paths"]["/tickets"]["get"]
    parameters = {parameter["name"] for parameter in operation["parameters"]}

    assert operation["security"] == [{"HTTPBearer": []}]
    assert {"page", "page_size", "status", "priority"} <= parameters
