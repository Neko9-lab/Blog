from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import inspect, select, text

from app.core.security import hash_password
from app.models.user import User
from app.models.category import Category
from app.models.config import SiteConfig


def ensure_schema(connection) -> None:
    inspector = inspect(connection)
    table_names = inspector.get_table_names()
    if "users" in table_names:
        user_columns = {column["name"] for column in inspector.get_columns("users")}
        if "ban_reason" not in user_columns:
            connection.execute(text("ALTER TABLE users ADD COLUMN ban_reason VARCHAR(255)"))
        if "ban_expires_at" not in user_columns:
            ban_expires_type = "TIMESTAMP WITH TIME ZONE" if connection.dialect.name == "postgresql" else "DATETIME"
            connection.execute(text(f"ALTER TABLE users ADD COLUMN ban_expires_at {ban_expires_type}"))

    if "posts" in table_names:
        post_columns = {column["name"] for column in inspector.get_columns("posts")}
        if "view_count" not in post_columns:
            connection.execute(text("ALTER TABLE posts ADD COLUMN view_count INTEGER DEFAULT 0"))
            connection.execute(text("UPDATE posts SET view_count = 0 WHERE view_count IS NULL"))
        if "comment_count" not in post_columns:
            connection.execute(text("ALTER TABLE posts ADD COLUMN comment_count INTEGER DEFAULT 0"))
            connection.execute(text("UPDATE posts SET comment_count = 0 WHERE comment_count IS NULL"))
        if "last_activity_at" not in post_columns:
            last_activity_type = "TIMESTAMP WITH TIME ZONE" if connection.dialect.name == "postgresql" else "DATETIME"
            connection.execute(text(f"ALTER TABLE posts ADD COLUMN last_activity_at {last_activity_type}"))
            connection.execute(text("UPDATE posts SET last_activity_at = COALESCE(updated_at, created_at) WHERE last_activity_at IS NULL"))


async def init_db(session: AsyncSession) -> None:
    # 初始化默认管理员与分类
    result = await session.execute(select(User).where(User.username == "admin"))
    admin = result.scalar_one_or_none()
    if not admin:
        admin = User(
            username="admin",
            email=None,
            phone=None,
            hashed_password=hash_password("admin123"),
            is_admin=True,
        )
        session.add(admin)

    result = await session.execute(select(Category).where(Category.name == "默认"))
    category = result.scalar_one_or_none()
    if not category:
        session.add(Category(name="默认"))

    result = await session.execute(select(SiteConfig))
    cfg = result.scalar_one_or_none()
    if not cfg:
        session.add(SiteConfig(site_name="BlogForum", announcement="", comment_enabled=True))

    await session.commit()
