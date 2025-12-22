# 后端架构

## 目录结构

```
apps/backend/src/
├── main.py               # FastAPI 入口，生命周期管理
├── config.py             # 配置管理（YAML 加载）
├── container.py          # 依赖注入容器
├── model_registry.py     # SQLAlchemy 模型注册
├── core/                 # 核心基础设施
│   ├── api/              # 统一响应格式
│   ├── cache/            # Redis 缓存服务
│   ├── config/           # 配置加载器
│   ├── context/          # 请求上下文
│   ├── database/         # 数据库会话管理
│   ├── logging/          # 日志配置
│   ├── sse/              # SSE 事件格式
│   └── type/             # 公共类型定义
├── domain/translate/     # 翻译业务域
│   ├── agent/            # LangGraph Agent
│   ├── api/              # API 路由
│   ├── graph/            # LangGraph 检查点
│   ├── model/            # SQLAlchemy 模型
│   ├── prompts/          # 提示词模板
│   ├── repository/       # 数据访问层
│   ├── schema/           # Pydantic 模型
│   └── service/          # 业务逻辑层
└── llm/                  # LLM 适配（DashScope）
```

## 分层架构

```
API → Service → Repository → Model
         ↓
       Agent → LLM
```

| 层 | 职责 |
|---|---|
| API | 路由定义、请求验证、依赖注入 |
| Service | 业务逻辑、事务管理、Agent 调用 |
| Repository | 数据访问、SQL 查询 |
| Agent | LangGraph 工作流、LLM 调用 |

## 请求链路

```
HTTP Request
    ↓
FastAPI Router (@inject)
    ↓
Depends(db_session) → AsyncSession
    ↓
TranslateService.translate_stream()
    ↓
TranslateAgent (LangGraph)
    ↓
TranslateRepository.create()
    ↓
session.commit()
    ↓
SSE Response
```

## 依赖注入

使用 `dependency-injector` 库，扁平化容器结构：

```python
# container.py
class AppContainer(containers.DeclarativeContainer):
    llm = providers.Singleton(create_dashscope_llm)
    translate_repository = providers.Singleton(TranslateRepository)
    translate_service = providers.Singleton(
        TranslateService,
        llm=llm,
        repository=translate_repository,
    )
```

API 层注入：

```python
@router.post("/stream")
@inject
async def translate_stream(
    request: TranslateRequest,
    session: Annotated[AsyncSession, Depends(db_session)],
    service: TranslateService = Depends(Provide["translate_service"]),
) -> StreamingResponse:
    ...
```

## Session 管理

- API 层通过 `Depends(db_session)` 获取 per-request Session
- Service 方法首参为 `session: AsyncSession`
- 写操作在 Service 内显式 `commit()`
- Repository 只执行查询，不管理事务

## 导入规范

```python
# 正确
from domain.translate.service import TranslateService
from core.database.session import db_session

# 错误
from src.domain.translate.service import TranslateService
```
