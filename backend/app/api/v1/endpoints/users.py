from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_db, get_current_user
from app.core.security import verify_password, hash_password
from app.models.user import User
from app.schemas.user import UpdateProfileRequest, ChangePasswordRequest
from app.utils.response import success


router = APIRouter()


def _display_name(user: User) -> str:
    return user.nickname or user.username


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
