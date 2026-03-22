import uuid
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from server.app.models.player import PlayerRole


class PlayerOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    role: str
    franchise: str
    cost: float
    image_url: str | None = None
    nationality: str | None = None


class PlayerCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    role: PlayerRole
    franchise: str = Field(..., min_length=1, max_length=100)
    cost: float = Field(..., gt=0)
    image_url: str | None = None


class PlayerUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    role: Optional[PlayerRole] = None
    franchise: Optional[str] = Field(None, min_length=1, max_length=100)
    cost: Optional[float] = Field(None, gt=0)
    image_url: Optional[str] = None
