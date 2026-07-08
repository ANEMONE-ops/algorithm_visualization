"""
算法可视化系统 - Algorithm Visualization System

交互式算法学习平台，支持多种算法的过程可视化、分步执行和AI问答。

语言版本: Python 3.10+
Web框架: FastAPI 0.104+
数据库: SQLite (via SQLAlchemy 2.0+)
"""

from .app import app

__all__ = ["app"]
__version__ = "1.0.0"
