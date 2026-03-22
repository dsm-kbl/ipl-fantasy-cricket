"""Admin API routes for player and match management."""

import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from server.app.core.database import get_db
from server.app.core.deps import get_admin_user
from server.app.models.user import User
from server.app.schemas.match import MatchCreate, MatchOut, MatchUpdate
from server.app.schemas.player import PlayerCreate, PlayerOut, PlayerUpdate
from server.app.schemas.points import PlayerPointsOut, PointsSubmission
from server.app.services import match_service, player_service, points_service

router = APIRouter(prefix="/api/admin", tags=["admin"])


@router.get("/players", response_model=list[PlayerOut])
async def list_players(
    _admin: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """List all players (admin only)."""
    return await player_service.list_players(db)


@router.post("/players", response_model=PlayerOut, status_code=201)
async def create_player(
    body: PlayerCreate,
    _admin: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new player (admin only)."""
    return await player_service.create_player(db, body)


@router.put("/players/{player_id}", response_model=PlayerOut)
async def update_player(
    player_id: uuid.UUID,
    body: PlayerUpdate,
    _admin: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """Update an existing player (admin only). Returns 404 if not found."""
    result = await player_service.update_player(db, player_id, body)
    if result is None:
        raise HTTPException(
            status_code=404,
            detail={
                "error": {
                    "code": "NOT_FOUND",
                    "message": "Player not found",
                    "details": [],
                }
            },
        )
    return result


@router.post("/matches", response_model=MatchOut, status_code=201)
async def create_match(
    body: MatchCreate,
    _admin: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new match (admin only).

    The player pool is automatically derived from players whose franchise
    matches either team_a or team_b — no separate storage needed.
    """
    return await match_service.create_match(db, body)


@router.put("/matches/{match_id}", response_model=MatchOut)
async def update_match(
    match_id: uuid.UUID,
    body: MatchUpdate,
    _admin: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """Update an existing match (admin only). Returns 404 if not found."""
    result = await match_service.update_match(db, match_id, body)
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


@router.post("/matches/{match_id}/points", response_model=list[PlayerPointsOut], status_code=201)
async def submit_match_points(
    match_id: uuid.UUID,
    body: PointsSubmission,
    _admin: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """Submit performance points for all players in a match (admin only).

    Points must be provided for every player in the match player pool.
    After saving, recalculates total_score for all fantasy teams in the match.
    """
    await points_service.submit_points(db, match_id, body.points)
    return await points_service.get_match_points(db, match_id)


@router.put("/matches/{match_id}/points", response_model=list[PlayerPointsOut], status_code=200)
async def update_match_points(
    match_id: uuid.UUID,
    body: PointsSubmission,
    _admin: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """Update performance points for all players in a match (admin only).

    Points must be provided for every player in the match player pool.
    After updating, recalculates total_score for all fantasy teams in the match.
    """
    await points_service.update_points(db, match_id, body.points)
    return await points_service.get_match_points(db, match_id)
