import pytest

from app.core.security import create_access_token


def _auth_header(user_id: int, is_admin: bool = False) -> dict:
    token = create_access_token(str(user_id), {"is_admin": is_admin})
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_login_success(client):
    payload = {"account": "user@example.com", "password": "PlainPassword123"}
    resp = await client.post("/api/v1/auth/login", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["code"] == 200
    assert "access_token" in data["data"]


@pytest.mark.asyncio
async def test_login_fail(client):
    payload = {"account": "user@example.com", "password": "WrongPassword"}
    resp = await client.post("/api/v1/auth/login", json=payload)
    assert resp.status_code in (400, 401)
    data = resp.json()
    assert data["code"] != 200


@pytest.mark.asyncio
async def test_create_post_requires_auth(client):
    payload = {"title": "Test", "content": "Hello", "category_id": 1}
    resp = await client.post("/api/v1/posts", json=payload)
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_create_post_with_auth(client):
    payload = {"title": "Test", "content": "Hello", "category_id": 1}
    resp = await client.post("/api/v1/posts", json=payload, headers=_auth_header(1))
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_like_and_favorite(client):
    headers = _auth_header(1)
    resp = await client.post("/api/v1/posts/1/like", headers=headers)
    assert resp.status_code == 200
    resp = await client.post("/api/v1/posts/1/favorite", headers=headers)
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_comment_requires_auth(client):
    payload = {"post_id": 1, "content": "Nice"}
    resp = await client.post("/api/v1/comments", json=payload)
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_comment_with_auth(client):
    payload = {"post_id": 1, "content": "Nice"}
    resp = await client.post("/api/v1/comments", json=payload, headers=_auth_header(1))
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_comment_disabled(client, fake_db):
    fake_db.config.comment_enabled = False
    payload = {"post_id": 1, "content": "Blocked"}
    resp = await client.post("/api/v1/comments", json=payload, headers=_auth_header(1))
    assert resp.status_code == 403
    fake_db.config.comment_enabled = True


@pytest.mark.asyncio
async def test_admin_stats_requires_admin(client):
    resp = await client.get("/api/v1/admin/stats", headers=_auth_header(1))
    assert resp.status_code == 403
    resp = await client.get("/api/v1/admin/stats", headers=_auth_header(2, True))
    assert resp.status_code == 200
