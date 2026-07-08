"""
算法可视化系统 - 豆包大模型 AI 对话模块
"""

import json
import logging
from typing import Optional

import httpx
from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from ..config import DOUBAO_API_KEY, DOUBAO_API_URL, DOUBAO_MODEL
from ..models import User
from .auth import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/ai", tags=["AI对话"])

# ---------------------------------------------------------------------------
# 算法知识库系统提示词
# ---------------------------------------------------------------------------

ALGORITHM_CONTEXT = """
你是一个算法可视化系统的智能助手。你精通以下算法：
1. 冒泡排序 (Bubble Sort) - O(n²) 时间，O(1) 空间 - 通过重复遍历数组，比较相邻元素并交换来排序
2. 最小生成树 Prim算法 - O(V²) 时间，O(V) 空间 - 从任意顶点开始，每次选最小权重边扩展
3. 哈夫曼树 - O(n log n) 时间，O(n) 空间 - 贪心算法构建最优前缀编码树
4. 汉诺塔 - O(2ⁿ) 时间，O(n) 空间 - 经典递归问题，T(n)=2T(n-1)+1
5. 图着色 (回溯法) - O(m^V) 时间，O(V) 空间 - NP完全问题的回溯求解
6. 快速排序 - O(n log n) 平均，O(log n) 空间 - 分治排序算法

系统功能包括：算法过程可视化、步进执行、自动播放、暂停、重置、回退、
测试用例、随机数据生成、算法对比、执行日志导出等。

请用中文回答用户关于算法、数据结构、复杂度分析或系统使用的问题。回答应该：
- 清晰、准确、易懂
- 结合可视化系统中的具体算法步骤来解释
- 鼓励用户通过可视化来加深理解
- 适当引用实际例子
"""


# ---------------------------------------------------------------------------
# 请求 / 响应模型
# ---------------------------------------------------------------------------

class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000, description="用户问题")
    algorithm_context: Optional[str] = Field(None, description="当前算法上下文")
    conversation_history: Optional[list] = Field(None, description="对话历史")


class ExplainStepRequest(BaseModel):
    algorithm_type: str = Field(..., description="算法类型")
    step_description: str = Field(..., description="步骤描述")


class ChatResponse(BaseModel):
    reply: str
    model: str


# ---------------------------------------------------------------------------
# 内部工具
# ---------------------------------------------------------------------------

def build_messages(
    message: str,
    algorithm_context: Optional[str],
    history: Optional[list],
) -> list:
    """构建发送给 LLM 的消息列表"""
    system_prompt = ALGORITHM_CONTEXT
    if algorithm_context:
        system_prompt += (
            f"\n\n用户当前正在查看的算法信息: {algorithm_context}"
        )

    messages = [{"role": "system", "content": system_prompt}]

    if history:
        for h in history[-10:]:
            messages.append({
                "role": h.get("role", "user"),
                "content": h.get("content", ""),
            })

    messages.append({"role": "user", "content": message})
    return messages


async def _call_doubao(
    messages: list,
    max_tokens: int = 2000,
    temperature: float = 0.7,
) -> tuple:
    """调用豆包大模型 API，返回 (是否成功, 回复内容/错误信息)"""
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            logger.info(f"Calling Doubao API: {DOUBAO_API_URL}")
            response = await client.post(
                DOUBAO_API_URL,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {DOUBAO_API_KEY}",
                },
                json={
                    "model": DOUBAO_MODEL,
                    "messages": messages,
                    "max_tokens": max_tokens,
                    "temperature": temperature,
                    "stream": False,
                },
            )

            logger.info(f"Doubao API response status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                reply = data["choices"][0]["message"]["content"]
                return True, reply
            else:
                error_detail = response.text[:300]
                logger.error(
                    f"Doubao API error: {response.status_code} - {error_detail}"
                )
                return False, f"API返回状态码 {response.status_code}: {error_detail}"

    except httpx.TimeoutException:
        logger.error("Doubao API timeout after 60s")
        return False, "AI服务请求超时（60秒），请检查网络连接后重试"
    except httpx.ConnectError as e:
        logger.error(f"Doubao API connection error: {e}")
        return False, f"无法连接到AI服务: {str(e)[:150]}"
    except Exception as e:
        logger.error(f"Doubao API unexpected error: {e}")
        return False, f"AI服务异常: {str(e)[:200]}"


# ---------------------------------------------------------------------------
# 端点
# ---------------------------------------------------------------------------

@router.post("/chat", response_model=ChatResponse)
async def chat(
    req: ChatRequest,
    current_user: User = Depends(get_current_user),
):
    """AI 对话接口"""
    messages = build_messages(
        req.message, req.algorithm_context, req.conversation_history,
    )
    success, reply = await _call_doubao(messages, max_tokens=2000, temperature=0.7)

    if success:
        return ChatResponse(reply=reply, model=DOUBAO_MODEL)
    else:
        return ChatResponse(
            reply=(
                f"[离线模式] {reply}\n\n"
                f"您的问题: {req.message[:150]}...\n\n"
                f"建议: 查看算法详情面板了解复杂度分析，"
                f"或使用预设测试用例观察执行过程。"
            ),
            model="offline-fallback",
        )


@router.post("/chat/explain-step")
async def explain_step(
    req: ExplainStepRequest,
    current_user: User = Depends(get_current_user),
):
    """解释当前算法步骤（教程模式）"""
    prompt = (
        f"用户正在学习{req.algorithm_type}算法，当前步骤是：\n"
        f"{req.step_description}\n\n"
        f"请用通俗易懂的语言解释这一步在做什么，为什么这样做，"
        f"有什么要点需要注意。用1-3句话简洁回答。"
    )

    messages = [
        {"role": "system", "content": ALGORITHM_CONTEXT},
        {"role": "user", "content": prompt},
    ]

    success, reply = await _call_doubao(messages, max_tokens=500, temperature=0.5)

    if success:
        return {"explanation": reply, "source": "ai"}
    else:
        return {
            "explanation": f"[离线模式] {req.step_description}",
            "source": "offline",
        }
