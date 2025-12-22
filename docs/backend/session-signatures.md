# Session 管理

## 核心原则

1. **入口注入**：API 层通过 `Depends(db_session)` 获取 per-request Session
2. **显式传递**：Session 作为 Service 方法首参传入
3. **显式提交**：写操作在 Service 内显式 `commit()`
4. **Repository 无状态**：只执行查询，不管理事务

## API 层

```python
@router.post("/stream")
@inject
async def translate_stream(
    request: TranslateRequest,
    session: Annotated[AsyncSession, Depends(db_session)],
    service: TranslateService = Depends(Provide["translate_service"]),
) -> StreamingResponse:
    async for event in service.translate_stream(session, request.content):
        yield sse_event(event["event"], event["data"])
```

## Service 层

```python
class TranslateService:
    async def translate(
        self,
        session: AsyncSession,  # 首参
        content: str,
        context: str | None = None,
    ) -> TranslateResponse:
        result = await self.agent.translate(content, context)
        await self.repository.create(session, result)
        await session.commit()  # 显式提交
        return TranslateResponse(...)
```

## Repository 层

```python
class TranslateRepository:
    async def create(
        self,
        session: AsyncSession,  # 显式接收
        result: TranslateResult,
    ) -> Translation:
        translation = Translation(...)
        session.add(translation)
        await session.flush()  # 只 flush，不 commit
        return translation
```

## 签名模板

```python
# Service 方法
async def method(self, session: AsyncSession, ...) -> T:
    ...
    await session.commit()

# Repository 方法
async def method(self, session: AsyncSession, ...) -> T:
    ...
    await session.flush()
```

## 常见错误

| 错误 | 正确 |
|-----|-----|
| Repository 内 commit | Service 内 commit |
| Service 内创建 Session | API 层注入 Session |
| 全局获取 Session | 显式参数传递 |
