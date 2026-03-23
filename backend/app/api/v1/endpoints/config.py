from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_db
from app.models.config import SiteConfig
from app.utils.response import success


router = APIRouter()


@router.get("")
async def get_public_config(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(SiteConfig))
    cfg = result.scalar_one_or_none()
    if not cfg:
        return success({"site_name": "BlogForum", "announcement": "", "comment_enabled": True})
    return success(
        {
            "site_name": cfg.site_name,
            "announcement": cfg.announcement,
            "comment_enabled": cfg.comment_enabled,
        }
    )
