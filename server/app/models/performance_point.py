import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, Float, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from server.app.core.database import Base


class PerformancePoint(Base):
    __tablename__ = "performance_points"
    __table_args__ = (UniqueConstraint("match_id", "player_id"),)

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    match_id = Column(UUID(as_uuid=True), ForeignKey("matches.id"), nullable=False)
    player_id = Column(UUID(as_uuid=True), ForeignKey("players.id"), nullable=False)
    points = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    match = relationship("Match", back_populates="points")
    player = relationship("Player", back_populates="points")
