import uuid
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from server.app.schemas.player import PlayerOut


class FantasyTeamCreate(BaseModel):
    match_id: uuid.UUID
    player_ids: list[uuid.UUID] = Field(..., min_length=11, max_length=11)
    toss_prediction: Optional[str] = None  # team name
    motm_prediction: Optional[uuid.UUID] = None  # player id


class FantasyTeamUpdate(BaseModel):
    player_ids: list[uuid.UUID] = Field(..., min_length=11, max_length=11)
    toss_prediction: Optional[str] = None
    motm_prediction: Optional[uuid.UUID] = None


class FantasyTeamOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    match_id: uuid.UUID
    total_score: float
    players: list[PlayerOut]
    remaining_budget: float
    toss_prediction: str | None = None
    motm_prediction: uuid.UUID | None = None


class ValidationResult(BaseModel):
    valid: bool
    errors: list[str]
