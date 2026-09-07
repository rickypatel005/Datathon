"""
AIDA Auto-Chart Selection & Generation Engine (Person 4 Scope)

Automatically deduces high-value visualizations based on dataset column metadata,
semantic data types, and statistical relationships:
- DateTime + Numeric -> Time Series Line Chart
- Categorical (< 25 distinct) + Numeric -> Aggregated Bar Chart
- Numeric + Numeric -> Scatter Plot with correlation
- >= 3 Numeric Columns -> Correlation Heatmap
- Numeric Column -> Distribution Histogram & Boxplot
- Categorical Column -> Frequency Distribution
"""

from typing import List, Dict, Any, Optional
import pandas as pd
import numpy as np


class AutoChartEngine:
    """
    Automatic chart selection engine generating standard Plotly-compatible JSON specs.
    """

    COLOR_PALETTE = [
        "#0EA5E9", "#10B981", "#F59E0B", "#EF4444", "#8B5CF6",
        "#EC4899", "#14B8A6", "#F97316", "#6366F1", "#84CC16"
    ]

    def __init__(self, max_charts: int = 6):
        self.max_charts = max_charts

    def analyze_and_generate(self, df: pd.DataFrame, target_col: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Examines DataFrame columns, infers statistical types, and returns ranked,
        applicable Plotly chart specifications.
        """
        if df.empty:
            return []

        charts: List[Dict[str, Any]] = []

        # Classify columns
        col_types = self._classify_columns(df)
        datetime_cols = col_types["datetime"]
        numeric_cols = col_types["numeric"]
        categorical_cols = col_types["categorical"]

        # 1. Time Series Line Chart (if datetime exists)
        if datetime_cols and numeric_cols:
            dt_col = datetime_cols[0]
            num_col = target_col if target_col in numeric_cols else numeric_cols[0]
            time_chart = self._generate_time_series(df, dt_col, num_col)
            if time_chart:
                charts.append(time_chart)

        # 2. Correlation Heatmap (if >= 3 numeric columns)
        if len(numeric_cols) >= 3:
            heatmap = self._generate_correlation_heatmap(df, numeric_cols[:8])
            if heatmap:
                charts.append(heatmap)

        # 3. Categorical vs Numeric Bar Chart
        if categorical_cols and numeric_cols:
            cat_col = categorical_cols[0]
            num_col = target_col if target_col in numeric_cols else numeric_cols[0]
            bar_chart = self._generate_cat_num_bar(df, cat_col, num_col)
            if bar_chart:
                charts.append(bar_chart)

        # 4. Numeric Scatter Plot (if >= 2 numeric columns)
        if len(numeric_cols) >= 2:
            x_col = numeric_cols[0]
            y_col = numeric_cols[1] if (target_col not in numeric_cols or target_col == x_col) else target_col
            scatter_chart = self._generate_scatter_plot(df, x_col, y_col, target_col if target_col in categorical_cols else None)
            if scatter_chart:
                charts.append(scatter_chart)

        # 5. Target / Primary Distribution
        primary_col = target_col or (numeric_cols[0] if numeric_cols else (categorical_cols[0] if categorical_cols else None))
        if primary_col:
            if primary_col in numeric_cols:
                dist_chart = self._generate_numeric_distribution(df, primary_col)
                if dist_chart:
                    charts.append(dist_chart)
            elif primary_col in categorical_cols:
                cat_dist = self._generate_cat_distribution(df, primary_col)
                if cat_dist:
                    charts.append(cat_dist)

        # 6. Boxplot for outlier detection (if numeric columns exist)
        if numeric_cols:
            box_col = target_col if (target_col in numeric_cols) else numeric_cols[-1]
            box_chart = self._generate_boxplot(df, box_col, categorical_cols[0] if categorical_cols else None)
            if box_chart:
                charts.append(box_chart)

        return charts[:self.max_charts]

    def _classify_columns(self, df: pd.DataFrame) -> Dict[str, List[str]]:
        datetime_cols = []
        numeric_cols = []
        categorical_cols = []

        for col in df.columns:
            # Check datetime
            if pd.api.types.is_datetime64_any_dtype(df[col]):
                datetime_cols.append(col)
                continue
            
            # Attempt date parsing for object cols if sample resembles date
            if df[col].dtype == object and df[col].dropna().count() > 0:
                sample = str(df[col].dropna().iloc[0])
                if any(char in sample for char in ["-", "/"]) and len(sample) <= 25:
                    try:
                        pd.to_datetime(df[col].dropna().iloc[:10])
                        datetime_cols.append(col)
                        continue
                    except Exception:
                        pass

            # Check numeric
            if pd.api.types.is_numeric_dtype(df[col]):
                # If unique values are <= 2 and binary, could be target/categorical
                if df[col].nunique() <= 2:
                    categorical_cols.append(col)
                else:
                    numeric_cols.append(col)
                continue

            # Check categorical
            nunique = df[col].nunique()
            if 1 < nunique <= 30:
                categorical_cols.append(col)

        return {
            "datetime": datetime_cols,
            "numeric": numeric_cols,
            "categorical": categorical_cols
        }

    def _generate_time_series(self, df: pd.DataFrame, dt_col: str, num_col: str) -> Optional[Dict[str, Any]]:
        try:
            temp = df[[dt_col, num_col]].dropna().copy()
            temp[dt_col] = pd.to_datetime(temp[dt_col], errors="coerce")
            temp = temp.dropna().sort_values(by=dt_col)
            if len(temp) > 100:
                # Resample or downsample to max 100 points
                temp = temp.iloc[::max(1, len(temp) // 100)]

            x_vals = [str(d) for d in temp[dt_col].dt.strftime("%Y-%m-%d").tolist()]
            y_vals = [float(v) for v in temp[num_col].tolist()]

            return {
                "id": f"chart-ts-{dt_col}-{num_col}",
                "title": f"Temporal Trajectory of {num_col}",
                "description": f"Historical progression of {num_col} across {dt_col}.",
                "category": "time_series",
                "chart_type": "line",
                "applicable": True,
                "data": [
                    {
                        "x": x_vals,
                        "y": y_vals,
                        "type": "scatter",
                        "mode": "lines+markers",
                        "name": num_col,
                        "line": {"color": self.COLOR_PALETTE[0], "width": 2.5}
                    }
                ],
                "layout": {
                    "title": f"{num_col} over Time",
                    "xaxis": {"title": dt_col},
                    "yaxis": {"title": num_col},
                    "margin": {"t": 40, "b": 40, "l": 50, "r": 20}
                }
            }
        except Exception:
            return None

    def _generate_correlation_heatmap(self, df: pd.DataFrame, numeric_cols: List[str]) -> Optional[Dict[str, Any]]:
        try:
            corr_df = df[numeric_cols].corr().fillna(0)
            z_vals = [[round(float(val), 2) for val in row] for row in corr_df.values]

            return {
                "id": "chart-correlation-heatmap",
                "title": "Numeric Feature Correlation Matrix",
                "description": "Pearson correlation coefficient across continuous variables.",
                "category": "correlation",
                "chart_type": "heatmap",
                "applicable": True,
                "data": [
                    {
                        "z": z_vals,
                        "x": list(corr_df.columns),
                        "y": list(corr_df.index),
                        "type": "heatmap",
                        "colorscale": "RdBu",
                        "reversescale": True,
                        "zmin": -1.0,
                        "zmax": 1.0
                    }
                ],
                "layout": {
                    "title": "Feature Correlation Heatmap",
                    "margin": {"t": 40, "b": 70, "l": 90, "r": 20}
                }
            }
        except Exception:
            return None

    def _generate_cat_num_bar(self, df: pd.DataFrame, cat_col: str, num_col: str) -> Optional[Dict[str, Any]]:
        try:
            agg = df.groupby(cat_col)[num_col].mean().dropna().sort_values(ascending=False).head(15)
            x_vals = [str(k) for k in agg.index.tolist()]
            y_vals = [round(float(v), 2) for v in agg.values.tolist()]

            return {
                "id": f"chart-bar-{cat_col}-{num_col}",
                "title": f"Mean {num_col} by {cat_col}",
                "description": f"Aggregated mean values of {num_col} segmented by {cat_col}.",
                "category": "category_comparison",
                "chart_type": "bar",
                "applicable": True,
                "data": [
                    {
                        "x": x_vals,
                        "y": y_vals,
                        "type": "bar",
                        "marker": {"color": self.COLOR_PALETTE[1]}
                    }
                ],
                "layout": {
                    "title": f"Average {num_col} by {cat_col}",
                    "xaxis": {"title": cat_col},
                    "yaxis": {"title": f"Mean {num_col}"},
                    "margin": {"t": 40, "b": 50, "l": 50, "r": 20}
                }
            }
        except Exception:
            return None

    def _generate_scatter_plot(self, df: pd.DataFrame, x_col: str, y_col: str, color_col: Optional[str] = None) -> Optional[Dict[str, Any]]:
        try:
            cols = [x_col, y_col] + ([color_col] if color_col else [])
            sample_df = df[cols].dropna()
            if len(sample_df) > 300:
                sample_df = sample_df.sample(n=300, random_state=42)

            data = []
            if color_col:
                groups = sample_df.groupby(color_col)
                for idx, (grp_name, grp) in enumerate(groups):
                    data.append({
                        "x": [float(v) for v in grp[x_col]],
                        "y": [float(v) for v in grp[y_col]],
                        "mode": "markers",
                        "type": "scatter",
                        "name": str(grp_name),
                        "marker": {
                            "color": self.COLOR_PALETTE[idx % len(self.COLOR_PALETTE)],
                            "size": 6,
                            "opacity": 0.75
                        }
                    })
            else:
                data.append({
                    "x": [float(v) for v in sample_df[x_col]],
                    "y": [float(v) for v in sample_df[y_col]],
                    "mode": "markers",
                    "type": "scatter",
                    "marker": {"color": self.COLOR_PALETTE[0], "size": 6, "opacity": 0.75}
                })

            return {
                "id": f"chart-scatter-{x_col}-{y_col}",
                "title": f"{y_col} vs {x_col} Relationship",
                "description": f"Bivariate scatter mapping between {x_col} and {y_col}.",
                "category": "correlation",
                "chart_type": "scatter",
                "applicable": True,
                "data": data,
                "layout": {
                    "title": f"{y_col} vs {x_col}",
                    "xaxis": {"title": x_col},
                    "yaxis": {"title": y_col},
                    "margin": {"t": 40, "b": 50, "l": 50, "r": 20}
                }
            }
        except Exception:
            return None

    def _generate_numeric_distribution(self, df: pd.DataFrame, num_col: str) -> Optional[Dict[str, Any]]:
        try:
            vals = df[num_col].dropna()
            if len(vals) > 500:
                vals = vals.sample(n=500, random_state=42)

            return {
                "id": f"chart-dist-{num_col}",
                "title": f"Distribution Profile: {num_col}",
                "description": f"Histogram spread and density characteristics of {num_col}.",
                "category": "distribution",
                "chart_type": "histogram",
                "applicable": True,
                "data": [
                    {
                        "x": [float(v) for v in vals],
                        "type": "histogram",
                        "marker": {"color": self.COLOR_PALETTE[4], "opacity": 0.8}
                    }
                ],
                "layout": {
                    "title": f"{num_col} Histogram",
                    "xaxis": {"title": num_col},
                    "yaxis": {"title": "Frequency Count"},
                    "margin": {"t": 40, "b": 40, "l": 50, "r": 20}
                }
            }
        except Exception:
            return None

    def _generate_cat_distribution(self, df: pd.DataFrame, cat_col: str) -> Optional[Dict[str, Any]]:
        try:
            counts = df[cat_col].value_counts().head(10)
            return {
                "id": f"chart-cat-dist-{cat_col}",
                "title": f"Category Distribution: {cat_col}",
                "description": f"Frequency counts across categories in {cat_col}.",
                "category": "distribution",
                "chart_type": "bar",
                "applicable": True,
                "data": [
                    {
                        "x": [str(k) for k in counts.index],
                        "y": [int(v) for v in counts.values],
                        "type": "bar",
                        "marker": {"color": self.COLOR_PALETTE[2]}
                    }
                ],
                "layout": {
                    "title": f"Top Categories in {cat_col}",
                    "xaxis": {"title": cat_col},
                    "yaxis": {"title": "Count"},
                    "margin": {"t": 40, "b": 50, "l": 50, "r": 20}
                }
            }
        except Exception:
            return None

    def _generate_boxplot(self, df: pd.DataFrame, num_col: str, cat_col: Optional[str] = None) -> Optional[Dict[str, Any]]:
        try:
            data = []
            if cat_col and df[cat_col].nunique() <= 5:
                for idx, (cat_val, grp) in enumerate(df.groupby(cat_col)):
                    vals = grp[num_col].dropna()
                    if len(vals) > 300:
                        vals = vals.sample(n=300, random_state=42)
                    data.append({
                        "y": [float(v) for v in vals],
                        "type": "box",
                        "name": str(cat_val),
                        "marker": {"color": self.COLOR_PALETTE[idx % len(self.COLOR_PALETTE)]}
                    })
            else:
                vals = df[num_col].dropna()
                if len(vals) > 500:
                    vals = vals.sample(n=500, random_state=42)
                data.append({
                    "y": [float(v) for v in vals],
                    "type": "box",
                    "name": num_col,
                    "marker": {"color": self.COLOR_PALETTE[3]}
                })

            return {
                "id": f"chart-box-{num_col}",
                "title": f"Outlier & Spread Analysis: {num_col}",
                "description": f"Quartile ranges and outlier inspection for {num_col}.",
                "category": "distribution",
                "chart_type": "box",
                "applicable": True,
                "data": data,
                "layout": {
                    "title": f"{num_col} Boxplot",
                    "yaxis": {"title": num_col},
                    "margin": {"t": 40, "b": 40, "l": 50, "r": 20}
                }
            }
        except Exception:
            return None
