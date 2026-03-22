"""Match service with CRUD operations and player pool auto-population."""

import uuid

from sqlalchemy import select, or_
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
        )
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
