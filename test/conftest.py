"""
pytest 配置与共享 fixtures
"""

import os
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

# 确保项目根目录在 sys.path 中
PROJECT_ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = PROJECT_ROOT / "src"
sys.path.insert(0, str(SRC_DIR))


@pytest.fixture(scope="session", autouse=True)
def clean_database():
    """测试会话开始前清理旧的数据库文件"""
    db_path = PROJECT_ROOT / "algorithm_viz.db"
    if db_path.exists():
        db_path.unlink()


@pytest.fixture(scope="module")
def client():
    """FastAPI TestClient"""
    from algorithm_viz.app import app

    with TestClient(app) as c:
        yield c


@pytest.fixture
def auth_headers(client):
    """注册新用户并返回带 Authorization header 的字典"""
    import uuid

    username = f"testuser_{uuid.uuid4().hex[:8]}"
    password = "testpass123"

    resp = client.post("/api/auth/register", json={
        "username": username,
        "password": password,
    })
    assert resp.status_code == 200, f"Registration failed: {resp.text}"
    token = resp.json()["access_token"]

    return {"Authorization": f"Bearer {token}"}
