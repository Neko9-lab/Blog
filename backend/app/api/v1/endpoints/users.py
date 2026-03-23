from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_db, get_current_user
from app.core.security import verify_password, hash_password
from app.models.comment import Comment
from app.models.post import Post, PostFavorite
from app.models.user import User
from app.schemas.user import UpdateProfileRequest, ChangePasswordRequest
from app.utils.response import success


router = APIRouter()


def _display_name(user: User) -> str:
    return user.nickname or user.username


def _serialize_post(post: Post, author: User | None = None) -> dict:
    return {
        "id": post.id,
        "title": post.title,
        "content": post.content,
        "category_id": post.category_id,
        "view_count": post.view_count,
        "like_count": post.like_count,
        "favorite_count": post.favorite_count,
        "comment_count": post.comment_count,
        "created_at": post.created_at.isoformat() if post.created_at else None,
        "last_activity_at": post.last_activity_at.isoformat() if getattr(post, "last_activity_at", None) else None,
        "author_id": post.author_id,
        "author_name": _display_name(author) if author else None,
        "author_avatar": author.avatar_url if author else None,
    }


@router.get("/me")
async def me(current_user: User = Depends(get_current_user)):
    return success(
        {
            "id": current_user.id,
            "username": current_user.username,
            "nickname": current_user.nickname,
            "avatar_url": current_user.avatar_url,
            "display_name": _display_name(current_user),
            "email": current_user.email,
            "phone": current_user.phone,
            "is_admin": current_user.is_admin,
        }
    )


@router.get("/me/posts")
async def my_posts(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Post).where(Post.author_id == current_user.id).order_by(Post.created_at.desc(), Post.id.desc())
    )
    items = result.scalars().all()
    return success([_serialize_post(post, current_user) for post in items])


@router.get("/me/participated-posts")
async def my_participated_posts(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    stmt = (
        select(Post, User)
        .join(Comment, Comment.post_id == Post.id)
        .join(User, User.id == Post.author_id)
        .where(Comment.user_id == current_user.id)
        .order_by(Comment.created_at.desc())
    )
    result = await db.execute(stmt)
    rows = result.all()
    seen = set()
    items = []
    for post, author in rows:
        if post.id in seen:
            continue
        seen.add(post.id)
        items.append(_serialize_post(post, author))
    return success(items)


@router.get("/me/favorites")
async def my_favorites(
    post_id: int | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    stmt = (
        select(Post, User)
        .join(PostFavorite, PostFavorite.post_id == Post.id)
        .join(User, User.id == Post.author_id)
        .where(PostFavorite.user_id == current_user.id)
        .order_by(PostFavorite.created_at.desc())
    )
    if post_id is not None:
        stmt = stmt.where(Post.id == post_id)

    result = await db.execute(stmt)
    rows = result.all()
    return success([_serialize_post(post, author) for post, author in rows])


@router.put("/me")
async def update_profile(
    payload: UpdateProfileRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if payload.username:
        current_user.username = payload.username
    if payload.nickname is not None:
        current_user.nickname = payload.nickname
    if payload.avatar_url is not None:
        current_user.avatar_url = payload.avatar_url
    await db.commit()
    return success({"id": current_user.id})


@router.post("/change-password")
async def change_password(
    payload: ChangePasswordRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not verify_password(payload.old_password, current_user.hashed_password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Old password incorrect")
    current_user.hashed_password = hash_password(payload.new_password)
    await db.commit()
    return success({"id": current_user.id})
