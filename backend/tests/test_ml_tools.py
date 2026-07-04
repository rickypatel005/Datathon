import pytest
import pandas as pd
from tools.ml_tools import (
    train_classification_model,
    train_regression_model,
    train_clustering_model,
)

@pytest.fixture
def classification_df():
    return pd.DataFrame({
        "feature1": [1.5, 2.3, 1.1, 4.5, 5.2, 5.0, 1.2, 4.8],
        "feature2": [0.5, 0.3, 0.8, 2.5, 2.2, 2.9, 0.4, 2.1],
        "target": ["A", "A", "A", "B", "B", "B", "A", "B"]
    })

@pytest.fixture
def regression_df():
    return pd.DataFrame({
        "feature1": [1, 2, 3, 4, 5, 6, 7, 8],
        "feature2": [2, 4, 6, 8, 10, 12, 14, 16],
        "target": [3, 6, 9, 12, 15, 18, 21, 24]
    })

def test_train_classification_model(classification_df):
    result = train_classification_model.invoke({
        "df": classification_df,
        "target_column": "target",
        "algorithm": "random_forest"
    })
    
    assert "metrics" in result
    assert "accuracy" in result["metrics"]
    assert "model" in result
    assert result["algorithm"] == "random_forest"

def test_train_regression_model(regression_df):
    result = train_regression_model.invoke({
        "df": regression_df,
        "target_column": "target",
        "algorithm": "linear_regression"
    })
    
    assert "metrics" in result
    assert "rmse" in result["metrics"]
    assert "model" in result
    assert result["algorithm"] == "linear_regression"

def test_train_clustering_model(classification_df):
    result = train_clustering_model.invoke({
        "df": classification_df,
        "algorithm": "kmeans",
        "feature_columns": ["feature1", "feature2"],
        "hyperparameters": {"n_clusters": 2}
    })
    
    assert "metrics" in result
    assert "model" in result
    assert result["metrics"]["n_clusters"] == 2
    assert "labels" in result
