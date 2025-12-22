---
name: pkg
description: "依赖升级。触发词：pkg、upgrade、deps、升级依赖、更新包、更新依赖、npm升级、pip升级。升级前端 pnpm 和后端 pip 依赖到最新版本。(project)"
allowed-tools: Bash(pnpm*), Bash(npm*), Bash(pip*), Bash(npx*), Read, Glob
---

# 依赖升级技能

你是依赖管理专家，负责将前端和后端项目的依赖升级到最新版本。

## 核心职责

当用户执行以下任务时，自动应用本 Skill：

1. **依赖升级** - "升级依赖"、"更新包"、"pkg upgrade"
2. **版本检查** - "检查过期包"、"哪些包需要更新"
3. **依赖清理** - "清理依赖"、"重装 node_modules"

## 升级流程

### 第一步：检查过期依赖

```bash
# 前端（pnpm）
cd apps/frontend && npx npm-check-updates

# 后端（pip）
cd apps/backend && pip list --outdated
```

### 第二步：执行升级

**前端依赖**：
```bash
# 更新 package.json 到最新版本
npx npm-check-updates -u

# 安装新版本
pnpm install

# 验证
pnpm lint && pnpm build
```

**后端依赖**：
```bash
# 检查 pyproject.toml 中的版本
# 手动更新版本号后安装
pip install --upgrade package-name
```

### 第三步：验证

```bash
# 前端验证
pnpm --filter @bridgetalk/frontend lint
pnpm --filter @bridgetalk/frontend build

# 后端验证
cd apps/backend
ruff check src/
pyright src/
```

## 输出格式

```markdown
## 依赖升级报告

### 前端 (apps/frontend)
| 包名 | 当前版本 | 最新版本 | 状态 |
|------|---------|---------|------|
| react | 19.0.0 | 19.1.0 | 已升级 |
| vite | 6.0.0 | 6.1.0 | 已升级 |

### 后端 (apps/backend)
| 包名 | 当前版本 | 最新版本 | 状态 |
|------|---------|---------|------|
| fastapi | 0.115.0 | 0.116.0 | 已升级 |
| langchain | 0.3.0 | 0.3.1 | 已升级 |

### 验证结果
- 前端 lint: 通过
- 前端 build: 通过
- 后端 ruff: 通过
- 后端 pyright: 通过
```

## 常用命令速查

### 前端
```bash
npx npm-check-updates           # 检查可升级的包
npx npm-check-updates -u        # 更新 package.json
npx npm-check-updates -i        # 交互式选择升级
pnpm outdated                   # pnpm 原生检查
pnpm install                    # 安装依赖
pnpm install --force            # 强制重装
```

### 后端
```bash
pip list --outdated             # 检查过期包
pip index versions package      # 查看包的所有版本
pip install --upgrade package   # 升级单个包
```

### 清理重装
```bash
# 前端
rm -rf node_modules pnpm-lock.yaml
pnpm store prune
pnpm install

# 后端
rm -rf .venv
python -m venv .venv
pip install -e ".[dev]"
```

## 注意事项

1. **升级前提交代码**：确保可以回滚
2. **渐进式升级**：先升级 minor/patch，再考虑 major
3. **验证测试**：每次升级后运行 lint + build
4. **查看 changelog**：major 版本升级前阅读变更日志

## 直接依赖 vs 间接依赖

- **直接依赖**：`pyproject.toml` / `package.json` 中声明的包 → 手动升级
- **间接依赖**：被直接依赖引入的包 → 自动随直接依赖更新，无需手动处理
