"""Player service with CRUD operations for admin management."""

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from server.app.models.player import Player
from server.app.schemas.player import PlayerCreate, PlayerOut, PlayerUpdate


async def list_players(db: AsyncSession) -> list[PlayerOut]:
    """Return all players."""
    result = await db.execute(select(Player))
    players = result.scalars().all()
    return [PlayerOut.model_validate(p) for p in players]


async def get_player(db: AsyncSession, player_id: uuid.UUID) -> PlayerOut | None:
    """Return a single player by id, or None if not found."""
    result = await db.execute(select(Player).where(Player.id == player_id))
    player = result.scalars().first()
    if player is None:
        return None
    return PlayerOut.model_validate(player)


async def create_player(db: AsyncSession, data: PlayerCreate) -> PlayerOut:
    """Create a new player and return it."""
    player = Player(
        id=uuid.uuid4(),
        name=data.name,
        role=data.role,
        franchise=data.franchise,
        cost=data.cost,
    )
    db.add(player)
    await db.commit()
    await db.refresh(player)
    return PlayerOut.model_validate(player)


async def update_player(
    db: AsyncSession, player_id: uuid.UUID, data: PlayerUpdate
) -> PlayerOut | None:
    """Update an existing player with partial data. Returns None if not found."""
    result = await db.execute(select(Player).where(Player.id == player_id))
    player = result.scalars().first()
    if player is None:
        return None

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(player, field, value)

    await db.commit()
    await db.refresh(player)
    return PlayerOut.model_validate(player)
