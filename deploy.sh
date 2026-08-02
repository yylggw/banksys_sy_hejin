#!/bin/bash
set -e

APP="banksys_sy_hejin"
IMAGE="${APP}:latest"
PORT_DEFAULT=8888
PORT_MAX=8908

# 检测端口是否被占用（主机进程或 Docker 容器）
port_in_use() {
  ss -ltnH 2>/dev/null | grep -q ":$1 " && return 0
  docker ps --format "{{.Ports}}" 2>/dev/null | grep -q ":$1->" && return 0
  return 1
}

# 先清理所有同名旧容器（无论端口）
echo ">> 清理旧容器..."
docker rm -f "$APP" 2>/dev/null || true

# 查找空闲端口（扩大区间到 8888-8908）
PORT=""
for p in $(seq "$PORT_DEFAULT" "$PORT_MAX"); do
  if ! port_in_use "$p"; then
    PORT="$p"
    break
  fi
done
if [ -z "$PORT" ]; then
  echo ">> 端口区间 ${PORT_DEFAULT}-${PORT_MAX} 也全部被占用，强制使用 8888..."
  PORT=$PORT_DEFAULT
fi
echo ">> 部署到主机端口 $PORT"

# 在服务器上构建 Docker 镜像（使用国内镜像源加速）
echo ">> 构建 Docker 镜像（使用 Tsinghua 镜像源）..."
docker build \
  --build-arg PIP_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple \
  -t "$IMAGE" \
  /opt/banksys_sy_hejin

# 停删旧容器（幂等，确保同名容器被移除）
docker rm -f "$APP" 2>/dev/null || true

# 启动新容器
echo ">> 启动容器..."
docker run -d \
  --name "$APP" \
  --restart unless-stopped \
  -p "${PORT}:8888" \
  "${IMAGE}"

# 等待启动并健康检查
echo ">> 等待服务启动..."
sleep 10
curl -fsS "http://localhost:${PORT}/health"
echo ""
echo ">> 部署成功: http://<SSH_HOST>:${PORT}/"