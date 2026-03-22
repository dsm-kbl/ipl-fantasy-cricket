"""Custom exception classes for the IPL Fantasy Cricket application.

Each exception maps to a specific error code and HTTP status from the design's
error categories table. FastAPI global exception handlers (registered in main.py)
catch these and return the standard JSON error envelope.
"""

from typing import Optional


class AppError(Exception):
    """Base application error. All custom exceptions inherit from this."""

    code: str = "INTERNAL_ERROR"
    status_code: int = 500
    message: str = "An unexpected error occurred"

    def __init__(
        self,
        message: Optional[str] = None,
        details: Optional[list[dict]] = None,
    ):
        self.message = message or self.__class__.message
        self.details = details or []
        super().__init__(self.message)


class ValidationError(AppError):
    code = "VALIDATION_ERROR"
    status_code = 400
    message = "Validation failed"


class AuthError(AppError):
    code = "AUTH_ERROR"
    status_code = 401
    message = "Authentication failed"


class ForbiddenError(AppError):
    code = "FORBIDDEN"
    status_code = 403
    message = "Access denied"


class NotFoundError(AppError):
    code = "NOT_FOUND"
    status_code = 404
    message = "Resource not found"


class ConflictError(AppError):
    code = "CONFLICT"
    status_code = 409
    message = "Resource conflict"


class TeamLockedError(AppError):
    code = "TEAM_LOCKED"
    status_code = 403
    message = "Team modifications are locked"


class BudgetExceededError(AppError):
    code = "BUDGET_EXCEEDED"
    status_code = 400
    message = "Player cost exceeds remaining budget"


class TeamFullError(AppError):
    code = "TEAM_FULL"
    status_code = 400
    message = "Fantasy team already has 11 players"


class TeamInvalidError(AppError):
    code = "TEAM_INVALID"
    status_code = 400
    message = "Fantasy team does not meet composition requirements"


class PointsIncompleteError(AppError):
    code = "POINTS_INCOMPLETE"
    status_code = 400
    message = "Points must be provided for all players in the match pool"


class ExternalApiError(AppError):
    code = "EXTERNAL_API_ERROR"
    status_code = 502
    message = "External API is unavailable"
