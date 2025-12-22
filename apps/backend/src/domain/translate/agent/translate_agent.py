"""翻译 Agent 主逻辑"""

from __future__ import annotations

import uuid
from collections.abc import AsyncIterator
from dataclasses import dataclass, field
from typing import Any, TypedDict, cast

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import AIMessageChunk, BaseMessage, HumanMessage, SystemMessage
from langgraph.graph import END, StateGraph
from langgraph.graph.state import CompiledStateGraph

from core.logging import get_logger
from domain.translate.agent.tools import (
    analyze_gaps_with_llm,
    get_system_prompt,
    identify_perspective_with_llm,
)
from domain.translate.graph.checkpoint import TenantAwareRedisSaver
from domain.translate.prompts.dev_to_pm import DEV_TO_PM_SYSTEM_PROMPT


logger = get_logger(__name__)


def _extract_text_content(message: BaseMessage) -> str:
    """从 LLM 消息中提取纯文本内容"""
    raw_content = message.content
    if isinstance(raw_content, str):
        return raw_content
    # LangChain 返回 list[str | dict] 格式的多部分内容
    text_parts: list[str] = []
    for part in cast(list[object], raw_content):
        if isinstance(part, str):
            text_parts.append(part)
        elif isinstance(part, dict) and "text" in part:
            text_parts.append(str(part["text"]))
    return "".join(text_parts)


def _extract_chunk_content(chunk: AIMessageChunk) -> str:
    """从流式消息块中提取文本内容"""
    raw_content = chunk.content
    if isinstance(raw_content, str):
        return raw_content
    if not raw_content:
        return ""
    # LangChain 返回 list[str | dict] 格式的多部分内容
    text_parts: list[str] = []
    for part in cast(list[object], raw_content):
        if isinstance(part, str):
            text_parts.append(part)
        elif isinstance(part, dict) and "text" in part:
            text_parts.append(str(part["text"]))
    return "".join(text_parts)


def _empty_gaps() -> list[dict[str, Any]]:
    return []


def _empty_suggestions() -> list[str]:
    return []


class TranslateState(TypedDict, total=False):
    content: str
    context: str | None
    detected_perspective: str
    confidence: float
    reason: str
    gaps: list[dict[str, Any]]
    suggestions: list[str]
    direction: str
    system_prompt: str
    translated_content: str
    error_message: str | None


@dataclass
class TranslateResult:
    """翻译结果"""

    original_content: str
    translated_content: str
    detected_perspective: str
    direction: str
    gaps: list[dict[str, Any]] = field(default_factory=_empty_gaps)
    suggestions: list[str] = field(default_factory=_empty_suggestions)


