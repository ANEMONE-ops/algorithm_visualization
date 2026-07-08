"""
算法可视化系统 - 冒泡排序算法
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


class BubbleSortEngine(AlgorithmEngine):
    """冒泡排序算法引擎"""

    def generate_steps(self, data: List[int]) -> List[StepInfo]:
        self.steps = []
        self.original_data = list(data)
        arr = list(data)
        n = len(arr)

        self.add_step(
            StepType.INIT,
            f"🔰 开始冒泡排序 | 数组长度: {n} | "
            f"原始数组: [{', '.join(map(str, arr))}]",
            data_snapshot=list(arr),
            highlights=[],
            variable_states={"i": -1, "j": -1, "swapped": False, "sorted_count": 0},
        )

        for i in range(n - 1):
            swapped = False
            self.add_step(
                StepType.INFO,
                f"📋 第 {i + 1} 轮遍历开始（前 {i} 个元素已排好）",
                data_snapshot=list(arr),
                highlights=list(range(n - i, n)),
                variable_states={
                    "i": i, "j": -1, "swapped": False, "sorted_count": i,
                },
            )

            for j in range(n - i - 1):
                self.add_step(
                    StepType.COMPARE,
                    f"🔍 比较 arr[{j}]={arr[j]} 和 arr[{j + 1}]={arr[j + 1]}",
                    data_snapshot=list(arr),
                    highlights=[j, j + 1],
                    variable_states={
                        "i": i, "j": j, "comparing": [j, j + 1], "sorted_count": i,
                    },
                )

                if arr[j] > arr[j + 1]:
                    old_arr = list(arr)
                    arr[j], arr[j + 1] = arr[j + 1], arr[j]
                    swapped = True
                    self.add_step(
                        StepType.SWAP,
                        f"🔄 {arr[j]} > {arr[j + 1]}，"
                        f"交换 arr[{j}] 和 arr[{j + 1}] → "
                        f"[{', '.join(map(str, arr))}]",
                        data_snapshot=list(arr),
                        highlights=[j, j + 1],
                        variable_states={
                            "i": i, "j": j, "swapped": True, "sorted_count": i,
                        },
                        extra_info={"before": old_arr, "after": list(arr)},
                    )
                else:
                    self.add_step(
                        StepType.COMPARE,
                        f"✅ {arr[j]} ≤ {arr[j + 1]}，不需要交换",
                        data_snapshot=list(arr),
                        highlights=[j, j + 1],
                        variable_states={
                            "i": i, "j": j, "swapped": swapped, "sorted_count": i,
                        },
                    )

            self.add_step(
                StepType.UPDATE,
                f"🏁 第 {i + 1} 轮结束 | arr[{n - i - 1}]={arr[n - i - 1]} 已就位 | "
                f"{'有交换' if swapped else '无交换'}",
                data_snapshot=list(arr),
                highlights=[n - i - 1],
                highlights_secondary=list(range(n - i, n)),
                variable_states={
                    "i": i, "j": n - i - 2, "swapped": swapped, "sorted_count": i + 1,
                },
            )

            if not swapped:
                self.add_step(
                    StepType.INFO,
                    "🎉 本轮无任何交换，数组已完全有序，提前结束！",
                    data_snapshot=list(arr),
                    highlights=list(range(n)),
                    variable_states={"early_stop": True, "sorted_count": n},
                )
                break

        self.add_step(
            StepType.COMPLETE,
            f"✨ 冒泡排序完成！最终结果: [{', '.join(map(str, arr))}]",
            data_snapshot=list(arr),
            highlights=list(range(n)),
            variable_states={"sorted_count": n},
        )
        return self.steps

    # ------------------------------------------------------------------
    # 静态工具方法
    # ------------------------------------------------------------------

    @staticmethod
    def get_test_cases() -> List[dict]:
        return [
            {
                "name": "测试用例1: 随机数组",
                "data": {"array": [64, 34, 25, 12, 22, 11, 90]},
                "description": "标准随机数组，展示冒泡排序基本过程",
            },
            {
                "name": "测试用例2: 近乎有序",
                "data": {"array": [1, 2, 4, 3, 5, 7, 6, 8]},
                "description": "近乎有序的数组，展示提前终止优化",
            },
            {
                "name": "测试用例3: 完全逆序",
                "data": {"array": [9, 8, 7, 6, 5, 4, 3, 2, 1]},
                "description": "完全逆序数组，展示最坏情况",
            },
            {
                "name": "测试用例4: 含重复元素",
                "data": {"array": [5, 3, 8, 3, 1, 5, 7, 1]},
                "description": "含重复元素的数组，展示稳定性",
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
            return False, f"数组长度不能小于 {MIN_ARRAY_SIZE}，当前长度: {len(arr)}"
        if len(arr) > MAX_ARRAY_SIZE:
            return False, f"数组长度不能大于 {MAX_ARRAY_SIZE}，当前长度: {len(arr)}"
        if not all(isinstance(x, (int, float)) for x in arr):
            return False, "数组元素必须是数字"
        return True, ""

    def get_result(self) -> dict:
        if self.steps:
            return {
                "sorted_array": self.steps[-1].data_snapshot,
                "original_array": self.original_data,
                "total_steps": self.total_steps,
                "comparisons": sum(
                    1 for s in self.steps if s.step_type == StepType.COMPARE
                ),
                "swaps": sum(
                    1 for s in self.steps if s.step_type == StepType.SWAP
                ),
            }
        return {}
