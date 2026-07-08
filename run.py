"""
算法可视化系统 - 开发服务器入口

语言版本: Python 3.10+
启动方式: python run.py
"""

import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "src.algorithm_viz.app:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
    )
