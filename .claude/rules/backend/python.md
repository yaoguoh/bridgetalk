---
paths: apps/backend/**/*.py
---

# Python 后端开发规范

本规则仅在编辑 `apps/backend/` 下的 Python 文件时生效。

## 质量标准

- Pyright 零错误、Ruff 零警告
- 函数必须有类型注解
- **禁止** `# noqa` 和 `# type: ignore`（Pydantic `**kwargs` 解包除外）

## 导入规范

- **禁止** `from src.xxx` 前缀
- 使用 `from domain.xxx`、`from core.xxx`、`from llm.xxx`

## 分层职责

| 层 | 职责 |
|----|------|
| **API** | `@inject` + `Depends(Provide["..."])` 注入 Service；静态路由在参数化路由前 |
| **Service** | 构造函数注入依赖，方法首参 `session: AsyncSession`，写操作显式 `flush/commit` |
| **Repository** | Singleton 无状态；所有方法显式接收 `session`；不创建 Session，不 commit |

## 常见陷阱

| 场景 | 错误 | 正确 |
|------|------|------|
| Session | Repository 内部获取 | Service 注入，Repository 显式接收 |
| 事务 | Repository 管理 | Service 内 `flush/commit` |
| 依赖 | `from main import app` | `@inject` + `Depends(Provide[...])` |
| 响应 | 直接返回数据 | `success_response()` |
| 路由 | 参数化路由在前 | 静态路由（`/batch`）在前 |

## 校验命令

```bash
# 在仓库根目录执行（需先激活虚拟环境）
cd apps/backend
ruff format src/ && ruff check --fix src/
pyright src/
```
