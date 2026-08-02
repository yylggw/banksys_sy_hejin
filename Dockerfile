ARG PYTHON_VERSION=3.11

FROM python:${PYTHON_VERSION}-slim

ARG PIP_INDEX_URL=https://pypi.org/simple

WORKDIR /app

# 安装系统依赖（curl for healthcheck）
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 安装 Python 生产依赖（使用镜像源加速，默认 Tsinghua 镜像在国内服务器更快）
COPY requirements.txt .
RUN pip install --no-cache-dir --timeout 300 -i "${PIP_INDEX_URL}" -r requirements.txt

# 复制应用代码（run.py 已合并到 app/main.py 中）
COPY app/ app/

EXPOSE 8888 8889

HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
  CMD curl -fsS http://localhost:8889/health || exit 1

# 直接 streamlit 运行（健康检查由 app/main.py 后台线程处理）
CMD ["streamlit", "run", "app/main.py", "--server.port", "8888", "--server.address", "0.0.0.0", "--server.headless", "true"]