"""Schemas used during login and token creation."""

from pydantic import BaseModel, ConfigDict, EmailStr, field_validator


class LoginRequest(BaseModel):
    """Credentials accepted by the login endpoint."""

    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    email: EmailStr
    password: str

    @field_validator("email", mode="before")
    @classmethod
    def normalize_email(cls, value):
        """Use the same lowercase email format as registration."""

        if isinstance(value, str):
            return value.strip().lower()
        return value


class TokenResponse(BaseModel):
    """The JWT returned after a successful login."""

    access_token: str
    token_type: str = "bearer"
