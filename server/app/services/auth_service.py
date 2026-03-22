"""Authentication service with register, login, and token verification."""

import re
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from server.app.core.security import create_access_token, hash_password, verify_password, verify_access_token
from server.app.models.user import User, UserRole
from server.app.schemas.auth import AuthTokenResponse, UserOut
from server.app.schemas.error import ErrorBody, ErrorDetail, ErrorResponse


class AuthError(Exception):
    """Base auth exception carrying an ErrorResponse and HTTP status code."""

    def __init__(self, status_code: int, error_response: ErrorResponse):
        self.status_code = status_code
        self.error_response = error_response
        super().__init__(error_response.error.message)


def _validate_registration(username: str, email: str, password: str) -> list[ErrorDetail]:
    """Validate registration inputs and return field-level errors."""
    errors: list[ErrorDetail] = []

    if not username or len(username.strip()) < 3:
        errors.append(ErrorDetail(field="username", message="Username must be at least 3 characters"))
    elif len(username) > 50:
        errors.append(ErrorDetail(field="username", message="Username must be at most 50 characters"))

    if not email or not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email):
        errors.append(ErrorDetail(field="email", message="Invalid email format"))

    if not password or len(password) < 8:
        errors.append(ErrorDetail(field="password", message="Password must be at least 8 characters"))
    elif len(password) > 128:
        errors.append(ErrorDetail(field="password", message="Password must be at most 128 characters"))

    return errors


async def register(
    db: AsyncSession, username: str, email: str, password: str
) -> UserOut:
    """Register a new user.

    Validates inputs, checks for duplicates, creates the user, and returns UserOut.

    Raises:
        AuthError: 400 for validation errors, 409 for duplicate email/username.
    """
    # Field-level validation
    validation_errors = _validate_registration(username, email, password)
    if validation_errors:
        raise AuthError(
            status_code=400,
            error_response=ErrorResponse(
                error=ErrorBody(
                    code="VALIDATION_ERROR",
                    message="Invalid registration data",
                    details=validation_errors,
                )
            ),
        )

    # Check duplicate username
    result = await db.execute(select(User).where(User.username == username))
    if result.scalars().first() is not None:
        raise AuthError(
            status_code=409,
            error_response=ErrorResponse(
                error=ErrorBody(
                    code="CONFLICT",
                    message="Username already in use",
                    details=[ErrorDetail(field="username", message="Username already in use")],
                )
            ),
        )

    # Check duplicate email
    result = await db.execute(select(User).where(User.email == email))
    if result.scalars().first() is not None:
        raise AuthError(
            status_code=409,
            error_response=ErrorResponse(
                error=ErrorBody(
                    code="CONFLICT",
                    message="Email already in use",
                    details=[ErrorDetail(field="email", message="Email already in use")],
                )
            ),
        )

    user = User(
        id=uuid.uuid4(),
        username=username,
        email=email,
        password_hash=hash_password(password),
        role=UserRole.USER,
    )
    db.add(user)
    await db.flush()

    return UserOut.model_validate(user)


async def login(db: AsyncSession, email: str, password: str) -> AuthTokenResponse:
    """Authenticate a user and return a JWT token.

    Raises:
        AuthError: 401 for invalid credentials.
    """
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalars().first()

    if user is None or not verify_password(password, user.password_hash):
        raise AuthError(
            status_code=401,
            error_response=ErrorResponse(
                error=ErrorBody(
                    code="AUTH_ERROR",
                    message="Invalid email or password",
                )
            ),
        )

    if not user.is_verified:
        raise AuthError(
            status_code=403,
            error_response=ErrorResponse(
                error=ErrorBody(
                    code="EMAIL_NOT_VERIFIED",
                    message="Please verify your email before logging in. Check your inbox for the verification link.",
                )
            ),
        )

    token = create_access_token(subject=str(user.id))
    return AuthTokenResponse(user=UserOut.model_validate(user), token=token)


async def get_user_by_token(db: AsyncSession, token: str) -> User:
    """Verify a JWT token and return the corresponding User.

    Raises:
        AuthError: 401 if token is invalid or user not found.
    """
    subject = verify_access_token(token)
    if subject is None:
        raise AuthError(
            status_code=401,
            error_response=ErrorResponse(
                error=ErrorBody(code="AUTH_ERROR", message="Invalid or expired token")
            ),
        )

    try:
        user_id = uuid.UUID(subject)
    except ValueError:
        raise AuthError(
            status_code=401,
            error_response=ErrorResponse(
                error=ErrorBody(code="AUTH_ERROR", message="Invalid token payload")
            ),
        )

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalars().first()
    if user is None:
        raise AuthError(
            status_code=401,
            error_response=ErrorResponse(
                error=ErrorBody(code="AUTH_ERROR", message="User not found")
            ),
        )

    return user
