"""
算法可视化系统 - 配置文件
"""

import os

# ---------------------------------------------------------------------------
# 路径配置
# ---------------------------------------------------------------------------
# 项目根目录（algorithm_viz 包位于 src/ 下，向上两级即为项目根）
_PROJECT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..")
)
STATIC_DIR = os.path.join(_PROJECT_ROOT, "static")

# ---------------------------------------------------------------------------
# 数据库配置
# ---------------------------------------------------------------------------
DATABASE_URL = "sqlite:///./algorithm_viz.db"

# ---------------------------------------------------------------------------
# JWT 配置
# ---------------------------------------------------------------------------
SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "algo-viz-secret-key-2024")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

# ---------------------------------------------------------------------------
# 豆包大模型 (火山方舟) 配置
# ---------------------------------------------------------------------------
DOUBAO_API_KEY = os.environ.get(
    "your_own_key",
    "your_own_passord",
)
DOUBAO_ENDPOINT_ID = "your_own_id"
DOUBAO_API_URL = "your_own_url"
DOUBAO_MODEL = "your_own_model"

# ---------------------------------------------------------------------------
# 算法参数约束
# ---------------------------------------------------------------------------
MAX_ARRAY_SIZE = 50
MIN_ARRAY_SIZE = 3
MAX_ARRAY_VALUE = 100
MIN_ARRAY_VALUE = 1

MAX_GRAPH_VERTICES = 10
MIN_GRAPH_VERTICES = 3
MAX_EDGE_WEIGHT = 50
MIN_EDGE_WEIGHT = 1

MAX_HUFFMAN_CHARS = 26
MIN_HUFFMAN_CHARS = 3

MAX_HANOI_DISKS = 8
MIN_HANOI_DISKS = 2

MAX_COLORS = 6
MIN_COLORS = 2

# ---------------------------------------------------------------------------
# CORS 配置
# ---------------------------------------------------------------------------
CORS_ORIGINS = ["*"]
