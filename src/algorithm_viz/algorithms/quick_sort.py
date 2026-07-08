"""
算法可视化系统 - 快速排序算法
"""

import random
from typing import List

from .base import AlgorithmEngine, StepInfo, StepType
from ..config import (
    MAX_ARRAY_SIZE,
    MIN_ARRAY_SIZE,
    MAX_ARRAY_VALUE,
    MIN_ARRAY_VALUE,
)


class QuickSortEngine(AlgorithmEngine):
    """快速排序算法引擎（Lomuto 分区方案）"""

    # ------------------------------------------------------------------
    # 公共接口
    # ------------------------------------------------------------------

    def generate_steps(self, data: List[int]) -> List[StepInfo]:
        self.steps = []
        self.original_data = list(data)
        arr = list(data)

        self.add_step(
            StepType.INIT,
            f"🔰 开始快速排序 | 数组长度: {len(arr)} | "
            f"原始数组: [{', '.join(map(str, arr))}]",
            data_snapshot=list(arr),
            highlights=[],
            variable_states={
                "pivot": None, "left": 0, "right": len(arr) - 1, "depth": 0,
            },
        )

        self._quick_sort(arr, 0, len(arr) - 1, 0)

        self.add_step(
            StepType.COMPLETE,
            f"✨ 快速排序完成！最终结果: [{', '.join(map(str, arr))}]",
            data_snapshot=list(arr),
            highlights=list(range(len(arr))),
            variable_states={"sorted": True},
        )
        return self.steps

    # ------------------------------------------------------------------
    # 递归核心
    # ------------------------------------------------------------------

    def _quick_sort(self, arr: List[int], low: int, high: int, depth: int) -> None:
        if low < high:
            self.add_step(
                StepType.RECURSE_ENTER,
                f"📥 递归调用: quick_sort(arr, {low}, {high}) | 深度: {depth} | "
                f"子数组: [{', '.join(map(str, arr[low:high+1]))}]",
                data_snapshot=list(arr),
                highlights=list(range(low, high + 1)),
                variable_states={
                    "low": low, "high": high, "depth": depth,
                    "subarray": arr[low:high+1],
                },
            )

            pi = self._partition(arr, low, high, depth)

            self.add_step(
                StepType.UPDATE,
                f"📌 基准元素 arr[{pi}]={arr[pi]} 已就位（分区完成）| "
                f"左侧 ≤ {arr[pi]} | 右侧 > {arr[pi]}",
                data_snapshot=list(arr),
                highlights=[pi],
                highlights_secondary=list(range(low, high + 1)),
                variable_states={
                    "pivot_index": pi, "pivot_value": arr[pi], "depth": depth,
                },
            )

            self._quick_sort(arr, low, pi - 1, depth + 1)
            self._quick_sort(arr, pi + 1, high, depth + 1)

            self.add_step(
                StepType.RECURSE_EXIT,
                f"📤 递归返回: quick_sort(arr, {low}, {high}) 完成 | "
                f"排序后: [{', '.join(map(str, arr[low:high+1]))}]",
                data_snapshot=list(arr),
                highlights=list(range(low, high + 1)),
                variable_states={"low": low, "high": high, "depth": depth},
            )

    def _partition(self, arr: List[int], low: int, high: int, depth: int) -> int:
        pivot = arr[high]
        self.add_step(
            StepType.SELECT,
            f"🎯 选择基准: arr[{high}]={pivot} | 深度: {depth}",
            data_snapshot=list(arr),
            highlights=[high],
            variable_states={
                "pivot": pivot, "pivot_index": high, "depth": depth,
            },
        )

        i = low - 1
        for j in range(low, high):
            self.add_step(
                StepType.COMPARE,
                f"🔍 比较 arr[{j}]={arr[j]} 与基准 {pivot}",
                data_snapshot=list(arr),
                highlights=[j, high],
                variable_states={
                    "j": j, "pivot": pivot, "i": i, "depth": depth,
                },
            )

            if arr[j] <= pivot:
                i += 1
                if i != j:
                    old_arr = list(arr)
                    arr[i], arr[j] = arr[j], arr[i]
                    self.add_step(
                        StepType.SWAP,
                        f"🔄 arr[{j}]={arr[j]} ≤ 基准{pivot}，"
                        f"交换 arr[{i}]↔arr[{j}] → "
                        f"[{', '.join(map(str, arr))}]",
                        data_snapshot=list(arr),
                        highlights=[i, j],
                        variable_states={
                            "i": i, "j": j, "pivot": pivot, "depth": depth,
                        },
                        extra_info={"before": old_arr, "after": list(arr)},
                    )
                else:
                    self.add_step(
                        StepType.UPDATE,
                        f"✅ arr[{j}] ≤ 基准，i移至 {i}（不需要交换）",
                        data_snapshot=list(arr),
                        highlights=[i],
                        variable_states={
                            "i": i, "j": j, "pivot": pivot, "depth": depth,
                        },
                    )

        # 将基准放到正确位置
        if i + 1 != high:
            old_arr = list(arr)
            arr[i + 1], arr[high] = arr[high], arr[i + 1]
            self.add_step(
                StepType.SWAP,
                f"🔄 将基准 {pivot} 放到正确位置 "
                f"arr[{i+1}] ↔ arr[{high}] → "
                f"[{', '.join(map(str, arr))}]",
                data_snapshot=list(arr),
                highlights=[i + 1, high],
                variable_states={"pivot_final": i + 1, "depth": depth},
                extra_info={"before": old_arr, "after": list(arr)},
            )

        return i + 1

    # ------------------------------------------------------------------
    # 静态工具方法
    # ------------------------------------------------------------------

    @staticmethod
    def get_test_cases() -> List[dict]:
        return [
            {
                "name": "测试用例1: 随机数组",
                "data": {"array": [64, 34, 25, 12, 22, 11, 90]},
                "description": "标准随机数组",
            },
            {
                "name": "测试用例2: 近乎有序",
                "data": {"array": [1, 2, 4, 3, 5, 7, 6, 8]},
                "description": "近乎有序数组",
            },
            {
                "name": "测试用例3: 完全逆序",
                "data": {"array": [9, 8, 7, 6, 5, 4, 3, 2, 1]},
                "description": "完全逆序（快排最坏情况）",
            },
        ]

    @staticmethod
    def generate_random_data() -> dict:
        size = random.randint(MIN_ARRAY_SIZE, 15)
        arr = [random.randint(MIN_ARRAY_VALUE, MAX_ARRAY_VALUE) for _ in range(size)]
        return {"array": arr}

    @staticmethod
    def validate_input(data: dict) -> tuple:
        if "array" not in data:
            return False, "缺少 'array' 字段"
        arr = data["array"]
        if not isinstance(arr, list):
            return False, "'array' 必须是数组"
        if len(arr) < MIN_ARRAY_SIZE:
            return False, f"数组长度不能小于 {MIN_ARRAY_SIZE}"
        if len(arr) > MAX_ARRAY_SIZE:
            return False, f"数组长度不能大于 {MAX_ARRAY_SIZE}"
        if not all(isinstance(x, (int, float)) for x in arr):
            return False, "数组元素必须是数字"
        return True, ""

    def get_result(self) -> dict:
        if self.steps:
            return {
                "sorted_array": self.steps[-1].data_snapshot,
                "original_array": self.original_data,
                "total_steps": self.total_steps,
            }
        return {}
