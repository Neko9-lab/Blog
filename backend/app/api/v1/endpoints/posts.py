from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy import select, func, case
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_db, get_current_user, get_current_admin
from app.models.comment import Comment
from app.models.post import Post, PostLike, PostFavorite
from app.models.user import User
from app.models.notification import Notification
from app.schemas.post import PostCreate, PostUpdate
from app.utils.response import success


router = APIRouter()


def _ensure_owner_or_admin(post: Post, user: User) -> None:
    if post.author_id != user.id and not user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No permission")


def _display_name(user: User) -> str:
    return user.nickname or user.username


def _serialize_post(post: Post, user: User, last_reply: dict | None = None) -> dict:
    return {
        "id": post.id,
        "title": post.title,
        "content": post.content,
        "category_id": post.category_id,
        "view_count": post.view_count,
        "like_count": post.like_count,
        "favorite_count": post.favorite_count,
        "comment_count": post.comment_count,
        "is_pinned": post.is_pinned,
        "is_featured": post.is_featured,
        "created_at": post.created_at.isoformat() if post.created_at else None,
        "last_activity_at": post.last_activity_at.isoformat() if post.last_activity_at else None,
        "last_reply_name": last_reply.get("name") if last_reply else None,
        "last_reply_avatar": last_reply.get("avatar") if last_reply else None,
        "author_id": post.author_id,
        "author_name": _display_name(user),
        "author_avatar": user.avatar_url,
    }


async def _get_last_reply_info(db: AsyncSession, post_ids: list[int]) -> dict[int, dict]:
    if not post_ids:
        return {}

    last_reply_info: dict[int, dict] = {}
    for post_id in post_ids:
        stmt = (
            select(Comment, User)
            .join(User, User.id == Comment.user_id)
            .where(Comment.post_id == post_id, Comment.is_approved == True)
            .order_by(Comment.created_at.desc(), Comment.id.desc())
            .limit(1)
        )
        result = await db.execute(stmt)
        row = result.first()
        if row:
            comment, user = row
            last_reply_info[comment.post_id] = {"name": _display_name(user), "avatar": user.avatar_url}
    return last_reply_info


