export type TaskType = 'classification' | 'regression' | 'time_series' | 'clustering';

export type InsightStatus = 'verified' | 'investigating' | 'challenged' | 'rejected';

export interface ColumnSchema {
  name: string;
  dtype: string;
  semantic_type: 'numeric' | 'categorical' | 'datetime' | 'id' | 'target' | 'text';
  unique_count: number;
  null_count: number;
  null_percentage: number;
  sample_values: (string | number)[];
}

export interface QualityReport {
  overall_score: number; // 0 - 100
  completeness_score: number;
  validity_score: number;
  outlier_score: number;
  missing_cells_total: number;
  duplicate_rows: number;
  total_rows: number;
  total_cols: number;
  cleaning_actions_taken: string[];
}

export interface LeakageWarning {
  column: string;
  risk_level: 'critical' | 'moderate' | 'low';
  reason: string;
  recommendation: string;
}

export interface DiscoveryContract {
  dataset_id: string;
  dataset_name: string;
  fingerprint: {
    shape: [number, number];
    memory_usage_mb: number;
    has_datetime: boolean;
    has_id_column: boolean;
    recommended_task: TaskType;
    target_candidates: string[];
    selected_target?: string;
  };
  schema: ColumnSchema[];
  quality_report: QualityReport;
  leakage_report: {
    has_leakage: boolean;
    warnings: LeakageWarning[];
  };
  router_recommendations: {
    models_to_benchmark: string[];
    validation_strategy: string;
    feature_engineering_notes: string[];
  };
}

export interface ModelBenchmarkResult {
  model_id: string;
  model_name: string;
  algorithm: string;
  is_champion: boolean;
  metrics: {
    accuracy?: number;
    f1_score?: number;
    roc_auc?: number;
    precision?: number;
    recall?: number;
    rmse?: number;
    mae?: number;
    r2_score?: number;
    silhouette?: number;
    [key: string]: number | undefined;
  };
  cv_mean: number;
  cv_std: number;
  training_time_sec: number;
  hyperparameters: Record<string, string | number | boolean>;
}

export interface ErrorAnalysisData {
  type: 'classification' | 'regression';
  confusion_matrix?: {
    labels: string[];
    matrix: number[][];
  };
  residuals?: {
    actual: number[];
    predicted: number[];
    residual: number[];
  };
  worst_performing_segments?: {
    feature: string;
    segment: string;
    error_rate: number;
    sample_count: number;
  }[];
}

export interface AnalysisContract {
  dataset_id: string;
  task_type: TaskType;
  target_column: string;
  validation_strategy: {
    method: string; // e.g. "5-Fold Stratified Cross Validation"
    split_ratio: string;
    stratified: boolean;
  };
  champion_model: string;
  models: ModelBenchmarkResult[];
  feature_importance: {
    feature: string;
    importance: number;
  }[];
  error_analysis: ErrorAnalysisData;
  time_series_analysis?: {
    trend: 'increasing' | 'decreasing' | 'stationary';
    seasonality_detected: boolean;
    seasonal_period?: number;
    stationarity_p_value?: number;
  };
}

export interface InsightEvidence {
  metric_name: string;
  metric_value: string | number;
  p_value?: number;
  effect_size?: number;
  sample_size: number;
  baseline_value?: string | number;
  chart_spec?: PlotlyChartSpec;
}

export interface InsightContract {
  id: string;
  title: string;
  claim: string;
  status: InsightStatus;
  confidence_score: number; // 0 - 100
  model_agreement: {
    agree_ratio: number; // e.g. 0.75 for 3 of 4 models
    agree_count: number;
    total_models: number;
    agreeing_models: string[];
    diverging_models: string[];
  };
  evidence: InsightEvidence;
  methodology: string;
  critic_counterargument?: string;
  verifier_resolution?: string;
  business_impact: 'high' | 'medium' | 'low';
}

export interface PlotlyChartSpec {
  id: string;
  title: string;
  description?: string;
  category?: 'distribution' | 'correlation' | 'time_series' | 'category_comparison' | 'model_evaluation';
  chart_type: 'line' | 'bar' | 'scatter' | 'heatmap' | 'box' | 'histogram';
  data: any[];
  layout: Record<string, any>;
  config?: Record<string, any>;
  applicable: boolean;
}

export interface KPICard {
  id: string;
  label: string;
  value: string | number;
  change?: string;
  is_positive?: boolean;
  subtitle?: string;
  icon_name?: string;
}

export interface DashboardContract {
  dataset_id: string;
  dataset_name: string;
  generated_at: string;
  task_type: TaskType;
  kpis: KPICard[];
  quality_summary: {
    overall_score: number;
    has_leakage: boolean;
    leakage_count: number;
    rows: number;
    columns: number;
  };
  charts: PlotlyChartSpec[];
  insights: InsightContract[];
  championship_summary: {
    champion_name: string;
    primary_metric_name: string;
    primary_metric_value: number;
    total_models_evaluated: number;
    validation_method: string;
  };
  applicable_sections: {
    overview: boolean;
    data_quality: boolean;
    time_series: boolean;
    model_championship: boolean;
    insights_investigation: boolean;
    correlations: boolean;
  };
}

export type PipelineStage = 
  | 'discovery'
  | 'quality_audit'
  | 'model_championship'
  | 'insight_investigation'
  | 'fact_verification'
  | 'dashboard_assembly';

export interface StageStatus {
  stage: PipelineStage;
  label: string;
  description: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  started_at?: string;
  completed_at?: string;
  duration_sec?: number;
  error_message?: string;
}

export interface PipelineProgress {
  dataset_id: string;
  is_running: boolean;
  overall_progress: number; // 0 - 100
  current_stage: PipelineStage | null;
  stages: StageStatus[];
  logs: string[];
}
