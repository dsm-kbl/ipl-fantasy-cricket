"""Dashboard service for user match history, rank, and team details."""

from datetime import datetime, timedelta
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from server.app.models.fantasy_team import FantasyTeam, FantasyTeamPlayer
from server.app.models.match import Match, MatchStatus
from server.app.models.performance_point import PerformancePoint
from server.app.models.user import User
from server.app.schemas.dashboard import (
    DashboardMatchDetail,
    DashboardResponse,
    MatchDetailPlayer,
    MatchParticipation,
    UpcomingMatchStatus,
)
from server.app.schemas.match import MatchOut
from server.app.services.leaderboard_service import get_overall_leaderboard
from server.app.services.match_service import auto_complete_past_matches


def _resolve_match_status(
    match: Match, has_team: bool, now: datetime
) -> str:
    """Determine the user's team status for an upcoming match."""
    lockout_time = match.start_time - timedelta(hours=1)
    if now >= lockout_time:
        return "locked"
    return "created" if has_team else "not created"


async def _find_user_rank(
    db: AsyncSession, user_id: UUID, leaderboard: list
) -> int | None:
    """Find the user's rank in the overall leaderboard by username."""
    result = await db.execute(select(User.username).where(User.id == user_id))
    row = result.first()
    if row is None:
        return None
    username = row[0]
    for entry in leaderboard:
        if entry.username == username:
            return entry.rank
    return None


async def get_dashboard(db: AsyncSession, user_id: UUID) -> DashboardResponse:
    """Build the full dashboard payload for a user.

    Includes:
    - participated matches with scores
    - overall leaderboard rank
    - upcoming match statuses (created / not_created / locked)
    """
    # --- Participated matches (user has a fantasy team) ---
    teams_result = await db.execute(
        select(FantasyTeam)
        .options(selectinload(FantasyTeam.match))
        .where(FantasyTeam.user_id == user_id)
    )
    teams = teams_result.scalars().all()

    participated: list[MatchParticipation] = []
    team_match_ids: set[UUID] = set()
    for team in teams:
        participated.append(
            MatchParticipation(
                match=MatchOut.model_validate(team.match),
                team_id=team.id,
                total_score=team.total_score,
            )
        )
        team_match_ids.add(team.match_id)

    participated.sort(key=lambda p: p.match.start_time, reverse=True)

    # --- Overall rank ---
    leaderboard = await get_overall_leaderboard(db)
    overall_rank = await _find_user_rank(db, user_id, leaderboard)

    # --- Auto-complete matches from past days ---
    await auto_complete_past_matches(db)

    # --- Upcoming matches with team status ---
    now = datetime.utcnow()  # noqa: DTZ003
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    upcoming_result = await db.execute(
        select(Match)
        .where(
            Match.status.in_([MatchStatus.UPCOMING, MatchStatus.LOCKED]),
            Match.start_time >= today_start,
        )
        .order_by(Match.start_time.asc())
    )
    upcoming: list[UpcomingMatchStatus] = [
        UpcomingMatchStatus(
            match=MatchOut.model_validate(m),
            status=_resolve_match_status(m, m.id in team_match_ids, now),
        )
        for m in upcoming_result.scalars().all()
    ]

    return DashboardResponse(
        participated_matches=participated,
        overall_rank=overall_rank,
        upcoming_matches=upcoming,
    )


async def get_dashboard_match_detail(
    db: AsyncSession, user_id: UUID, match_id: UUID
) -> DashboardMatchDetail | None:
    """Return the user's fantasy team composition with per-player performance points.

    Returns None if the user has no team for this match.
    """
    team_result = await db.execute(
        select(FantasyTeam)
        .options(
            selectinload(FantasyTeam.players).selectinload(FantasyTeamPlayer.player),
            selectinload(FantasyTeam.match),
        )
        .where(
            FantasyTeam.user_id == user_id,
            FantasyTeam.match_id == match_id,
        )
    )
    team = team_result.scalars().first()
    if team is None:
        return None

    # Load performance points for this match
    pp_result = await db.execute(
        select(PerformancePoint).where(PerformancePoint.match_id == match_id)
    )
    points_map = {pp.player_id: pp.points for pp in pp_result.scalars().all()}

    players = [
        MatchDetailPlayer(
            player_id=tp.player.id,
            player_name=tp.player.name,
            franchise=tp.player.franchise,
            role=tp.player.role.value if hasattr(tp.player.role, "value") else str(tp.player.role),
            cost=tp.player.cost,
            points=points_map.get(tp.player.id),
        )
        for tp in team.players
    ]

    return DashboardMatchDetail(
        match=MatchOut.model_validate(team.match),
        team_id=team.id,
        total_score=team.total_score,
        players=players,
    )
