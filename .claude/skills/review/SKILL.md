---
name: review
description: "代码审查与重构。触发词：审查代码、review、检查质量、重构、代码精简、优化设计。自动运行 ruff/pyright/eslint，识别重构点，给出设计模式建议。(project)"
allowed-tools: Read, Grep, Glob, Bash(ruff*), Bash(pyright*), Bash(pnpm lint*), Bash(pnpm tsc*)
---

# 代码审查技能

## 触发场景

- 审查代码、review、检查质量
- 重构、代码精简、优化设计

## 审查流程

### 1. 静态分析

```bash
# 后端
cd apps/backend
ruff check src/ --fix
pyright src/

# 前端
pnpm --filter @bridgetalk/frontend lint
```

### 2. 重构检测

| 条件 | 阈值 |
|------|------|
| 函数行数 | > 80 行（多步骤流程可放宽至 120 行） |
| 嵌套深度 | > 3 层 |
| 重复代码 | > 3 次 |

### 3. 架构检查

- 后端：Session 显式传递、依赖注入在容器、分层正确
- 前端：组件单一职责、Hook 规范、禁止 any

### 4. 代码清理

- 未使用的导入/变量
- TODO/FIXME 注释
- 调试代码

## 输出格式

```markdown
### P0 - 必须修复
- [文件:行号] 问题 → 建议

### P1 - 建议修复
- [文件:行号] 问题 → 建议

### 设计模式建议
- 场景 → 推荐模式
```

## 参考

- @PATTERNS.md - 重构模式速查
- @docs/backend/architecture.md - 后端架构
- @docs/frontend/development.md - 前端规范
