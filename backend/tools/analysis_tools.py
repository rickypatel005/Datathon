"""
Dataset analysis tools used by CrewAI agents.
Wraps Pandas operations into callable tool functions.
"""
import pandas as pd
import numpy as np
import json
import os
from typing import Optional, Dict, Any, List


def load_dataset(file_path: str) -> pd.DataFrame:
    """Load a dataset from file path. Supports CSV, Excel, JSON."""
    ext = os.path.splitext(file_path)[1].lower()
    if ext == ".csv":
        return pd.read_csv(file_path)
    elif ext in (".xlsx", ".xls"):
        return pd.read_excel(file_path)
    elif ext == ".json":
        return pd.read_json(file_path)
    else:
        raise ValueError(f"Unsupported file type: {ext}")


def get_dataset_overview(df: pd.DataFrame) -> Dict[str, Any]:
    """Generate a comprehensive overview of the dataset."""
    overview = {
        "shape": {"rows": int(df.shape[0]), "columns": int(df.shape[1])},
        "columns": [],
        "memory_usage_mb": round(df.memory_usage(deep=True).sum() / 1024 / 1024, 2),
        "duplicate_rows": int(df.duplicated().sum()),
    }

    for col in df.columns:
        col_info = {
            "name": col,
            "dtype": str(df[col].dtype),
            "null_count": int(df[col].isnull().sum()),
            "null_percentage": round(df[col].isnull().sum() / len(df) * 100, 2),
            "unique_count": int(df[col].nunique()),
        }
        if pd.api.types.is_numeric_dtype(df[col]):
            col_info["min"] = float(df[col].min()) if not pd.isna(df[col].min()) else None
            col_info["max"] = float(df[col].max()) if not pd.isna(df[col].max()) else None
            col_info["mean"] = round(float(df[col].mean()), 4) if not pd.isna(df[col].mean()) else None
            col_info["std"] = round(float(df[col].std()), 4) if not pd.isna(df[col].std()) else None
            col_info["median"] = float(df[col].median()) if not pd.isna(df[col].median()) else None
        else:
            top_values = df[col].value_counts().head(5).to_dict()
            col_info["top_values"] = {str(k): int(v) for k, v in top_values.items()}

        overview["columns"].append(col_info)

    return overview


def clean_dataset(df: pd.DataFrame, strategies: Optional[Dict] = None) -> Dict[str, Any]:
    """
    Clean the dataset: handle missing values, duplicates, outliers.
    Returns cleaned DataFrame and a report of changes.
    """
    report = {"changes": [], "original_shape": list(df.shape)}
    cleaned = df.copy()

    # Remove duplicate rows
    dup_count = cleaned.duplicated().sum()
    if dup_count > 0:
        cleaned = cleaned.drop_duplicates()
        report["changes"].append(f"Removed {dup_count} duplicate rows")

    # Handle missing values per column
    for col in cleaned.columns:
        null_count = cleaned[col].isnull().sum()
        if null_count == 0:
            continue

        null_pct = null_count / len(cleaned) * 100

        if null_pct > 60:
            cleaned = cleaned.drop(columns=[col])
            report["changes"].append(f"Dropped column '{col}' ({null_pct:.1f}% missing)")
        elif pd.api.types.is_numeric_dtype(cleaned[col]):
            median_val = cleaned[col].median()
            cleaned[col] = cleaned[col].fillna(median_val)
            report["changes"].append(f"Filled '{col}' nulls with median ({median_val:.2f})")
        else:
            mode_val = cleaned[col].mode()
            if len(mode_val) > 0:
                cleaned[col] = cleaned[col].fillna(mode_val[0])
                report["changes"].append(f"Filled '{col}' nulls with mode ('{mode_val[0]}')")

    # Detect outliers using IQR for numeric columns
    outlier_info = {}
    for col in cleaned.select_dtypes(include=[np.number]).columns:
        Q1 = cleaned[col].quantile(0.25)
        Q3 = cleaned[col].quantile(0.75)
        IQR = Q3 - Q1
        lower = Q1 - 1.5 * IQR
        upper = Q3 + 1.5 * IQR
        outlier_count = int(((cleaned[col] < lower) | (cleaned[col] > upper)).sum())
        if outlier_count > 0:
            outlier_info[col] = {
                "count": outlier_count,
                "lower_bound": round(float(lower), 4),
                "upper_bound": round(float(upper), 4),
            }

    report["cleaned_shape"] = list(cleaned.shape)
    report["outliers"] = outlier_info

    return {"dataframe": cleaned, "report": report}


