"""Initial tables: users, players, matches, fantasy_teams, fantasy_team_players, performance_points

Revision ID: 0001
Revises:
Create Date: 2024-01-01 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Enum types
userrole_enum = postgresql.ENUM("USER", "ADMIN", name="userrole", create_type=False)
playerrole_enum = postgresql.ENUM(
    "BATSMAN", "BOWLER", "ALL_ROUNDER", "WICKET_KEEPER", name="playerrole", create_type=False
)
matchstatus_enum = postgresql.ENUM(
    "UPCOMING", "LOCKED", "IN_PROGRESS", "COMPLETED", name="matchstatus", create_type=False
)


def upgrade() -> None:
    # Create enum types
    userrole_enum.create(op.get_bind(), checkfirst=True)
    playerrole_enum.create(op.get_bind(), checkfirst=True)
    matchstatus_enum.create(op.get_bind(), checkfirst=True)

    # --- users ---
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("username", sa.String(), nullable=False),
        sa.Column("email", sa.String(), nullable=False),
        sa.Column("password_hash", sa.String(), nullable=False),
        sa.Column("role", userrole_enum, nullable=False, server_default="USER"),
        sa.Column("is_verified", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.UniqueConstraint("username"),
        sa.UniqueConstraint("email"),
    )

    # --- players ---
    op.create_table(
        "players",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("role", playerrole_enum, nullable=False),
        sa.Column("franchise", sa.String(), nullable=False),
        sa.Column("cost", sa.Float(), nullable=False),
        sa.Column("external_id", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.UniqueConstraint("external_id"),
    )

    # --- matches ---
    op.create_table(
        "matches",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("team_a", sa.String(), nullable=False),
        sa.Column("team_b", sa.String(), nullable=False),
        sa.Column("venue", sa.String(), nullable=False),
        sa.Column("start_time", sa.DateTime(), nullable=False),
        sa.Column("status", matchstatus_enum, nullable=False, server_default="UPCOMING"),
        sa.Column("external_id", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.UniqueConstraint("external_id"),
    )

    # --- fantasy_teams ---
    op.create_table(
        "fantasy_teams",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("match_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("matches.id"), nullable=False),
        sa.Column("total_score", sa.Float(), nullable=False, server_default=sa.text("0")),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.UniqueConstraint("user_id", "match_id"),
    )

    # --- fantasy_team_players ---
    op.create_table(
        "fantasy_team_players",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "fantasy_team_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("fantasy_teams.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("player_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("players.id"), nullable=False),
        sa.UniqueConstraint("fantasy_team_id", "player_id"),
    )

    # --- performance_points ---
    op.create_table(
        "performance_points",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("match_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("matches.id"), nullable=False),
        sa.Column("player_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("players.id"), nullable=False),
        sa.Column("points", sa.Float(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.UniqueConstraint("match_id", "player_id"),
    )


def downgrade() -> None:
    op.drop_table("performance_points")
    op.drop_table("fantasy_team_players")
    op.drop_table("fantasy_teams")
    op.drop_table("matches")
    op.drop_table("players")
    op.drop_table("users")

    # Drop enum types
    matchstatus_enum.drop(op.get_bind(), checkfirst=True)
    playerrole_enum.drop(op.get_bind(), checkfirst=True)
    userrole_enum.drop(op.get_bind(), checkfirst=True)