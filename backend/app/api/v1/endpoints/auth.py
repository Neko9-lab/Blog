from fastapi import APIRouter, Depends, HTTPException, status
from redis import Redis
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from loguru import logger
import random

from app.core.deps import get_db, get_redis, ensure_user_not_banned
from app.core.rate_limit import RateLimiter
from app.core.security import create_access_token, create_refresh_token, verify_password, hash_password, decode_token
from app.models.user import User
from app.schemas.auth import LoginRequest, RegisterRequest, ResetPasswordRequest
from app.utils.response import success


router = APIRouter()


def _code_key(account: str) -> str:
    return f"verify:{account}"


@router.post("/send-code")
async def send_code(account: str, redis: Redis = Depends(get_redis)):
    code = f"{random.randint(100000, 999999)}"
    redis.setex(_code_key(account), 300, code)
    # 中文注释：开发环境直接输出验证码，生产环境应接入短信/邮箱服务
    logger.info("Verify code for {}: {}", account, code)
    return success({"message": "code sent"})


@router.post("/login")
async def login(payload: LoginRequest, db: AsyncSession = Depends(get_db), redis: Redis = Depends(get_redis)):
    limiter = RateLimiter(redis)
    if limiter.is_locked(payload.account):
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="Too many attempts")

    result = await db.execute(
        select(User).where(
            or_(User.email == payload.account, User.phone == payload.account, User.username == payload.account)
        )
    )
    user = result.scalar_one_or_none()
    if not user or not verify_password(payload.password, user.hashed_password):
        limiter.record_failure(payload.account)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    await ensure_user_not_banned(db, user)

    limiter.clear(payload.account)
    access_token = create_access_token(str(user.id), {"is_admin": user.is_admin})
    refresh_token = create_refresh_token(str(user.id))
    return success({"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"})


@router.post("/refresh")
async def refresh_token(refresh_token: str):
    # 中文注释：JWT 刷新逻辑
    # 参考文档：https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/
    payload = decode_token(refresh_token)
    if payload.get("type") != "refresh":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    access_token = create_access_token(payload["sub"], {"is_admin": payload.get("is_admin", False)})
    return success({"access_token": access_token, "token_type": "bearer"})


@router.post("/register")
async def register(payload: RegisterRequest, db: AsyncSession = Depends(get_db), redis: Redis = Depends(get_redis)):
    account = payload.email or payload.phone
    if not account:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email or phone required")

    code = redis.get(_code_key(account))
    if not code or code != payload.code:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid code")

    conflict_fields = [User.username == payload.username]
    if payload.email:
        conflict_fields.append(User.email == payload.email)
    if payload.phone:
        conflict_fields.append(User.phone == payload.phone)

    result = await db.execute(select(User).where(or_(*conflict_fields)))
    existing_users = result.scalars().all()
    if existing_users:
        for existing_user in existing_users:
            if existing_user.username == payload.username:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already exists")
            if payload.email and existing_user.email == payload.email:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already exists")
            if payload.phone and existing_user.phone == payload.phone:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Phone already exists")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User already exists")

    user = User(
        username=payload.username,
        email=payload.email,
        phone=payload.phone,
        hashed_password=hash_password(payload.password),
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return success({"id": user.id})


@router.post("/reset-password")
async def reset_password(payload: ResetPasswordRequest, db: AsyncSession = Depends(get_db), redis: Redis = Depends(get_redis)):
    code = redis.get(_code_key(payload.account))
    if not code or code != payload.code:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid code")

    result = await db.execute(
        select(User).where(or_(User.email == payload.account, User.phone == payload.account, User.username == payload.account))
    )
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    user.hashed_password = hash_password(payload.new_password)
    await db.commit()
    return success({"message": "password updated"})
