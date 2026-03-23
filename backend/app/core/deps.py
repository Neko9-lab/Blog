import time
from datetime import datetime, timezone
from typing import AsyncGenerator

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from redis import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import decode_token
from app.db.session import async_session
from app.models.user import User


oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.api_prefix}/auth/login")


class _MemoryRedis:
    def __init__(self):
        self.store = {}
        self.expire_at = {}

    def _cleanup(self, key):
        exp = self.expire_at.get(key)
        if exp and time.time() > exp:
            self.store.pop(key, None)
            self.expire_at.pop(key, None)

    def get(self, key):
        self._cleanup(key)
        return self.store.get(key)

    def incr(self, key, amount=1):
        self._cleanup(key)
        val = int(self.store.get(key) or 0) + amount
        self.store[key] = str(val)
        return val

    def expire(self, key, ttl):
        self.expire_at[key] = time.time() + ttl
        return True

    def setex(self, key, ttl, value):
        self.store[key] = str(value)
        self.expire_at[key] = time.time() + ttl
        return True

    def ttl(self, key):
        self._cleanup(key)
        exp = self.expire_at.get(key)
        if not exp:
            return -1
        return int(exp - time.time())

    def delete(self, key):
        self.store.pop(key, None)
        self.expire_at.pop(key, None)
        return 1

    def pipeline(self):
        return self

    def execute(self):
        return None


_memory_redis = _MemoryRedis()


def _normalize_ban_time(value: datetime | None) -> datetime | None:
    if value is None:
        return None
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def _build_ban_detail(user: User) -> str:
    reason = user.ban_reason or "Banned by administrator"
    expires_at = _normalize_ban_time(user.ban_expires_at)
    if expires_at is None:
        return f"User banned permanently: {reason}"
    return f"User banned until {expires_at.strftime('%Y-%m-%d %H:%M UTC')}: {reason}"


async def ensure_user_not_banned(db: AsyncSession, user: User) -> User:
    if not user.is_banned:
        return user

    expires_at = _normalize_ban_time(user.ban_expires_at)
    if expires_at and expires_at <= datetime.now(timezone.utc):
        user.is_banned = False
        user.ban_reason = None
        user.ban_expires_at = None
        await db.commit()
        await db.refresh(user)
        return user

    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=_build_ban_detail(user))


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    session = async_session()
    try:
        yield session
    finally:
        await session.close()


def get_redis() -> Redis:
    if not settings.redis_url:
        # 待优化：开发环境无 Redis 时使用内存限流
        return _memory_redis  # type: ignore[return-value]
    return Redis.from_url(settings.redis_url, decode_responses=True)


async def get_current_user(
    db: AsyncSession = Depends(get_db),
    token: str = Depends(oauth2_scheme),
) -> User:
    try:
        payload = decode_token(token)
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token") from exc
    if payload.get("type") != "access":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    user_id = int(payload.get("sub", 0))
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid user")

    await ensure_user_not_banned(db, user)
    return user


async def get_current_admin(user: User = Depends(get_current_user)) -> User:
    if not user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin only")
    return user
