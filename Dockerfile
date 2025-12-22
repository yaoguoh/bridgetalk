# ============================================================
# BridgeTalk Dockerfile
# 多阶段构建：前端 + 后端一体部署
# ============================================================

# ============ 阶段 1: 构建前端 ============
FROM node:20-slim AS frontend-builder

WORKDIR /app/frontend

# 安装 pnpm
RUN corepack enable && corepack prepare pnpm@latest --activate

# 复制依赖文件
COPY apps/frontend/package.json apps/frontend/pnpm-lock.yaml* ./

# 安装依赖
RUN pnpm install --frozen-lockfile || pnpm install

# 复制源代码
COPY apps/frontend/ ./

# 构建前端
RUN pnpm build

# ============ 阶段 2: 最终镜像 ============
FROM python:3.12-slim

# 设置时区和环境变量
ENV TZ=Asia/Shanghai
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    tzdata \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 复制后端代码
COPY apps/backend/ ./

# 安装 Python 依赖
RUN pip install --no-cache-dir -e .

# 从前端构建阶段复制静态文件
COPY --from=frontend-builder /app/frontend/dist /app/static

# 暴露端口
EXPOSE 8000

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# 启动命令
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
