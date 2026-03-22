"""Fantasy team service with validation, lockout, and CRUD operations."""

import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional

from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from server.app.models.fantasy_team import FantasyTeam, FantasyTeamPlayer
from server.app.models.match import Match
from server.app.models.player import Player, PlayerRole
from server.app.schemas.fantasy_team import FantasyTeamOut, ValidationResult
from server.app.schemas.player import PlayerOut


BUDGET_LIMIT = 100.0
TEAM_SIZE = 11
MAX_OVERSEAS = 4
ROLE_MINIMUMS = {
    PlayerRole.WICKET_KEEPER: 1,
    PlayerRole.BATSMAN: 4,
    PlayerRole.BOWLER: 3,
    PlayerRole.ALL_ROUNDER: 1,
}


class TeamLockedError(Exception):
    """Raised when a fantasy team modification is attempted after lockout."""
    pass


class BudgetExceededError(Exception):
    """Raised when the selected players exceed the budget limit."""
    pass


class TeamValidationError(Exception):
    """Raised when team validation fails."""

    def __init__(self, errors: list[str]):
        self.errors = errors
        super().__init__("; ".join(errors))


async def validate_team(
    db: AsyncSession,
    player_ids: list[uuid.UUID],
    match_id: uuid.UUID,
) -> ValidationResult:
    """Validate a fantasy team against all constraints.

    Checks:
    - Exactly 11 players
    - No duplicate players
    - All players belong to the match player pool
    - Total cost <= 100 credits
    - Role minimums: 1 WK, 3 BAT, 3 BOWL, 1 AR
    """
    errors: list[str] = []

    # Check duplicates
    unique_ids = set(player_ids)
    if len(unique_ids) != len(player_ids):
        errors.append("Duplicate players are not allowed")

    # Check team size
    if len(player_ids) != TEAM_SIZE:
        errors.append(f"Team must have exactly {TEAM_SIZE} players, got {len(player_ids)}")

    # Fetch match to determine franchises
    match_result = await db.execute(select(Match).where(Match.id == match_id))
    match = match_result.scalars().first()
    if match is None:
        errors.append("Match not found")
        return ValidationResult(valid=False, errors=errors)

    # Fetch all players in the match pool
    pool_result = await db.execute(
        select(Player).where(
            or_(Player.franchise == match.team_a, Player.franchise == match.team_b)
        )
    )
    pool_players = {p.id: p for p in pool_result.scalars().all()}

    # Check all selected players belong to the pool
    invalid_players = unique_ids - set(pool_players.keys())
    if invalid_players:
        errors.append(
            f"{len(invalid_players)} player(s) do not belong to the match player pool"
        )

    # Only check cost and roles if all players are valid pool members
    valid_selected = [pool_players[pid] for pid in unique_ids if pid in pool_players]

    # Check total cost
    total_cost = sum(p.cost for p in valid_selected)
    if total_cost > BUDGET_LIMIT:
        errors.append(
            f"Total cost {total_cost} exceeds budget limit of {BUDGET_LIMIT} credits"
        )

    # Check role minimums
    role_counts: dict[PlayerRole, int] = {}
    for p in valid_selected:
        role_counts[p.role] = role_counts.get(p.role, 0) + 1

    for role, minimum in ROLE_MINIMUMS.items():
        count = role_counts.get(role, 0)
        if count < minimum:
            errors.append(
                f"Minimum {minimum} {role.value} required, got {count}"
            )

    # Check overseas player limit (max 4)
    overseas_count = sum(
        1 for p in valid_selected
        if p.nationality and p.nationality != "India"
    )
    if overseas_count > MAX_OVERSEAS:
        errors.append(
            f"Maximum {MAX_OVERSEAS} overseas players allowed, got {overseas_count}"
        )

    return ValidationResult(valid=len(errors) == 0, errors=errors)


def check_lockout(match: Match) -> None:
    """Raise TeamLockedError if the match is past lockout time.

    lockout_time = match.start_time - 1 hour
    """
    lockout_time = match.start_time - timedelta(hours=1)
    if datetime.now(timezone.utc).replace(tzinfo=None) >= lockout_time:
        raise TeamLockedError(
            "Team modifications are locked starting 1 hour before match start"
        )


def _build_team_response(team: FantasyTeam) -> FantasyTeamOut:
    """Build a FantasyTeamOut response with remaining budget."""
    players = [PlayerOut.model_validate(tp.player) for tp in team.players]
    total_cost = sum(tp.player.cost for tp in team.players)
    return FantasyTeamOut(
        id=team.id,
        user_id=team.user_id,
        match_id=team.match_id,
        total_score=team.total_score,
        players=players,
        remaining_budget=BUDGET_LIMIT - total_cost,
        toss_prediction=team.toss_prediction,
        motm_prediction=team.motm_prediction,
    )


