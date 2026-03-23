"""add user ban metadata

Revision ID: 0003_add_user_ban_metadata
Revises: 0002_add_profile_notifications
Create Date: 2026-03-23
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "0003_add_user_ban_metadata"
down_revision = "0002_add_profile_notifications"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("users", sa.Column("ban_reason", sa.String(length=255), nullable=True))
    op.add_column("users", sa.Column("ban_expires_at", sa.DateTime(timezone=True), nullable=True))


def downgrade() -> None:
    op.drop_column("users", "ban_expires_at")
    op.drop_column("users", "ban_reason")
