"""Points service for submitting, updating, and recalculating performance points."""

import uuid

from fastapi import HTTPException
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from server.app.models.fantasy_team import FantasyTeam, FantasyTeamPlayer
from server.app.models.match import Match
from server.app.models.performance_point import PerformancePoint
from server.app.models.player import Player
from server.app.schemas.points import PlayerPoints


async def _get_match_or_404(db: AsyncSession, match_id: uuid.UUID) -> Match:
    """Fetch a match by ID or raise 404."""
    result = await db.execute(select(Match).where(Match.id == match_id))
    match = result.scalars().first()
    if match is None:
        raise HTTPException(
            status_code=404,
            detail={
                "error": {
                    "code": "NOT_FOUND",
                    "message": "Match not found",
                    "details": [],
                }
            },
        )
    return match


async def _get_player_pool_ids(db: AsyncSession, match: Match) -> set[uuid.UUID]:
    """Return the set of player IDs in the match's player pool."""
    result = await db.execute(
        select(Player.id).where(
            or_(Player.franchise == match.team_a, Player.franchise == match.team_b)
        )
    )
    return {row[0] for row in result.all()}


def _validate_completeness(
    points: list[PlayerPoints], pool_ids: set[uuid.UUID]
) -> None:
    """Raise 400 POINTS_INCOMPLETE if points don't cover every player in the pool."""
    submitted_ids = {p.player_id for p in points}
    missing = pool_ids - submitted_ids
    if missing:
        raise HTTPException(
            status_code=400,
            detail={
                "error": {
                    "code": "POINTS_INCOMPLETE",
                    "message": f"Points missing for {len(missing)} player(s) in the match player pool",
                    "details": [
                        {"field": "player_id", "message": str(pid)} for pid in missing
                    ],
                }
            },
        )


async def submit_points(
    db: AsyncSession, match_id: uuid.UUID, points: list[PlayerPoints]
) -> list[PerformancePoint]:
    """Submit performance points for a match.

    Validates that points cover every player in the match player pool,
    creates PerformancePoint records, and recalculates all fantasy team scores.
    """
    match = await _get_match_or_404(db, match_id)
    pool_ids = await _get_player_pool_ids(db, match)
    _validate_completeness(points, pool_ids)

    # Check no existing points for this match
    existing = await db.execute(
        select(PerformancePoint).where(PerformancePoint.match_id == match_id).limit(1)
    )
    if existing.scalars().first() is not None:
        raise HTTPException(
            status_code=409,
            detail={
                "error": {
                    "code": "CONFLICT",
                    "message": "Points already submitted for this match. Use PUT to update.",
                    "details": [],
                }
            },
        )

    records = []
    for pp in points:
        record = PerformancePoint(
            id=uuid.uuid4(),
            match_id=match_id,
            player_id=pp.player_id,
            points=pp.points,
        )
        db.add(record)
        records.append(record)

    await db.flush()
    await recalculate_team_scores(db, match_id)
    return records


async def update_points(
    db: AsyncSession, match_id: uuid.UUID, points: list[PlayerPoints]
) -> list[PerformancePoint]:
    """Update existing performance points for a match.

    Validates completeness, updates PerformancePoint records,
    and recalculates all fantasy team scores.
    """
    match = await _get_match_or_404(db, match_id)
    pool_ids = await _get_player_pool_ids(db, match)
    _validate_completeness(points, pool_ids)

    # Build a lookup of submitted points
    points_map = {pp.player_id: pp.points for pp in points}

    # Fetch existing records
    result = await db.execute(
        select(PerformancePoint).where(PerformancePoint.match_id == match_id)
    )
    existing_records = {r.player_id: r for r in result.scalars().all()}

    updated = []
    for player_id, pts in points_map.items():
        if player_id in existing_records:
            existing_records[player_id].points = pts
            updated.append(existing_records[player_id])
        else:
            record = PerformancePoint(
                id=uuid.uuid4(),
                match_id=match_id,
                player_id=player_id,
                points=pts,
            )
            db.add(record)
            updated.append(record)

    await db.flush()
    await recalculate_team_scores(db, match_id)
    return updated


async def recalculate_team_scores(db: AsyncSession, match_id: uuid.UUID) -> None:
    """Recalculate total_score for every fantasy team in the given match.

    For each team, sum the PerformancePoints of its 11 selected players,
    plus bonus points for correct toss and MOTM predictions.
    """
    TOSS_BONUS = 10.0
    MOTM_BONUS = 25.0

    # Load match to check toss_winner and motm
    match_result = await db.execute(select(Match).where(Match.id == match_id))
    match = match_result.scalars().first()

    # Load all performance points for this match into a lookup
    pp_result = await db.execute(
        select(PerformancePoint).where(PerformancePoint.match_id == match_id)
    )
    points_map = {r.player_id: r.points for r in pp_result.scalars().all()}

    # Load all fantasy teams for this match with their players
    teams_result = await db.execute(
        select(FantasyTeam)
        .where(FantasyTeam.match_id == match_id)
        .options(selectinload(FantasyTeam.players))
    )
    teams = teams_result.scalars().all()

    for team in teams:
        total = sum(
            points_map.get(tp.player_id, 0.0) for tp in team.players
        )

        # Prediction bonuses
        if match and match.toss_winner and team.toss_prediction:
            if team.toss_prediction.strip().lower() == match.toss_winner.strip().lower():
                total += TOSS_BONUS

        if match and match.motm_player_id and team.motm_prediction:
            if team.motm_prediction == match.motm_player_id:
                total += MOTM_BONUS

        team.total_score = total

    await db.flush()


async def get_match_points(
    db: AsyncSession, match_id: uuid.UUID
) -> list[dict]:
    """Return per-player points summary for a match.

    Returns a list of dicts with player_id, player_name, franchise, role, and points.
    """
    await _get_match_or_404(db, match_id)

    result = await db.execute(
        select(PerformancePoint, Player)
        .join(Player, PerformancePoint.player_id == Player.id)
        .where(PerformancePoint.match_id == match_id)
    )
    rows = result.all()

    return [
        {
            "player_id": pp.player_id,
            "player_name": player.name,
            "franchise": player.franchise,
            "role": player.role.value if hasattr(player.role, "value") else str(player.role),
            "points": pp.points,
        }
        for pp, player in rows
    ]
