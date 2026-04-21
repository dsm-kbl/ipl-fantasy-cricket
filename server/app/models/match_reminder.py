"""Model for tracking which match reminders have been sent to users."""

import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID

from server.app.core.database import Base


class MatchReminderSent(Base):
    """Tracks match reminder emails sent to users to prevent duplicates."""

    __tablename__ = "match_reminders_sent"
    __table_args__ = (
        UniqueConstraint("match_id", "user_id", "reminder_type"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    match_id = Column(UUID(as_uuid=True), ForeignKey("matches.id"), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    reminder_type = Column(String, nullable=False)  # "60min" or "30min"
    sent_at = Column(DateTime, default=datetime.utcnow, nullable=False)
