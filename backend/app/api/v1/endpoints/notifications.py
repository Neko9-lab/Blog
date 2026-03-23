from fastapi import APIRouter, Depends
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_db, get_current_user
from app.models.notification import Notification
from app.models.user import User
from app.utils.response import success


router = APIRouter()


def _display_name(user: User) -> str:
    return user.nickname or user.username


@router.get("")
async def list_notifications(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    stmt = (
        select(Notification, User.username, User.nickname, User.avatar_url)
        .outerjoin(User, User.id == Notification.actor_id)
        .where(Notification.user_id == current_user.id)
        .order_by(Notification.created_at.desc())
    )
    result = await db.execute(stmt)
    rows = result.all()
    return success(
        [
            {
                "id": n.id,
                "type": n.type,
                "content": n.content,
                "source_id": n.source_id,
                "is_read": n.is_read,
                "created_at": n.created_at.isoformat() if n.created_at else None,
                "actor_name": (nickname or username) if username else None,
                "actor_avatar": avatar_url,
            }
            for n, username, nickname, avatar_url in rows
        ]
    )


@router.get("/unread-count")
async def unread_count(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    stmt = select(func.count()).select_from(Notification).where(
        Notification.user_id == current_user.id, Notification.is_read == False  # noqa: E712
    )
    result = await db.execute(stmt)
    count = result.scalar_one()
    return success({"count": count})


@router.post("/{notification_id}/read")
async def mark_read(
    notification_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    notif = await db.get(Notification, notification_id)
    if notif and notif.user_id == current_user.id:
        notif.is_read = True
        await db.commit()
    return success({"id": notification_id})


@router.post("/read-all")
async def mark_all_read(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    stmt = select(Notification).where(Notification.user_id == current_user.id, Notification.is_read == False)  # noqa: E712
    result = await db.execute(stmt)
    notifs = result.scalars().all()
    for n in notifs:
        n.is_read = True
    await db.commit()
    return success({"count": len(notifs)})
