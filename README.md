# BridgeTalk

**职能沟通翻译助手** - 弥合产品经理与开发工程师之间的沟通鸿沟。

BridgeTalk 是一款基于大语言模型的智能翻译工具，能够自动识别输入文本的视角（产品/开发），分析缺失的关键信息，并将内容翻译成对方更容易理解的语言。

## 核心价值

- **消除理解偏差**：产品需求不再模糊，技术方案不再晦涩
- **主动发现盲点**：识别沟通中遗漏的关键信息
- **实时反馈**：流式输出，边生成边呈现

---

## 功能特性

### 视角自动识别

基于 LLM 分析输入文本，智能判断是产品视角还是开发视角：
- 产品视角特征：用户需求、业务价值、功能描述、体验目标
- 开发视角特征：技术实现、系统架构、接口设计、性能指标
- 输出置信度和判断理由

### 缺失信息分析

根据识别的视角类型，使用差异化的检查点分析缺失信息：

**产品视角缺失检查**：
- 用户场景和使用流程
- 业务价值和预期收益
- 优先级和时间要求
- 成功指标和验收标准
- 边界条件和异常处理

**开发视角缺失检查**：
- 系统架构和技术选型
- 接口设计和数据结构
- 性能指标和扩展性
- 技术风险和依赖项
- 开发周期和资源评估

### 智能翻译

根据目标受众自动选择翻译策略：
- **PM → DEV**：将模糊需求转化为清晰功能点，用技术术语描述实现
- **DEV → PM**：去技术化表述，用业务场景替代技术术语

### 流式输出

采用 SSE（Server-Sent Events）实时推送翻译结果：
- 视角识别完成即时反馈
- 缺失分析实时呈现
- 翻译内容逐字流式输出

### 历史管理

所有翻译记录持久化存储，支持：
- 分页查询历史记录
- 查看翻译详情
- 回顾缺失分析结果

---

## 技术栈

### 后端

| 组件 | 版本 | 用途 |
|------|------|------|
| Python | 3.13+ | 运行时 |
| FastAPI | 0.127+ | Web 框架 |
| LangGraph | 0.3+ | Agent 编排 |
| LangChain | 0.3+ | LLM 集成 |
| DashScope | - | 通义千问 API |
| PostgreSQL | 15+ | 关系数据库 |
| SQLAlchemy | 2.0+ | ORM |
| Alembic | 1.17+ | 数据库迁移 |
| Redis | 7+ | 状态检查点 |
| sse-starlette | 3.0+ | SSE 支持 |
| dependency-injector | 4.48+ | 依赖注入 |

### 前端

| 组件 | 版本 | 用途 |
|------|------|------|
| React | 19 | UI 框架 |
| TypeScript | 5.6+ | 类型系统 |
| Tailwind CSS | 4.x | 样式框架 |
| Vite | 6.x | 构建工具 |
| React Router | 7.x | 路由管理 |
| lucide-react | - | 图标库 |

---

## 快速开始

### 环境要求

- Python 3.13+
- Node.js 20+
- pnpm（推荐）或 npm
- Docker & Docker Compose

### 1. 克隆仓库

```bash
git clone https://github.com/your-org/bridgetalk.git
cd bridgetalk
```

### 2. 启动依赖服务

项目依赖 PostgreSQL 和 Redis，使用 Docker Compose 一键启动：

```bash
docker compose up -d
```

验证服务状态：

```bash
docker compose ps
```

预期输出：
```
NAME                  STATUS
bridgetalk-postgres   running (healthy)
bridgetalk-redis      running (healthy)
```

### 3. 后端启动

```bash
# 激活虚拟环境（仓库根目录）
source .venv/bin/activate

# 安装依赖
pip install -e apps/backend

# 进入后端目录
cd apps/backend

# 设置 DashScope API Key（必需）
export DASHSCOPE_API_KEY=your_api_key

# 启动服务（自动执行数据库迁移）
python -m uvicorn src.main:app --reload --port 8008
```

