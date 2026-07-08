"""
算法可视化系统 - FastAPI 应用工厂

语言版本: Python 3.10+
Web 框架: FastAPI 0.104+
启动方式: python run.py 或 uvicorn src.algorithm_viz.app:app
"""

import os
import contextlib

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse

from .config import CORS_ORIGINS, STATIC_DIR
from .database import init_db
from .routers import (
    auth_router,
    ai_router,
    algorithms_router,
    compare_router,
    export_router,
    knowledge_router,
)


# ---------------------------------------------------------------------------
# 应用生命周期
# ---------------------------------------------------------------------------

@contextlib.asynccontextmanager
async def lifespan(app: FastAPI):
    """应用启动 / 关闭时的生命周期管理"""
    init_db()
    print("[OK] Database initialized")
    print("[OK] Algorithm Visualization System started!")
    yield


# ---------------------------------------------------------------------------
# 创建 FastAPI 应用实例
# ---------------------------------------------------------------------------

app = FastAPI(
    title="算法过程可视化系统",
    description=(
        "交互式算法学习平台，支持多种算法的过程可视化、"
        "分步执行和AI问答"
    ),
    version="1.0.0",
    lifespan=lifespan,
)

# ---------------------------------------------------------------------------
# CORS 中间件
# ---------------------------------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# 注册 API 路由
# ---------------------------------------------------------------------------

app.include_router(auth_router)
app.include_router(ai_router)
app.include_router(algorithms_router)
app.include_router(compare_router)
app.include_router(export_router)
app.include_router(knowledge_router)

# ---------------------------------------------------------------------------
# 静态文件挂载
# ---------------------------------------------------------------------------

if os.path.exists(STATIC_DIR):
    app.mount(
        "/css",
        StaticFiles(directory=os.path.join(STATIC_DIR, "css")),
        name="css",
    )
    app.mount(
        "/js",
        StaticFiles(directory=os.path.join(STATIC_DIR, "js")),
        name="js",
    )


# ---------------------------------------------------------------------------
# 健康检查
# ---------------------------------------------------------------------------

@app.get("/api/health")
def health_check():
    """健康检查端点"""
    from .algorithms import ALGORITHM_REGISTRY

    return {
        "status": "ok",
        "version": "1.0.0",
        "algorithms": len(ALGORITHM_REGISTRY),
    }


# ---------------------------------------------------------------------------
# 前端页面路由
# ---------------------------------------------------------------------------

@app.get("/")
@app.get("/index.html")
def serve_index():
    """提供前端首页"""
    index_path = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"error": "frontend not found"}


@app.get("/login.html")
def serve_login():
    """提供登录页面"""
    login_path = os.path.join(STATIC_DIR, "login.html")
    if os.path.exists(login_path):
        return FileResponse(login_path)
    return {"error": "frontend not found"}


# ---------------------------------------------------------------------------
# 全局异常处理
# ---------------------------------------------------------------------------

@app.exception_handler(404)
async def not_found_handler(request, exc):
    return JSONResponse(
        status_code=404,
        content={"error": "资源不存在", "detail": str(exc)},
    )
