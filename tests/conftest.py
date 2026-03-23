import sys
import time
from pathlib import Path

import pytest_asyncio
from httpx import AsyncClient

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
sys.path.insert(0, str(BACKEND))

from main import app  # noqa: E402
from app.core.deps import get_db, get_redis  # noqa: E402
from app.core.security import hash_password  # noqa: E402


class _FakeUser:
    def __init__(self, user_id: int, username: str, password: str, is_admin: bool = False):
        self.id = user_id
        self.username = username
        self.email = f"{username}@example.com"
        self.phone = None
        self.is_admin = is_admin
        self.is_banned = False
        self.hashed_password = hash_password(password)


class _FakePost:
    def __init__(self, post_id: int, author_id: int):
        self.id = post_id
        self.title = "Test Post"
        self.content = "Hello"
        self.author_id = author_id
        self.category_id = 1
        self.like_count = 0
        self.favorite_count = 0
        self.is_pinned = False
        self.is_featured = False


class _FakeComment:
    def __init__(self, comment_id: int, post_id: int, user_id: int, username: str):
        self.id = comment_id
        self.post_id = post_id
        self.user_id = user_id
        self.content = "Nice"
        self.parent_id = None
        self.level = 1
        self.is_approved = True
        self.username = username


class _FakeConfig:
    def __init__(self):
        self.site_name = "BlogForum"
        self.announcement = ""
        self.comment_enabled = True


class _FakeResult:
    def __init__(self, obj):
        self._obj = obj

    def scalar_one_or_none(self):
        return self._obj

    def scalar_one(self):
        return self._obj

    def scalars(self):
        return _FakeScalars(self._obj if isinstance(self._obj, list) else [])

    def all(self):
        return self._obj if isinstance(self._obj, list) else []


class _FakeScalars:
    def __init__(self, items):
        self._items = items

    def all(self):
        return self._items


class _FakeSession:
    def __init__(self):
        self.users = [
            _FakeUser(1, "testuser", "PlainPassword123", is_admin=False),
            _FakeUser(2, "admin", "admin123", is_admin=True),
        ]
        self.posts = [_FakePost(1, 1)]
        self.comments = [_FakeComment(1, 1, 1, "testuser")]
        self.config = _FakeConfig()
        self._next_post_id = 2
        self._next_comment_id = 2

    async def get(self, model, obj_id):
        name = model.__name__
        if name == "User":
            for u in self.users:
                if u.id == obj_id:
                    return u
        if name == "Post":
            for p in self.posts:
                if p.id == obj_id:
                    return p
        if name == "Comment":
            for c in self.comments:
                if c.id == obj_id:
                    return c
        return None

    def add(self, obj):
        name = obj.__class__.__name__
        if name == "Post":
            obj.id = self._next_post_id
            self._next_post_id += 1
            self.posts.append(obj)
        elif name == "Comment":
            obj.id = self._next_comment_id
            self._next_comment_id += 1
            self.comments.append(obj)
        return None

    async def refresh(self, _obj):
        return None

    async def commit(self):
        return None

    def close(self):
        return None

    async def execute(self, stmt):
        s = str(stmt)
        if "FROM users" in s:
            return _FakeResult(self.users[0])
        if "count" in s and "posts" in s:
            return _FakeResult(len(self.posts))
        if "count" in s and "users" in s:
            return _FakeResult(len(self.users))
        if "FROM site_config" in s:
            return _FakeResult(self.config)
        if "FROM posts" in s:
            return _FakeResult(self.posts)
        if "FROM comments" in s and "JOIN users" in s:
            rows = [(c, c.username) for c in self.comments if c.is_approved]
            return _FakeResult(rows)
        if "FROM comments" in s:
            return _FakeResult(self.comments)
        return _FakeResult(None)


class _FakePipeline:
    def __init__(self, redis):
        self.redis = redis
        self.ops = []

    def incr(self, key, amount=1):
        self.ops.append(("incr", key, amount))
        return self

    def expire(self, key, ttl):
        self.ops.append(("expire", key, ttl))
        return self

    def execute(self):
        for op in self.ops:
            if op[0] == "incr":
                self.redis.incr(op[1], op[2])
            elif op[0] == "expire":
                self.redis.expire(op[1], op[2])
        self.ops = []


class _FakeRedis:
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
        return _FakePipeline(self)


fake_session = _FakeSession()


async def _override_db():
    yield fake_session


def _override_redis():
    return _FakeRedis()


@pytest_asyncio.fixture
async def client():
    app.dependency_overrides[get_db] = _override_db
    app.dependency_overrides[get_redis] = _override_redis
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def fake_db():
    return fake_session
