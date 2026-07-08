"""
算法可视化系统 - 算法模块注册表
"""

from .base import AlgorithmEngine, StepInfo, StepType
from .bubble_sort import BubbleSortEngine
from .quick_sort import QuickSortEngine
from .mst import MSTEngine
from .huffman import HuffmanEngine
from .hanoi import HanoiEngine
from .graph_coloring import GraphColoringEngine

__all__ = [
    "AlgorithmEngine",
    "StepInfo",
    "StepType",
    "BubbleSortEngine",
    "QuickSortEngine",
    "MSTEngine",
    "HuffmanEngine",
    "HanoiEngine",
    "GraphColoringEngine",
    "ALGORITHM_REGISTRY",
    "get_algorithm_info",
    "get_all_algorithms",
]

# ---------------------------------------------------------------------------
# 算法注册表
# ---------------------------------------------------------------------------

ALGORITHM_REGISTRY = {
    "bubble_sort": {
        "name": "冒泡排序",
        "category": "排序算法",
        "engine": BubbleSortEngine,
        "difficulty": "低-中",
        "time_complexity": "O(n²)",
        "space_complexity": "O(1)",
        "description": (
            "冒泡排序重复遍历数组，比较相邻元素并交换顺序错误的元素。"
            "每一轮遍历会将当前未排序部分的最大值'浮'到末尾。"
        ),
        "input_fields": [
            {
                "name": "array",
                "label": "数组数据",
                "type": "array",
                "placeholder": "如: 64,34,25,12,22,11,90",
            }
        ],
    },
    "quick_sort": {
        "name": "快速排序",
        "category": "排序算法",
        "engine": QuickSortEngine,
        "difficulty": "中",
        "time_complexity": "O(n log n)",
        "space_complexity": "O(log n)",
        "description": (
            "快速排序使用分治策略，选择一个基准元素，"
            "将数组分为小于和大于基准的两部分，递归排序。"
        ),
        "input_fields": [
            {
                "name": "array",
                "label": "数组数据",
                "type": "array",
                "placeholder": "如: 64,34,25,12,22,11,90",
            }
        ],
    },
    "mst": {
        "name": "最小生成树 (Prim算法)",
        "category": "图算法",
        "engine": MSTEngine,
        "difficulty": "中",
        "time_complexity": "O(V²) 或 O(E log V)",
        "space_complexity": "O(V)",
        "description": (
            "Prim算法从任意顶点开始，每次选择连接已访问顶点和"
            "未访问顶点的最小权重边，直到所有顶点都被包含。"
        ),
        "input_fields": [
            {"name": "vertices", "label": "顶点数", "type": "number", "min": 3, "max": 10},
            {"name": "edges", "label": "邻接矩阵(0表示无边)", "type": "matrix"},
        ],
    },
    "huffman": {
        "name": "哈夫曼树",
        "category": "树结构",
        "engine": HuffmanEngine,
        "difficulty": "中",
        "time_complexity": "O(n log n)",
        "space_complexity": "O(n)",
        "description": (
            "哈夫曼树是一种带权路径长度最短的二叉树。"
            "通过不断合并两个最小频率的节点来构建，用于数据压缩编码。"
        ),
        "input_fields": [
            {
                "name": "chars",
                "label": "字符",
                "type": "string",
                "placeholder": "如: A,B,C,D,E,F",
            },
            {
                "name": "freqs",
                "label": "频率",
                "type": "array",
                "placeholder": "如: 5,9,12,13,16,45",
            },
        ],
    },
    "hanoi": {
        "name": "汉诺塔",
        "category": "递归",
        "engine": HanoiEngine,
        "difficulty": "中-高",
        "time_complexity": "O(2ⁿ)",
        "space_complexity": "O(n)",
        "description": (
            "汉诺塔问题：将所有盘子从A柱移动到C柱，"
            "每次只能移动一个盘子，大盘不能放在小盘上面。经典递归问题。"
        ),
        "input_fields": [
            {"name": "disks", "label": "盘子数量", "type": "number", "min": 2, "max": 8}
        ],
    },
    "graph_coloring": {
        "name": "图着色 (回溯法)",
        "category": "回溯",
        "engine": GraphColoringEngine,
        "difficulty": "中-高",
        "time_complexity": "O(m^V)",
        "space_complexity": "O(V)",
        "description": (
            "图着色问题：用m种颜色给图的顶点着色，"
            "使得相邻顶点颜色不同。使用回溯法尝试所有可能的着色方案。"
        ),
        "input_fields": [
            {"name": "vertices", "label": "顶点数", "type": "number", "min": 3, "max": 10},
            {"name": "colors", "label": "颜色数", "type": "number", "min": 2, "max": 6},
            {"name": "edges", "label": "邻接矩阵(0/1)", "type": "matrix"},
        ],
    },
}


def get_algorithm_info(algo_id: str) -> dict:
    """获取单个算法的注册信息"""
    return ALGORITHM_REGISTRY.get(algo_id)


def get_all_algorithms() -> dict:
    """获取所有算法列表（不含 engine 对象，可直接 JSON 序列化）"""
    result = {}
    for key, value in ALGORITHM_REGISTRY.items():
        result[key] = {
            "name": value["name"],
            "category": value["category"],
            "difficulty": value["difficulty"],
            "time_complexity": value["time_complexity"],
            "space_complexity": value["space_complexity"],
            "description": value["description"],
            "input_fields": value["input_fields"],
        }
    return result
