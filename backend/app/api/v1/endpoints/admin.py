from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_db, get_current_admin
from app.models.post import Post
from app.models.category import Category
from app.models.user import User
from app.models.config import SiteConfig
from app.schemas.config import SiteConfigUpdate
from app.schemas.category import CategoryCreate, CategoryUpdate
from app.utils.response import success


router = APIRouter()


@router.get("/stats")
async def stats(
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(get_current_admin),
):
    # 待优化：接入 Redis 缓存 10 分钟
    total_users = await db.execute(select(func.count()).select_from(User))
    total_posts = await db.execute(select(func.count()).select_from(Post))
    return success(
        {
            "total_users": total_users.scalar_one(),
            "total_posts": total_posts.scalar_one(),
            "new_today": 0,
        }
    )


@router.get("/config")
async def get_config(
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(get_current_admin),
):
    result = await db.execute(select(SiteConfig))
    cfg = result.scalar_one_or_none()
    if not cfg:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Config not found")
    return success(
        {
            "site_name": cfg.site_name,
            "announcement": cfg.announcement,
            "comment_enabled": cfg.comment_enabled,
        }
    )


@router.put("/config")
async def update_config(
    payload: SiteConfigUpdate,
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(get_current_admin),
):
    result = await db.execute(select(SiteConfig))
    cfg = result.scalar_one_or_none()
    if not cfg:
        cfg = SiteConfig(site_name="BlogForum", announcement="", comment_enabled=True)
        db.add(cfg)

    if payload.site_name is not None:
        cfg.site_name = payload.site_name
    if payload.announcement is not None:
        cfg.announcement = payload.announcement
    if payload.comment_enabled is not None:
        cfg.comment_enabled = payload.comment_enabled

    await db.commit()
    return success({"message": "updated"})


@router.get("/logs")
async def get_logs(
    lines: int = 200,
    _admin: User = Depends(get_current_admin),
):
    log_path = Path("logs") / "app.log"
    if not log_path.exists():
        return success([])
    data = log_path.read_text(encoding="utf-8", errors="ignore").splitlines()
    return success(data[-lines:])


@router.get("/categories")
async def list_categories(
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(get_current_admin),
):
    result = await db.execute(select(Category).order_by(Category.id.asc()))
    items = result.scalars().all()
    return success([{"id": c.id, "name": c.name} for c in items])


@router.post("/categories")
async def create_category(
    payload: CategoryCreate,
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(get_current_admin),
):
    category = Category(name=payload.name)
    db.add(category)
    await db.commit()
    await db.refresh(category)
    return success({"id": category.id, "name": category.name})


@router.put("/categories/{category_id}")
async def update_category(
    category_id: int,
    payload: CategoryUpdate,
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(get_current_admin),
):
    category = await db.get(Category, category_id)
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    if payload.name is not None:
        category.name = payload.name
    await db.commit()
    return success({"id": category.id, "name": category.name})


@router.delete("/categories/{category_id}")
async def delete_category(
    category_id: int,
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(get_current_admin),
):
    category = await db.get(Category, category_id)
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    await db.delete(category)
    await db.commit()
    return success({"id": category_id})
