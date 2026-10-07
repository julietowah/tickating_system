"""Schemas for creating and returning ticket comments."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class CommentCreate(BaseModel):
    """Information accepted when adding a comment."""

    # Whitespace is stripped before the minimum-length check runs.
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    body: str = Field(min_length=1)


class CommentResponse(BaseModel):
    """Comment information returned by the API."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    ticket_id: int
    author_id: int
    body: str
    created_at: datetime
