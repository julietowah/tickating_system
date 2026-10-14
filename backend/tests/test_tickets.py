"""Tests for ticket creation."""

import os

os.environ.setdefault("SECRET_KEY", "test-secret-key")

import pytest
from pydantic import ValidationError

from app.main import app
from app.models.ticket import TicketStatus
from app.models.user import User
from app.schemas.ticket import TicketCreate
from app.services.tickets import create_ticket


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
