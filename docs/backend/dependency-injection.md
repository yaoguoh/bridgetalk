# 依赖注入

基于 `dependency-injector` 库的扁平化容器设计。

## 容器定义

```python
# container.py
from dependency_injector import containers, providers

class AppContainer(containers.DeclarativeContainer):
    config = providers.Singleton(lambda: config_manager)
    llm = providers.Singleton(create_dashscope_llm)
    translate_repository = providers.Singleton(TranslateRepository)
    translate_service = providers.Singleton(
        TranslateService,
        llm=llm,
        repository=translate_repository,
    )
```

## 容器初始化

```python
# main.py
@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncGenerator[None]:
    ...
    container = AppContainer()
    container.wire(modules=["domain.translate.api.routes"])
    _app.state.container = container
    ...
```

## API 层注入

```python
from dependency_injector.wiring import Provide, inject

@router.post("/stream")
@inject
async def translate_stream(
    request: TranslateRequest,
    session: Annotated[AsyncSession, Depends(db_session)],
    service: TranslateService = Depends(Provide["translate_service"]),
) -> StreamingResponse:
    ...
```

## 规则

| 规则 | 说明 |
|-----|-----|
| 装饰器顺序 | `@router` 在外，`@inject` 紧贴函数 |
| Provider 类型 | Singleton 用于无状态服务，Factory 用于需要新实例的场景 |
| 显式依赖 | Provider 必须显式传入所有依赖 |
| 注入位置 | 仅 API 层使用 `@inject`，Service 不装饰 |

## 常见错误

```python
# 错误：装饰器顺序错误
@inject
@router.post("/")
async def handler(): ...

# 正确
@router.post("/")
@inject
async def handler(): ...
```

```python
# 错误：Service 内获取容器
class TranslateService:
    def __init__(self):
        from main import app
        self.repo = app.state.container.translate_repository()

# 正确：构造函数注入
class TranslateService:
    def __init__(self, llm: BaseChatModel, repository: TranslateRepository):
        self.llm = llm
        self.repository = repository
```
