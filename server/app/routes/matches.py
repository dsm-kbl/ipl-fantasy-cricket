"""Public API routes for match listing and player pool display."""

import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from server.app.core.database import get_db
from server.app.schemas.match import MatchOut, MatchWithPlayers
from server.app.schemas.leaderboard import LeaderboardEntry
from server.app.schemas.points import PlayerPointsOut
from server.app.services import leaderboard_service, match_service, points_service

router = APIRouter(prefix="/api/matches", tags=["matches"])


@router.get("", response_model=list[MatchOut])
async def list_upcoming_matches(
    db: AsyncSession = Depends(get_db),
):
    """Return all upcoming matches with team names, date, time, and venue."""
    return await match_service.get_upcoming_matches(db)


@router.get("/{match_id}", response_model=MatchWithPlayers)
async def get_match_detail(
    match_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    """Return match details with the full player pool (union of both franchise squads)."""
    result = await match_service.get_match_with_player_pool(db, match_id)
    if result is None:
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
    return result


@router.get("/{match_id}/leaderboard", response_model=list[LeaderboardEntry])
async def get_match_leaderboard(
    match_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    """Return the per-match leaderboard ranked by match score."""
    return await leaderboard_service.get_match_leaderboard(db, match_id)


@router.get("/{match_id}/points", response_model=list[PlayerPointsOut])
async def get_match_points(
    match_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    """Return per-player performance points summary for a completed match."""
    return await points_service.get_match_points(db, match_id)
