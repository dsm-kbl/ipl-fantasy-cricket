"""Shared test fixtures for IPL Fantasy Cricket backend tests."""

import os
import uuid
from datetime import datetime, timedelta

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from server.app.core.database import Base, get_db
from server.app.models import (
    FantasyTeam,
    FantasyTeamPlayer,
    Match,
    MatchStatus,
    PerformancePoint,
    Player,
    PlayerRole,
    User,
    UserRole,
)
from server.main import app

# Use in-memory SQLite for fast, isolated tests. Override with
# APP_TEST_DATABASE_URL env var to point at a real PostgreSQL instance.
TEST_DATABASE_URL = os.environ.get(
    "APP_TEST_DATABASE_URL", "sqlite+aiosqlite://"
)


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest.fixture()
async def async_engine():
    """Create a fresh async engine per test."""
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)

    # Enable SQLite foreign key support when using SQLite
    if TEST_DATABASE_URL.startswith("sqlite"):

        @event.listens_for(engine.sync_engine, "connect")
        def _set_sqlite_pragma(dbapi_conn, connection_record):
            cursor = dbapi_conn.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest.fixture()
async def db_session(async_engine) -> AsyncSession:
    """Provide an async DB session for tests, rolled back after each test."""
    session_factory = async_sessionmaker(
        async_engine, class_=AsyncSession, expire_on_commit=False
    )
    async with session_factory() as session:
        yield session


@pytest.fixture()
async def test_client(async_engine, db_session):
    """Provide an httpx AsyncClient wired to the FastAPI app with test DB."""

    async def _override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = _override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client

    app.dependency_overrides.clear()


# ---------------------------------------------------------------------------
# Helper factory fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def create_user(db_session: AsyncSession):
    """Factory fixture to create a regular User record in the test DB."""

    async def _create(
        username: str = "testuser",
        email: str = "test@example.com",
        password_hash: str = "hashed_pw",
        role: UserRole = UserRole.USER,
        is_verified: bool = False,
    ) -> User:
        user = User(
            id=uuid.uuid4(),
            username=username,
            email=email,
            password_hash=password_hash,
            role=role,
            is_verified=is_verified,
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)
        return user

    return _create


@pytest.fixture()
def create_admin_user(db_session: AsyncSession):
    """Factory fixture to create an Admin User record in the test DB."""

    async def _create(
        username: str = "adminuser",
        email: str = "admin@example.com",
        password_hash: str = "hashed_pw",
    ) -> User:
        user = User(
            id=uuid.uuid4(),
            username=username,
            email=email,
            password_hash=password_hash,
            role=UserRole.ADMIN,
            is_verified=True,
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)
        return user

    return _create


@pytest.fixture()
def create_player(db_session: AsyncSession):
    """Factory fixture to create a Player record in the test DB."""

    async def _create(
        name: str = "Virat Kohli",
        role: PlayerRole = PlayerRole.BATSMAN,
        franchise: str = "RCB",
        cost: float = 12.0,
        external_id: str | None = None,
    ) -> Player:
        player = Player(
            id=uuid.uuid4(),
            name=name,
            role=role,
            franchise=franchise,
            cost=cost,
            external_id=external_id,
        )
        db_session.add(player)
        await db_session.commit()
        await db_session.refresh(player)
        return player

    return _create


@pytest.fixture()
def create_match(db_session: AsyncSession):
    """Factory fixture to create a Match record in the test DB."""

    async def _create(
        team_a: str = "CSK",
        team_b: str = "MI",
        venue: str = "Wankhede Stadium",
        start_time: datetime | None = None,
        status: MatchStatus = MatchStatus.UPCOMING,
        external_id: str | None = None,
    ) -> Match:
        if start_time is None:
            start_time = datetime.utcnow() + timedelta(days=1)
        match = Match(
            id=uuid.uuid4(),
            team_a=team_a,
            team_b=team_b,
            venue=venue,
            start_time=start_time,
            status=status,
            external_id=external_id,
        )
        db_session.add(match)
        await db_session.commit()
        await db_session.refresh(match)
        return match

    return _create


@pytest.fixture()
def create_fantasy_team(db_session: AsyncSession):
    """Factory fixture to create a FantasyTeam with associated players."""

    async def _create(
        user: User,
        match: Match,
        players: list[Player] | None = None,
    ) -> FantasyTeam:
        team = FantasyTeam(
            id=uuid.uuid4(),
            user_id=user.id,
            match_id=match.id,
            total_score=0,
        )
        db_session.add(team)
        await db_session.flush()

        for player in players or []:
            link = FantasyTeamPlayer(
                id=uuid.uuid4(),
                fantasy_team_id=team.id,
                player_id=player.id,
            )
            db_session.add(link)

        await db_session.commit()
        await db_session.refresh(team)
        return team

    return _create


@pytest.fixture()
def create_performance_point(db_session: AsyncSession):
    """Factory fixture to create a PerformancePoint record."""

    async def _create(
        match: Match,
        player: Player,
        points: float = 10.0,
    ) -> PerformancePoint:
        pp = PerformancePoint(
            id=uuid.uuid4(),
            match_id=match.id,
            player_id=player.id,
            points=points,
        )
        db_session.add(pp)
        await db_session.commit()
        await db_session.refresh(pp)
        return pp

    return _create
