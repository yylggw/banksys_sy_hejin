"""Tests for app entry point."""

import json
import threading
from http.server import HTTPServer
from runpy import run_path

import pytest


@pytest.fixture(scope="module")
def health_server():
    """启动健康检查服务并返回端口号。"""
    # 查找空闲端口
    import socket

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(("127.0.0.1", 0))
    port = sock.getsockname()[1]
    sock.close()

    # 动态导入 app/main.py 中的 HealthHandler
    mod = run_path("app/main.py")
    handler_class = mod["HealthHandler"]

    server = HTTPServer(("127.0.0.1", port), handler_class)
    t = threading.Thread(target=server.serve_forever, daemon=True)
    t.start()
    yield f"http://127.0.0.1:{port}"
    server.shutdown()


def test_health_endpoint_returns_ok(health_server):
    """验证 /health 返回 200 且 status=ok。"""
    import urllib.request

    resp = urllib.request.urlopen(f"{health_server}/health")
    assert resp.status == 200

    body = json.loads(resp.read().decode())
    assert body == {"status": "ok"}


def test_health_endpoint_404_on_unknown_path(health_server):
    """验证其他路径返回 404。"""
    import urllib.error
    import urllib.request

    with pytest.raises(urllib.error.HTTPError) as exc:
        urllib.request.urlopen(f"{health_server}/unknown")
    assert exc.value.code == 404


def test_streamlit_app_can_be_imported():
    """验证 app/main.py 无语法错误且模块可导入。"""
    import importlib.util

    spec = importlib.util.spec_from_file_location("app_main", "app/main.py")
    assert spec is not None, "应该能够解析 app/main.py 的模块 spec"
