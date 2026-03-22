import uuid

from pydantic import BaseModel


class PlayerPoints(BaseModel):
    player_id: uuid.UUID
    points: float


class PointsSubmission(BaseModel):
    points: list[PlayerPoints]


class PlayerPointsOut(BaseModel):
    player_id: uuid.UUID
    player_name: str
    franchise: str
    role: str
    points: float
