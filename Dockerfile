# 构建阶段
FROM python:3.13-slim AS builder

WORKDIR /app

# 安装构建依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 创建虚拟环境
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# 复制项目文件并安装依赖
COPY pyproject.toml README.md ./
COPY app ./app
RUN pip install --no-cache-dir .

# 运行阶段
FROM python:3.13-slim AS runtime

WORKDIR /app

# 安装运行时依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 从构建阶段复制虚拟环境
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# 创建非 root 用户
RUN groupadd -r akgate && useradd -r -g akgate akgate

# 复制应用代码和配置
COPY --chown=akgate:akgate app ./app
COPY --chown=akgate:akgate gunicorn.conf.py ./

# 切换到非 root 用户
USER akgate

# 暴露端口
EXPOSE 5000

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

# 设置环境变量
ENV FLASK_APP=app \
    FLASK_ENV=production \
    PYTHONUNBUFFERED=1

# 使用 gunicorn 启动（生产环境）
CMD ["gunicorn", "-c", "gunicorn.conf.py", "app:create_app()"]
