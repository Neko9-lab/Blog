from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.security import hash_password
from app.models.user import User
from app.models.category import Category
from app.models.config import SiteConfig


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
