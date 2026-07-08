"""
算法可视化系统 - 汉诺塔算法
"""

import random
from typing import List

from .base import AlgorithmEngine, StepInfo, StepType
from ..config import MAX_HANOI_DISKS, MIN_HANOI_DISKS


class HanoiEngine(AlgorithmEngine):
    """汉诺塔算法引擎"""

    def generate_steps(self, data: dict) -> List[StepInfo]:
        self.steps = []
        self.original_data = data
        n = data["disks"]

        pegs = {
            "A": list(range(n, 0, -1)),
            "B": [],
            "C": [],
        }
        self.move_count = 0

        self.add_step(
            StepType.INIT,
            f"🔰 开始汉诺塔问题求解 | 盘子数: {n} | "
            f"目标: 将所有盘子从A柱移动到C柱\n"
            f"规则: 每次移动一个盘子，大盘不能放在小盘上面",
            data_snapshot={"pegs": self._copy_pegs(pegs), "n": n},
            variable_states={
                "move_count": 0, "total_moves_needed": 2 ** n - 1,
            },
        )

        self.add_step(
            StepType.INFO,
            f"📐 汉诺塔递推公式: T(n) = 2T(n-1) + 1 | "
            f"最少需要 {2 ** n - 1} 步",
            data_snapshot={"pegs": self._copy_pegs(pegs), "n": n},
            variable_states={
                "formula": "T(n)=2ⁿ-1", "min_moves": 2 ** n - 1,
            },
        )

        self._hanoi(n, "A", "C", "B", pegs)

        self.add_step(
            StepType.COMPLETE,
            f"✨ 汉诺塔求解完成！共 {self.move_count} 步移动 | "
            f"理论最少步数: {2 ** n - 1} | "
            f"{'✅ 达到最优解！' if self.move_count == 2 ** n - 1 else '⚠️ 未达最优'}",
            data_snapshot={"pegs": self._copy_pegs(pegs), "n": n},
            variable_states={
                "move_count": self.move_count,
                "optimal": self.move_count == 2 ** n - 1,
            },
        )
        return self.steps

    # ------------------------------------------------------------------
    # 递归核心
    # ------------------------------------------------------------------

    def _hanoi(self, n: int, source: str, target: str, auxiliary: str, pegs: dict):
        if n == 1:
            self._move_disk(source, target, 1, pegs)
            return

        self.add_step(
            StepType.RECURSE_ENTER,
            f"📥 递归: 将 {n-1} 个盘子从 {source} 移到 {auxiliary}"
            f"（借助 {target}）",
            data_snapshot={"pegs": self._copy_pegs(pegs), "n": n},
            variable_states={
                "recursion_depth": n, "source": source, "target": auxiliary,
                "move_count": self.move_count,
            },
            highlights=[],
            highlights_secondary=[],
        )

        self._hanoi(n - 1, source, auxiliary, target, pegs)
        self._move_disk(source, target, n, pegs)

        self.add_step(
            StepType.RECURSE_ENTER,
            f"📥 递归: 将 {n-1} 个盘子从 {auxiliary} 移到 {target}"
            f"（借助 {source}）",
            data_snapshot={"pegs": self._copy_pegs(pegs), "n": n},
            variable_states={
                "recursion_depth": n, "source": auxiliary, "target": target,
                "move_count": self.move_count,
            },
        )

        self._hanoi(n - 1, auxiliary, target, source, pegs)

        self.add_step(
            StepType.RECURSE_EXIT,
            f"📤 递归返回: {n} 个盘子从 {source} 到 {target} 的移动完成",
            data_snapshot={"pegs": self._copy_pegs(pegs), "n": n},
            variable_states={
                "recursion_depth": n, "move_count": self.move_count,
            },
        )

    def _move_disk(self, source: str, target: str, disk: int, pegs: dict):
        if pegs[source] and pegs[source][-1] == disk:
            pegs[source].pop()
            pegs[target].append(disk)
            self.move_count += 1

            before_pegs = self._copy_pegs(pegs)
            before_pegs[source].append(disk)
            before_pegs[target].pop()

            self.add_step(
                StepType.SWAP,
                f"🔄 第 {self.move_count} 步: 移动盘子 {disk} | "
                f"{source} → {target}\n"
                f"  {source}柱: [{', '.join(map(str, pegs[source])) if pegs[source] else '空'}]\n"
                f"  {target}柱: [{', '.join(map(str, pegs[target]))}]",
                data_snapshot={
                    "pegs": self._copy_pegs(pegs),
                    "n": self.original_data["disks"],
                },
                variable_states={
                    "move_count": self.move_count, "disk": disk,
                    "from": source, "to": target,
                },
                extra_info={
                    "before": {"pegs": before_pegs},
                    "after": {"pegs": self._copy_pegs(pegs)},
                },
            )

    @staticmethod
    def _copy_pegs(pegs: dict) -> dict:
        return {k: list(v) for k, v in pegs.items()}

    # ------------------------------------------------------------------
    # 静态工具方法
    # ------------------------------------------------------------------

    @staticmethod
    def get_test_cases() -> List[dict]:
        return [
            {
                "name": "测试用例1: 2个盘子",
                "data": {"disks": 2},
                "description": "最小盘子数，展示基本递归模式 (最少3步)",
            },
            {
                "name": "测试用例2: 3个盘子",
                "data": {"disks": 3},
                "description": "经典3盘汉诺塔 (最少7步)",
            },
            {
                "name": "测试用例3: 4个盘子",
                "data": {"disks": 4},
                "description": "4盘汉诺塔，展示递归深度 (最少15步)",
            },
            {
                "name": "测试用例4: 5个盘子",
                "data": {"disks": 5},
                "description": "5盘汉诺塔，更多递归层级 (最少31步)",
            },
        ]

    @staticmethod
    def generate_random_data() -> dict:
        disks = random.randint(MIN_HANOI_DISKS, 5)
        return {"disks": disks}

    @staticmethod
    def validate_input(data: dict) -> tuple:
        if "disks" not in data:
            return False, "缺少 'disks' 字段"
        n = data["disks"]
        if not isinstance(n, int) or n < MIN_HANOI_DISKS:
            return False, f"盘子数至少为 {MIN_HANOI_DISKS}"
        if n > MAX_HANOI_DISKS:
            return False, (
                f"盘子数最多为 {MAX_HANOI_DISKS}"
                f"（步数为2ⁿ-1，{MAX_HANOI_DISKS}盘=255步）"
            )
        return True, ""

    def get_result(self) -> dict:
        if self.steps:
            return {
                "move_count": self.move_count,
                "total_steps": self.total_steps,
                "optimal_moves": (
                    2 ** self.original_data["disks"] - 1
                    if self.original_data else 0
                ),
                "is_optimal": (
                    self.move_count == (2 ** self.original_data["disks"] - 1)
                    if self.original_data else False
                ),
            }
        return {}
