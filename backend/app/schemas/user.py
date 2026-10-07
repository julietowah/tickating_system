"""Schemas for creating and returning users."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from app.models.user import UserRole


class UserCreate(BaseModel):
    """Information accepted when a user registers."""

    # Strip surrounding spaces and reject fields such as "role".
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    full_name: str = Field(min_length=2, max_length=120)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)

    @field_validator("email", mode="before")
    @classmethod
    def normalize_email(cls, value):
        """Store email addresses in lowercase for reliable comparisons."""

        if isinstance(value, str):
            return value.strip().lower()
        return value


class UserResponse(BaseModel):
    """Safe user information returned by the API."""

    # This lets Pydantic read values from a SQLAlchemy User object.
    model_config = ConfigDict(from_attributes=True)

    id: int
    full_name: str
    email: EmailStr
    role: UserRole
    created_at: datetime

    # password and password_hash are intentionally not response fields.
