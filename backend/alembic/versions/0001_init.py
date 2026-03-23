"""Auto-generated Alembic template."""

from alembic import op
import sqlalchemy as sa

revision = "0001_init"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("email", sa.String(length=255), nullable=True),
        sa.Column("phone", sa.String(length=32), nullable=True),
        sa.Column("username", sa.String(length=64), nullable=False),
        sa.Column("hashed_password", sa.String(length=255), nullable=False),
        sa.Column("is_admin", sa.Boolean(), nullable=True),
        sa.Column("is_banned", sa.Boolean(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_users_id", "users", ["id"], unique=False)
    op.create_index("ix_users_email", "users", ["email"], unique=True)
    op.create_index("ix_users_phone", "users", ["phone"], unique=True)
    op.create_index("ix_users_username", "users", ["username"], unique=True)

    op.create_table(
        "categories",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=64), nullable=False),
    )
    op.create_index("ix_categories_id", "categories", ["id"], unique=False)

    op.create_table(
        "posts",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("author_id", sa.Integer(), nullable=False),
        sa.Column("category_id", sa.Integer(), nullable=True),
        sa.Column("is_pinned", sa.Boolean(), nullable=True),
        sa.Column("is_featured", sa.Boolean(), nullable=True),
        sa.Column("like_count", sa.Integer(), nullable=True),
        sa.Column("favorite_count", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["author_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["category_id"], ["categories.id"]),
    )
    op.create_index("ix_posts_id", "posts", ["id"], unique=False)
    op.create_index("ix_posts_author_id", "posts", ["author_id"], unique=False)
    op.create_index("ix_posts_category_id", "posts", ["category_id"], unique=False)
    op.create_index("ix_posts_title", "posts", ["title"], unique=False)

    op.create_table(
        "comments",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("post_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("parent_id", sa.Integer(), nullable=True),
        sa.Column("level", sa.Integer(), nullable=True),
        sa.Column("is_approved", sa.Boolean(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["post_id"], ["posts.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["parent_id"], ["comments.id"]),
    )
    op.create_index("ix_comments_id", "comments", ["id"], unique=False)
    op.create_index("ix_comments_post_id", "comments", ["post_id"], unique=False)
    op.create_index("ix_comments_user_id", "comments", ["user_id"], unique=False)

    op.create_table(
        "daily_stats",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("total_users", sa.Integer(), nullable=True),
        sa.Column("total_posts", sa.Integer(), nullable=True),
        sa.Column("new_users", sa.Integer(), nullable=True),
    )
    op.create_index("ix_daily_stats_id", "daily_stats", ["id"], unique=False)

    op.create_table(
        "site_config",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("site_name", sa.String(length=128), nullable=True),
        sa.Column("announcement", sa.String(length=512), nullable=True),
        sa.Column("comment_enabled", sa.Boolean(), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_site_config_id", "site_config", ["id"], unique=False)

    op.create_table(
        "post_likes",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("post_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(["post_id"], ["posts.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.UniqueConstraint("post_id", "user_id", name="uq_post_like"),
    )
    op.create_index("ix_post_likes_id", "post_likes", ["id"], unique=False)
    op.create_index("ix_post_likes_post_id", "post_likes", ["post_id"], unique=False)
    op.create_index("ix_post_likes_user_id", "post_likes", ["user_id"], unique=False)

    op.create_table(
        "post_favorites",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("post_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(["post_id"], ["posts.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.UniqueConstraint("post_id", "user_id", name="uq_post_favorite"),
    )
    op.create_index("ix_post_favorites_id", "post_favorites", ["id"], unique=False)
    op.create_index("ix_post_favorites_post_id", "post_favorites", ["post_id"], unique=False)
    op.create_index("ix_post_favorites_user_id", "post_favorites", ["user_id"], unique=False)


def downgrade() -> None:
    op.drop_table("post_favorites")
    op.drop_table("post_likes")
    op.drop_table("site_config")
    op.drop_table("daily_stats")
    op.drop_table("comments")
    op.drop_table("posts")
    op.drop_table("categories")
    op.drop_table("users")
