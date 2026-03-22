"""Public API routes for the overall leaderboard."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from server.app.core.database import get_db
from server.app.schemas.leaderboard import LeaderboardEntry
from server.app.services import leaderboard_service

router = APIRouter(prefix="/api/leaderboard", tags=["leaderboard"])


@router.get("", response_model=list[LeaderboardEntry])
async def get_overall_leaderboard(
    db: AsyncSession = Depends(get_db),
):
    """Return the overall leaderboard ranked by cumulative points."""
    return await leaderboard_service.get_overall_leaderboard(db)
