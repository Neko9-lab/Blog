from datetime import datetime, timedelta, timezone
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_db, get_current_admin
from app.models.post import Post
from app.models.category import Category
from app.models.user import User
from app.models.config import SiteConfig
from app.schemas.config import SiteConfigUpdate
from app.schemas.category import CategoryCreate, CategoryUpdate
from app.schemas.user import BanUserRequest
from app.utils.response import success


router = APIRouter()


def _display_name(user: User) -> str:
    return user.nickname or user.username


def _serialize_ban_expires_at(value):
    return value.isoformat() if value else None


@router.get("/stats")
async def stats(
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(get_current_admin),
):
    total_users = await db.execute(select(func.count()).select_from(User))
    total_posts = await db.execute(select(func.count()).select_from(Post))
    return success(
        {
            "total_users": total_users.scalar_one(),
            "total_posts": total_posts.scalar_one(),
            "new_today": 0,
        }
    )


@router.get("/users")
async def list_users(
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(get_current_admin),
):
    result = await db.execute(select(User).order_by(User.id.desc()))
    users = result.scalars().all()
    return success(
        [
            {
                "id": user.id,
                "username": user.username,
                "nickname": user.nickname,
                "display_name": _display_name(user),
                "email": user.email,
                "phone": user.phone,
                "is_admin": user.is_admin,
                "is_banned": user.is_banned,
                "ban_reason": user.ban_reason,
                "ban_expires_at": _serialize_ban_expires_at(user.ban_expires_at),
                "created_at": user.created_at.isoformat() if user.created_at else None,
            }
            for user in users
        ]
    )


@router.post("/users/{user_id}/ban")
async def ban_user(
    user_id: int,
    payload: BanUserRequest,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if user.id == admin.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot ban yourself")

    user.is_banned = True
    user.ban_reason = payload.reason.strip()
    user.ban_expires_at = None if payload.permanent else datetime.now(timezone.utc) + timedelta(days=payload.duration_days or 0)
    await db.commit()
    await db.refresh(user)
    return success(
        {
            "id": user.id,
            "is_banned": user.is_banned,
            "ban_reason": user.ban_reason,
            "ban_expires_at": _serialize_ban_expires_at(user.ban_expires_at),
        }
    )


@router.post("/users/{user_id}/unban")
async def unban_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(get_current_admin),
):
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    user.is_banned = False
    user.ban_reason = None
    user.ban_expires_at = None
    await db.commit()
    return success({"id": user.id, "is_banned": user.is_banned})


@router.get("/posts")
async def list_posts(
    q: str | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(get_current_admin),
):
    stmt = select(Post, User, Category).join(User, User.id == Post.author_id).outerjoin(Category, Category.id == Post.category_id)
    if q:
        stmt = stmt.where(
            (Post.title.ilike(f"%{q}%"))
            | (User.username.ilike(f"%{q}%"))
            | (User.nickname.ilike(f"%{q}%"))
        )
    stmt = stmt.order_by(Post.created_at.desc(), Post.id.desc())
    result = await db.execute(stmt)
    rows = result.all()
    return success(
        [
            {
                "id": post.id,
                "title": post.title,
                "author_name": _display_name(author),
                "category_name": category.name if category else "未分类",
                "view_count": post.view_count,
                "comment_count": post.comment_count,
                "like_count": post.like_count,
                "favorite_count": post.favorite_count,
                "is_pinned": post.is_pinned,
                "is_featured": post.is_featured,
                "created_at": post.created_at.isoformat() if post.created_at else None,
            }
            for post, author, category in rows
        ]
    )


@router.post("/posts/{post_id}/pin")
async def toggle_pin_post(
    post_id: int,
    enabled: bool,
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(get_current_admin),
):
    post = await db.get(Post, post_id)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    post.is_pinned = enabled
    await db.commit()
    return success({"id": post.id, "is_pinned": post.is_pinned})


@router.post("/posts/{post_id}/feature")
async def toggle_feature_post(
    post_id: int,
    enabled: bool,
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(get_current_admin),
):
    post = await db.get(Post, post_id)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    post.is_featured = enabled
    await db.commit()
    return success({"id": post.id, "is_featured": post.is_featured})


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
