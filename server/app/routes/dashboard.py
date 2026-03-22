"""User dashboard API routes."""

import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from server.app.core.database import get_db
from server.app.core.deps import get_current_user
from server.app.models.user import User
from server.app.schemas.dashboard import DashboardMatchDetail, DashboardResponse
from server.app.services import dashboard_service

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("", response_model=DashboardResponse)
async def get_dashboard(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Return the authenticated user's dashboard with match history, rank, and upcoming statuses."""
    return await dashboard_service.get_dashboard(db, current_user.id)


@router.get("/match/{match_id}", response_model=DashboardMatchDetail)
async def get_dashboard_match_detail(
    match_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Return the user's fantasy team composition with per-player performance points for a match."""
    result = await dashboard_service.get_dashboard_match_detail(
        db, current_user.id, match_id
    )
    if result is None:
        raise HTTPException(
            status_code=404,
            detail={
                "error": {
                    "code": "NOT_FOUND",
                    "message": "No fantasy team found for this match",
                    "details": [],
                }
            },
        )
    return result
