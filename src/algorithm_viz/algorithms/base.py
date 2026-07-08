"""
算法可视化系统 - 算法基类
"""

from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from enum import Enum


class StepType(Enum):
    """步骤类型"""

    COMPARE = "compare"
    SWAP = "swap"
    SELECT = "select"
    UPDATE = "update"
    COMPLETE = "complete"
    INIT = "init"
    RECURSE_ENTER = "recurse_enter"
    RECURSE_EXIT = "recurse_exit"
    BACKTRACK = "backtrack"
    MERGE = "merge"
    SPLIT = "split"
    INFO = "info"


@dataclass
class StepInfo:
    """单步信息"""

    step_index: int
    step_type: StepType
    description: str
    data_snapshot: Any = None
    highlights: List[int] = field(default_factory=list)
    highlights_secondary: List[int] = field(default_factory=list)
    variable_states: Dict[str, Any] = field(default_factory=dict)
    extra_info: Dict[str, Any] = field(default_factory=dict)


class AlgorithmEngine:
    """算法引擎基类 — 所有具体算法引擎的抽象父类"""

    def __init__(self) -> None:
        self.steps: List[StepInfo] = []
        self.original_data: Any = None

    # ------------------------------------------------------------------
    # 子类必须重写的方法
    # ------------------------------------------------------------------

    def generate_steps(self, data: Any) -> List[StepInfo]:
        """生成算法执行步骤（子类必须实现）"""
        raise NotImplementedError("子类必须实现 generate_steps 方法")

    # ------------------------------------------------------------------
    # 公共方法
    # ------------------------------------------------------------------

    def add_step(self, step_type: StepType, description: str, **kwargs) -> StepInfo:
        """向步骤列表中添加一个步骤"""
        step = StepInfo(
            step_index=len(self.steps),
            step_type=step_type,
            description=description,
            **kwargs,
        )
        self.steps.append(step)
        return step

    def get_step(self, index: int) -> Optional[StepInfo]:
        """获取指定索引的步骤"""
        if 0 <= index < len(self.steps):
            return self.steps[index]
        return None

    @property
    def total_steps(self) -> int:
        return len(self.steps)

    def to_dict(self) -> Dict:
        """将步骤列表转换为可 JSON 序列化的字典"""
        return {
            "total_steps": self.total_steps,
            "steps": [
                {
                    "step_index": s.step_index,
                    "step_type": (
                        s.step_type.value
                        if isinstance(s.step_type, StepType)
                        else s.step_type
                    ),
                    "description": s.description,
                    "data_snapshot": s.data_snapshot,
                    "highlights": s.highlights,
                    "highlights_secondary": s.highlights_secondary,
                    "variable_states": s.variable_states,
                    "extra_info": s.extra_info,
                }
                for s in self.steps
            ],
        }

    def get_result(self) -> Dict:
        """获取算法执行结果（子类可重写以提供更丰富的信息）"""
        return {}

    # ------------------------------------------------------------------
    # 静态工具方法
    # ------------------------------------------------------------------

    @staticmethod
    def get_test_cases() -> List[Dict]:
        """获取预设测试用例"""
        return []

    @staticmethod
    def generate_random_data() -> Any:
        """生成随机测试数据"""
        return None

    @staticmethod
    def validate_input(data: Any) -> tuple:
        """验证输入数据，返回 (是否有效, 错误信息)"""
        return True, ""
