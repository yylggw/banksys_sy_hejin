#!/bin/bash
set -e

APP="banksys_sy_hejin"
IMAGE="${APP}:latest"
PORT_DEFAULT=8888
PORT_MAX=8898

# 检测端口是否被占用（主机进程或 Docker 容器）
port_in_use() {
  ss -ltnH 2>/dev/null | grep -q ":$1 " && return 0
  docker ps --format "{{.Ports}}" 2>/dev/null | grep -q ":$1->" && return 0
  return 1
}

# 在预留区间找空闲端口
PORT=""
for p in $(seq "$PORT_DEFAULT" "$PORT_MAX"); do
  if ! port_in_use "$p"; then
    PORT="$p"
    break
  fi
done
if [ -z "$PORT" ]; then
  echo ">> 预留端口区间 ${PORT_DEFAULT}-${PORT_MAX} 已全部占用，部署中止"
  exit 1
fi
echo ">> 部署到主机端口 $PORT"

# 停删旧容器（幂等）
docker rm -f "$APP" 2>/dev/null || true

# 启动新容器
docker run -d \
  --name "$APP" \
  --restart unless-stopped \
  -p "${PORT}:8888" \
  "${IMAGE}"

# 等待启动并健康检查
sleep 5
curl -fsS "http://localhost:${PORT}/health"
echo ""
echo ">> 部署成功: http://<SSH_HOST>:${PORT}/"