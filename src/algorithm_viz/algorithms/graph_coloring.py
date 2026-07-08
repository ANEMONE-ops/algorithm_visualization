"""
算法可视化系统 - 图着色算法 (回溯法)
"""

import random
from typing import List

from .base import AlgorithmEngine, StepInfo, StepType
from ..config import (
    MAX_GRAPH_VERTICES,
    MIN_GRAPH_VERTICES,
    MAX_COLORS,
    MIN_COLORS,
)


class GraphColoringEngine(AlgorithmEngine):
    """图着色回溯算法引擎"""

    def generate_steps(self, data: dict) -> List[StepInfo]:
        self.steps = []
        self.original_data = data
        vertices = data["vertices"]
        m = data["colors"]
        matrix = data["edges"]

        # 构建邻接表
        adj = {i: [] for i in range(vertices)}
        for i in range(vertices):
            for j in range(vertices):
                if matrix[i][j] == 1 and i != j:
                    adj[i].append(j)

        self.add_step(
            StepType.INIT,
            f"🔰 开始图着色问题求解（回溯法）| 顶点数: {vertices} | "
            f"颜色数: {m}\n"
            f"颜色: {', '.join([self._color_name(c) for c in range(m)])}",
            data_snapshot={
                "vertices": vertices,
                "adjacency": {i: list(adj[i]) for i in range(vertices)},
                "coloring": [-1] * vertices,
                "colors": m,
            },
            variable_states={
                "current_vertex": 0, "assigned_count": 0, "backtrack_count": 0,
            },
        )

        coloring = [-1] * vertices
        self.backtrack_count = 0
        self.found_solutions = []

        self._backtrack(0, vertices, m, adj, coloring)

        if self.found_solutions:
            solution = self.found_solutions[0]
            color_names = [self._color_name(c) for c in solution]
            self.add_step(
                StepType.COMPLETE,
                f"✨ 图着色求解完成！找到 {len(self.found_solutions)} 个可行解\n"
                f"第一个解: {dict(enumerate(color_names))}\n"
                f"回溯次数: {self.backtrack_count}",
                data_snapshot={
                    "vertices": vertices,
                    "adjacency": {i: list(adj[i]) for i in range(vertices)},
                    "coloring": solution,
                    "colors": m,
                },
                variable_states={
                    "solution": solution,
                    "backtrack_count": self.backtrack_count,
                    "total_solutions": len(self.found_solutions),
                },
            )
        else:
            self.add_step(
                StepType.COMPLETE,
                f"❌ 用 {m} 种颜色无法完成着色 | "
                f"回溯次数: {self.backtrack_count}\n"
                f"建议增加颜色数或减少图的密度",
                data_snapshot={
                    "vertices": vertices,
                    "adjacency": {i: list(adj[i]) for i in range(vertices)},
                    "coloring": coloring,
                    "colors": m,
                },
                variable_states={
                    "no_solution": True,
                    "backtrack_count": self.backtrack_count,
                },
            )
        return self.steps

    # ------------------------------------------------------------------
    # 回溯核心
    # ------------------------------------------------------------------

    def _backtrack(self, v: int, vertices: int, m: int, adj: dict, coloring: List[int]):
        if v == vertices:
            self.found_solutions.append(list(coloring))
            self.add_step(
                StepType.INFO,
                f"🎯 找到一个可行解: "
                f"{dict(enumerate([self._color_name(c) for c in coloring]))}",
                data_snapshot={
                    "vertices": vertices,
                    "coloring": list(coloring),
                    "current_vertex": v,
                    "is_solution": True,
                },
                variable_states={
                    "current_vertex": v, "solution_found": True,
                    "backtrack_count": self.backtrack_count,
                },
            )
            return

        self.add_step(
            StepType.SELECT,
            f"📍 处理顶点 {v}，尝试分配颜色...",
            data_snapshot={
                "vertices": vertices,
                "coloring": list(coloring),
                "current_vertex": v,
            },
            highlights=[v],
            variable_states={
                "current_vertex": v, "backtrack_count": self.backtrack_count,
            },
        )

        for c in range(m):
            if self._is_safe(v, c, adj, coloring):
                coloring[v] = c
                color_name = self._color_name(c)
                self.add_step(
                    StepType.UPDATE,
                    f"🎨 为顶点 {v} 分配颜色 '{color_name}' ({c}) | "
                    f"邻居颜色约束检查通过 ✓",
                    data_snapshot={
                        "vertices": vertices,
                        "coloring": list(coloring),
                        "current_vertex": v,
                        "trying_color": c,
                    },
                    highlights=[v],
                    variable_states={
                        "current_vertex": v, "color": c,
                        "color_name": color_name,
                        "backtrack_count": self.backtrack_count,
                    },
                )

                self._backtrack(v + 1, vertices, m, adj, coloring)

                if len(self.found_solutions) >= 1:
                    return

                coloring[v] = -1
                self.backtrack_count += 1
                self.add_step(
                    StepType.BACKTRACK,
                    f"↩️ 回溯: 撤销顶点 {v} 的颜色 '{color_name}'，"
                    f"尝试下一种颜色",
                    data_snapshot={
                        "vertices": vertices,
                        "coloring": list(coloring),
                        "current_vertex": v,
                    },
                    highlights=[v],
                    variable_states={
                        "current_vertex": v, "backtrack": True,
                        "backtrack_count": self.backtrack_count,
                    },
                )

    @staticmethod
    def _is_safe(v: int, c: int, adj: dict, coloring: List[int]) -> bool:
        for neighbor in adj[v]:
            if coloring[neighbor] == c:
                return False
        return True

    @staticmethod
    def _color_name(index: int) -> str:
        names = ["🔴红", "🟢绿", "🔵蓝", "🟡黄", "🟣紫", "🟠橙"]
        return names[index] if index < len(names) else f"颜色{index}"

    # ------------------------------------------------------------------
    # 静态工具方法
    # ------------------------------------------------------------------

    @staticmethod
    def get_test_cases() -> List[dict]:
        matrix1 = [
            [0, 1, 1, 0],
            [1, 0, 1, 1],
            [1, 1, 0, 1],
            [0, 1, 1, 0],
        ]
        matrix2 = [
            [0, 1, 0, 0, 1],
            [1, 0, 1, 0, 0],
            [0, 1, 0, 1, 0],
            [0, 0, 1, 0, 1],
            [1, 0, 0, 1, 0],
        ]
        matrix3 = [
            [0, 1, 0, 1],
            [1, 0, 1, 0],
            [0, 1, 0, 1],
            [1, 0, 1, 0],
        ]
        return [
            {
                "name": "测试用例1: 4顶点图(3色)",
                "data": {"vertices": 4, "colors": 3, "edges": matrix1},
                "description": "4顶点图，使用3种颜色着色",
            },
            {
                "name": "测试用例2: 5顶点环图C5(3色)",
                "data": {"vertices": 5, "colors": 3, "edges": matrix2},
                "description": "5顶点环图，展示奇环需要3种颜色",
            },
            {
                "name": "测试用例3: 4顶点二分图(2色)",
                "data": {"vertices": 4, "colors": 2, "edges": matrix3},
                "description": "二分图，只需2种颜色即可完成着色",
            },
        ]

    @staticmethod
    def generate_random_data() -> dict:
        vertices = random.randint(MIN_GRAPH_VERTICES, 6)
        colors = random.randint(MIN_COLORS, 4)
        matrix = [[0] * vertices for _ in range(vertices)]
        edge_prob = 0.4
        for i in range(vertices):
            for j in range(i + 1, vertices):
                if random.random() < edge_prob:
                    matrix[i][j] = 1
                    matrix[j][i] = 1
        return {"vertices": vertices, "colors": colors, "edges": matrix}

    @staticmethod
    def validate_input(data: dict) -> tuple:
        if "vertices" not in data:
            return False, "缺少 'vertices' 字段"
        if "colors" not in data:
            return False, "缺少 'colors' 字段"
        if "edges" not in data:
            return False, "缺少 'edges' 字段"
        v = data["vertices"]
        m = data["colors"]
        if not isinstance(v, int) or v < MIN_GRAPH_VERTICES or v > MAX_GRAPH_VERTICES:
            return False, (
                f"顶点数必须在 {MIN_GRAPH_VERTICES} 到 "
                f"{MAX_GRAPH_VERTICES} 之间"
            )
        if not isinstance(m, int) or m < MIN_COLORS or m > MAX_COLORS:
            return False, f"颜色数必须在 {MIN_COLORS} 到 {MAX_COLORS} 之间"
        matrix = data["edges"]
        if not isinstance(matrix, list) or len(matrix) != v:
            return False, f"邻接矩阵必须是 {v}×{v} 的二维数组"
        for row in matrix:
            if not isinstance(row, list) or len(row) != v:
                return False, f"邻接矩阵每行必须有 {v} 个元素"
            if not all(x in (0, 1) for x in row):
                return False, "邻接矩阵元素必须是0或1"
        return True, ""

    def get_result(self) -> dict:
        if self.steps:
            return {
                "solutions_count": len(self.found_solutions),
                "solution": (
                    self.found_solutions[0] if self.found_solutions else None
                ),
                "backtrack_count": self.backtrack_count,
                "total_steps": self.total_steps,
            }
        return {}
