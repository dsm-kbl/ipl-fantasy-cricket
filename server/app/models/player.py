import enum
import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, Enum, Float, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from server.app.core.database import Base


class PlayerRole(str, enum.Enum):
    BATSMAN = "BATSMAN"
    BOWLER = "BOWLER"
    ALL_ROUNDER = "ALL_ROUNDER"
    WICKET_KEEPER = "WICKET_KEEPER"


class Player(Base):
    __tablename__ = "players"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    role = Column(Enum(PlayerRole), nullable=False)
    franchise = Column(String, nullable=False)
    cost = Column(Float, nullable=False)
    image_url = Column(String, nullable=True)
    nationality = Column(String, nullable=True, default="India")
    external_id = Column(String, unique=True, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    team_players = relationship("FantasyTeamPlayer", back_populates="player")
    points = relationship("PerformancePoint", back_populates="player")
