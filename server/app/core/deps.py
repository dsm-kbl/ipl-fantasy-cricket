"""FastAPI dependencies for authentication and authorization."""

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from server.app.core.database import get_db
from server.app.models.user import User, UserRole
from server.app.services.auth_service import AuthError, get_user_by_token

bearer_scheme = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    """Extract and verify JWT from the Authorization Bearer header.

    Returns the authenticated User or raises 401.
    """
    try:
        user = await get_user_by_token(db, credentials.credentials)
        return user
    except AuthError as exc:
        raise HTTPException(
            status_code=exc.status_code,
            detail=exc.error_response.model_dump(),
        )


async def get_admin_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """Require the current user to have the ADMIN role.

    Returns the admin User or raises 403.
    """
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=403,
            detail={
                "error": {
                    "code": "FORBIDDEN",
                    "message": "Admin access required",
                    "details": [],
                }
            },
        )
    return current_user
