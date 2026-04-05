"""API routes for fantasy team CRUD operations."""

import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from server.app.core.database import get_db
from server.app.core.deps import get_current_user
from server.app.models.user import User, UserRole
from server.app.schemas.fantasy_team import FantasyTeamCreate, FantasyTeamOut, FantasyTeamUpdate
from server.app.services.fantasy_team_service import (
    BudgetExceededError,
    TeamLockedError,
    TeamValidationError,
    create_team,
    delete_team,
    get_team_for_match,
    update_team,
)

router = APIRouter(prefix="/api/fantasy-teams", tags=["fantasy-teams"])

_LOCKOUT_MSG = "Team modifications are locked starting 1 hour before match start"


def _raise_locked() -> None:
    raise HTTPException(
        status_code=403,
        detail={
            "error": {
                "code": "TEAM_LOCKED",
                "message": _LOCKOUT_MSG,
                "details": [],
            }
        },
    )


def _raise_validation(errors: list[str]) -> None:
    raise HTTPException(
        status_code=400,
        detail={
            "error": {
                "code": "TEAM_INVALID",
                "message": "Team validation failed",
                "details": [{"message": e} for e in errors],
            }
        },
    )


@router.post("", response_model=FantasyTeamOut, status_code=201)
async def create_fantasy_team(
    body: FantasyTeamCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a fantasy team for a match.

    Validates team composition, checks lockout, checks budget, and saves.
    Admins are not allowed to create fantasy teams.
    """
    if current_user.role == UserRole.ADMIN:
        raise HTTPException(
            status_code=403,
            detail={
                "error": {
                    "code": "FORBIDDEN",
                    "message": "Admin users cannot create fantasy teams",
                    "details": [],
                }
            },
        )
    try:
        return await create_team(db, current_user.id, body.match_id, body.player_ids, body.toss_prediction, body.motm_prediction)
    except TeamLockedError:
        _raise_locked()
    except TeamValidationError as exc:
        _raise_validation(exc.errors)
    except BudgetExceededError:
        raise HTTPException(
            status_code=400,
            detail={
                "error": {
                    "code": "BUDGET_EXCEEDED",
                    "message": "Total player cost exceeds the 100 credit budget",
                    "details": [],
                }
            },
        )


@router.get("/{match_id}", response_model=FantasyTeamOut)
async def get_fantasy_team(
    match_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get the current user's fantasy team for a specific match."""
    result = await get_team_for_match(db, current_user.id, match_id)
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


@router.put("/{team_id}", response_model=FantasyTeamOut)
async def update_fantasy_team(
    team_id: uuid.UUID,
    body: FantasyTeamUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update an existing fantasy team with a new set of players.

    Validates team composition, checks lockout, recalculates budget, and saves.
    """
    try:
        result = await update_team(db, team_id, current_user.id, body.player_ids, body.toss_prediction, body.motm_prediction)
    except TeamLockedError:
        _raise_locked()
    except TeamValidationError as exc:
        _raise_validation(exc.errors)
    except BudgetExceededError:
        raise HTTPException(
            status_code=400,
            detail={
                "error": {
                    "code": "BUDGET_EXCEEDED",
                    "message": "Total player cost exceeds the 100 credit budget",
                    "details": [],
                }
            },
        )

    if result is None:
        raise HTTPException(
            status_code=404,
            detail={
                "error": {
                    "code": "NOT_FOUND",
                    "message": "Fantasy team not found",
                    "details": [],
                }
            },
        )
    return result


@router.delete("/{team_id}", status_code=204)
async def delete_fantasy_team(
    team_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a fantasy team. Only allowed before lockout."""
    try:
        deleted = await delete_team(db, team_id, current_user.id)
    except TeamLockedError:
        _raise_locked()

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail={
                "error": {
                    "code": "NOT_FOUND",
                    "message": "Fantasy team not found",
                    "details": [],
                }
            },
        )
