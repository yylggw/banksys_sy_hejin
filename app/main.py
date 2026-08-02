"""Streamlit 应用主入口 — 包含健康检查服务。

可直接运行:
  streamlit run app/main.py --server.port 8888

健康检查: http://localhost:8889/health（独立 HTTP 服务）
"""

import sys
from pathlib import Path

# 确保项目根目录在模块搜索路径中，否则 pages 里的 from app.utils... 会报 ModuleNotFoundError
_project_root = Path(__file__).resolve().parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

import streamlit as st

# ===== 健康检查服务（后台线程，端口 8889） =====


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
        pass  # 静默日志


def _start_health_server() -> None:
    """在 8889 端口启动健康检查服务（非阻塞）。"""
    server = HTTPServer(("0.0.0.0", 8889), HealthHandler)
    server.serve_forever()


# 在 Streamlit 完全加载前启动健康检查线程
_health_thread = threading.Thread(target=_start_health_server, daemon=True)
_health_thread.start()


# ===== Streamlit 入口 =====

st.set_page_config(
    page_title="银行营销预测系统",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded",
)


def main() -> None:
    """应用主入口，渲染侧边栏导航。"""
    st.sidebar.title("🏦 银行营销系统")
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 功能导航")
    st.sidebar.markdown("请通过上方页面选择器切换功能")

    st.title("🏦 银行营销预测系统")
    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📊 数据分析")
        st.markdown(
            """
            对银行营销数据进行多维度可视化探索：
            - 客户画像（年龄、职业、教育等分布）
            - 认购率分析
            - 特征相关性热力图
            """
        )

    with col2:
        st.subheader("🤖 在线预测")
        st.markdown(
            """
            通过点选表单输入客户信息，预测是否会认购定期存款：
            - 人口统计信息
            - 金融与联系信息
            - 经济背景指标
            """
        )

    st.markdown("---")
    st.info("👈 请从左侧顶部下拉菜单选择功能页面")


if __name__ == "__main__":
    main()
