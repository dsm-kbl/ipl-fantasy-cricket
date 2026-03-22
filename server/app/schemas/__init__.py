# Pydantic request/response schemas
from server.app.schemas.auth import (
    AuthTokenResponse,
    LoginRequest,
    RegisterRequest,
    UserOut,
)
from server.app.schemas.error import ErrorBody, ErrorDetail, ErrorResponse
from server.app.schemas.fantasy_team import (
    FantasyTeamCreate,
    FantasyTeamOut,
    ValidationResult,
)
from server.app.schemas.leaderboard import LeaderboardEntry
from server.app.schemas.match import MatchCreate, MatchOut, MatchWithPlayers
from server.app.schemas.player import PlayerCreate, PlayerOut, PlayerUpdate
from server.app.schemas.points import PlayerPoints, PlayerPointsOut, PointsSubmission

__all__ = [
    # Auth
    "RegisterRequest",
    "LoginRequest",
    "UserOut",
    "AuthTokenResponse",
    # Player
    "PlayerOut",
    "PlayerCreate",
    "PlayerUpdate",
    # Match
    "MatchOut",
    "MatchCreate",
    "MatchWithPlayers",
    # Fantasy Team
    "FantasyTeamCreate",
    "FantasyTeamOut",
    "ValidationResult",
    # Points
    "PlayerPoints",
    "PlayerPointsOut",
    "PointsSubmission",
    # Leaderboard
    "LeaderboardEntry",
    # Error
    "ErrorDetail",
    "ErrorBody",
    "ErrorResponse",
]
