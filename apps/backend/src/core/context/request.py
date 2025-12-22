"""请求上下文管理模块，提供默认租户访问"""

from __future__ import annotations

from contextvars import ContextVar
from dataclasses import dataclass, field
from typing import Any

from core.logging import get_logger


logger = get_logger(__name__)
_DEFAULT_REALM = "default"


def _empty_roles() -> list[str]:
    return []


def _empty_organization() -> list[str]:
    return []


def _empty_token() -> dict[str, Any]:
    return {}


@dataclass
class RequestContextParams:
    """请求上下文参数对象"""

    realm: str = _DEFAULT_REALM
    username: str = "anonymous"
    roles: list[str] | None = None
    request_id: str | None = None
    organization: list[str] | None = None
    token: dict[str, Any] | None = None


@dataclass
class RequestContext:
    """请求上下文信息"""

    realm: str = _DEFAULT_REALM
    username: str = "anonymous"
    roles: list[str] = field(default_factory=_empty_roles)
    request_id: str | None = None
    organization: list[str] = field(default_factory=_empty_organization)
    token: dict[str, Any] = field(default_factory=_empty_token)


_request_context: ContextVar[RequestContext | None] = ContextVar("request_context", default=None)


def set_request_context(params: RequestContextParams) -> RequestContext:
    """设置当前请求上下文"""
    context = RequestContext(
        realm=params.realm,
        username=params.username,
        roles=params.roles or [],
        request_id=params.request_id,
        organization=params.organization or [],
        token=params.token or {},
    )
    _request_context.set(context)
    logger.debug("设置请求上下文: %s", context)
    return context


def get_request_context() -> RequestContext:
    """获取当前请求上下文，如果不存在则返回默认上下文"""
    if (context := _request_context.get()) is None:
        return RequestContext()
    return context


def current_realm() -> str:
    """获取当前租户"""
    return get_request_context().realm


def clear_request_context() -> None:
    """清理请求上下文"""
    _request_context.set(None)
