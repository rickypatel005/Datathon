"""
Machine Learning tools for model training and evaluation.
"""
import pandas as pd
import numpy as np
import pickle
import os
from typing import Optional, Dict, Any, List, Tuple
from langchain.tools import tool
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor, GradientBoostingClassifier, GradientBoostingRegressor
from sklearn.linear_model import LogisticRegression, LinearRegression, Ridge, Lasso
from sklearn.svm import SVC, SVR
from sklearn.tree import DecisionTreeClassifier, DecisionTreeRegressor
from sklearn.neighbors import KNeighborsClassifier, KNeighborsRegressor
from sklearn.naive_bayes import GaussianNB
from sklearn.neural_network import MLPClassifier, MLPRegressor
from sklearn.cluster import KMeans, DBSCAN, AgglomerativeClustering
from sklearn.mixture import GaussianMixture
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    mean_squared_error, r2_score, silhouette_score,
    classification_report, confusion_matrix
)


def _prepare_features(
    df: pd.DataFrame,
    target_column: Optional[str] = None,
    feature_columns: Optional[List[str]] = None,
) -> Tuple[pd.DataFrame, Optional[pd.Series], List[str]]:
    """Prepare feature matrix and target vector."""
    if feature_columns:
        X = df[feature_columns].copy()
    else:
        exclude = [target_column] if target_column else []
        X = df.drop(columns=exclude, errors="ignore").copy()

    # Drop non-numeric columns that can't be encoded easily
    cat_cols = X.select_dtypes(include=["object", "category"]).columns.tolist()
    encoders = {}
    for col in cat_cols:
        if X[col].nunique() <= 20:  # Only encode low-cardinality
            le = LabelEncoder()
            X[col] = le.fit_transform(X[col].astype(str))
            encoders[col] = le
        else:
            X = X.drop(columns=[col])

    # Fill remaining NaNs
    X = X.fillna(X.median(numeric_only=True))
    feature_names = X.columns.tolist()

    y = None
    if target_column and target_column in df.columns:
        y = df[target_column].copy()
        if y.dtype == "object":
            le = LabelEncoder()
            y = pd.Series(le.fit_transform(y.astype(str)), name=target_column)

    return X, y, feature_names


