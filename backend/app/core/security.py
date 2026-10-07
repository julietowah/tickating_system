"""Password hashing and JWT helper functions."""

from datetime import datetime, timedelta, timezone

import jwt
from pwdlib import PasswordHash

from app.core.config import settings


# recommended() currently selects Argon2, a secure password-hashing algorithm.
password_hasher = PasswordHash.recommended()
ALGORITHM = "HS256"


def hash_password(password: str) -> str:
    """Convert a plain password into a secure hash for database storage."""

    return password_hasher.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    """Check a plain password against the stored hash."""

    return password_hasher.verify(password, password_hash)


def create_access_token(user_id: int, expires_delta: timedelta | None = None) -> str:
    """Create a signed token containing the user's ID and expiry time."""

    expires_at = datetime.now(timezone.utc) + (
        expires_delta
        or timedelta(minutes=settings.access_token_expire_minutes)
    )
    payload = {"sub": str(user_id), "exp": expires_at}

    return jwt.encode(payload, settings.secret_key, algorithm=ALGORITHM)


def decode_access_token(token: str) -> int:
    """Validate a token and return the user ID stored inside it."""

    payload = jwt.decode(token, settings.secret_key, algorithms=[ALGORITHM])
    user_id = payload.get("sub")

    if user_id is None:
        raise jwt.InvalidTokenError("Token does not contain a user ID")

    try:
        return int(user_id)
    except (TypeError, ValueError) as error:
        raise jwt.InvalidTokenError("Token contains an invalid user ID") from error
