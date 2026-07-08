"""
算法可视化系统 - 算法执行 API 路由
（从 main.py 中提取，遵循单一职责原则）
"""

import time

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field

from ..algorithms import (
    ALGORITHM_REGISTRY,
    get_algorithm_info,
    get_all_algorithms,
)

router = APIRouter(prefix="/api/algorithms", tags=["算法"])


# ---------------------------------------------------------------------------
# 请求模型
# ---------------------------------------------------------------------------

class RunAlgorithmRequest(BaseModel):
    algorithm_id: str = Field(..., description="算法ID")
    data: dict = Field(..., description="输入数据")


# ---------------------------------------------------------------------------
# 端点
# ---------------------------------------------------------------------------

@router.get("")
def list_algorithms():
    """获取所有可用算法列表"""
    return {"algorithms": get_all_algorithms()}


@router.get("/{algorithm_id}")
def get_algorithm_detail(algorithm_id: str):
    """获取算法详情（含测试用例）"""
    info = get_algorithm_info(algorithm_id)
    if not info:
        raise HTTPException(
            status_code=404, detail=f"算法 '{algorithm_id}' 不存在"
        )

    engine_class = info["engine"]
    return {
        "id": algorithm_id,
        "name": info["name"],
        "category": info["category"],
        "difficulty": info["difficulty"],
        "time_complexity": info["time_complexity"],
        "space_complexity": info["space_complexity"],
        "description": info["description"],
        "input_fields": info["input_fields"],
        "test_cases": engine_class.get_test_cases(),
    }


@router.post("/run")
def run_algorithm(req: RunAlgorithmRequest):
    """运行算法并返回所有执行步骤"""
    algo_info = get_algorithm_info(req.algorithm_id)
    if not algo_info:
        raise HTTPException(
            status_code=404, detail=f"算法 '{req.algorithm_id}' 不存在"
        )

    engine_class = algo_info["engine"]
    engine = engine_class()

    # 验证输入
    valid, error = engine_class.validate_input(req.data)
    if not valid:
        raise HTTPException(
            status_code=400, detail=f"输入验证失败: {error}"
        )

    # 提取实际运行数据
    if req.algorithm_id in ("bubble_sort", "quick_sort"):
        run_data = req.data["array"]
    else:
        run_data = req.data

    # 执行并计时
    start = time.time()
    steps = engine.generate_steps(run_data)
    elapsed = int((time.time() - start) * 1000)

    return {
        "algorithm_id": req.algorithm_id,
        "algorithm_name": algo_info["name"],
        "category": algo_info["category"],
        "time_complexity": algo_info["time_complexity"],
        "space_complexity": algo_info["space_complexity"],
        "description": algo_info["description"],
        "execution_time_ms": elapsed,
        "total_steps": engine.total_steps,
        "steps": engine.to_dict(),
        "result": engine.get_result(),
    }


@router.post("/random-data")
def generate_random_data(algorithm_id: str = Query(...)):
    """为指定算法生成随机测试数据"""
    algo_info = get_algorithm_info(algorithm_id)
    if not algo_info:
        raise HTTPException(
            status_code=404, detail=f"算法 '{algorithm_id}' 不存在"
        )

    engine_class = algo_info["engine"]
    random_data = engine_class.generate_random_data()
    return {"algorithm_id": algorithm_id, "data": random_data}


@router.post("/validate")
def validate_algorithm_input(
    algorithm_id: str = Query(...),
    data: dict = None,
):
    """验证算法输入数据"""
    if data is None:
        data = {}
    algo_info = get_algorithm_info(algorithm_id)
    if not algo_info:
        raise HTTPException(
            status_code=404, detail=f"算法 '{algorithm_id}' 不存在"
        )

    engine_class = algo_info["engine"]
    valid, error = engine_class.validate_input(data)
    return {"valid": valid, "error": error, "algorithm_id": algorithm_id}


@router.get("/{algorithm_id}/test-cases")
def get_algorithm_test_cases(algorithm_id: str):
    """获取算法的预设测试用例"""
    algo_info = get_algorithm_info(algorithm_id)
    if not algo_info:
        raise HTTPException(
            status_code=404, detail=f"算法 '{algorithm_id}' 不存在"
        )

    engine_class = algo_info["engine"]
    test_cases = engine_class.get_test_cases()
    return {"algorithm_id": algorithm_id, "test_cases": test_cases}