后端服务地址：http://localhost:8008

API 文档：http://localhost:8008/docs

### 4. 前端启动

```bash
# 回到仓库根目录
cd ../..

# 安装依赖
pnpm install

# 启动开发服务器
pnpm --filter @bridgetalk/frontend dev
```

前端服务地址：http://localhost:5173

### 5. 开始使用

1. 访问 http://localhost:5173
2. 在聊天页面输入需求或技术方案
3. 系统自动识别视角并翻译

---

## 配置说明

配置文件位于 `apps/backend/config.yaml`。

### 数据库配置

```yaml
database:
  host: "127.0.0.1"       # 数据库地址
  port: 5432              # 端口
  username: "postgres"    # 用户名
  password: "password"    # 密码
  name: "bridgetalk"      # 数据库名
  pool_size: 10           # 连接池基础大小
  max_overflow: 5         # 额外连接数
  pool_timeout: 30        # 获取连接超时（秒）
  pool_recycle: 3600      # 连接回收周期（秒）
  pool_pre_ping: true     # 连接健康检查
```

### LLM 配置

```yaml
llm:
  dashscope:
    api_key: "${DASHSCOPE_API_KEY}"  # 从环境变量读取
    model_name: "qwen-max"           # 模型名称
    temperature: 0.7                 # 生成温度
    max_tokens: 4096                 # 最大 token 数
```

支持的模型：`qwen-max`、`qwen-plus`、`qwen-turbo` 等通义千问系列。

### 服务器配置

```yaml
server:
  host: "0.0.0.0"         # 监听地址
  port: 8008              # 监听端口
  cors_origins:           # 允许的跨域来源
    - "http://localhost:5173"
    - "http://127.0.0.1:5173"
```

### Redis 配置

```yaml
redis:
  host: "127.0.0.1"       # Redis 地址
  port: 6379              # 端口
  password: ""            # 密码（可选）
  database: 0             # 数据库编号
  key_prefix: "bridgetalk" # 键前缀
```

### 环境变量

| 变量名 | 必填 | 说明 |
|--------|------|------|
| DASHSCOPE_API_KEY | 是 | 通义千问 API Key，获取地址：https://dashscope.console.aliyun.com/ |

---

## API 文档

### 端点列表

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /api/translate | 同步翻译 |
| POST | /api/translate/stream | 流式翻译 |
| GET | /api/translate/history | 获取历史列表 |
| GET | /api/translate/{id} | 获取翻译详情 |

### POST /api/translate/stream

流式翻译接口，返回 SSE 事件流。

**请求体**：
```json
{
  "content": "需要一个智能推荐功能，提升用户停留时长",
  "context": "可选的补充上下文"
}
```

**SSE 事件类型**：

| 事件 | 说明 | 数据格式 |
|------|------|---------|
| perspective_detected | 视角识别完成 | `{ perspective, confidence, reason }` |
| gaps_identified | 缺失信息分析完成 | `{ gaps: [{category, description, importance}], suggestions }` |
| translation_start | 开始翻译 | `{ direction }` |
| content_delta | 翻译内容增量 | `{ delta }` |
| message_done | 翻译完成 | `{ translation_id }` |
| error | 错误信息 | `{ message }` |

**示例响应流**：
```
event: perspective_detected
data: {"perspective": "pm", "confidence": 0.92, "reason": "文本关注用户体验和业务价值"}

event: gaps_identified
data: {"gaps": [{"category": "用户场景", "description": "未说明目标用户群体", "importance": "high"}], "suggestions": ["明确目标用户画像"]}

event: translation_start
data: {"direction": "pm_to_dev"}

event: content_delta
data: {"delta": "## 功能需求\n"}

event: content_delta
data: {"delta": "实现智能推荐系统..."}

event: message_done
data: {"translation_id": "550e8400-e29b-41d4-a716-446655440000"}
```

