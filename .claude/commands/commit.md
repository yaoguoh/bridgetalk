---
description: 生成符合规范的提交消息
---

分析当前 git diff，生成符合项目 Git 提交规范的提交消息。

## 提交规范

格式：`<emoji> <type>: <description>`

| Emoji | 类型 | 说明 |
|-------|------|------|
| ✨ | New Features | 新功能 |
| 🐞 | Bug Fixes | BUG修复 |
| 🔨 | Dependency Upgrades | 依赖升级 |
| 📔 | Documentation | 更新文档 |
| ♻️ | Refactor | 代码重构 |

## 执行步骤

1. 运行 `git diff --cached --stat` 查看已暂存的变更
2. 如果没有暂存变更，运行 `git diff --stat` 查看未暂存变更
3. 分析变更内容，判断属于哪种类型
4. 生成简洁的中文描述（1-2 句话，聚焦 "why" 而非 "what"）
5. 输出完整的提交消息

## 输出格式

```
<emoji> <type>: <简短标题>

<详细描述（可选，说明主要变更点）>
```
