"""Dependency that loads the user represented by a bearer token."""

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.security import decode_access_token
from app.db.session import get_db
from app.models.user import User


# auto_error=False lets us return HTTP 401 for a missing token instead of 403.
bearer_scheme = HTTPBearer(auto_error=False)


def credentials_error():
    """Create the same response for every invalid authentication token."""

    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
):
    """Validate the bearer token and load its user from the database."""

    if credentials is None or credentials.scheme.lower() != "bearer":
        raise credentials_error()

    try:
        user_id = decode_access_token(credentials.credentials)
    except jwt.InvalidTokenError:
        raise credentials_error()

    user = db.get(User, user_id)
    if user is None:
        raise credentials_error()

    return user
