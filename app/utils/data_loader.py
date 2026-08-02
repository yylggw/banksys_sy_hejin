"""
数据加载与预处理工具。

提供从 CSV 文件加载银行营销数据集的函数，
支持 Streamlit 缓存、基本统计摘要与列分类。
"""

from pathlib import Path
from typing import Any

import pandas as pd
import streamlit as st

# 数据列定义（按类型分组）
CATEGORICAL_COLS = [
    "job",
    "marital",
    "education",
    "default",
    "housing",
    "loan",
    "contact",
    "month",
    "day_of_week",
    "poutcome",
]

NUMERICAL_COLS = [
    "age",
    "duration",
    "campaign",
    "pdays",
    "previous",
    "emp_var_rate",
    "cons_price_index",
    "cons_conf_index",
    "lending_rate3m",
    "nr_employed",
]

TARGET_COL = "subscribe"

ALL_FEATURE_COLS = CATEGORICAL_COLS + NUMERICAL_COLS
ALL_COLS = ["id"] + ALL_FEATURE_COLS + [TARGET_COL]

# 项目根目录（向上找 data/）
_PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_TRAIN_PATH = _PROJECT_ROOT / "data" / "train.csv"
DEFAULT_TEST_PATH = _PROJECT_ROOT / "data" / "test.csv"


@st.cache_data(show_spinner="正在加载数据...")
def load_data(path: str | Path = DEFAULT_TRAIN_PATH) -> pd.DataFrame:
    """从 CSV 加载银行营销数据集。

    Args:
        path: CSV 文件路径，默认 data/train.csv。

    Returns:
        包含全部列的 DataFrame。
    """
    df = pd.read_csv(path)
    _validate_columns(df)
    return df


def _validate_columns(df: pd.DataFrame) -> None:
    """校验 DataFrame 是否包含预期的关键列。"""
    required = {TARGET_COL, "age", "job"}
    missing = required - set(df.columns)
    if missing:
        msg = f"数据缺少必要列: {missing}"
        raise ValueError(msg)


def get_basic_info(df: pd.DataFrame) -> dict[str, Any]:
    """返回数据集基本统计信息。"""
    return {
        "total_rows": len(df),
        "total_cols": len(df.columns),
        "columns": list(df.columns),
        "cat_cols": [c for c in CATEGORICAL_COLS if c in df.columns],
        "num_cols": [c for c in NUMERICAL_COLS if c in df.columns],
        "has_target": TARGET_COL in df.columns,
    }


def get_target_distribution(df: pd.DataFrame) -> pd.Series:
    """返回目标变量的分布计数。"""
    return df[TARGET_COL].value_counts()


def get_subscribe_rate_by(df: pd.DataFrame, group_col: str) -> pd.DataFrame:
    """按分组列计算认购率。"""
    grouped = df.groupby(group_col)[TARGET_COL].agg(
        total="count",
        subscribed=lambda x: (x == "yes").sum(),
    )
    grouped["rate"] = (grouped["subscribed"] / grouped["total"] * 100).round(2)
    return grouped.reset_index()


def get_numerical_summary(df: pd.DataFrame) -> pd.DataFrame:
    """返回数值列的统计摘要。"""
    num_cols = [c for c in NUMERICAL_COLS if c in df.columns]
    return df[num_cols].describe().T
