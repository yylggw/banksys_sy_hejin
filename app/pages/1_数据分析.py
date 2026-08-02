# noqa: N999 — Streamlit 需要中文文件名做页面标题
"""
数据分析交互页面。

提供：
- 数据集概览
- 客户画像（年龄、职业、婚姻、教育分布）
- 认购分析（目标分布、各维度认购率）
- 数值特征统计与相关性热力图
"""

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import streamlit as st

from app.utils.data_loader import (
    DEFAULT_TRAIN_PATH,
    NUMERICAL_COLS,
    TARGET_COL,
    get_basic_info,
    get_numerical_summary,
    get_subscribe_rate_by,
    get_target_distribution,
    load_data,
)

# 全局 matplotlib 配置
plt.rcParams["font.sans-serif"] = ["SimHei", "Microsoft YaHei", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False

# 颜色常量
COLOR_PRIMARY = "#1f77b4"
COLOR_SECONDARY = "#ff7f0e"
COLOR_TARGET_YES = "#2ca02c"
COLOR_TARGET_NO = "#d62728"


@st.cache_data
def _load_train_data() -> pd.DataFrame:
    """加载训练数据（带缓存）。"""
    return load_data(DEFAULT_TRAIN_PATH)


def _render_overview(df: pd.DataFrame) -> None:
    """数据集概览板块。"""
    st.subheader("📋 数据集概览")
    info = get_basic_info(df)

    col1, col2, col3 = st.columns(3)
    col1.metric("总记录数", f"{info['total_rows']:,}")
    col2.metric("特征列数", info["total_cols"] - 2)  # 去掉 id 和 target
    col3.metric("目标列", "subscribe (yes/no)")

    with st.expander("📄 查看全部列名"):
        st.write(info["columns"])

    st.caption("前 5 行预览")
    st.dataframe(df.head(), use_container_width=True)


def _render_customer_profile(df: pd.DataFrame) -> None:
    """客户画像板块：年龄分布 + 分类特征分布。"""
    st.subheader("👤 客户画像")

    # 年龄分布
    st.markdown("**年龄分布**")
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.hist(df["age"].dropna(), bins=30, color=COLOR_PRIMARY, edgecolor="white")
    ax.set_xlabel("年龄")
    ax.set_ylabel("人数")
    ax.axvline(
        df["age"].median(),
        color=COLOR_SECONDARY,
        linestyle="--",
        label=f"中位数 {df['age'].median():.0f}",
    )
    ax.legend()
    st.pyplot(fig)
    plt.close(fig)

    # 分类特征分布（职业、婚姻、教育）
    plot_cols = [c for c in ["job", "marital", "education"] if c in df.columns]
    if plot_cols:
        tabs = st.tabs(
            [
                {"job": "职业", "marital": "婚姻状况", "education": "教育水平"}.get(
                    c, c
                )
                for c in plot_cols
            ]
        )
        for tab, col in zip(tabs, plot_cols):
            with tab:
                freq = df[col].value_counts()
                fig, ax = plt.subplots(figsize=(10, 4))
                bars = ax.barh(freq.index, freq.values, color=COLOR_PRIMARY)
                for bar, v in zip(bars, freq.values):
                    ax.text(
                        bar.get_width() + 10,
                        bar.get_y() + bar.get_height() / 2,
                        str(v),
                        va="center",
                        fontsize=9,
                    )
                ax.set_xlabel("人数")
                st.pyplot(fig)
                plt.close(fig)


def _render_subscribe_analysis(df: pd.DataFrame) -> None:
    """认购分析板块。"""
    st.subheader("🎯 认购分析")

    # 目标分布饼图
    col_left, col_right = st.columns([1, 2])
    with col_left:
        dist = get_target_distribution(df)
        fig, ax = plt.subplots(figsize=(5, 5))
        colors = [COLOR_TARGET_NO, COLOR_TARGET_YES]
        _wedges, _texts, _autotexts = ax.pie(
            dist.values,
            labels=dist.index,
            autopct="%1.1f%%",
            colors=colors,
            startangle=90,
            explode=(0, 0.05),
        )
        ax.set_title("认购分布")
        st.pyplot(fig)
        plt.close(fig)

    with col_right:
        total = len(df)
        subscribed = (df[TARGET_COL] == "yes").sum()
        st.metric(
            "认购人数", f"{subscribed:,}", delta=f"{subscribed / total * 100:.1f}%"
        )
        st.metric("未认购人数", f"{total - subscribed:,}")
        st.metric("总样本", f"{total:,}")

    # 各维度认购率对比
    st.markdown("**各维度认购率**")
    rate_cols = [
        c
        for c in ["job", "education", "marital", "housing", "loan", "contact"]
        if c in df.columns
    ]
    if rate_cols:
        tabs = st.tabs(
            [
                {
                    "job": "职业",
                    "education": "教育",
                    "marital": "婚姻",
                    "housing": "房贷",
                    "loan": "个人贷款",
                    "contact": "联系方式",
                }.get(c, c)
                for c in rate_cols
            ]
        )
        for tab, col in zip(tabs, rate_cols):
            with tab:
                rate_df = get_subscribe_rate_by(df, col)
                fig, ax = plt.subplots(figsize=(10, 5))
                bars = ax.barh(rate_df[col], rate_df["rate"], color=COLOR_PRIMARY)
                for bar, v in zip(bars, rate_df["rate"]):
                    ax.text(
                        bar.get_width() + 0.3,
                        bar.get_y() + bar.get_height() / 2,
                        f"{v:.1f}%",
                        va="center",
                        fontsize=9,
                    )
                ax.set_xlabel("认购率 (%)")
                ax.set_xlim(0, rate_df["rate"].max() * 1.3)
                st.pyplot(fig)
                plt.close(fig)

                with st.expander("📊 查看详细数据"):
                    st.dataframe(rate_df, use_container_width=True)


def _render_numerical_analysis(df: pd.DataFrame) -> None:
    """数值特征分析板块。"""
    st.subheader("📈 数值特征分析")

    num_cols = [c for c in NUMERICAL_COLS if c in df.columns]
    if not num_cols:
        st.info("数据中无可用的数值特征。")
        return

    # 统计摘要表
    st.markdown("**描述性统计**")
    summary = get_numerical_summary(df)
    st.dataframe(summary.style.format("{:.2f}"), use_container_width=True)

    # 相关性热力图
    st.markdown("**特征相关性热力图**")
    corr = df[num_cols].corr()
    fig, ax = plt.subplots(figsize=(12, 8))
    sns.heatmap(
        corr,
        annot=True,
        fmt=".2f",
        cmap="RdBu_r",
        center=0,
        square=True,
        linewidths=0.5,
        ax=ax,
    )
    ax.set_title("数值特征 Pearson 相关系数")
    st.pyplot(fig)
    plt.close(fig)


def main() -> None:
    """数据分析页主入口。"""
    st.title("📊 数据分析")
    st.markdown("基于银行营销数据集的多维度交互式探索。")

    try:
        df = _load_train_data()
    except FileNotFoundError:
        st.error("❌ 未找到数据文件。请确认 `data/train.csv` 存在于项目目录中。")
        st.info("数据文件不进入 Git，需要手动放置。")
        return
    except ValueError as e:
        st.error(f"❌ 数据格式错误: {e}")
        return

    # 四个功能板块
    _render_overview(df)
    st.markdown("---")

    _render_customer_profile(df)
    st.markdown("---")

    _render_subscribe_analysis(df)
    st.markdown("---")

    _render_numerical_analysis(df)

    st.caption("数据来源: data/train.csv")


if __name__ == "__main__":
    main()
