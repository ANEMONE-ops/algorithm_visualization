"""
算法可视化系统 - 最小生成树 (Prim算法)
"""

import random
from typing import List, Dict

from .base import AlgorithmEngine, StepInfo, StepType
from ..config import MAX_GRAPH_VERTICES, MIN_GRAPH_VERTICES, MAX_EDGE_WEIGHT


class MSTEngine(AlgorithmEngine):
    """Prim 最小生成树算法引擎"""

    def generate_steps(self, data: dict) -> List[StepInfo]:
        self.steps = []
        self.original_data = data
        vertices = data["vertices"]
        matrix = data["edges"]

        # 构建邻接表
        adj = {i: [] for i in range(vertices)}
        for i in range(vertices):
            for j in range(vertices):
                if matrix[i][j] > 0 and i != j:
                    adj[i].append((j, matrix[i][j]))

        self.add_step(
            StepType.INIT,
            f"🔰 开始Prim最小生成树算法 | 顶点数: {vertices} | 从顶点0开始构建",
            data_snapshot={
                "vertices": vertices,
                "adjacency": {
                    i: [(j, w) for j, w in adj[i]] for i in range(vertices)
                },
                "mst_edges": [],
                "visited": [False] * vertices,
                "current": 0,
            },
            variable_states={"visited_count": 0, "mst_weight": 0},
        )

        visited = [False] * vertices
        mst_edges = []
        total_weight = 0

        visited[0] = True
        self.add_step(
            StepType.SELECT,
            "📍 选择起始顶点 0，将其标记为已访问",
            data_snapshot=self._make_snapshot(
                vertices, adj, mst_edges, visited, 0, [],
            ),
            highlights=[0],
            variable_states={"visited_count": 1, "mst_weight": 0},
        )

        for _ in range(vertices - 1):
            min_edge = None
            min_weight = float("inf")

            candidate_edges = []
            for u in range(vertices):
                if visited[u]:
                    for v, w in adj[u]:
                        if not visited[v]:
                            candidate_edges.append((u, v, w))

            self.add_step(
                StepType.COMPARE,
                f"🔍 扫描所有候选边（连接已访问和未访问顶点的边），"
                f"共 {len(candidate_edges)} 条",
                data_snapshot=self._make_snapshot(
                    vertices, adj, mst_edges, visited, None, candidate_edges,
                ),
                highlights=[u for u in range(vertices) if visited[u]],
                variable_states={
                    "candidate_count": len(candidate_edges),
                    "visited_count": sum(visited),
                    "mst_weight": total_weight,
                },
            )

            for u in range(vertices):
                if visited[u]:
                    for v, w in adj[u]:
                        if not visited[v] and w < min_weight:
                            min_weight = w
                            min_edge = (u, v)

            if min_edge is None:
                self.add_step(
                    StepType.INFO,
                    "⚠️ 图不连通！部分顶点无法到达。",
                    data_snapshot=self._make_snapshot(
                        vertices, adj, mst_edges, visited, None, [],
                    ),
                    variable_states={"error": "graph_disconnected"},
                )
                break

            u, v = min_edge
            self.add_step(
                StepType.SELECT,
                f"✅ 选择最小边: ({u}, {v}) 权重={min_weight}",
                data_snapshot=self._make_snapshot(
                    vertices, adj, mst_edges, visited, v,
                    [(u, v, min_weight)],
                ),
                highlights=[u, v],
                variable_states={
                    "selected_edge": (u, v, min_weight),
                    "visited_count": sum(visited),
                    "mst_weight": total_weight,
                },
            )

            mst_edges.append((u, v, min_weight))
            total_weight += min_weight
            visited[v] = True

            self.add_step(
                StepType.UPDATE,
                f"📌 将边 ({u}, {v}) 权重={min_weight} 加入MST | "
                f"顶点 {v} 标记为已访问 | MST当前总权重: {total_weight}",
                data_snapshot=self._make_snapshot(
                    vertices, adj, mst_edges, visited, v, [],
                ),
                highlights=[u, v],
                highlights_secondary=[i for i in range(vertices) if visited[i]],
                variable_states={
                    "visited_count": sum(visited),
                    "mst_weight": total_weight,
                    "mst_edges_count": len(mst_edges),
                },
            )

        self.add_step(
            StepType.COMPLETE,
            f"✨ Prim算法完成！MST包含 {len(mst_edges)} 条边，"
            f"总权重: {total_weight} | "
            f"边集合: {[(u, v, w) for u, v, w in mst_edges]}",
            data_snapshot=self._make_snapshot(
                vertices, adj, mst_edges, visited, None, [],
            ),
            highlights=[i for i in range(vertices) if visited[i]],
            variable_states={
                "visited_count": sum(visited),
                "mst_weight": total_weight,
                "mst_edges": mst_edges,
            },
        )
        return self.steps

    # ------------------------------------------------------------------
    # 内部工具
    # ------------------------------------------------------------------

    def _make_snapshot(self, vertices, adj, mst_edges, visited, current, candidates):
        return {
            "vertices": vertices,
            "adjacency": {i: adj[i] for i in range(vertices)},
            "mst_edges": list(mst_edges),
            "visited": list(visited),
            "current": current,
            "candidates": candidates,
        }

    # ------------------------------------------------------------------
    # 静态工具方法
    # ------------------------------------------------------------------

    @staticmethod
    def get_test_cases() -> List[dict]:
        matrix1 = [
            [0, 2, 0, 6, 0],
            [2, 0, 3, 8, 5],
            [0, 3, 0, 0, 7],
            [6, 8, 0, 0, 9],
            [0, 5, 7, 9, 0],
        ]
        matrix2 = [
            [0, 4, 0, 0, 1, 0],
            [4, 0, 8, 0, 0, 0],
            [0, 8, 0, 7, 0, 2],
            [0, 0, 7, 0, 9, 0],
            [1, 0, 0, 9, 0, 3],
            [0, 0, 2, 0, 3, 0],
        ]
        matrix3 = [
            [0, 10, 0, 30, 0, 0],
            [10, 0, 20, 0, 0, 0],
            [0, 20, 0, 5, 0, 15],
            [30, 0, 5, 0, 25, 0],
            [0, 0, 0, 25, 0, 12],
            [0, 0, 15, 0, 12, 0],
        ]
        return [
            {
                "name": "测试用例1: 5顶点连通图",
                "data": {"vertices": 5, "edges": matrix1},
                "description": "标准5顶点无向连通图",
            },
            {
                "name": "测试用例2: 6顶点密集图",
                "data": {"vertices": 6, "edges": matrix2},
                "description": "6顶点较密集连通图",
            },
            {
                "name": "测试用例3: 6顶点稀疏图",
                "data": {"vertices": 6, "edges": matrix3},
                "description": "6顶点稀疏连通图",
            },
        ]

    @staticmethod
    def generate_random_data() -> dict:
        vertices = random.randint(MIN_GRAPH_VERTICES, 8)
        matrix = [[0] * vertices for _ in range(vertices)]
        # 生成树保证连通性
        for i in range(1, vertices):
            j = random.randint(0, i - 1)
            w = random.randint(1, MAX_EDGE_WEIGHT)
            matrix[i][j] = w
            matrix[j][i] = w
        # 随机添加额外边
        extra_edges = random.randint(0, vertices)
        for _ in range(extra_edges):
            i = random.randint(0, vertices - 1)
            j = random.randint(0, vertices - 1)
            if i != j and matrix[i][j] == 0:
                w = random.randint(1, MAX_EDGE_WEIGHT)
                matrix[i][j] = w
                matrix[j][i] = w
        return {"vertices": vertices, "edges": matrix}

    @staticmethod
    def validate_input(data: dict) -> tuple:
        if "vertices" not in data:
            return False, "缺少 'vertices' 字段"
        if "edges" not in data:
            return False, "缺少 'edges' 字段"
        v = data["vertices"]
        if not isinstance(v, int) or v < MIN_GRAPH_VERTICES or v > MAX_GRAPH_VERTICES:
            return False, (
                f"顶点数必须在 {MIN_GRAPH_VERTICES} 到 "
                f"{MAX_GRAPH_VERTICES} 之间"
            )
        matrix = data["edges"]
        if not isinstance(matrix, list) or len(matrix) != v:
            return False, f"邻接矩阵必须是 {v}×{v} 的二维数组"
        for row in matrix:
            if not isinstance(row, list) or len(row) != v:
                return False, f"邻接矩阵每行必须有 {v} 个元素"
        for i in range(v):
            for j in range(v):
                if matrix[i][j] != matrix[j][i]:
                    return False, (
                        f"邻接矩阵不对称: "
                        f"matrix[{i}][{j}] ≠ matrix[{j}][{i}]"
                    )
        return True, ""

    def get_result(self) -> dict:
        if self.steps and self.steps[-1].data_snapshot:
            snap = self.steps[-1].data_snapshot
            return {
                "mst_edges": snap.get("mst_edges", []),
                "total_weight": self.steps[-1].variable_states.get("mst_weight", 0),
                "total_steps": self.total_steps,
            }
        return {}
