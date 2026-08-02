"""
应用入口: 启动健康检查 HTTP 服务 + Streamlit 应用。
"""

import subprocess
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer


class HealthHandler(BaseHTTPRequestHandler):
    """健康检查端点, 返回 {"status": "ok"}"""

    def do_GET(self) -> None:
        if self.path == "/health":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(b'{"status": "ok"}')
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, *args) -> None:
        """静默日志, 不污染 stdout"""


def _start_health_server() -> None:
    """在 8889 端口启动健康检查服务(非阻塞)。"""
    server = HTTPServer(("0.0.0.0", 8889), HealthHandler)
    server.serve_forever()


def main() -> None:
    # 后台线程: 健康检查服务
    t = threading.Thread(target=_start_health_server, daemon=True)
    t.start()

    # 前台: Streamlit 应用
    subprocess.run(
        [
            "streamlit",
            "run",
            "app/main.py",
            "--server.port",
            "8888",
            "--server.address",
            "0.0.0.0",
            "--server.headless",
            "true",
        ],
        check=True,
    )


if __name__ == "__main__":
    main()