async def create_team(
    db: AsyncSession,
    user_id: uuid.UUID,
    match_id: uuid.UUID,
    player_ids: list[uuid.UUID],
    toss_prediction: str | None = None,
    motm_prediction: uuid.UUID | None = None,
) -> FantasyTeamOut:
    """Create a new fantasy team for a user and match.

    Validates team composition, checks lockout, and saves.
    """
    # Fetch match
    match_result = await db.execute(select(Match).where(Match.id == match_id))
    match = match_result.scalars().first()
    if match is None:
        raise TeamValidationError(["Match not found"])

    # Check lockout
    check_lockout(match)

    # Validate team
    validation = await validate_team(db, player_ids, match_id)
    if not validation.valid:
        raise TeamValidationError(validation.errors)

    # Check if user already has a team for this match
    existing_result = await db.execute(
        select(FantasyTeam).where(
            FantasyTeam.user_id == user_id,
            FantasyTeam.match_id == match_id,
        )
    )
    if existing_result.scalars().first() is not None:
        raise TeamValidationError(["You already have a team for this match"])

    # Create team
    team = FantasyTeam(
        id=uuid.uuid4(),
        user_id=user_id,
        match_id=match_id,
        total_score=0,
        toss_prediction=toss_prediction,
        motm_prediction=motm_prediction,
    )
    db.add(team)
    await db.flush()

    # Add players
    for pid in player_ids:
        db.add(FantasyTeamPlayer(
            id=uuid.uuid4(),
            fantasy_team_id=team.id,
            player_id=pid,
        ))
    await db.flush()

    # Reload with relationships
    result = await db.execute(
        select(FantasyTeam)
        .options(selectinload(FantasyTeam.players).selectinload(FantasyTeamPlayer.player))
        .where(FantasyTeam.id == team.id)
    )
    team = result.scalars().first()
    return _build_team_response(team)


async def update_team(
    db: AsyncSession,
    team_id: uuid.UUID,
    user_id: uuid.UUID,
    player_ids: list[uuid.UUID],
    toss_prediction: str | None = None,
    motm_prediction: uuid.UUID | None = None,
) -> FantasyTeamOut:
    """Update an existing fantasy team with a new set of players.

    Validates team composition, checks lockout, replaces players, and recalculates budget.
    """
    # Fetch team
    result = await db.execute(
        select(FantasyTeam)
        .options(selectinload(FantasyTeam.players).selectinload(FantasyTeamPlayer.player))
        .where(FantasyTeam.id == team_id)
    )
    team = result.scalars().first()
    if team is None:
        return None
    if team.user_id != user_id:
        return None

    # Fetch match for lockout check
    match_result = await db.execute(select(Match).where(Match.id == team.match_id))
    match = match_result.scalars().first()
    check_lockout(match)

    # Validate new team composition
    validation = await validate_team(db, player_ids, team.match_id)
    if not validation.valid:
        raise TeamValidationError(validation.errors)

    # Update predictions
    team.toss_prediction = toss_prediction
    team.motm_prediction = motm_prediction

    # Remove old players and add new ones
    for tp in team.players:
        await db.delete(tp)
    await db.flush()

    for pid in player_ids:
        db.add(FantasyTeamPlayer(
            id=uuid.uuid4(),
            fantasy_team_id=team.id,
            player_id=pid,
        ))
    await db.flush()

    # Reload with relationships
    result = await db.execute(
        select(FantasyTeam)
        .options(selectinload(FantasyTeam.players).selectinload(FantasyTeamPlayer.player))
        .where(FantasyTeam.id == team.id)
    )
    team = result.scalars().first()
    return _build_team_response(team)


async def delete_team(
    db: AsyncSession,
    team_id: uuid.UUID,
    user_id: uuid.UUID,
) -> bool:
    """Delete a fantasy team. Returns True if deleted, False if not found/not owned."""
    result = await db.execute(
        select(FantasyTeam).where(FantasyTeam.id == team_id)
    )
    team = result.scalars().first()
    if team is None or team.user_id != user_id:
        return False

    # Fetch match for lockout check
    match_result = await db.execute(select(Match).where(Match.id == team.match_id))
    match = match_result.scalars().first()
    check_lockout(match)

    await db.delete(team)
    await db.flush()
    return True


async def get_team_for_match(
    db: AsyncSession,
    user_id: uuid.UUID,
    match_id: uuid.UUID,
) -> Optional[FantasyTeamOut]:
    """Get the user's fantasy team for a specific match, or None."""
    result = await db.execute(
        select(FantasyTeam)
        .options(selectinload(FantasyTeam.players).selectinload(FantasyTeamPlayer.player))
        .where(
            FantasyTeam.user_id == user_id,
            FantasyTeam.match_id == match_id,
        )
    )
    team = result.scalars().first()
    if team is None:
        return None
    return _build_team_response(team)
