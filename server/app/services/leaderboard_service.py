"""Leaderboard service for overall and per-match rankings."""

from uuid import UUID

from sqlalchemy import func, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from server.app.models.fantasy_team import FantasyTeam
from server.app.models.user import User, UserRole
from server.app.schemas.leaderboard import LeaderboardEntry


async def get_overall_leaderboard(db: AsyncSession) -> list[LeaderboardEntry]:
    """Return the overall leaderboard ranked by cumulative points descending.

    Tiebreaker: users with more matches participated rank higher.
    Admin users are excluded.
    """
    stmt = (
        select(
            User.username,
            func.coalesce(func.sum(FantasyTeam.total_score), 0).label("total_points"),
            func.count(FantasyTeam.id).label("matches_played"),
        )
        .join(FantasyTeam, FantasyTeam.user_id == User.id)
        .where(User.role != UserRole.ADMIN)
        .group_by(User.id, User.username)
        .order_by(
            desc("total_points"),
            desc("matches_played"),
        )
    )

    result = await db.execute(stmt)
    rows = result.all()

    return [
        LeaderboardEntry(
            rank=idx + 1,
            username=row.username,
            total_points=row.total_points,
            matches_played=row.matches_played,
        )
        for idx, row in enumerate(rows)
    ]


async def get_match_leaderboard(
    db: AsyncSession, match_id: UUID
) -> list[LeaderboardEntry]:
    """Return the per-match leaderboard ranked by match score descending.
    Admin users are excluded.
    """
    stmt = (
        select(
            User.username,
            FantasyTeam.total_score.label("total_points"),
        )
        .join(FantasyTeam, FantasyTeam.user_id == User.id)
        .where(FantasyTeam.match_id == match_id)
        .where(User.role != UserRole.ADMIN)
        .order_by(desc("total_points"))
    )

    result = await db.execute(stmt)
    rows = result.all()

    return [
        LeaderboardEntry(
            rank=idx + 1,
            username=row.username,
            total_points=row.total_points,
            matches_played=1,
        )
        for idx, row in enumerate(rows)
    ]
