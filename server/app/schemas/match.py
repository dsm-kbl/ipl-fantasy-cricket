import uuid
from datetime import datetime, timezone
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_serializer

from server.app.schemas.player import PlayerOut


class MatchOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    team_a: str
    team_b: str
    venue: str
    start_time: datetime
    status: str
    toss_winner: str | None = None
    motm_player_id: uuid.UUID | None = None

    @field_serializer("start_time")
    def serialize_start_time(self, value: datetime) -> str:
        """Ensure start_time is serialized with Z suffix so browsers treat it as UTC."""
        return value.strftime("%Y-%m-%dT%H:%M:%SZ")


class MatchCreate(BaseModel):
    team_a: str = Field(..., min_length=1, max_length=100)
    team_b: str = Field(..., min_length=1, max_length=100)
    venue: str = Field(..., min_length=1, max_length=200)
    start_time: datetime


class MatchUpdate(BaseModel):
    team_a: Optional[str] = Field(None, min_length=1, max_length=100)
    team_b: Optional[str] = Field(None, min_length=1, max_length=100)
    venue: Optional[str] = Field(None, min_length=1, max_length=200)
    start_time: Optional[datetime] = None
    status: Optional[str] = None
    toss_winner: Optional[str] = None
    motm_player_id: Optional[uuid.UUID] = None


class MatchWithPlayers(BaseModel):
    match: MatchOut
    players: list[PlayerOut]