def perform_eda(df: pd.DataFrame) -> Dict[str, Any]:
    """Perform full exploratory data analysis."""
    eda = {}

    # Basic statistics
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    categorical_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()

    if numeric_cols:
        stats = df[numeric_cols].describe().round(4).to_dict()
        eda["numeric_statistics"] = stats

        # Correlation matrix
        corr = df[numeric_cols].corr().round(4)
        eda["correlation_matrix"] = corr.to_dict()

        # Skewness and Kurtosis
        eda["skewness"] = df[numeric_cols].skew().round(4).to_dict()
        eda["kurtosis"] = df[numeric_cols].kurtosis().round(4).to_dict()

        # High correlations (|r| > 0.7)
        high_corr = []
        for i in range(len(numeric_cols)):
            for j in range(i + 1, len(numeric_cols)):
                r = corr.iloc[i, j]
                if abs(r) > 0.7:
                    high_corr.append({
                        "col1": numeric_cols[i],
                        "col2": numeric_cols[j],
                        "correlation": round(float(r), 4),
                    })
        eda["high_correlations"] = high_corr

    if categorical_cols:
        cat_stats = {}
        for col in categorical_cols:
            vc = df[col].value_counts().head(10)
            cat_stats[col] = {
                "unique_count": int(df[col].nunique()),
                "top_values": {str(k): int(v) for k, v in vc.items()},
            }
        eda["categorical_statistics"] = cat_stats

    # Distribution info for numeric columns
    distributions = {}
    for col in numeric_cols:
        distributions[col] = {
            "histogram_values": df[col].dropna().tolist()[:500],  # Limit for serialization
            "mean": round(float(df[col].mean()), 4) if not pd.isna(df[col].mean()) else None,
            "median": round(float(df[col].median()), 4) if not pd.isna(df[col].median()) else None,
        }
    eda["distributions"] = distributions

    return eda


def preprocess_for_visualization(df: pd.DataFrame) -> tuple[pd.DataFrame, list[str]]:
    """
    Full preprocessing pipeline for visualization:
    1. Drop duplicate rows
    2. Impute missing values (median for numeric, mode for categorical)
    3. Remove outliers via IQR clipping (cap at 1.5*IQR bounds)
    4. Standard-scale numeric columns (z-score normalization) — stored as separate columns
    Returns the processed DataFrame and a list of preprocessing steps taken.
    """
    steps = []
    processed = df.copy()

    # 1. Drop duplicates
    n_dups = processed.duplicated().sum()
    if n_dups > 0:
        processed = processed.drop_duplicates()
        steps.append(f"Removed {n_dups} duplicate row(s).")

    # 2. Impute missing values
    for col in processed.columns:
        n_null = processed[col].isnull().sum()
        if n_null == 0:
            continue
        if pd.api.types.is_numeric_dtype(processed[col]):
            fill = processed[col].median()
            processed[col] = processed[col].fillna(fill)
            steps.append(f"Imputed {n_null} missing value(s) in '{col}' with median ({fill:.3g}).")
        else:
            mode_vals = processed[col].mode()
            if len(mode_vals) > 0:
                processed[col] = processed[col].fillna(mode_vals[0])
                steps.append(f"Imputed {n_null} missing value(s) in '{col}' with mode ('{mode_vals[0]}').")

    # 3. Remove outliers via IQR clipping for numeric columns
    numeric_cols = processed.select_dtypes(include=[np.number]).columns.tolist()
    total_clipped = 0
    for col in numeric_cols:
        Q1 = processed[col].quantile(0.25)
        Q3 = processed[col].quantile(0.75)
        IQR = Q3 - Q1
        if IQR == 0:
            continue
        lower = Q1 - 1.5 * IQR
        upper = Q3 + 1.5 * IQR
        n_outliers = int(((processed[col] < lower) | (processed[col] > upper)).sum())
        if n_outliers > 0:
            processed[col] = processed[col].clip(lower=lower, upper=upper)
            total_clipped += n_outliers
    if total_clipped > 0:
        steps.append(f"Clipped {total_clipped} outlier value(s) across numeric columns using IQR method.")

    # 4. Standard scaling (z-score) — applied to numeric cols for plotting consistency
    scaled_cols = []
    for col in numeric_cols:
        std = processed[col].std()
        mean = processed[col].mean()
        if std > 0:
            processed[col] = (processed[col] - mean) / std
            scaled_cols.append(col)
    if scaled_cols:
        steps.append(f"Applied standard scaling (z-score) to {len(scaled_cols)} numeric column(s): {', '.join(scaled_cols[:5])}{'...' if len(scaled_cols) > 5 else ''}.")

    return processed, steps


