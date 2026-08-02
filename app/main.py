"""
Streamlit 应用主入口。

提供多页面导航:
- 1_数据分析.py: 交互式数据看板
- 2_在线预测.py: 在线认购预测
"""

import streamlit as st

# 必须在任何其他 streamlit 命令之前设置
st.set_page_config(
    page_title="银行营销预测系统",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded",
)


def main() -> None:
    """应用主入口，渲染侧边栏导航."""
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