class TranslateAgent:
    """智能翻译 Agent"""

    def __init__(self, llm: BaseChatModel) -> None:
        self.llm = llm
        self.checkpointer = TenantAwareRedisSaver()
        self.graph = self._build_graph(include_translation=True)
        self.preprocess_graph = self._build_graph(include_translation=False)

    def _build_graph(
        self, *, include_translation: bool
    ) -> CompiledStateGraph[TranslateState, None, TranslateState, TranslateState]:
        graph: StateGraph[TranslateState] = StateGraph(TranslateState)
        graph.add_node("detect_perspective", self._node_detect_perspective)
        graph.add_node("analyze_gaps", self._node_analyze_gaps)
        if include_translation:
            graph.add_node("translate", self._node_translate)
        graph.set_entry_point("detect_perspective")
        graph.add_edge("detect_perspective", "analyze_gaps")
        if include_translation:
            graph.add_edge("analyze_gaps", "translate")
            graph.add_edge("translate", END)
        else:
            graph.add_edge("analyze_gaps", END)
        return graph.compile(checkpointer=self.checkpointer)

    async def _node_detect_perspective(self, state: TranslateState) -> TranslateState:
        try:
            content = state.get("content", "")
            # 使用 AI 分析视角
            result = await identify_perspective_with_llm(content, self.llm)
            logger.info("AI 视角识别完成: %s (置信度: %s)", result["perspective"], result["confidence"])
            return {
                "detected_perspective": result["perspective"],
                "confidence": result["confidence"],
                "reason": result["reason"],
            }
        except Exception as e:
            logger.exception("视角识别节点失败")
            return {
                "detected_perspective": "unknown",
                "confidence": 0.0,
                "reason": "识别过程发生错误",
                "error_message": f"视角识别失败: {e!s}",
            }

    async def _node_analyze_gaps(self, state: TranslateState) -> TranslateState:
        if state.get("error_message"):
            return {}

        try:
            content = state.get("content", "")
            perspective = state.get("detected_perspective", "unknown")
            # 使用 AI 分析缺失信息
            result = await analyze_gaps_with_llm(content, perspective, self.llm)
            gaps = result.get("gaps", [])
            suggestions = result.get("suggestions", [])
            logger.info("AI 缺失分析完成: 发现 %d 项缺失信息", len(gaps))
            # 确定翻译方向
            direction = "pm_to_dev" if perspective == "pm" else "dev_to_pm"
            system_prompt = get_system_prompt(direction)
            return {
                "gaps": gaps,
                "suggestions": suggestions,
                "direction": direction,
                "system_prompt": system_prompt,
            }
        except Exception as e:
            logger.exception("缺失分析节点失败")
            perspective = state.get("detected_perspective", "unknown")
            direction = "pm_to_dev" if perspective == "pm" else "dev_to_pm"
            system_prompt = get_system_prompt(direction)
            return {
                "gaps": [],
                "suggestions": [],
                "direction": direction,
                "system_prompt": system_prompt,
                "error_message": f"缺失分析失败: {e!s}",
            }

    async def _node_translate(self, state: TranslateState) -> TranslateState:
        if state.get("error_message"):
            return {"translated_content": ""}

        try:
            system_prompt = state.get("system_prompt", "")
            content = state.get("content", "")
            gaps = state.get("gaps", [])
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=self._build_translate_prompt(content, state.get("context"), gaps)),
            ]
            response = await self.llm.ainvoke(messages)
            translated_content = _extract_text_content(response)
            return {"translated_content": translated_content}
        except Exception as e:
            logger.exception("翻译节点失败")
            return {
                "translated_content": "",
                "error_message": f"翻译失败: {e!s}",
            }

    async def translate(
        self,
        content: str,
        context: str | None = None,
    ) -> TranslateResult:
        """执行翻译（同步模式）"""
        thread_id = uuid.uuid4().hex
        state = await self.graph.ainvoke(
            {"content": content, "context": context},
            config={"configurable": {"thread_id": thread_id}},
        )
        perspective = state.get("detected_perspective", "unknown")
        confidence = state.get("confidence", 0.0)
        gaps = state.get("gaps", [])
        suggestions = state.get("suggestions", [])
        direction = state.get("direction", "dev_to_pm")
        translated_content = state.get("translated_content", "")
        logger.info("翻译完成，方向: %s，置信度: %s", direction, confidence)

        return TranslateResult(
            original_content=content,
            translated_content=translated_content,
            detected_perspective=perspective,
            direction=direction,
            gaps=gaps,
            suggestions=suggestions,
        )

    async def translate_stream(
        self,
        content: str,
        context: str | None = None,
    ) -> AsyncIterator[dict[str, Any]]:
        """执行翻译（流式模式）"""
        thread_id = uuid.uuid4().hex

        # 阶段 1: 预处理（视角识别 + 缺失分析）
        try:
            state = await self.preprocess_graph.ainvoke(
                {"content": content, "context": context},
                config={"configurable": {"thread_id": thread_id}},
            )
        except Exception as e:
            logger.exception("预处理阶段失败")
            yield {
                "event": "error",
                "data": {"message": f"预处理失败: {e!s}", "stage": "preprocess"},
            }
            return

        # 检查预处理是否有错误
        if error := state.get("error_message"):
            logger.warning("预处理阶段返回错误: %s", error)
            yield {
                "event": "error",
                "data": {"message": error, "stage": "preprocess"},
            }
            return

        perspective = state.get("detected_perspective", "unknown")
        confidence = state.get("confidence", 0.0)
        reason = state.get("reason", "无")
        logger.info("[流式] AI 识别视角: %s, 置信度: %s", perspective, confidence)
        yield {
            "event": "perspective_detected",
            "data": {
                "perspective": perspective,
                "confidence": confidence,
                "reason": reason,
            },
        }

        gaps = state.get("gaps", [])
        suggestions = state.get("suggestions", [])
        if gaps:
            yield {
                "event": "gaps_identified",
                "data": {
                    "gaps": gaps,
                    "suggestions": suggestions,
                },
            }

        direction = state.get("direction", "dev_to_pm")
        system_prompt = state.get("system_prompt", DEV_TO_PM_SYSTEM_PROMPT)

        yield {
            "event": "translation_start",
            "data": {"direction": direction},
        }

        # 阶段 2: 流式翻译
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=self._build_translate_prompt(content, context, gaps)),
        ]

        try:
            content_parts: list[str] = []
            async for chunk in self.llm.astream(messages):
                delta = _extract_chunk_content(chunk)
                if delta:
                    content_parts.append(delta)
                    yield {
                        "event": "content_delta",
                        "data": {"delta": delta},
                    }
            full_content = "".join(content_parts)

            logger.info("[流式] 翻译完成，方向: %s", direction)
            yield {
                "event": "message_done",
                "data": {
                    "translated_content": full_content,
                    "detected_perspective": perspective,
                    "direction": direction,
                    "gaps": gaps,
                    "suggestions": suggestions,
                },
            }
        except Exception as e:
            logger.exception("翻译阶段失败")
            yield {
                "event": "error",
                "data": {"message": f"翻译失败: {e!s}", "stage": "translate"},
            }

    def _build_translate_prompt(
        self,
        content: str,
        context: str | None,
        gaps: list[dict[str, Any]],
    ) -> str:
        """构建翻译提示"""
        prompt_parts = [f"请翻译以下内容：\n\n{content}"]

        if context:
            prompt_parts.append(f"\n\n补充上下文：\n{context}")

        if gaps:
            gap_descriptions = [f"- {g['description']}" for g in gaps]
            prompt_parts.append(
                "\n\n注意：输入中可能缺失以下信息，请在翻译时适当补充或标注：\n" + "\n".join(gap_descriptions)
            )

        return "".join(prompt_parts)
