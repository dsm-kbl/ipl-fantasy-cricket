"""Match service with CRUD operations and player pool auto-population."""

import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy import select, or_, update
from sqlalchemy.ext.asyncio import AsyncSession

from server.app.models.match import Match, MatchStatus
from server.app.models.player import Player
from server.app.schemas.match import MatchCreate, MatchOut, MatchUpdate, MatchWithPlayers
from server.app.schemas.player import PlayerOut


async def create_match(db: AsyncSession, data: MatchCreate) -> MatchOut:
    """Create a new match and return it."""
    match = Match(
        id=uuid.uuid4(),
        team_a=data.team_a,
        team_b=data.team_b,
        venue=data.venue,
        start_time=data.start_time,
        status=MatchStatus.UPCOMING,
    )
    db.add(match)
    await db.commit()
    await db.refresh(match)
    return MatchOut.model_validate(match)


async def update_match(
    db: AsyncSession, match_id: uuid.UUID, data: MatchUpdate
) -> MatchOut | None:
    """Update an existing match with partial data. Returns None if not found."""
    result = await db.execute(select(Match).where(Match.id == match_id))
    match = result.scalars().first()
    if match is None:
        return None

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(match, field, value)

    await db.commit()
    await db.refresh(match)
    return MatchOut.model_validate(match)


async def get_match_with_player_pool(
    db: AsyncSession, match_id: uuid.UUID
) -> MatchWithPlayers | None:
    """Return a match with all players from both franchises (the player pool).

    The player pool is derived at query time — players where
    franchise == match.team_a OR franchise == match.team_b.
    """
    result = await db.execute(select(Match).where(Match.id == match_id))
    match = result.scalars().first()
    if match is None:
        return None

    players_result = await db.execute(
        select(Player).where(
            or_(Player.franchise == match.team_a, Player.franchise == match.team_b)
        ).order_by(Player.franchise, Player.name)
    )
    players = players_result.scalars().all()

    return MatchWithPlayers(
        match=MatchOut.model_validate(match),
        players=[PlayerOut.model_validate(p) for p in players],
    )


async def get_upcoming_matches(db: AsyncSession) -> list[MatchOut]:
    """Return all matches with UPCOMING status."""
    result = await db.execute(
        select(Match).where(Match.status == MatchStatus.UPCOMING)
    )
    matches = result.scalars().all()
    return [MatchOut.model_validate(m) for m in matches]


async def get_all_matches(db: AsyncSession) -> list[MatchOut]:
    """Return all matches regardless of status, with completed matches last."""
    result = await db.execute(
        select(Match).order_by(
            (Match.status == MatchStatus.COMPLETED).asc(),
            Match.start_time.asc(),
        )
    )
    matches = result.scalars().all()
    return [MatchOut.model_validate(m) for m in matches]


async def auto_complete_past_matches(db: AsyncSession) -> int:
    """Mark non-completed matches as COMPLETED if their match day has passed.

    Returns the number of matches updated.
    """
    now = datetime.utcnow()  # noqa: DTZ003
    # Start of today (midnight UTC) — any match before this is from a past day
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)

    result = await db.execute(
        update(Match)
        .where(
            Match.status.in_([
                MatchStatus.UPCOMING,
                MatchStatus.LOCKED,
                MatchStatus.IN_PROGRESS,
            ]),
            Match.start_time < today_start,
        )
        .values(status=MatchStatus.COMPLETED)
    )
    await db.commit()
    return result.rowcount