@router.post("")
async def create_post(
    payload: PostCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    now = datetime.now(timezone.utc)
    post = Post(
        title=payload.title,
        content=payload.content,
        category_id=payload.category_id,
        author_id=current_user.id,
        view_count=0,
        comment_count=0,
        last_activity_at=now,
    )
    db.add(post)
    await db.commit()
    await db.refresh(post)
    return success({"id": post.id, "title": post.title, "category_id": post.category_id})


@router.put("/{post_id}")
async def update_post(
    post_id: int,
    payload: PostUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    post = await db.get(Post, post_id)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    _ensure_owner_or_admin(post, current_user)

    if payload.title is not None:
        post.title = payload.title
    if payload.content is not None:
        post.content = payload.content
    if payload.category_id is not None:
        post.category_id = payload.category_id
    post.last_activity_at = datetime.now(timezone.utc)

    await db.commit()
    return success({"id": post.id})


@router.delete("/{post_id}")
async def delete_post(
    post_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    post = await db.get(Post, post_id)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    _ensure_owner_or_admin(post, current_user)

    await db.delete(post)
    await db.commit()
    return success({"id": post_id})


@router.post("/{post_id}/pin")
async def pin_post(
    post_id: int,
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(get_current_admin),
):
    post = await db.get(Post, post_id)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    post.is_pinned = True
    await db.commit()
    return success({"id": post.id, "is_pinned": post.is_pinned})


@router.post("/{post_id}/feature")
async def feature_post(
    post_id: int,
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(get_current_admin),
):
    post = await db.get(Post, post_id)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    post.is_featured = True
    await db.commit()
    return success({"id": post.id, "is_featured": post.is_featured})


@router.post("/{post_id}/like")
async def like_post(
    post_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    post = await db.get(Post, post_id)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

    stmt = select(PostLike).where(PostLike.post_id == post_id, PostLike.user_id == current_user.id)
    result = await db.execute(stmt)
    if result.scalar_one_or_none():
        return success({"liked": True})

    db.add(PostLike(post_id=post_id, user_id=current_user.id))
    post.like_count = max(0, (post.like_count or 0) + 1)

    if post.author_id != current_user.id:
        db.add(
            Notification(
                user_id=post.author_id,
                actor_id=current_user.id,
                type="like",
                content=f"{_display_name(current_user)} 赞了你的帖子",
                source_id=post.id,
            )
        )

    await db.commit()
    return success({"liked": True})


@router.delete("/{post_id}/like")
async def unlike_post(
    post_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    stmt = select(PostLike).where(PostLike.post_id == post_id, PostLike.user_id == current_user.id)
    result = await db.execute(stmt)
    like = result.scalar_one_or_none()
    if like:
        post = await db.get(Post, post_id)
        if post:
            post.like_count = max(0, (post.like_count or 0) - 1)
        await db.delete(like)
        await db.commit()
    return success({"liked": False})


@router.post("/{post_id}/favorite")
async def favorite_post(
    post_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    post = await db.get(Post, post_id)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

    stmt = select(PostFavorite).where(PostFavorite.post_id == post_id, PostFavorite.user_id == current_user.id)
    result = await db.execute(stmt)
    if result.scalar_one_or_none():
        return success({"favorited": True})

    db.add(PostFavorite(post_id=post_id, user_id=current_user.id))
    post.favorite_count = max(0, (post.favorite_count or 0) + 1)
    await db.commit()
    return success({"favorited": True})


@router.delete("/{post_id}/favorite")
async def unfavorite_post(
    post_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    stmt = select(PostFavorite).where(PostFavorite.post_id == post_id, PostFavorite.user_id == current_user.id)
    result = await db.execute(stmt)
    fav = result.scalar_one_or_none()
    if fav:
        post = await db.get(Post, post_id)
        if post:
            post.favorite_count = max(0, (post.favorite_count or 0) - 1)
        await db.delete(fav)
        await db.commit()
    return success({"favorited": False})


@router.get("")
async def list_posts(
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=50),
    q: str | None = None,
    order: str = "new",
    category_id: int | None = Query(default=None),
    view: str = Query(default="all"),
):
    stmt = select(Post, User).join(User, User.id == Post.author_id)
    count_stmt = select(func.count()).select_from(Post)
    if q:
        stmt = stmt.where(Post.title.ilike(f"%{q}%"))
        count_stmt = count_stmt.where(Post.title.ilike(f"%{q}%"))
    if category_id is not None:
        stmt = stmt.where(Post.category_id == category_id)
        count_stmt = count_stmt.where(Post.category_id == category_id)
    if view == "featured":
        stmt = stmt.where(Post.is_featured == True)
        count_stmt = count_stmt.where(Post.is_featured == True)
    elif view == "unanswered":
        stmt = stmt.where(Post.comment_count == 0)
        count_stmt = count_stmt.where(Post.comment_count == 0)

    pinned_order = case((Post.is_pinned == True, 1), else_=0)  # noqa: E712
    featured_order = case((Post.is_featured == True, 1), else_=0)  # noqa: E712
    if order == "hot":
        stmt = stmt.order_by(
            pinned_order.desc(),
            featured_order.desc(),
            Post.view_count.desc(),
            Post.like_count.desc(),
            Post.comment_count.desc(),
            Post.favorite_count.desc(),
            Post.last_activity_at.desc(),
        )
    elif order == "active":
        stmt = stmt.order_by(pinned_order.desc(), featured_order.desc(), Post.last_activity_at.desc(), Post.id.desc())
    else:
        stmt = stmt.order_by(pinned_order.desc(), featured_order.desc(), Post.created_at.desc(), Post.id.desc())

    total = await db.execute(count_stmt)
    total_count = total.scalar_one()

    result = await db.execute(stmt.limit(size).offset((page - 1) * size))
    rows = result.all()
    last_reply_info = await _get_last_reply_info(db, [post.id for post, _ in rows])
    return success(
        {
            "items": [_serialize_post(p, u, last_reply_info.get(p.id)) for p, u in rows],
            "total": total_count,
            "page": page,
            "size": size,
        }
    )


@router.get("/{post_id}")
async def get_post(post_id: int, db: AsyncSession = Depends(get_db)):
    stmt = select(Post, User).join(User, User.id == Post.author_id).where(Post.id == post_id)
    result = await db.execute(stmt)
    row = result.first()
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    post, user = row
    post.view_count = max(0, (post.view_count or 0) + 1)
    if not post.last_activity_at:
        post.last_activity_at = post.created_at or datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(post)
    last_reply_info = await _get_last_reply_info(db, [post.id])
    return success(_serialize_post(post, user, last_reply_info.get(post.id)))
