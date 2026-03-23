"""add post last activity

Revision ID: 0005_add_post_last_activity
Revises: 0004_add_post_forum_metrics
Create Date: 2026-03-23
"""

from alembic import op
import sqlalchemy as sa


revision = "0005_add_post_last_activity"
down_revision = "0004_add_post_forum_metrics"
branch_labels = None
depends_on = None


def _get_columns(bind, table_name: str) -> set[str]:
    inspector = sa.inspect(bind)
    return {column["name"] for column in inspector.get_columns(table_name)}


def upgrade() -> None:
    bind = op.get_bind()
    columns = _get_columns(bind, "posts")
    if "last_activity_at" not in columns:
        op.add_column(
            "posts",
            sa.Column("last_activity_at", sa.DateTime(timezone=True), nullable=True, server_default=sa.text("now()")),
        )


def downgrade() -> None:
    bind = op.get_bind()
    columns = _get_columns(bind, "posts")
    if "last_activity_at" in columns:
        op.drop_column("posts", "last_activity_at")
