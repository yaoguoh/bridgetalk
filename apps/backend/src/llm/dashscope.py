"""DashScope LLM 适配器"""

from __future__ import annotations

from typing import cast

import httpx
from langchain_community.chat_models import ChatTongyi
from langchain_core.language_models import BaseChatModel

from config import config_manager
from core.logging import get_logger


logger = get_logger(__name__)


def create_dashscope_llm() -> BaseChatModel:
    """创建 DashScope LLM 实例（带重试机制）"""
    llm_config = config_manager.llm.dashscope

    # ChatTongyi 的参数名与 pyright 识别不一致，使用 type: ignore
    client = ChatTongyi(
        model=llm_config.model_name,
        dashscope_api_key=llm_config.api_key,  # type: ignore[call-arg]
        temperature=llm_config.temperature,  # type: ignore[call-arg]
        max_tokens=llm_config.max_tokens,  # type: ignore[call-arg]
        request_timeout=llm_config.request_timeout,  # type: ignore[call-arg]
        streaming=True,
    )

    # 添加重试机制：指数退避 + 随机抖动，最多 3 次
    # with_retry 返回 Runnable，但实际保留了 BaseChatModel 的所有能力
    logger.info("LLM 客户端已配置重试机制：最多 3 次，指数退避")
    return cast(
        BaseChatModel,
        client.with_retry(
            retry_if_exception_type=(
                httpx.ReadError,
                httpx.ConnectError,
                httpx.TimeoutException,
                httpx.NetworkError,
                ConnectionError,
                TimeoutError,
            ),
            wait_exponential_jitter=True,
            stop_after_attempt=3,
        ),
    )
