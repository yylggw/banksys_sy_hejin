"""Tests for app/utils/data_loader.py."""

from pathlib import Path

import pandas as pd
import pytest

from app.utils.data_loader import (
    CATEGORICAL_COLS,
    DEFAULT_TRAIN_PATH,
    NUMERICAL_COLS,
    TARGET_COL,
    _validate_columns,
    get_basic_info,
    get_numerical_summary,
    get_subscribe_rate_by,
    get_target_distribution,
    load_data,
)

# ---- Fixtures ----


@pytest.fixture
def sample_df() -> pd.DataFrame:
    """创建一个小型样本 DataFrame 用于测试。"""
    return pd.DataFrame(
        {
            "id": [1, 2, 3],
            "age": [30, 45, 25],
            "job": ["admin.", "technician", "blue-collar"],
            "marital": ["married", "single", "divorced"],
            "education": ["university.degree", "high.school", "basic.9y"],
            "default": ["no", "unknown", "no"],
            "housing": ["yes", "no", "yes"],
            "loan": ["no", "yes", "no"],
            "contact": ["cellular", "telephone", "cellular"],
            "month": ["may", "jun", "jul"],
            "day_of_week": ["mon", "tue", "wed"],
            "duration": [120, 300, 50],
            "campaign": [1, 3, 1],
            "pdays": [999, 0, 999],
            "previous": [0, 1, 0],
            "poutcome": ["nonexistent", "failure", "nonexistent"],
            "emp_var_rate": [1.4, -1.8, 1.1],
            "cons_price_index": [93.5, 94.0, 92.8],
            "cons_conf_index": [-36.4, -42.0, -38.5],
            "lending_rate3m": [2.5, 3.0, 2.8],
            "nr_employed": [5099.0, 4975.0, 5100.0],
            TARGET_COL: ["no", "yes", "no"],
        }
    )


# ---- Tests ----


def test_load_data_file_not_found():
    """给定不存在的路径，应当抛出 FileNotFoundError。"""
    with pytest.raises(FileNotFoundError):
        load_data(Path("/nonexistent/path.csv"))


def test_load_data_missing_required_column(tmp_path: Path):
    """给定缺少必要列的 CSV，应当抛出 ValueError。"""
    bad_csv = tmp_path / "bad.csv"
    bad_csv.write_text("a,b,c\n1,2,3\n")
    with pytest.raises(ValueError, match="缺少必要列"):
        load_data(bad_csv)


def test_validate_columns_ok(sample_df: pd.DataFrame):
    """给定包含必要列的 DataFrame，不抛出异常。"""
    # 不应抛出
    _validate_columns(sample_df)


def test_validate_columns_missing():
    """给定缺少 subscribe 列的 DataFrame，应当抛出 ValueError。"""
    bad = pd.DataFrame({"a": [1], "b": [2]})
    with pytest.raises(ValueError, match="缺少必要列"):
        _validate_columns(bad)


def test_get_basic_info(sample_df: pd.DataFrame):
    """get_basic_info 应正确返回元数据。"""
    info = get_basic_info(sample_df)
    assert info["total_rows"] == 3
    assert info["total_cols"] == 22
    assert info["has_target"] is True
    assert "age" in info["num_cols"]
    assert "job" in info["cat_cols"]


def test_get_target_distribution(sample_df: pd.DataFrame):
    """get_target_distribution 应返回正确的计数。"""
    dist = get_target_distribution(sample_df)
    assert dist["no"] == 2
    assert dist["yes"] == 1


def test_get_subscribe_rate_by(sample_df: pd.DataFrame):
    """get_subscribe_rate_by 应按组计算认购率。"""
    rate_df = get_subscribe_rate_by(sample_df, "job")
    assert "rate" in rate_df.columns
    assert "subscribed" in rate_df.columns
    assert "total" in rate_df.columns
    # 只一个 admin. 样本且 subscribe=no -> rate=0
    admin_row = rate_df[rate_df["job"] == "admin."]
    assert admin_row["rate"].iloc[0] == 0.0
    # 一个 technician 样本且 subscribe=yes -> rate=100
    tech_row = rate_df[rate_df["job"] == "technician"]
    assert tech_row["rate"].iloc[0] == 100.0


def test_get_numerical_summary(sample_df: pd.DataFrame):
    """get_numerical_summary 应返回数值列的 describe 摘要。"""
    summary = get_numerical_summary(sample_df)
    assert "age" in summary.index
    assert "duration" in summary.index
    assert "mean" in summary.columns


def test_column_constants():
    """列常量应包含关键字段。"""
    assert "job" in CATEGORICAL_COLS
    assert "age" in NUMERICAL_COLS
    assert TARGET_COL == "subscribe"
    assert DEFAULT_TRAIN_PATH.name == "train.csv"
