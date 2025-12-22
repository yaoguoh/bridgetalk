"""Agent 工具定义"""

from __future__ import annotations

import json
from typing import Any, Literal

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import BaseModel, Field

from domain.translate.prompts.dev_to_pm import DEV_TO_PM_SYSTEM_PROMPT
from domain.translate.prompts.pm_to_dev import PM_TO_DEV_SYSTEM_PROMPT


class PerspectiveResult(BaseModel):
    """视角识别结果"""

    perspective: Literal["pm", "dev", "unknown"] = Field(description="识别的视角类型")
    confidence: float = Field(ge=0, le=1, description="置信度")
    reason: str = Field(description="判断理由")


class GapItem(BaseModel):
    """缺失信息项"""

    category: str = Field(description="分类")
    description: str = Field(description="缺失信息描述")
    importance: Literal["high", "medium", "low"] = Field(description="重要程度")


class GapsResult(BaseModel):
    """缺失分析结果"""

    gaps: list[GapItem] = Field(default_factory=list[GapItem], description="缺失信息列表")
    suggestions: list[str] = Field(default_factory=list[str], description="建议补充的问题")


PERSPECTIVE_ANALYSIS_PROMPT = """你是一个专业的沟通分析师，擅长识别文本的表述视角。

请分析以下文本内容，判断它是产品经理视角还是开发工程师视角的表述。

判断依据：
- **产品经理视角**：关注用户需求、业务价值、功能描述、使用场景、用户体验、商业目标
- **开发工程师视角**：关注技术实现、系统架构、接口设计、性能优化、代码逻辑、技术方案

请返回 JSON 格式的分析结果：
{{
  "perspective": "pm" 或 "dev" 或 "unknown",
  "confidence": 0.0-1.0 的置信度,
  "reason": "判断理由，简要说明为什么判断为该视角"
}}

待分析内容：
{content}

请返回 JSON 结果（只返回 JSON，不要其他内容）："""


GAPS_ANALYSIS_PROMPT_PM = """你是一个资深的开发工程师，正在审阅产品经理的需求描述。

请分析以下产品需求，识别其中可能缺失的关键信息，这些信息对于开发工程师理解和实现需求非常重要。

关注点：
- 用户场景和目标用户是否清晰
- 业务价值和预期收益是否明确
- 功能边界和验收标准是否定义
- 优先级和时间要求是否说明
- 异常情况和边界条件是否考虑

产品需求：
{content}

请返回 JSON 格式的分析结果：
{{
  "gaps": [
    {{
      "category": "分类（如：用户场景、业务价值、验收标准等）",
      "description": "具体缺失的信息描述",
      "importance": "high/medium/low"
    }}
  ],
  "suggestions": [
    "建议产品经理补充回答的问题"
  ]
}}

注意：
- 只列出真正缺失的关键信息，不要过度挑剔
- 如果需求描述已经比较完整，可以返回空列表
- suggestions 中的问题要具体、易于回答

请返回 JSON 结果（只返回 JSON，不要其他内容）："""


GAPS_ANALYSIS_PROMPT_DEV = """你是一个资深的产品经理，正在审阅开发工程师的技术方案。

请分析以下技术方案，识别其中可能缺失的关键信息，这些信息对于产品经理理解方案和做出决策非常重要。

关注点：
- 整体架构和技术选型是否清晰
- 接口设计和数据流是否明确
- 技术风险和应对方案是否评估
- 开发周期和资源需求是否说明
- 对用户体验的影响是否考虑

技术方案：
{content}

请返回 JSON 格式的分析结果：
{{
  "gaps": [
    {{
      "category": "分类（如：系统架构、接口设计、技术风险等）",
      "description": "具体缺失的信息描述",
      "importance": "high/medium/low"
    }}
  ],
  "suggestions": [
    "建议开发工程师补充说明的问题"
  ]
}}

注意：
- 只列出真正缺失的关键信息，不要过度挑剔
- 如果技术方案已经比较完整，可以返回空列表
- suggestions 中的问题要具体、易于回答

请返回 JSON 结果（只返回 JSON，不要其他内容）："""


