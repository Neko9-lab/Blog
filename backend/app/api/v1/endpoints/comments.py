from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_db, get_current_user, get_current_admin
from app.models.comment import Comment
from app.models.user import User
from app.models.config import SiteConfig
from app.models.post import Post
from app.models.notification import Notification
from app.schemas.comment import CommentCreate, CommentUpdate
from app.utils.response import success


router = APIRouter()


def _ensure_owner_or_admin(comment: Comment, user: User) -> None:
    if comment.user_id != user.id and not user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No permission")


def _display_name(user: User) -> str:
    return user.nickname or user.username


@router.post("")
async def create_comment(
    payload: CommentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(SiteConfig))
    cfg = result.scalar_one_or_none()
    if cfg and not cfg.comment_enabled:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Comments disabled")

    level = 1
    parent = None
    if payload.parent_id:
        parent = await db.get(Comment, payload.parent_id)
        level = (parent.level + 1) if parent else 1
        if level > 3:
            # 待优化：支持更深层级的评论结构
            level = 3
    comment = Comment(
        post_id=payload.post_id,
        user_id=current_user.id,
        content=payload.content,
        parent_id=payload.parent_id,
        level=level,
        is_approved=True,
    )
    db.add(comment)

    post = await db.get(Post, payload.post_id)
    if post and post.author_id != current_user.id:
        db.add(
            Notification(
                user_id=post.author_id,
                actor_id=current_user.id,
                type="comment",
                content=f"{_display_name(current_user)} 评论了你的帖子",
                source_id=post.id,
            )
        )

    if parent and parent.user_id != current_user.id:
        db.add(
            Notification(
                user_id=parent.user_id,
                actor_id=current_user.id,
                type="reply",
                content=f"{_display_name(current_user)} 回复了你的评论",
                source_id=parent.id,
            )
        )

    await db.commit()
    await db.refresh(comment)
    return success(
        {
            "id": comment.id,
            "post_id": comment.post_id,
            "parent_id": comment.parent_id,
            "level": comment.level,
        }
    )


@router.put("/{comment_id}")
async def update_comment(
    comment_id: int,
    payload: CommentUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    comment = await db.get(Comment, comment_id)
    if not comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")
    _ensure_owner_or_admin(comment, current_user)
    comment.content = payload.content
    await db.commit()
    return success({"id": comment.id})


@router.delete("/{comment_id}")
async def delete_comment(
    comment_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    comment = await db.get(Comment, comment_id)
    if not comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")
    _ensure_owner_or_admin(comment, current_user)
    await db.delete(comment)
    await db.commit()
    return success({"id": comment_id})


@router.post("/{comment_id}/approve")
async def approve_comment(
    comment_id: int,
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(get_current_admin),
):
    comment = await db.get(Comment, comment_id)
    if not comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")
    comment.is_approved = True
    await db.commit()
    return success({"id": comment.id, "is_approved": comment.is_approved})


@router.post("/{comment_id}/reject")
async def reject_comment(
    comment_id: int,
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(get_current_admin),
):
    comment = await db.get(Comment, comment_id)
    if not comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")
    comment.is_approved = False
    await db.commit()
    return success({"id": comment.id, "is_approved": comment.is_approved})


@router.get("")
async def list_comments(post_id: int, db: AsyncSession = Depends(get_db)):
    stmt = (
        select(Comment, User.username, User.nickname, User.avatar_url)
        .join(User, User.id == Comment.user_id)
        .where(Comment.post_id == post_id, Comment.is_approved == True)  # noqa: E712
        .order_by(Comment.created_at.asc())
    )
    result = await db.execute(stmt)
    rows = result.all()
    return success(
        [
            {
                "id": c.id,
                "post_id": c.post_id,
                "content": c.content,
                "parent_id": c.parent_id,
                "level": c.level,
                "username": username,
                "nickname": nickname,
                "avatar_url": avatar_url,
                "display_name": nickname or username,
            }
            for c, username, nickname, avatar_url in rows
        ]
    )
