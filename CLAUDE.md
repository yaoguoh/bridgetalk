# CLAUDE

## 技术栈

- 后端：Python 3.13 + FastAPI + LangGraph + DashScope
- 数据库：PostgreSQL + SQLAlchemy + Alembic + Redis
- 前端：React 19 + TypeScript + Tailwind 4 + Vite

## 项目结构

```
apps/backend/src/
├── main.py, config.py, container.py
├── core/           # 基础设施（api/cache/database/logging/sse）
├── domain/         # 业务域（translate/agent/service/repository）
└── llm/            # LLM 适配

apps/frontend/src/
├── components/     # 组件（layout/translate/ui）
├── hooks/          # 自定义 Hook
└── pages/          # 页面
```

## 快速命令

```bash
# 后端
source .venv/bin/activate
cd apps/backend && python -m uvicorn src.main:app --reload

# 前端
pnpm --filter @bridgetalk/frontend dev

# 校验
cd apps/backend && ruff format src/ && ruff check --fix src/ && pyright src/
pnpm --filter @bridgetalk/frontend lint && pnpm --filter @bridgetalk/frontend exec tsc --noEmit
```

## 规则索引

详细规范见 `.claude/rules/`：
- `principles.md` - 核心原则
- `workflow.md` - 任务流程
- `backend/python.md` - Python 规范
- `frontend/react.md` - React 规范
