"""Add notifications_enabled to users and match_reminders_sent table

Revision ID: a1b2c3d4e5f6
Revises: ebcc1313d22c
Create Date: 2026-04-22 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, None] = 'ebcc1313d22c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'users',
        sa.Column('notifications_enabled', sa.Boolean(), nullable=False, server_default=sa.true()),
    )
    op.create_table(
        'match_reminders_sent',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('match_id', sa.UUID(), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('reminder_type', sa.String(), nullable=False),
        sa.Column('sent_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['match_id'], ['matches.id']),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('match_id', 'user_id', 'reminder_type'),
    )
    op.create_index('ix_match_reminders_sent_match_id', 'match_reminders_sent', ['match_id'])


def downgrade() -> None:
    op.drop_index('ix_match_reminders_sent_match_id', table_name='match_reminders_sent')
    op.drop_table('match_reminders_sent')
    op.drop_column('users', 'notifications_enabled')
