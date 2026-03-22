import enum
import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, Enum, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from server.app.core.database import Base


class MatchStatus(str, enum.Enum):
    UPCOMING = "UPCOMING"
    LOCKED = "LOCKED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"


class Match(Base):
    __tablename__ = "matches"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    team_a = Column(String, nullable=False)
    team_b = Column(String, nullable=False)
    venue = Column(String, nullable=False)
    start_time = Column(DateTime, nullable=False)
    status = Column(Enum(MatchStatus), default=MatchStatus.UPCOMING, nullable=False)
    external_id = Column(String, unique=True, nullable=True)
    toss_winner = Column(String, nullable=True)  # team name that won the toss
    motm_player_id = Column(UUID(as_uuid=True), ForeignKey("players.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    fantasy_teams = relationship("FantasyTeam", back_populates="match")
    points = relationship("PerformancePoint", back_populates="match")
