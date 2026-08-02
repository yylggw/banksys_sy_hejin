ARG PYTHON_VERSION=3.11

FROM python:${PYTHON_VERSION}-slim

ARG PIP_INDEX_URL=https://pypi.org/simple

WORKDIR /app

# 安装系统依赖（matplotlib/seaborn 需要）
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 安装 Python 生产依赖
COPY requirements.txt .
RUN pip install --no-cache-dir --timeout 120 -i "${PIP_INDEX_URL}" -r requirements.txt

# 复制应用代码
COPY app/ app/
COPY run.py .

EXPOSE 8888

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD curl -fsS http://localhost:8889/health || exit 1

CMD ["python", "run.py"]