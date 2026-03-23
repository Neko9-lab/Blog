import time
from redis import Redis

from app.core.config import settings


class RateLimiter:
    def __init__(self, redis: Redis):
        self.redis = redis

    def _key(self, account: str) -> str:
        return f"login:fail:{account}"

    def record_failure(self, account: str) -> None:
        key = self._key(account)
        pipe = self.redis.pipeline()
        pipe.incr(key, 1)
        pipe.expire(key, settings.rate_limit_window_seconds)
        pipe.execute()

    def is_locked(self, account: str) -> bool:
        key = self._key(account)
        count = self.redis.get(key)
        if count is None:
            return False
        if int(count) >= settings.rate_limit_max_attempts:
            # ??????????????????????
            # ?????https://redis.io/docs/latest/develop/data-types/strings/
            ttl = self.redis.ttl(key)
            if ttl < settings.rate_limit_lock_seconds:
                self.redis.expire(key, settings.rate_limit_lock_seconds)
            return True
        return False

    def clear(self, account: str) -> None:
        self.redis.delete(self._key(account))