### POST /api/translate

同步翻译接口，等待完成后返回完整结果。

**请求体**：同流式接口

**响应**：
```json
{
  "translated_content": "## 功能需求\n...",
  "original_content": "需要一个智能推荐功能...",
  "direction": "pm_to_dev",
  "detected_perspective": "pm",
  "gaps": [
    {
      "category": "用户场景",
      "description": "未说明目标用户群体",
      "importance": "high"
    }
  ],
  "suggestions": ["明确目标用户画像"]
}
```

### GET /api/translate/history

获取翻译历史列表。

**查询参数**：
- `page`：页码（默认 1）
- `size`：每页数量（默认 20）

**响应**：
```json
{
  "items": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "content": "原始内容...",
      "translated_content": "翻译结果...",
      "direction": "pm_to_dev",
      "detected_perspective": "pm",
      "gaps": [...],
      "created_at": "2024-01-15T10:30:00Z"
    }
  ],
  "total": 100,
  "page": 1,
  "size": 20
}
```

### GET /api/translate/{id}

获取单条翻译详情。

**响应**：
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "content": "原始内容...",
  "translated_content": "翻译结果...",
  "direction": "pm_to_dev",
  "detected_perspective": "pm",
  "gaps": [...],
  "created_at": "2024-01-15T10:30:00Z"
}
```

---

## 智能 Agent 工作流

BridgeTalk 采用 LangGraph 构建三阶段智能工作流：

```
用户输入
    │
    ▼
┌─────────────────────────────────────┐
│  阶段 1：视角识别 (detect_perspective)  │
│  ─────────────────────────────────  │
│  • 分析文本特征                         │
│  • 判断产品视角 or 开发视角              │
│  • 输出置信度和理由                      │
└─────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────┐
│  阶段 2：缺失分析 (analyze_gaps)         │
│  ─────────────────────────────────  │
│  • 根据视角选择检查点                    │
│  • 识别缺失的关键信息                    │
│  • 生成补充建议                         │
└─────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────┐
│  阶段 3：执行翻译 (translate)            │
│  ─────────────────────────────────  │
│  • 选择对应翻译提示词                    │
│  • 融入缺失信息上下文                    │
│  • 流式生成翻译结果                      │
└─────────────────────────────────────┘
    │
    ▼
