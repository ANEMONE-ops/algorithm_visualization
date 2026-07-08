"""
认证模块单元测试
"""

import uuid

import pytest


def _unique_username(prefix: str = "user") -> str:
    return f"{prefix}_{uuid.uuid4().hex[:8]}"


class TestAuth:
    """测试用户注册 / 登录 API"""

    def test_register_success(self, client):
        username = _unique_username("newuser")
        resp = client.post("/api/auth/register", json={
            "username": username,
            "password": "password123",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert "access_token" in data
        assert data["username"] == username
        assert data["token_type"] == "bearer"

    def test_register_duplicate(self, client):
        """重复注册应返回 400"""
        username = _unique_username("dupuser")
        client.post("/api/auth/register", json={
            "username": username,
            "password": "password123",
        })
        resp = client.post("/api/auth/register", json={
            "username": username,
            "password": "password456",
        })
        assert resp.status_code == 400

    def test_register_short_username(self, client):
        resp = client.post("/api/auth/register", json={
            "username": "ab",
            "password": "password123",
        })
        assert resp.status_code == 422  # Pydantic validation error

    def test_login_success(self, client):
        username = _unique_username("loginuser")
        client.post("/api/auth/register", json={
            "username": username,
            "password": "correctpass",
        })
        resp = client.post("/api/auth/login", json={
            "username": username,
            "password": "correctpass",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert "access_token" in data

    def test_login_wrong_password(self, client):
        username = _unique_username("badpwuser")
        client.post("/api/auth/register", json={
            "username": username,
            "password": "rightpass",
        })
        resp = client.post("/api/auth/login", json={
            "username": username,
            "password": "wrongpass",
        })
        assert resp.status_code == 401

    def test_login_nonexistent_user(self, client):
        resp = client.post("/api/auth/login", json={
            "username": _unique_username("ghost"),
            "password": "whatever",
        })
        assert resp.status_code == 401

    def test_get_me_authorized(self, client, auth_headers):
        resp = client.get("/api/auth/me", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert "username" in data
        assert data["id"] > 0

    def test_get_me_unauthorized(self, client):
        resp = client.get("/api/auth/me")
        assert resp.status_code == 403  # Forbidden (no auth header)

    def test_login_nonexistent(self, client):
        resp = client.post("/api/auth/login", json={
            "username": _unique_username("noone"),
            "password": "nopass",
        })
        assert resp.status_code == 401
