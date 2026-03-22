import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, Float, ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from server.app.core.database import Base


class FantasyTeam(Base):
    __tablename__ = "fantasy_teams"
    __table_args__ = (UniqueConstraint("user_id", "match_id"),)

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    match_id = Column(UUID(as_uuid=True), ForeignKey("matches.id"), nullable=False)
    total_score = Column(Float, default=0, nullable=False)
    toss_prediction = Column(String, nullable=True)  # team name predicted to win toss
    motm_prediction = Column(UUID(as_uuid=True), ForeignKey("players.id"), nullable=True)  # predicted MOTM player
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="fantasy_teams")
    match = relationship("Match", back_populates="fantasy_teams")
    players = relationship("FantasyTeamPlayer", back_populates="fantasy_team", cascade="all, delete-orphan")


class FantasyTeamPlayer(Base):
    __tablename__ = "fantasy_team_players"
    __table_args__ = (UniqueConstraint("fantasy_team_id", "player_id"),)

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    fantasy_team_id = Column(UUID(as_uuid=True), ForeignKey("fantasy_teams.id", ondelete="CASCADE"), nullable=False)
    player_id = Column(UUID(as_uuid=True), ForeignKey("players.id"), nullable=False)

    fantasy_team = relationship("FantasyTeam", back_populates="players")
    player = relationship("Player", back_populates="team_players")
