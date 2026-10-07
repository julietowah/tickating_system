"""Database operations used for registration and login."""

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.security import hash_password, verify_password
from app.models.user import User
from app.schemas.user import UserCreate


def get_user_by_email(db: Session, email: str):
    """Find one user by their normalized email address."""

    return db.scalar(select(User).where(User.email == email))


def register_user(db: Session, user_data: UserCreate):
    """Create a normal user, or return None when the email already exists."""

    if get_user_by_email(db, str(user_data.email)):
        return None

    user = User(
        full_name=user_data.full_name,
        email=str(user_data.email),
        password_hash=hash_password(user_data.password),
    )
    db.add(user)

    try:
        db.commit()
    except IntegrityError:
        # The database also protects against two simultaneous registrations.
        db.rollback()
        return None

    db.refresh(user)
    return user


def authenticate_user(db: Session, email: str, password: str):
    """Return the user when both credentials are correct."""

    user = get_user_by_email(db, email)

    if user is None or not verify_password(password, user.password_hash):
        return None

    return user
