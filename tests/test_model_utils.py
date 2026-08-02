"""Tests for app/utils/model_utils.py."""

from pathlib import Path

import pandas as pd
import pytest
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline

from app.utils.model_utils import (
    _build_pipeline,
    load_model,
    predict,
)

# ---- Fixtures ----


@pytest.fixture
def sample_df() -> pd.DataFrame:
    """Create a small sample DataFrame for testing."""
    # 10 rows, 5 no + 5 yes, so stratified split works (each class >= 2)
    data = {
        "id": list(range(1, 11)),
        "age": [30, 45, 25, 35, 50, 28, 55, 32, 40, 22],
        "job": [
            "admin.",
            "technician",
            "blue-collar",
            "management",
            "retired",
            "admin.",
            "services",
            "student",
            "technician",
            "blue-collar",
        ],
        "marital": [
            "married",
            "single",
            "divorced",
            "married",
            "married",
            "single",
            "married",
            "single",
            "divorced",
            "single",
        ],
        "education": [
            "university.degree",
            "high.school",
            "basic.9y",
            "university.degree",
            "basic.4y",
            "professional.course",
            "high.school",
            "basic.6y",
            "university.degree",
            "basic.9y",
        ],
        "default": ["no", "unknown", "no", "no", "no", "no", "no", "no", "no", "no"],
        "housing": ["yes", "no", "yes", "yes", "no", "yes", "yes", "no", "no", "yes"],
        "loan": ["no", "yes", "no", "no", "no", "yes", "no", "no", "yes", "yes"],
        "contact": [
            "cellular",
            "telephone",
            "cellular",
            "cellular",
            "telephone",
            "cellular",
            "cellular",
            "telephone",
            "cellular",
            "telephone",
        ],
        "month": ["may", "jun", "jul", "may", "aug", "apr", "may", "jun", "jul", "aug"],
        "day_of_week": [
            "mon",
            "tue",
            "wed",
            "thu",
            "fri",
            "mon",
            "tue",
            "wed",
            "thu",
            "fri",
        ],
        "duration": [120, 300, 50, 200, 400, 80, 500, 30, 250, 60],
        "campaign": [1, 3, 1, 2, 4, 2, 1, 5, 2, 3],
        "pdays": [999, 0, 999, 999, 0, 999, 10, 999, 999, 999],
        "previous": [0, 1, 0, 0, 2, 0, 1, 0, 0, 0],
        "poutcome": [
            "nonexistent",
            "failure",
            "nonexistent",
            "nonexistent",
            "success",
            "nonexistent",
            "failure",
            "nonexistent",
            "nonexistent",
            "nonexistent",
        ],
        "emp_var_rate": [1.4, -1.8, 1.1, -0.5, 0.2, 1.4, -3.0, 1.1, -0.5, 1.1],
        "cons_price_index": [
            93.5,
            94.0,
            92.8,
            93.0,
            94.5,
            93.5,
            92.0,
            92.8,
            93.0,
            92.8,
        ],
        "cons_conf_index": [
            -36.4,
            -42.0,
            -38.5,
            -40.0,
            -35.0,
            -36.4,
            -50.0,
            -38.5,
            -40.0,
            -38.5,
        ],
        "lending_rate3m": [2.5, 3.0, 2.8, 3.2, 2.0, 2.5, 4.0, 2.8, 3.2, 2.8],
        "nr_employed": [
            5099.0,
            4975.0,
            5100.0,
            5050.0,
            5010.0,
            5099.0,
            4950.0,
            5100.0,
            5050.0,
            5100.0,
        ],
        "subscribe": ["no", "yes", "no", "no", "yes", "yes", "no", "yes", "no", "yes"],
    }
    return pd.DataFrame(data)


@pytest.fixture
def csv_with_sample(tmp_path: Path, sample_df: pd.DataFrame) -> Path:
    """Write sample data to a temporary CSV file."""
    path = tmp_path / "train.csv"
    sample_df.to_csv(path, index=False)
    return path


# ---- Tests ----


class TestPipeline:
    def test_build_pipeline(self):
        pipeline = _build_pipeline()
        assert isinstance(pipeline, Pipeline)
        assert "preprocessor" in pipeline.named_steps
        assert "classifier" in pipeline.named_steps
        assert isinstance(pipeline.named_steps["classifier"], RandomForestClassifier)


class TestTraining:
    def test_train_and_predict(self, csv_with_sample: Path, tmp_path: Path):
        import app.utils.model_utils as mu

        original_path = mu.MODEL_PATH
        model_path = tmp_path / "model.joblib"
        mu.MODEL_PATH = model_path

        try:
            result = mu.train(csv_with_sample)
            assert "auc" in result
            assert "n_train" in result
            assert "n_val" in result
            assert result["n_train"] > 0
            assert result["n_val"] > 0
            assert model_path.exists()

            model = mu.load_model(model_path)
            assert model is not None

            sample = pd.DataFrame(
                [
                    {
                        "age": 35,
                        "job": "admin.",
                        "marital": "married",
                        "education": "university.degree",
                        "default": "no",
                        "housing": "yes",
                        "loan": "no",
                        "contact": "cellular",
                        "month": "may",
                        "day_of_week": "mon",
                        "duration": 200,
                        "campaign": 2,
                        "pdays": 999,
                        "previous": 0,
                        "poutcome": "nonexistent",
                        "emp_var_rate": 1.4,
                        "cons_price_index": 93.5,
                        "cons_conf_index": -36.4,
                        "lending_rate3m": 2.5,
                        "nr_employed": 5099.0,
                    }
                ]
            )

            pred = predict(sample, model)
            assert "prediction" in pred
            assert pred["prediction"] in ("yes", "no")
            assert "probability_subscribe" in pred
            assert 0 <= pred["probability_subscribe"] <= 1
        finally:
            mu.MODEL_PATH = original_path


class TestModelLoad:
    def test_load_model_not_found(self, tmp_path: Path):
        model = load_model(tmp_path / "nonexistent.joblib")
        assert model is None


class TestPredictWithoutModel:
    def test_predict_without_model(self, monkeypatch: pytest.MonkeyPatch):
        import app.utils.model_utils as mu

        monkeypatch.setattr(mu, "load_model", lambda path=None: None)

        sample = pd.DataFrame(
            [
                {
                    "age": 30,
                    "job": "admin.",
                    "marital": "no",
                    "education": "no",
                    "default": "no",
                    "housing": "no",
                    "loan": "no",
                    "contact": "no",
                    "month": "no",
                    "day_of_week": "no",
                    "duration": 100,
                    "campaign": 1,
                    "pdays": 999,
                    "previous": 0,
                    "poutcome": "nonexistent",
                    "emp_var_rate": 1.1,
                    "cons_price_index": 93.0,
                    "cons_conf_index": -36.0,
                    "lending_rate3m": 2.5,
                    "nr_employed": 5000.0,
                }
            ]
        )

        result = mu.predict(sample, model=None)
        assert "error" in result
        assert "未训练" in result["error"]
