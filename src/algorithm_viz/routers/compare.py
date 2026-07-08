"""
算法可视化系统 - 算法对比模块 & 用户测试数据管理
"""

import time
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import User, UserTestCase
from .auth import get_current_user
from ..algorithms import (
    ALGORITHM_REGISTRY,
    get_algorithm_info,
    get_all_algorithms,
)

router = APIRouter(prefix="/api/compare", tags=["算法对比"])


# ---------------------------------------------------------------------------
# 请求模型
# ---------------------------------------------------------------------------

class CompareRequest(BaseModel):
    algo_a: str = Field(..., description="算法A的ID")
    algo_b: str = Field(..., description="算法B的ID")
    data_a: Optional[dict] = Field(None, description="算法A的输入数据")
    data_b: Optional[dict] = Field(None, description="算法B的输入数据")


class SaveTestCaseRequest(BaseModel):
    algorithm_type: str
    name: str
    input_data: str


# ---------------------------------------------------------------------------
# 对比端点
# ---------------------------------------------------------------------------

@router.get("/algorithms")
def get_comparable_algorithms():
    """获取所有可对比的算法列表"""
    algos = get_all_algorithms()
    result = []
    for k, v in algos.items():
        result.append({
            "id": k,
            "name": v["name"],
            "category": v["category"],
            "time_complexity": v["time_complexity"],
            "space_complexity": v["space_complexity"],
        })
    return {"algorithms": result}


@router.post("/run")
def run_comparison(req: CompareRequest):
    """运行两个算法的对比"""
    info_a = get_algorithm_info(req.algo_a)
    info_b = get_algorithm_info(req.algo_b)

    if not info_a:
        raise HTTPException(
            status_code=404, detail=f"算法 '{req.algo_a}' 不存在"
        )
    if not info_b:
        raise HTTPException(
            status_code=404, detail=f"算法 '{req.algo_b}' 不存在"
        )

    results = []
    for algo_id, info, input_data in [
        (req.algo_a, info_a, req.data_a),
        (req.algo_b, info_b, req.data_b),
    ]:
        engine_class = info["engine"]

        if not input_data:
            random_data = engine_class.generate_random_data()
            if algo_id in ("bubble_sort", "quick_sort"):
                input_data = {
                    "array": random_data.get("array", [5, 3, 1, 4, 2]),
                }
            else:
                input_data = random_data

        if algo_id in ("bubble_sort", "quick_sort"):
            run_data = input_data.get("array", [])
        else:
            run_data = input_data

        engine = engine_class()
        valid, error = engine_class.validate_input(input_data)
        if not valid:
            raise HTTPException(
                status_code=400,
                detail=f"{info['name']} 输入验证失败: {error}",
            )

        start = time.time()
        engine.generate_steps(run_data)
        elapsed = int((time.time() - start) * 1000)

        results.append({
            "algorithm_id": algo_id,
            "algorithm_name": info["name"],
            "category": info["category"],
            "time_complexity": info["time_complexity"],
            "space_complexity": info["space_complexity"],
            "total_steps": engine.total_steps,
            "execution_time_ms": elapsed,
            "steps": engine.to_dict(),
            "result": engine.get_result(),
        })

    return {
        "pair_name": f"{info_a['name']} vs {info_b['name']}",
        "algo_a": req.algo_a,
        "algo_b": req.algo_b,
        "algorithms": results,
    }


@router.post("/run-same-input")
def run_comparison_same_input(
    algo_a: str = Query(...),
    algo_b: str = Query(...),
    data: dict = None,
):
    """两个算法使用相同输入数据运行对比"""
    return run_comparison(CompareRequest(
        algo_a=algo_a, algo_b=algo_b, data_a=data, data_b=data,
    ))


# ---------------------------------------------------------------------------
# 用户测试数据管理
# ---------------------------------------------------------------------------

@router.post("/save-test-case")
def save_user_test_case(
    req: SaveTestCaseRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """保存用户自定义测试数据"""
    tc = UserTestCase(
        user_id=current_user.id,
        algorithm_type=req.algorithm_type,
        name=req.name,
        input_data=req.input_data,
    )
    db.add(tc)
    db.commit()
    return {"message": "测试数据保存成功", "id": tc.id}


@router.get("/test-cases")
def get_user_test_cases(
    algorithm_type: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取用户保存的测试数据"""
    query = db.query(UserTestCase).filter(
        UserTestCase.user_id == current_user.id,
    )
    if algorithm_type:
        query = query.filter(UserTestCase.algorithm_type == algorithm_type)
    cases = query.order_by(UserTestCase.created_at.desc()).all()

    return {
        "test_cases": [
            {
                "id": tc.id,
                "algorithm_type": tc.algorithm_type,
                "name": tc.name,
                "input_data": tc.input_data,
                "created_at": (
                    tc.created_at.isoformat() if tc.created_at else None
                ),
            }
            for tc in cases
        ],
    }


@router.delete("/test-cases/{case_id}")
def delete_user_test_case(
    case_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """删除用户自定义测试数据"""
    tc = db.query(UserTestCase).filter(
        UserTestCase.id == case_id,
        UserTestCase.user_id == current_user.id,
    ).first()
    if not tc:
        raise HTTPException(status_code=404, detail="测试数据不存在")
    db.delete(tc)
    db.commit()
    return {"message": "删除成功"}
