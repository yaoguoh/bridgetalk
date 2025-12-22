# Skills 目录

本目录包含项目的 Agent Skills，用于扩展 Claude 在本项目中的专业能力。

## 当前可用 Skills

### review

**代码审查与重构**

- 触发词：审查代码、review、检查质量、重构、代码精简
- 功能：自动运行 ruff/pyright/eslint，识别重构点，给出设计模式建议
- 五步审查流程：静态分析 → 重构检测 → 架构合规 → 代码清理 → 抽象优化

### pkg

**依赖升级**

- 触发词：pkg、upgrade、deps、升级依赖、更新包、npm升级、pip升级
- 功能：升级前端 pnpm 和后端 pip 依赖到最新版本
- 流程：检查过期 → 执行升级 → 验证通过

### search

**多源信息检索**

- 触发词：search、搜索、查询最佳实践、对比调研
- 功能：并行调用 Exa/Context7/WebFetch，综合对比分析
- 输出：表格对比 + 综合结论 + 参考链接

## Skill 目录结构

```
skill-name/
├── SKILL.md          # 必需：能力定义（YAML头 + 指令）
├── references/       # 可选：详细参考文档
└── scripts/          # 可选：可执行脚本
```

## 使用方式

Skills 根据用户请求**自动加载**，无需手动指定。

示例触发：
- "升级依赖到最新版本" → 自动加载 pkg
- "帮我审查代码" → 自动加载 review
- "search React hooks 最佳实践" → 自动加载 search