@tool
def train_classification_model(
    file_path: str,
    target_column: str,
    algorithm: str = "random_forest",
    feature_columns: Optional[List[str]] = None,
    hyperparameters: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Train a classification model and return metrics."""
    from tools.analysis_tools import load_dataset
    df = load_dataset.invoke({"file_path": file_path})
    X, y, features = _prepare_features(df, target_column, feature_columns)
    if y is None:
        return {"error": f"Target column '{target_column}' not found"}

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Scale features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    params = hyperparameters or {}

    if algorithm == "random_forest":
        model = RandomForestClassifier(
            n_estimators=params.get("n_estimators", 100),
            max_depth=params.get("max_depth", None),
            random_state=42,
        )
    elif algorithm == "logistic_regression":
        model = LogisticRegression(max_iter=1000, random_state=42)
    elif algorithm == "svm":
        model = SVC(kernel=params.get("kernel", "rbf"), probability=True, random_state=42)
    elif algorithm == "decision_tree":
        model = DecisionTreeClassifier(max_depth=params.get("max_depth", None), random_state=42)
    elif algorithm == "gradient_boosting":
        model = GradientBoostingClassifier(n_estimators=params.get("n_estimators", 100), learning_rate=params.get("learning_rate", 0.1), random_state=42)
    elif algorithm == "knn":
        model = KNeighborsClassifier(n_neighbors=params.get("n_neighbors", 5))
    elif algorithm == "naive_bayes":
        model = GaussianNB()
    elif algorithm == "mlp":
        model = MLPClassifier(max_iter=1000, random_state=42)
    else:
        model = RandomForestClassifier(n_estimators=100, random_state=42)

    model.fit(X_train_scaled, y_train)
    y_pred = model.predict(X_test_scaled)

    metrics = {
        "accuracy": round(float(accuracy_score(y_test, y_pred)), 4),
        "precision": round(float(precision_score(y_test, y_pred, average="weighted", zero_division=0)), 4),
        "recall": round(float(recall_score(y_test, y_pred, average="weighted", zero_division=0)), 4),
        "f1_score": round(float(f1_score(y_test, y_pred, average="weighted", zero_division=0)), 4),
    }

    # Feature importance
    if hasattr(model, "feature_importances_"):
        importances = dict(zip(features, [round(float(x), 4) for x in model.feature_importances_]))
        importances = dict(sorted(importances.items(), key=lambda x: x[1], reverse=True))
        metrics["feature_importance"] = importances

    # Confusion matrix
    cm = confusion_matrix(y_test, y_pred)
    metrics["confusion_matrix"] = cm.tolist()

    return {"model": model, "scaler": scaler, "metrics": metrics, "algorithm": algorithm, "features": features}


@tool
def train_regression_model(
    file_path: str,
    target_column: str,
    algorithm: str = "random_forest",
    feature_columns: Optional[List[str]] = None,
    hyperparameters: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Train a regression model and return metrics."""
    from tools.analysis_tools import load_dataset
    df = load_dataset.invoke({"file_path": file_path})
    X, y, features = _prepare_features(df, target_column, feature_columns)
    if y is None:
        return {"error": f"Target column '{target_column}' not found"}

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    params = hyperparameters or {}

    if algorithm == "linear_regression":
        model = LinearRegression()
    elif algorithm == "random_forest":
        model = RandomForestRegressor(
            n_estimators=params.get("n_estimators", 100),
            max_depth=params.get("max_depth", None),
            random_state=42,
        )
    elif algorithm == "svr":
        model = SVR(kernel=params.get("kernel", "rbf"))
    elif algorithm == "decision_tree":
        model = DecisionTreeRegressor(max_depth=params.get("max_depth", None), random_state=42)
    elif algorithm == "gradient_boosting":
        model = GradientBoostingRegressor(n_estimators=params.get("n_estimators", 100), learning_rate=params.get("learning_rate", 0.1), random_state=42)
    elif algorithm == "knn":
        model = KNeighborsRegressor(n_neighbors=params.get("n_neighbors", 5))
    elif algorithm == "ridge":
        model = Ridge(alpha=params.get("alpha", 1.0))
    elif algorithm == "lasso":
        model = Lasso(alpha=params.get("alpha", 1.0))
    elif algorithm == "mlp":
        model = MLPRegressor(max_iter=1000, random_state=42)
    else:
        model = RandomForestRegressor(n_estimators=100, random_state=42)

    model.fit(X_train_scaled, y_train)
    y_pred = model.predict(X_test_scaled)

    metrics = {
        "rmse": round(float(np.sqrt(mean_squared_error(y_test, y_pred))), 4),
        "r2_score": round(float(r2_score(y_test, y_pred)), 4),
        "mae": round(float(np.mean(np.abs(y_test - y_pred))), 4),
    }

    if hasattr(model, "feature_importances_"):
        importances = dict(zip(features, [round(float(x), 4) for x in model.feature_importances_]))
        importances = dict(sorted(importances.items(), key=lambda x: x[1], reverse=True))
        metrics["feature_importance"] = importances

    return {"model": model, "scaler": scaler, "metrics": metrics, "algorithm": algorithm, "features": features}


@tool
def train_clustering_model(
    file_path: str,
    algorithm: str = "kmeans",
    feature_columns: Optional[List[str]] = None,
    hyperparameters: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Train a clustering model and return metrics."""
    from tools.analysis_tools import load_dataset
    df = load_dataset.invoke({"file_path": file_path})
    X, _, features = _prepare_features(df, None, feature_columns)

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    params = hyperparameters or {}

    if algorithm == "kmeans":
        n_clusters = params.get("n_clusters", 3)
        model = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    elif algorithm == "dbscan":
        model = DBSCAN(eps=params.get("eps", 0.5), min_samples=params.get("min_samples", 5))
    elif algorithm == "agglomerative":
        model = AgglomerativeClustering(n_clusters=params.get("n_clusters", 3))
    elif algorithm == "gaussian_mixture":
        model = GaussianMixture(n_components=params.get("n_clusters", 3), random_state=42)
    else:
        model = KMeans(n_clusters=3, random_state=42, n_init=10)

    labels = model.fit_predict(X_scaled)

    metrics = {
        "n_clusters": int(len(set(labels)) - (1 if -1 in labels else 0)),
        "cluster_sizes": {str(k): int(v) for k, v in zip(*np.unique(labels, return_counts=True))},
    }

    if len(set(labels)) > 1 and len(set(labels)) < len(X_scaled):
        try:
            metrics["silhouette_score"] = round(float(silhouette_score(X_scaled, labels)), 4)
        except Exception:
            pass

    return {"model": model, "scaler": scaler, "metrics": metrics, "algorithm": algorithm, "features": features, "labels": labels.tolist()}


@tool
def save_model(model_data: Dict, path: str) -> str:
    """Serialize and save model to disk."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as f:
        pickle.dump({"model": model_data["model"], "scaler": model_data["scaler"]}, f)
    return path
