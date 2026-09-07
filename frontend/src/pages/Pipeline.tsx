import { useState } from 'react';
import { useStore } from '../store/useStore';
import {
  GitFork,
  CheckCircle2,
  Play,
  RotateCcw,
  Terminal,
  Cpu
} from 'lucide-react';
import clsx from 'clsx';

export function Pipeline() {
  const { activeScenario, dashboardContract } = useStore();
  const [selectedStageIdx, setSelectedStageIdx] = useState<number>(0);
  const [isRunning, setIsRunning] = useState(false);

  const datasetName = dashboardContract?.dataset_name || (activeScenario === 'sales' ? 'retail_daily_sales.csv' : 'customer_churn.csv');

  const stages = [
    {
      id: 'stage-1',
      number: '01',
      title: 'Dataset Discovery & Fingerprinting',
      status: 'completed',
      duration: '1.2s',
      summary: 'Schema inferred, semantic entities classified, and target candidates identified.',
      metrics: [
        { label: 'Observed Rows', val: activeScenario === 'sales' ? '730' : '7,043' },
        { label: 'Feature Space', val: activeScenario === 'sales' ? '12' : '21' },
        { label: 'Memory Footprint', val: '1.18 MB' },
        { label: 'Candidate Target', val: activeScenario === 'sales' ? 'Daily_Sales' : 'Churn' },
      ],
      details: [
        'Detected 1 DateTime column and verified continuous temporal continuity without gaps.',
        'Profiled cardinality distributions across categorical features.',
        'Identified entity primary keys and quarantined customerID to prevent model memorization.'
      ]
    },
    {
      id: 'stage-2',
      number: '02',
      title: 'Data Quality & Leakage Audit',
      status: 'completed',
      duration: '0.9s',
      summary: 'Data health verified at 94.2%. Missing cells imputed and leakage risks eliminated.',
      metrics: [
        { label: 'Overall Quality', val: '94.2%' },
        { label: 'Missing Cells', val: '11 Imputed' },
        { label: 'Duplicate Rows', val: '0 Found' },
        { label: 'Leakage Risk', val: '1 Isolated' },
      ],
      details: [
        'Imputed TotalCharges empty strings with column median ($1,397.48).',
        'Scanned for high correlation with target variable (no deterministic leak detected).',
        'Quarantined customerID feature from feature space.'
      ]
    },
    {
      id: 'stage-3',
      number: '03',
      title: 'Model Championship Benchmark',
      status: 'completed',
      duration: '3.4s',
      summary: 'Cross-validated 4 algorithms with Stratified K-Fold. LightGBM selected as champion.',
      metrics: [
        { label: 'Champion Model', val: 'LightGBM' },
        { label: 'Primary ROC-AUC', val: '0.854' },
        { label: 'Cross-Val Scheme', val: '5-Fold Stratified' },
        { label: 'Tournament Time', val: '7.9s' },
      ],
      details: [
        'Evaluated LightGBM, XGBoost, Random Forest, and Regularized Logistic Regression.',
        'Strict holdout isolation with zero test leakage.',
        'Computed full confusion matrix and SHAP feature attribution vectors.'
      ]
    },
    {
      id: 'stage-4',
      number: '04',
      title: 'Multi-Perspective Investigation',
      status: 'completed',
      duration: '2.1s',
      summary: 'Autonomous agents probed feature interactions, subgroup vulnerabilities, and nonlinear trends.',
      metrics: [
        { label: 'Hypotheses Formed', val: '12' },
        { label: 'Passed Statistical Tests', val: '8' },
        { label: 'Strong Effect Sizes', val: '5' },
        { label: 'Subgroups Probed', val: '16' },
      ],
      details: [
        'Isolated interaction between Contract Term (Month-to-month) and short tenure (<6 months).',
        'Analyzed additive churn delta when Fiber Optic is unbundled from Tech Support.',
        'Mapped Electronic Check payment method correlation with billing tenure.'
      ]
    },
    {
      id: 'stage-5',
      number: '05',
      title: 'Cross-Examination & Fact Verification',
      status: 'completed',
      duration: '1.5s',
      summary: 'Independent Critic challenged findings with counterfactual controls; Verifier resolved disputes.',
      metrics: [
        { label: 'Verified Findings', val: '2 Confirmed' },
        { label: 'Challenged Findings', val: '1 Flagged' },
        { label: 'Refuted Hypotheses', val: '4 Dropped' },
        { label: 'Mean Confidence', val: '94.0%' },
      ],
      details: [
        'Critic challenged tenure finding against demographic age bias; Verifier confirmed invariance (p < 0.001).',
        'Critic challenged Electronic Check finding; isolated confounding contract duration; downgraded to advisory.',
        'Model consensus verified across 4 distinct architectures.'
      ]
    },
    {
      id: 'stage-6',
      number: '06',
      title: 'Dashboard Contract Assembly',
      status: 'completed',
      duration: '0.4s',
      summary: 'Machine-readable UI spec compiled and rendered into the dynamic presentation layer.',
      metrics: [
        { label: 'KPIs Generated', val: '4' },
        { label: 'Plotly Charts Built', val: '4' },
        { label: 'Applicable Sections', val: '5 Active' },
        { label: 'Contract Schema', val: 'v1.0 Valid' },
      ],
      details: [
        'AutoChart heuristic selected 4 high-value Plotly specs (bar, histogram, boxplot, heatmap).',
        'Packaged structured JSON payload consumable by any REST or GraphQL consumer.',
        'Generated executive summary dossier for PDF export.'
      ]
    }
  ];

  const currentStage = stages[selectedStageIdx];

  const handleSimulateRun = () => {
    setIsRunning(true);
    setTimeout(() => {
      setIsRunning(false);
    }, 1500);
  };

  return (
    <div className="space-y-6 max-w-7xl mx-auto pb-12">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-border pb-4">
        <div>
          <div className="flex items-center gap-2">
            <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-primary/10 text-primary border border-primary/20">
              <GitFork className="w-3.5 h-3.5" />
              Autonomous Pipeline Stepper
            </span>
            <span className="font-mono text-xs text-on-surface-variant">
              Target: {datasetName}
            </span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-bold tracking-tight text-on-surface mt-1">
            AIDA 6-Stage Investigation Lifecycle
          </h1>
          <p className="text-xs sm:text-sm text-on-surface-variant mt-0.5">
            Deterministic stage gates, dependency contracts, and multi-agent audit trails.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={handleSimulateRun}
            disabled={isRunning}
            className="inline-flex items-center gap-1.5 px-3.5 py-2 rounded-xl bg-primary hover:bg-primary/90 text-white font-semibold text-xs shadow-md shadow-primary/20 transition-all disabled:opacity-50"
          >
            {isRunning ? (
              <>
                <RotateCcw className="w-3.5 h-3.5 animate-spin" />
                <span>Executing Pipeline...</span>
              </>
            ) : (
              <>
                <Play className="w-3.5 h-3.5 fill-current" />
                <span>Re-run Full Pipeline</span>
              </>
            )}
          </button>
        </div>
      </div>

      {/* Pipeline Visual Stepper Track */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3">
        {stages.map((stage, idx) => {
          const isSelected = selectedStageIdx === idx;
          return (
            <button
              key={stage.id}
              onClick={() => setSelectedStageIdx(idx)}
              className={clsx(
                "p-3.5 rounded-xl border text-left transition-all relative flex flex-col justify-between h-32",
                isSelected
                  ? "bg-surface-container border-primary ring-2 ring-primary/40 shadow-md"
                  : "bg-surface-container-low border-border/80 hover:border-primary/40"
              )}
            >
              <div className="flex items-center justify-between w-full">
                <span className="font-mono text-xs font-bold text-secondary">
                  {stage.number}
                </span>
                <CheckCircle2 className="w-4 h-4 text-emerald-400" />
              </div>

              <div>
                <h4 className="font-bold text-xs text-on-surface line-clamp-2 mt-1">
                  {stage.title}
                </h4>
                <span className="font-mono text-[10px] text-on-surface-variant block mt-1">
                  Duration: {stage.duration}
                </span>
              </div>
            </button>
          );
        })}
      </div>

      {/* Selected Stage Detail Panel */}
      <div className="bg-surface-container-low border border-border rounded-2xl p-6 shadow-sm space-y-6">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-border/80 pb-4">
          <div className="flex items-center gap-3">
            <span className="w-9 h-9 rounded-xl bg-primary/20 text-primary font-mono font-bold text-sm flex items-center justify-center border border-primary/30">
              {currentStage.number}
            </span>
            <div>
              <div className="flex items-center gap-2">
                <span className="text-[10px] font-mono uppercase px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 font-bold">
                  Exit Gate Passed
                </span>
                <span className="text-xs text-on-surface-variant font-mono">
                  Runtime: {currentStage.duration}
                </span>
              </div>
              <h2 className="text-xl font-bold text-on-surface mt-0.5">
                {currentStage.title}
              </h2>
            </div>
          </div>

          <div className="text-xs text-on-surface-variant max-w-md">
            {currentStage.summary}
          </div>
        </div>

        {/* Stage Quantitative Metrics Grid */}
        <div>
          <h3 className="text-xs font-bold uppercase tracking-wider text-on-surface-variant mb-3 flex items-center gap-1.5">
            <Cpu className="w-3.5 h-3.5 text-secondary" />
            <span>Output Artifact Telemetry</span>
          </h3>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
            {currentStage.metrics.map((metric, i) => (
              <div key={i} className="p-3.5 rounded-xl bg-surface-container border border-border/70">
                <span className="text-[11px] text-on-surface-variant block">{metric.label}</span>
                <p className="font-mono text-base font-bold text-on-surface mt-0.5">{metric.val}</p>
              </div>
            ))}
          </div>
        </div>

        {/* Stage Process Audit Log */}
        <div className="space-y-2">
          <h3 className="text-xs font-bold uppercase tracking-wider text-on-surface-variant flex items-center gap-1.5">
            <Terminal className="w-3.5 h-3.5 text-tertiary" />
            <span>Stage Execution Journal</span>
          </h3>
          <div className="space-y-2">
            {currentStage.details.map((item, idx) => (
              <div key={idx} className="p-3 rounded-lg bg-surface-container/60 border border-border/50 text-xs text-on-surface flex items-start gap-2.5">
                <span className="w-1.5 h-1.5 rounded-full bg-secondary mt-1.5 flex-shrink-0" />
                <span className="leading-relaxed">{item}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
