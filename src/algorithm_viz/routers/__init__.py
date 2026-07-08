"""
算法可视化系统 - API 路由模块
"""

from .auth import router as auth_router
from .ai_chat import router as ai_router
from .algorithms import router as algorithms_router
from .compare import router as compare_router
from .export_log import router as export_router
from .knowledge import router as knowledge_router

__all__ = [
    "auth_router",
    "ai_router",
    "algorithms_router",
    "compare_router",
    "export_router",
    "knowledge_router",
]
