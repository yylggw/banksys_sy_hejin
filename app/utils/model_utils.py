"""
模型训练与预测工具。

提供：
- 基于 scikit-learn Pipeline 的离线训练（OneHotEncoder + StandardScaler + RandomForestClassifier）
- 模型序列化与加载（joblib）
- 在线预测（单样本 → 概率）
"""

from pathlib import Path
from typing import Any

import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from app.utils.data_loader import (
    CATEGORICAL_COLS,
    DEFAULT_TEST_PATH,
    DEFAULT_TRAIN_PATH,
    NUMERICAL_COLS,
    TARGET_COL,
    load_data,
)

# 模型文件路径
_PROJECT_ROOT = Path(__file__).resolve().parents[2]
MODEL_DIR = _PROJECT_ROOT / "models"
MODEL_PATH = MODEL_DIR / "model.joblib"

# 训练参数
RANDOM_STATE = 42
TEST_SIZE = 0.2
N_ESTIMATORS = 200
MAX_DEPTH = 12
MIN_SAMPLES_LEAF = 5


def _build_pipeline() -> Pipeline:
    """构建完整的训练 Pipeline。

    Returns:
        含预处理（编码 + 标准化）和分类器的 Pipeline。
    """
    categorical_cols = [c for c in CATEGORICAL_COLS]
    numerical_cols = [c for c in NUMERICAL_COLS]

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", StandardScaler(), numerical_cols),
            (
                "cat",
                OneHotEncoder(handle_unknown="ignore", sparse_output=False),
                categorical_cols,
            ),
        ],
    )

    pipeline = Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            (
                "classifier",
                RandomForestClassifier(
                    n_estimators=N_ESTIMATORS,
                    max_depth=MAX_DEPTH,
                    min_samples_leaf=MIN_SAMPLES_LEAF,
                    random_state=RANDOM_STATE,
                    class_weight="balanced",
                    n_jobs=-1,
                ),
            ),
        ],
    )
    return pipeline


def train(train_path: str | Path = DEFAULT_TRAIN_PATH) -> dict[str, Any]:
    """使用训练数据训练模型并评估。

    Args:
        train_path: 训练 CSV 路径。

    Returns:
        包含指标和模型路径的字典。
    """
    df = load_data(train_path)

    X = df[CATEGORICAL_COLS + NUMERICAL_COLS]
    y = (df[TARGET_COL] == "yes").astype(int)

    X_train, X_val, y_train, y_val = train_test_split(
        X,
        y,
        test_size=TEST_SIZE,
        random_state=RANDOM_STATE,
        stratify=y,
    )

    pipeline = _build_pipeline()
    pipeline.fit(X_train, y_train)

    # 验证集评估
    y_pred_proba = pipeline.predict_proba(X_val)[:, 1]
    auc = roc_auc_score(y_val, y_pred_proba)

    # 训练集评估（仅供参考）
    y_train_proba = pipeline.predict_proba(X_train)[:, 1]
    train_auc = roc_auc_score(y_train, y_train_proba)

    # 保存模型
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(pipeline, MODEL_PATH)

    return {
        "auc": round(auc, 4),
        "train_auc": round(train_auc, 4),
        "model_path": str(MODEL_PATH),
        "n_train": len(X_train),
        "n_val": len(X_val),
        "n_features": X.shape[1],
    }


def load_model(path: str | Path = MODEL_PATH) -> Pipeline | None:
    """加载已训练的模型。

    Args:
        path: 模型文件路径。

    Returns:
        加载的 Pipeline，如果模型不存在则返回 None。
    """
    model_path = Path(path)
    if not model_path.exists():
        return None
    return joblib.load(model_path)


def predict(
    features: pd.DataFrame,
    model: Pipeline | None = None,
) -> dict[str, Any]:
    """对单条样本进行预测。

    Args:
        features: 包含所有特征的单行 DataFrame。
        model: 已训练的 Pipeline；如果为 None 则自动加载。

    Returns:
        包含预测结果和概率的字典。
    """
    if model is None:
        model = load_model()
        if model is None:
            return {"error": "模型未训练，请先训练"}

    proba = model.predict_proba(features)[0]
    prediction = int(proba[1] >= 0.5)

    return {
        "prediction": "yes" if prediction == 1 else "no",
        "probability_subscribe": round(float(proba[1]), 4),
        "probability_not_subscribe": round(float(proba[0]), 4),
    }


def test_model_on_test_set(
    test_path: str | Path = DEFAULT_TEST_PATH,
    model: Pipeline | None = None,
) -> dict[str, Any]:
    """在测试集上评估模型。

    Args:
        test_path: 测试 CSV 路径。
        model: 已训练的 Pipeline；如果为 None 则自动加载。

    Returns:
        测试集 AUC 和其他指标。
    """
    df = load_data(test_path)

    X_test = df[CATEGORICAL_COLS + NUMERICAL_COLS]
    y_test = (df[TARGET_COL] == "yes").astype(int)

    if model is None:
        model = load_model()
        if model is None:
            return {"error": "模型未训练，请先训练"}

    y_pred_proba = model.predict_proba(X_test)[:, 1]
    auc = roc_auc_score(y_test, y_pred_proba)

    return {
        "test_auc": round(auc, 4),
        "n_test": len(X_test),
    }


if __name__ == "__main__":
    import json
    import sys

    print(">> 开始训练模型...")
    metrics = train()
    print(f">> 训练完成: {json.dumps(metrics, indent=2, ensure_ascii=False)}")

    # 尝试测试集评估（测试集可能不含标签列）
    try:
        test_results = test_model_on_test_set()
        print(
            f">> 测试集评估: {json.dumps(test_results, indent=2, ensure_ascii=False)}"
        )
    except ValueError as e:
        print(f">> 测试集跳过（可能无标签列）: {e}")

    sys.exit(0)
