---
paths: apps/frontend/**/*.{ts,tsx}
---

# React 前端开发规范

本规则仅在编辑 `apps/frontend/` 下的 TypeScript/React 文件时生效。

## 类型安全

- **禁止** 使用 `any` 类型
- 启用 strict mode
- 使用 `type` 而非 `interface`（除非需要扩展）

## Hooks 规范

- 所有依赖必须声明
- 使用函数式更新 `setState(prev => ...)`

## 构建验证

`pnpm run build` 必须成功

## 代码校验命令

每次修改后必须运行：

```bash
# 类型检查（必须 0 errors）
pnpm --filter @bridgetalk/frontend exec tsc -b --noEmit

# Lint（必须 0 errors 0 warnings）
pnpm --filter @bridgetalk/frontend lint
```

- 遇到问题使用 Exa 查询最佳处理方式
- **禁止** 使用 `@ts-ignore` 或 `eslint-disable` 等忽略处理

## 技术栈

- **React 19**：函数组件 + Hooks
- **TypeScript 5.6**：严格模式
- **Tailwind CSS 4.x**：实用优先 CSS
- **Vite 6**：构建与开发
- **lucide-react**：图标库

## 组件命名

- PascalCase 命名
- 文件名 = 组件名
