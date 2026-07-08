"""
算法可视化系统 - 哈夫曼树算法
"""

import random
import heapq
from typing import List

from .base import AlgorithmEngine, StepInfo, StepType
from ..config import MAX_HUFFMAN_CHARS, MIN_HUFFMAN_CHARS


class HuffmanNode:
    """哈夫曼树节点"""

    def __init__(self, char, freq, left=None, right=None):
        self.char = char
        self.freq = freq
        self.left = left
        self.right = right
        self.node_id = 0

    def __lt__(self, other):
        return self.freq < other.freq

    def __repr__(self):
        return f"Node({self.char}:{self.freq})"


class HuffmanEngine(AlgorithmEngine):
    """哈夫曼树算法引擎"""

    def __init__(self):
        super().__init__()
        self.node_counter = 0

    def generate_steps(self, data: dict) -> List[StepInfo]:
        self.steps = []
        self.node_counter = 0
        self.original_data = data
        chars = data["chars"]
        freqs = data["freqs"]

        # 创建初始节点
        nodes = []
        for c, f in zip(chars, freqs):
            node = HuffmanNode(c, f)
            node.node_id = self.node_counter
            self.node_counter += 1
            nodes.append(node)

        self.add_step(
            StepType.INIT,
            f"🔰 开始构建哈夫曼树 | 字符集: {', '.join(chars)} | "
            f"频率: {', '.join(map(str, freqs))}",
            data_snapshot=self._make_snapshot(nodes, []),
            variable_states={"node_count": len(nodes), "merged_count": 0},
        )

        heap = nodes[:]
        heapq.heapify(heap)
        merged_history = []

        round_num = 0
        while len(heap) > 1:
            round_num += 1
            left = heapq.heappop(heap)
            right = heapq.heappop(heap)

            self.add_step(
                StepType.SELECT,
                f"🔍 第 {round_num} 轮：选取两个最小频率节点: "
                f"'{left.char}'({left.freq}) 和 '{right.char}'({right.freq})",
                data_snapshot=self._make_snapshot(
                    heap + [left, right], merged_history, [left, right],
                ),
                highlights=[left.node_id, right.node_id],
                variable_states={
                    "left": f"{left.char}({left.freq})",
                    "right": f"{right.char}({right.freq})",
                    "merged_count": round_num,
                },
            )

            merged = HuffmanNode(
                f"({left.char}+{right.char})",
                left.freq + right.freq,
                left,
                right,
            )
            merged.node_id = self.node_counter
            self.node_counter += 1
            merged_history.append({
                "parent_id": merged.node_id,
                "parent_char": merged.char,
                "parent_freq": merged.freq,
                "left_id": left.node_id,
                "left_char": left.char,
                "left_freq": left.freq,
                "right_id": right.node_id,
                "right_char": right.char,
                "right_freq": right.freq,
            })

            heapq.heappush(heap, merged)

            self.add_step(
                StepType.MERGE,
                f"🔗 合并 '{left.char}'({left.freq}) + "
                f"'{right.char}'({right.freq}) → "
                f"新节点 '{merged.char}'({merged.freq}) | "
                f"堆中剩余: {len(heap)} 个节点",
                data_snapshot=self._make_snapshot(heap[:], merged_history),
                highlights=[merged.node_id],
                highlights_secondary=[left.node_id, right.node_id],
                variable_states={
                    "merged_char": merged.char,
                    "merged_freq": merged.freq,
                    "heap_size": len(heap),
                    "merged_count": round_num,
                },
            )

        # 生成哈夫曼编码
        root = heap[0] if heap else None
        codes = {}
        if root:
            self._generate_codes(root, "", codes)
            self.add_step(
                StepType.INFO,
                f"📋 哈夫曼编码结果:\n"
                + "\n".join(f"  '{c}': {code}" for c, code in codes.items()),
                data_snapshot=self._make_snapshot([root], merged_history),
                variable_states={
                    "codes": codes,
                    "total_bits": sum(
                        freqs[chars.index(c)] * len(code)
                        for c, code in codes.items()
                    ),
                },
            )

        total_wpl = (
            sum(freqs[chars.index(c)] * len(code) for c, code in codes.items())
            if root else 0
        )
        self.add_step(
            StepType.COMPLETE,
            f"✨ 哈夫曼树构建完成！共 {len(codes)} 个字符编码 | "
            f"带权路径长度(WPL): {total_wpl} | "
            f"树高: {self._get_height(root) if root else 0}",
            data_snapshot=self._make_snapshot(
                [root] if root else [], merged_history,
            ),
            variable_states={
                "codes": codes,
                "wpl": total_wpl,
                "tree_height": self._get_height(root) if root else 0,
            },
        )
        return self.steps

    # ------------------------------------------------------------------
    # 内部工具
    # ------------------------------------------------------------------

    def _make_snapshot(self, nodes, merged_history, selected=None):
        return {
            "nodes": [
                {
                    "id": n.node_id, "char": n.char, "freq": n.freq,
                    "left": n.left.node_id if n.left else None,
                    "right": n.right.node_id if n.right else None,
                }
                for n in nodes
            ],
            "merged_history": merged_history,
            "selected": [n.node_id for n in selected] if selected else [],
        }

    def _generate_codes(self, node, code, codes):
        if node is None:
            return
        if node.left is None and node.right is None:
            codes[node.char] = code if code else "0"
            return
        self._generate_codes(node.left, code + "0", codes)
        self._generate_codes(node.right, code + "1", codes)

    @staticmethod
    def _get_height(node):
        if node is None:
            return 0
        return 1 + max(
            HuffmanEngine._get_height(node.left),
            HuffmanEngine._get_height(node.right),
        )

    # ------------------------------------------------------------------
    # 静态工具方法
    # ------------------------------------------------------------------

    @staticmethod
    def get_test_cases() -> List[dict]:
        return [
            {
                "name": "测试用例1: 经典频率分布",
                "data": {
                    "chars": ["A", "B", "C", "D", "E", "F"],
                    "freqs": [5, 9, 12, 13, 16, 45],
                },
                "description": "经典哈夫曼编码示例，频率差异明显",
            },
            {
                "name": "测试用例2: 均匀频率",
                "data": {
                    "chars": ["a", "b", "c", "d", "e"],
                    "freqs": [10, 10, 10, 10, 10],
                },
                "description": "所有字符频率相等，展示平衡树构建",
            },
            {
                "name": "测试用例3: 3字符简单示例",
                "data": {"chars": ["X", "Y", "Z"], "freqs": [1, 2, 3]},
                "description": "最少字符的简单示例",
            },
            {
                "name": "测试用例4: 极端频率差异",
                "data": {"chars": ["A", "B", "C", "D"], "freqs": [1, 1, 1, 100]},
                "description": "极端频率差异，展示编码长度对比",
            },
        ]

    @staticmethod
    def generate_random_data() -> dict:
        count = random.randint(MIN_HUFFMAN_CHARS, 8)
        chars = [chr(65 + i) for i in range(count)]
        freqs = [random.randint(1, 50) for _ in range(count)]
        return {"chars": chars, "freqs": freqs}

    @staticmethod
    def validate_input(data: dict) -> tuple:
        if "chars" not in data:
            return False, "缺少 'chars' 字段"
        if "freqs" not in data:
            return False, "缺少 'freqs' 字段"
        chars = data["chars"]
        freqs = data["freqs"]
        if not isinstance(chars, list) or not isinstance(freqs, list):
            return False, "'chars' 和 'freqs' 必须是列表"
        if len(chars) != len(freqs):
            return False, f"字符数({len(chars)})与频率数({len(freqs)})不匹配"
        if len(chars) < MIN_HUFFMAN_CHARS:
            return False, f"至少需要 {MIN_HUFFMAN_CHARS} 个字符"
        if len(chars) > MAX_HUFFMAN_CHARS:
            return False, f"最多支持 {MAX_HUFFMAN_CHARS} 个字符"
        if not all(isinstance(f, (int, float)) and f > 0 for f in freqs):
            return False, "频率必须是正数"
        return True, ""

    def get_result(self) -> dict:
        if self.steps:
            codes = self.steps[-1].variable_states.get("codes", {})
            return {
                "codes": codes,
                "total_steps": self.total_steps,
                "wpl": self.steps[-1].variable_states.get("wpl", 0),
            }
        return {}
