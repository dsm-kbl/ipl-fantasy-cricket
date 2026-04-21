"""Notification service for sending match reminders to users."""

import logging
import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from server.app.models.fantasy_team import FantasyTeam
from server.app.models.match import Match, MatchStatus
from server.app.models.match_reminder import MatchReminderSent
from server.app.models.user import User, UserRole
from server.app.services.email_service import send_match_reminder_email

logger = logging.getLogger(__name__)

IST = timezone(timedelta(hours=5, minutes=30))

# Reminder windows: a cron running every 15 min catches matches that fall in
# either of these windows. We only send once per (user, match, reminder_type).
REMINDER_WINDOWS = [
    # type, min_minutes, max_minutes
    ("60min", 55, 70),
    ("30min", 25, 40),
]


def _format_ist(dt: datetime) -> str:
    """Format a UTC datetime as IST time string (e.g., '7:30 PM')."""
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    ist = dt.astimezone(IST)
    return ist.strftime("%-I:%M %p")


async def _find_matches_in_window(
    db: AsyncSession, now: datetime, min_minutes: int, max_minutes: int
) -> list[Match]:
    """Find matches starting between min_minutes and max_minutes from now."""
    window_start = now + timedelta(minutes=min_minutes)
    window_end = now + timedelta(minutes=max_minutes)
    result = await db.execute(
        select(Match)
        .where(Match.status.in_([MatchStatus.UPCOMING, MatchStatus.LOCKED]))
        .where(Match.start_time >= window_start)
        .where(Match.start_time <= window_end)
    )
    return list(result.scalars().all())


async def _users_without_team_for_match(
    db: AsyncSession, match_id: uuid.UUID
) -> list[User]:
    """Return verified, notification-opted-in users who have no team for this match."""
    # Find users who already have a team for this match
    teams_result = await db.execute(
        select(FantasyTeam.user_id).where(FantasyTeam.match_id == match_id)
    )
    users_with_team = {row[0] for row in teams_result.all()}

    # Find all eligible users
    users_result = await db.execute(
        select(User)
        .where(User.role != UserRole.ADMIN)
        .where(User.is_verified.is_(True))
        .where(User.notifications_enabled.is_(True))
    )
    all_users = users_result.scalars().all()

    return [u for u in all_users if u.id not in users_with_team]


async def _already_notified(
    db: AsyncSession, match_id: uuid.UUID, user_id: uuid.UUID, reminder_type: str
) -> bool:
    """Check if we've already sent this reminder to this user for this match."""
    result = await db.execute(
        select(MatchReminderSent).where(
            MatchReminderSent.match_id == match_id,
            MatchReminderSent.user_id == user_id,
            MatchReminderSent.reminder_type == reminder_type,
        )
    )
    return result.scalars().first() is not None


async def _record_reminder_sent(
    db: AsyncSession, match_id: uuid.UUID, user_id: uuid.UUID, reminder_type: str
) -> None:
    """Record that a reminder was sent."""
    db.add(
        MatchReminderSent(
            id=uuid.uuid4(),
            match_id=match_id,
            user_id=user_id,
            reminder_type=reminder_type,
        )
    )


async def send_pending_match_reminders(db: AsyncSession) -> dict:
    """Main entry point: find matches in reminder windows and send emails.

    Returns a dict with counts of what was processed.
    """
    now = datetime.utcnow()  # noqa: DTZ003
    stats = {"windows_checked": 0, "matches_found": 0, "emails_sent": 0, "skipped": 0}

    for reminder_type, min_min, max_min in REMINDER_WINDOWS:
        stats["windows_checked"] += 1
        matches = await _find_matches_in_window(db, now, min_min, max_min)

        for match in matches:
            stats["matches_found"] += 1
            users = await _users_without_team_for_match(db, match.id)
            minutes_to_start = int((match.start_time - now).total_seconds() / 60)

            logger.info(
                "Match %s vs %s starts in ~%d min, %d users without a team",
                match.team_a, match.team_b, minutes_to_start, len(users),
            )

            for user in users:
                if await _already_notified(db, match.id, user.id, reminder_type):
                    stats["skipped"] += 1
                    continue

                success = send_match_reminder_email(
                    to_email=user.email,
                    username=user.username,
                    team_a=match.team_a,
                    team_b=match.team_b,
                    start_time_ist=_format_ist(match.start_time),
                    minutes_to_start=minutes_to_start,
                    match_id=str(match.id),
                )

                if success:
                    await _record_reminder_sent(db, match.id, user.id, reminder_type)
                    stats["emails_sent"] += 1

        await db.commit()

    return stats
