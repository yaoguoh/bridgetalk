"""
应用级依赖注入容器

使用 dependency-injector 构建 IoC 容器，采用扁平化结构。
依赖显式传递，保持可读性与可维护性。
"""

from dependency_injector import containers, providers

from config import config_manager
from domain.translate.repository.translate_repository import TranslateRepository
from domain.translate.service.translate_service import TranslateService
from llm.dashscope import create_dashscope_llm


class AppContainer(containers.DeclarativeContainer):
    """应用级根容器（扁平化结构）"""

    config = providers.Singleton(lambda: config_manager)

    llm = providers.Singleton(create_dashscope_llm)

    translate_repository = providers.Singleton(TranslateRepository)

    translate_service = providers.Singleton(
        TranslateService,
        llm=llm,
        repository=translate_repository,
    )
