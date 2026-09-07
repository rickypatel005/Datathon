"""Discovery Contract Schema (Input from Person 1 - Data Discovery).

Encapsulates dataset profiling, dynamic column schemas, statistical distributions,
missingness reports, and correlation matrices without any hardcoded domain logic.
"""

from __future__ import annotations
from typing import Any, Dict, List, Literal, Optional
from pydantic import BaseModel, Field, ConfigDict


class DistributionStats(BaseModel):
    """Statistical distribution metrics for a numeric column."""
    model_config = ConfigDict(extra="ignore")

    count: int = Field(..., description="Number of non-null observations")
    mean: float = Field(..., description="Arithmetic mean")
    std: float = Field(..., description="Standard deviation")
    min: float = Field(..., description="Minimum value")
    q25: float = Field(..., description="25th percentile (Q1)")
    median: float = Field(..., description="50th percentile (Median)")
    q75: float = Field(..., description="75th percentile (Q3)")
    max: float = Field(..., description="Maximum value")
    skewness: Optional[float] = Field(None, description="Fisher-Pearson skewness")
    kurtosis: Optional[float] = Field(None, description="Excess kurtosis")


class ColumnProfile(BaseModel):
    """Profiling summary for an individual dataset column."""
    model_config = ConfigDict(extra="ignore")

    name: str = Field(..., description="Column identifier / name")
    semantic_type: Literal[
        "numeric", "categorical", "datetime", "boolean", "text", "identifier", "unknown"
    ] = Field(default="unknown", description="Inferred semantic type")
    raw_dtype: str = Field(..., description="Native pandas/SQL data type")
    null_count: int = Field(default=0, ge=0, description="Total missing/null values")
    null_percentage: float = Field(default=0.0, ge=0.0, le=100.0, description="Missing rate [0-100]")
    unique_count: int = Field(default=0, ge=0, description="Count of distinct values")
    cardinality_ratio: float = Field(default=0.0, ge=0.0, le=1.0, description="Unique values / total rows")
    distribution: Optional[DistributionStats] = Field(None, description="Numeric distribution stats if applicable")
    top_categories: Optional[Dict[str, int]] = Field(None, description="Frequency counts for top categories")
    is_constant: bool = Field(default=False, description="True if column contains only 1 distinct value")


class CorrelationMatrix(BaseModel):
    """Pairwise correlation matrix for numeric columns."""
    model_config = ConfigDict(extra="ignore")

    method: Literal["pearson", "spearman", "kendall"] = Field(
        default="pearson", description="Correlation calculation method"
    )
    matrix: Dict[str, Dict[str, float]] = Field(
        default_factory=dict,
        description="Nested mapping: column_a -> {column_b: correlation_coefficient}",
    )


class MissingnessReport(BaseModel):
    """Overall dataset missingness breakdown."""
    model_config = ConfigDict(extra="ignore")

    total_missing_cells: int = Field(default=0, ge=0)
    overall_missing_percentage: float = Field(default=0.0, ge=0.0, le=100.0)
    columns_with_missing: List[str] = Field(default_factory=list)


class DiscoveryContract(BaseModel):
    """Complete Discovery Contract ingested from Person 1 (Data Discovery)."""
    model_config = ConfigDict(extra="ignore")

    dataset_id: str = Field(..., description="Unique dataset identifier")
    dataset_name: str = Field(..., description="Filename or resource name")
    row_count: int = Field(..., ge=0, description="Total number of records")
    column_count: int = Field(..., ge=0, description="Total number of features")
    columns: Dict[str, ColumnProfile] = Field(
        default_factory=dict,
        description="Dictionary mapping column names to their statistical profile",
    )
    correlations: Optional[CorrelationMatrix] = Field(
        None, description="Numeric pairwise correlation matrix"
    )
    missingness: Optional[MissingnessReport] = Field(
        None, description="Comprehensive missingness report"
    )
    sample_rows: Optional[List[Dict[str, Any]]] = Field(
        None, description="First few rows for qualitative reference"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Arbitrary pipeline or dataset metadata"
    )

    def get_column(self, col_name: str) -> Optional[ColumnProfile]:
        """Safely fetch profile for a column name."""
        return self.columns.get(col_name)

    def get_correlation(self, col_a: str, col_b: str) -> Optional[float]:
        """Safely retrieve correlation between two columns if calculated."""
        if not self.correlations or not self.correlations.matrix:
            return None
        # Check both (col_a, col_b) and symmetric (col_b, col_a)
        if col_a in self.correlations.matrix and col_b in self.correlations.matrix[col_a]:
            return self.correlations.matrix[col_a][col_b]
        if col_b in self.correlations.matrix and col_a in self.correlations.matrix[col_b]:
            return self.correlations.matrix[col_b][col_a]
        return None
