"""SSE 事件定义"""

from __future__ import annotations

from enum import Enum
from typing import Any

import orjson


class SSEEventType(str, Enum):
    """SSE 事件类型"""

    MESSAGE_START = "message_start"
    CONTENT_DELTA = "content_delta"
    MESSAGE_DONE = "message_done"
    ERROR = "error"
    PING = "ping"


def _to_json(data: dict[str, Any]) -> str:
    """转换为 JSON 字符串"""
    return orjson.dumps(data).decode()


def sse_message_start(request_id: str) -> dict[str, str]:
    """消息开始事件"""
    return {
        "event": SSEEventType.MESSAGE_START.value,
        "data": _to_json({"request_id": request_id}),
    }


def sse_content_delta(text: str) -> dict[str, str]:
    """内容增量事件"""
    return {
        "event": SSEEventType.CONTENT_DELTA.value,
        "data": _to_json({"delta": {"text": text}}),
    }


def sse_message_done(
    content: str,
    suggestions: list[str] | None = None,
) -> dict[str, str]:
    """消息完成事件"""
    return {
        "event": SSEEventType.MESSAGE_DONE.value,
        "data": _to_json(
            {
                "content": content,
                "suggestions": suggestions or [],
            }
        ),
    }


def sse_error(message: str, code: str | None = None) -> dict[str, str]:
    """错误事件"""
    return {
        "event": SSEEventType.ERROR.value,
        "data": _to_json(
            {
                "error": {"message": message, "code": code},
            }
        ),
    }


def sse_ping() -> dict[str, str]:
    """心跳事件"""
    return {
        "event": SSEEventType.PING.value,
        "data": "",
    }


def sse_event(event_type: str, data: dict[str, Any]) -> str:
    """生成通用 SSE 事件字符串"""
    return f"event: {event_type}\ndata: {_to_json(data)}\n\n"
