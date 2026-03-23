"""add post forum metrics

Revision ID: 0004_add_post_forum_metrics
Revises: 0003_add_user_ban_metadata
Create Date: 2026-03-23
"""

from alembic import op
import sqlalchemy as sa


revision = "0004_add_post_forum_metrics"
down_revision = "0003_add_user_ban_metadata"
branch_labels = None
depends_on = None


def _get_columns(bind, table_name: str) -> set[str]:
    inspector = sa.inspect(bind)
    return {column["name"] for column in inspector.get_columns(table_name)}


def upgrade() -> None:
    bind = op.get_bind()
    columns = _get_columns(bind, "posts")
    if "view_count" not in columns:
        op.add_column("posts", sa.Column("view_count", sa.Integer(), nullable=True, server_default="0"))
    if "comment_count" not in columns:
        op.add_column("posts", sa.Column("comment_count", sa.Integer(), nullable=True, server_default="0"))


def downgrade() -> None:
    bind = op.get_bind()
    columns = _get_columns(bind, "posts")
    if "comment_count" in columns:
        op.drop_column("posts", "comment_count")
    if "view_count" in columns:
        op.drop_column("posts", "view_count")