def generate_chart_data(
    df: pd.DataFrame,
    chart_type: str,
    x_column: Optional[str] = None,
    y_column: Optional[str] = None,
    color_column: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Generate Plotly-compatible chart data using the full dataset.
    Runs preprocessing pipeline (dedup, impute, outlier clip, scale) before plotting.
    """
    # Run full preprocessing on the complete dataset
    processed, preprocess_steps = preprocess_for_visualization(df)

    color_palette = ["#3B82F6", "#10B981", "#F59E0B", "#EF4444", "#8B5CF6", "#06B6D4", "#EC4899"]

    if chart_type == "countplot" and x_column and x_column in processed.columns:
        vc = processed[x_column].value_counts().reset_index()
        vc.columns = [x_column, "count"]
        vc = vc.sort_values("count", ascending=False).head(30)
        return {
            "type": "countplot",
            "data": [{
                "x": vc[x_column].astype(str).tolist(),
                "y": vc["count"].tolist(),
                "type": "bar",
                "marker": {"color": color_palette[0]},
                "name": "Count",
            }],
            "layout": {
                "title": f"Count Plot — {x_column}",
                "xaxis": {"title": x_column, "tickangle": -45},
                "yaxis": {"title": "Count"},
                "bargap": 0.3,
            },
            "preprocessing_steps": preprocess_steps,
        }

    if chart_type == "histogram" and x_column and x_column in processed.columns:
        values = processed[x_column].dropna().tolist()
        return {
            "type": "histogram",
            "data": [{
                "x": values,
                "type": "histogram",
                "name": x_column,
                "marker": {"color": color_palette[0]},
                "nbinsx": 40,
            }],
            "layout": {
                "title": f"Distribution of {x_column} (preprocessed)",
                "xaxis": {"title": f"{x_column} (scaled)"},
                "yaxis": {"title": "Frequency"},
                "bargap": 0.05,
            },
            "preprocessing_steps": preprocess_steps,
        }

    elif chart_type == "scatter" and x_column and y_column and x_column in processed.columns and y_column in processed.columns:
        if color_column and color_column in processed.columns:
            unique_colors = processed[color_column].unique().tolist()
            traces = []
            for i, val in enumerate(unique_colors[:20]):
                mask = processed[color_column] == val
                traces.append({
                    "x": processed.loc[mask, x_column].tolist(),
                    "y": processed.loc[mask, y_column].tolist(),
                    "mode": "markers",
                    "type": "scatter",
                    "name": str(val),
                    "marker": {"color": color_palette[i % len(color_palette)], "size": 6, "opacity": 0.7},
                })
        else:
            traces = [{
                "x": processed[x_column].tolist(),
                "y": processed[y_column].tolist(),
                "mode": "markers",
                "type": "scatter",
                "name": f"{x_column} vs {y_column}",
                "marker": {"color": color_palette[0], "size": 6, "opacity": 0.7},
            }]
        return {
            "type": "scatter",
            "data": traces,
            "layout": {
                "title": f"{x_column} vs {y_column} (preprocessed)",
                "xaxis": {"title": f"{x_column} (scaled)"},
                "yaxis": {"title": f"{y_column} (scaled)"},
            },
            "preprocessing_steps": preprocess_steps,
        }

    elif chart_type == "bar" and x_column and x_column in processed.columns:
        if y_column and y_column in processed.columns:
            grouped = processed.groupby(x_column)[y_column].mean().sort_values(ascending=False).head(25)
            y_title = f"Mean {y_column} (scaled)"
        else:
            grouped = processed[x_column].value_counts().head(25)
            y_title = "Count"
        return {
            "type": "bar",
            "data": [{
                "x": [str(x) for x in grouped.index.tolist()],
                "y": [round(float(v), 4) for v in grouped.values.tolist()],
                "type": "bar",
                "marker": {"color": color_palette[0]},
            }],
            "layout": {
                "title": f"Bar Chart — {x_column}",
                "xaxis": {"title": x_column, "tickangle": -45},
                "yaxis": {"title": y_title},
                "bargap": 0.3,
            },
            "preprocessing_steps": preprocess_steps,
        }

    elif chart_type == "pie" and x_column and x_column in processed.columns:
        vc = processed[x_column].value_counts().head(12)
        return {
            "type": "pie",
            "data": [{
                "labels": [str(x) for x in vc.index.tolist()],
                "values": vc.values.tolist(),
                "type": "pie",
                "marker": {"colors": color_palette},
                "hole": 0.35,
            }],
            "layout": {"title": f"Proportion of {x_column}"},
            "preprocessing_steps": preprocess_steps,
        }

    elif chart_type == "boxplot" and x_column and x_column in processed.columns:
        cols = [c for c in [x_column, y_column] if c and c in processed.columns and pd.api.types.is_numeric_dtype(processed[c])]
        traces = []
        for i, col in enumerate(cols):
            traces.append({
                "y": processed[col].tolist(),
                "type": "box",
                "name": col,
                "marker": {"color": color_palette[i % len(color_palette)]},
                "boxmean": "sd",
            })
        return {
            "type": "box",
            "data": traces,
            "layout": {
                "title": "Box Plot (after outlier clipping & scaling)",
                "yaxis": {"title": "Scaled Value"},
            },
            "preprocessing_steps": preprocess_steps,
        }

    elif chart_type == "heatmap":
        numeric_cols = processed.select_dtypes(include=[np.number]).columns.tolist()
        if len(numeric_cols) < 2:
            return {"type": "heatmap", "data": [], "layout": {"title": "Not enough numeric columns"}, "preprocessing_steps": preprocess_steps}
        corr = processed[numeric_cols].corr().round(4)
        return {
            "type": "heatmap",
            "data": [{
                "z": corr.values.tolist(),
                "x": numeric_cols,
                "y": numeric_cols,
                "type": "heatmap",
                "colorscale": "RdBu",
                "zmin": -1,
                "zmax": 1,
            }],
            "layout": {"title": "Correlation Heatmap (preprocessed data)"},
            "preprocessing_steps": preprocess_steps,
        }

    elif chart_type == "line" and x_column and y_column and x_column in processed.columns and y_column in processed.columns:
        sorted_df = processed.sort_values(x_column)
        return {
            "type": "line",
            "data": [{
                "x": sorted_df[x_column].tolist(),
                "y": sorted_df[y_column].tolist(),
                "type": "scatter",
                "mode": "lines",
                "name": y_column,
                "line": {"color": color_palette[0], "width": 2},
            }],
            "layout": {
                "title": f"{y_column} over {x_column} (preprocessed)",
                "xaxis": {"title": x_column},
                "yaxis": {"title": f"{y_column} (scaled)"},
            },
            "preprocessing_steps": preprocess_steps,
        }

    return {
        "type": chart_type,
        "data": [],
        "layout": {"title": "Chart type not supported or missing columns"},
        "preprocessing_steps": preprocess_steps,
    }

