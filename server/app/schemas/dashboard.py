"""Dashboard response schemas."""

import uuid

from pydantic import BaseModel

from server.app.schemas.match import MatchOut


class MatchParticipation(BaseModel):
    """A match the user participated in, with their fantasy team score."""

    match: MatchOut
    team_id: uuid.UUID
    total_score: float


class UpcomingMatchStatus(BaseModel):
    """An upcoming match with the user's team status."""

    match: MatchOut
    status: str  # "created", "not_created", "locked"


class DashboardResponse(BaseModel):
    """Top-level dashboard payload."""

    participated_matches: list[MatchParticipation]
    overall_rank: int | None
    upcoming_matches: list[UpcomingMatchStatus]


class MatchDetailPlayer(BaseModel):
    """A player in the user's fantasy team with their performance points."""

    player_id: uuid.UUID
    player_name: str
    franchise: str
    role: str
    cost: float
    points: float | None


class DashboardMatchDetail(BaseModel):
    """Detailed view of a user's fantasy team for a specific match."""

    match: MatchOut
    team_id: uuid.UUID
    total_score: float
    players: list[MatchDetailPlayer]
    toss_prediction: str | None = None
    motm_prediction: uuid.UUID | None = None
    motm_player_name: str | None = None
