"""Schemas for creating, updating, and returning tickets."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.ticket import TicketPriority, TicketStatus


class TicketCreate(BaseModel):
    """Information accepted when creating a ticket."""

    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    title: str = Field(min_length=5, max_length=120)
    description: str = Field(min_length=20)
    priority: TicketPriority = TicketPriority.MEDIUM


class TicketContentUpdate(BaseModel):
    """Fields a ticket owner is allowed to edit."""

    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    # None means the client chose not to update that field.
    title: str | None = Field(default=None, min_length=5, max_length=120)
    description: str | None = Field(default=None, min_length=20)
    priority: TicketPriority | None = None


class TicketStatusUpdate(BaseModel):
    """The status field that only an administrator may change."""

    model_config = ConfigDict(extra="forbid")

    status: TicketStatus


class TicketResponse(BaseModel):
    """Ticket information returned by the API."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str
    priority: TicketPriority
    status: TicketStatus
    owner_id: int
    created_at: datetime
    updated_at: datetime