def _extract_json_from_response(response: str) -> dict[str, Any]:
    """从 LLM 响应中提取 JSON"""
    content = response.strip()
    # 尝试直接解析
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        pass
    # 尝试提取 ```json ... ``` 代码块
    if "```json" in content:
        start = content.find("```json") + 7
        end = content.find("```", start)
        if end > start:
            return json.loads(content[start:end].strip())
    # 尝试提取 { ... } 部分
    start = content.find("{")
    end = content.rfind("}") + 1
    if start >= 0 < end:
        return json.loads(content[start:end])
    msg = f"无法从响应中提取 JSON: {content[:200]}"
    raise ValueError(msg)


async def identify_perspective_with_llm(content: str, llm: BaseChatModel) -> dict[str, Any]:
    """使用 LLM 识别输入文本的视角类型

    Args:
        content: 需要分析的文本内容
        llm: LLM 实例

    Returns:
        识别结果字典，包含 perspective、confidence 和 reason
    """
    messages = [
        SystemMessage(content="你是一个专业的沟通分析师，擅长识别文本的表述视角。请严格按要求返回 JSON 格式。"),
        HumanMessage(content=PERSPECTIVE_ANALYSIS_PROMPT.format(content=content)),
    ]

    try:
        response = await llm.ainvoke(messages)
        response_text = str(response.content) if hasattr(response, "content") else str(response)
        result = _extract_json_from_response(response_text)
        # 验证并规范化结果
        perspective = result.get("perspective", "unknown")
        if perspective not in ("pm", "dev", "unknown"):
            perspective = "unknown"
        confidence = float(result.get("confidence", 0.5))
        confidence = max(0.0, min(1.0, confidence))
        reason = str(result.get("reason", "AI 分析结果"))
        return {
            "perspective": perspective,
            "confidence": round(confidence, 2),
            "reason": reason,
        }
    except Exception as e:
        return {
            "perspective": "unknown",
            "confidence": 0.5,
            "reason": f"AI 分析失败: {e!s}",
        }


async def analyze_gaps_with_llm(
    content: str, perspective: str, llm: BaseChatModel
) -> dict[str, Any]:
    """使用 LLM 分析输入文本中缺失的关键信息

    Args:
        content: 需要分析的文本内容
        perspective: 文本的视角类型（pm 或 dev）
        llm: LLM 实例

    Returns:
        分析结果字典，包含 gaps 和 suggestions
    """
    if perspective == "pm":
        prompt = GAPS_ANALYSIS_PROMPT_PM.format(content=content)
    elif perspective == "dev":
        prompt = GAPS_ANALYSIS_PROMPT_DEV.format(content=content)
    else:
        # unknown 视角时不分析
        return {"gaps": [], "suggestions": []}

    messages = [
        SystemMessage(content="你是一个专业的需求分析师，擅长发现沟通中的信息缺失。请严格按要求返回 JSON 格式。"),
        HumanMessage(content=prompt),
    ]

    try:
        response = await llm.ainvoke(messages)
        response_text = str(response.content) if hasattr(response, "content") else str(response)
        result = _extract_json_from_response(response_text)
        # 验证并规范化结果
        gaps = result.get("gaps", [])
        suggestions = result.get("suggestions", [])
        # 确保 gaps 格式正确
        validated_gaps: list[dict[str, Any]] = []
        for gap in gaps:
            if isinstance(gap, dict) and "category" in gap and "description" in gap:
                validated_gaps.append({
                    "category": str(gap["category"]),
                    "description": str(gap["description"]),
                    "importance": gap.get("importance", "medium"),
                })
        return {
            "gaps": validated_gaps,
            "suggestions": [str(s) for s in suggestions] if suggestions else [],
        }
    except Exception as e:
        return {
            "gaps": [],
            "suggestions": [],
            "error": f"AI 分析失败: {e!s}",
        }


def get_system_prompt(direction: str) -> str:
    """获取翻译方向对应的系统提示词"""
    if direction == "pm_to_dev":
        return PM_TO_DEV_SYSTEM_PROMPT
    return DEV_TO_PM_SYSTEM_PROMPT