翻译结果 + 缺失分析 + 补充建议
```

### 翻译策略

**PM → DEV 翻译**（产品需求 → 技术方案）：
- 结构化输出：将模糊需求转化为清晰功能点
- 技术可行性：用技术术语描述实现
- 边界明确：明确功能边界和异常处理
- 可衡量：将体验指标转化为技术指标

**DEV → PM 翻译**（技术方案 → 业务语言）：
- 去技术化：用业务场景代替技术术语
- 可视化：用流程图思维辅助说明
- 结果导向：强调对用户和业务的影响
- 风险可视：用业务影响描述技术风险

---

## 项目结构

```
bridgetalk/
├── apps/
│   ├── backend/
│   │   ├── src/
│   │   │   ├── main.py              # 应用入口
│   │   │   ├── config.py            # 配置管理
│   │   │   ├── container.py         # 依赖注入容器
│   │   │   ├── core/                # 核心模块
│   │   │   │   ├── api/             # API 响应格式
│   │   │   │   ├── cache/           # Redis 缓存服务
│   │   │   │   ├── context/         # 请求上下文
│   │   │   │   ├── database/        # 数据库连接/迁移
│   │   │   │   ├── logging/         # 日志配置
│   │   │   │   └── sse/             # SSE 事件处理
│   │   │   ├── domain/translate/    # 翻译业务域
│   │   │   │   ├── agent/           # LangGraph Agent
│   │   │   │   │   ├── translate_agent.py  # Agent 实现
│   │   │   │   │   └── tools.py     # 工具函数
│   │   │   │   ├── api/routes.py    # API 路由
│   │   │   │   ├── graph/           # 检查点管理
│   │   │   │   ├── model/           # 数据模型
│   │   │   │   ├── prompts/         # 提示词
│   │   │   │   │   ├── pm_to_dev.py # PM→DEV 提示词
│   │   │   │   │   └── dev_to_pm.py # DEV→PM 提示词
│   │   │   │   ├── repository/      # 仓储层
│   │   │   │   ├── schema/          # 请求/响应模型
│   │   │   │   └── service/         # 服务层
│   │   │   └── llm/                 # LLM 适配器
│   │   │       └── dashscope.py     # DashScope 适配
│   │   ├── alembic/                 # 数据库迁移
│   │   ├── config.yaml              # 配置文件
│   │   └── pyproject.toml           # Python 依赖
│   │
│   └── frontend/
│       ├── src/
│       │   ├── App.tsx              # 根组件
│       │   ├── api/                 # API 类型定义
│       │   ├── components/          # React 组件
│       │   │   ├── layout/          # 布局组件
│       │   │   ├── translate/       # 翻译相关组件
│       │   │   └── ui/              # UI 基础组件
│       │   ├── hooks/               # 自定义 Hook
│       │   │   └── useTranslate.ts  # 翻译状态管理
│       │   ├── pages/               # 页面组件
│       │   │   ├── HomePage.tsx     # 首页
│       │   │   ├── ChatPage.tsx     # 聊天页
│       │   │   └── HistoryPage.tsx  # 历史页
│       │   └── router/              # 路由配置
│       ├── package.json
│       └── vite.config.ts
│
├── docker-compose.yml               # Docker 服务编排
└── .claude/                         # Claude Code 配置
    └── rules/                       # 开发规范
```

---

## 前端页面

### 首页 (/)

项目介绍页面，展示核心功能特性：
- 项目价值主张
- 六大功能特性卡片
- 快速开始入口

### 聊天页 (/chat)

核心交互页面，支持三种状态：

**初始状态**：
- 大标题引导输入
- 文本输入框
- 快速开始按钮

**翻译进行中**：
- 左侧（3/4）：翻译结果区域，Markdown 实时渲染
- 右侧（1/4）：分析面板，展示视角识别和缺失信息

**翻译完成**：
- 完整翻译结果
- 底部输入栏支持继续对话

### 历史页 (/history)

翻译记录管理：
- 分页展示历史记录
- 视角标签颜色区分
- 内容摘要预览
- 点击查看详情

---

## 数据模型

### Translation 表

| 字段 | 类型 | 说明 |
|------|------|------|
| id | UUID | 主键 |
| content | TEXT | 原始输入内容 |
| translated_content | TEXT | 翻译结果 |
| direction | VARCHAR(20) | 翻译方向：pm_to_dev / dev_to_pm |
| detected_perspective | VARCHAR(20) | 识别视角：pm / dev / unknown |
| gaps_identified | JSONB | 缺失信息和建议 |
| created_at | TIMESTAMP | 创建时间 |

**索引**：
- `ix_translations_created_at`：按创建时间排序
- `ix_translations_direction`：按翻译方向筛选

---

## 开发指南

### 代码检查

```bash
# 后端
cd apps/backend
ruff format src/              # 格式化
ruff check --fix src/         # Lint 检查
pyright src/                  # 类型检查

# 前端
pnpm --filter @bridgetalk/frontend lint
pnpm --filter @bridgetalk/frontend exec tsc --noEmit
```

### 数据库迁移

```bash
cd apps/backend

# 生成迁移文件
alembic revision --autogenerate -m "描述"

# 执行迁移
alembic upgrade head

# 回滚
alembic downgrade -1
```

### 目录规范

- **后端**：遵循 DDD 分层架构（API → Service → Repository）
- **前端**：按功能划分组件目录

---

## 许可证

MIT
