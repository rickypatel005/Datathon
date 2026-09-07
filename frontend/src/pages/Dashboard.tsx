import { useEffect, useState } from 'react';
import { useStore } from '../store/useStore';
import { fetchWithAuth, API_BASE_URL } from '../utils/apiClient';
import type { DashboardContract, AnalysisContract, KPICard, PlotlyChartSpec, InsightContract } from '../types/contracts';
import mockData from '../mocks/mock_contracts.json';

import { AutoChart } from '../components/AutoChart';
import { InsightCard } from '../components/InsightCard';
import { ModelChampionship } from '../components/ModelChampionship';
import { QualityLeakageBanner } from '../components/QualityLeakageBanner';
import { PipelineProgress } from '../components/PipelineProgress';

import {
  Sparkles,
  Database,
  BarChart2,
  BrainCircuit,
  Trophy,
  CheckCircle,
  AlertTriangle,
  Calendar,
  RefreshCw
} from 'lucide-react';
import clsx from 'clsx';

export function Dashboard() {
  const {
    activeDatasetId,
    isDemoMode,
    setDemoMode,
    activeScenario,
    setActiveScenario,
    dashboardContract,
    setDashboardContract,
    pipelineProgress,
    setPipelineProgress
  } = useStore();

  const [isLoading, setIsLoading] = useState(false);
  const [isTriggeringPipeline, setIsTriggeringPipeline] = useState(false);
  const [analysisData, setAnalysisData] = useState<AnalysisContract | null>(null);

  // Helper to load scenario data
  const loadScenario = (scenarioKey: 'churn' | 'sales') => {
    const rawMock = mockData as any;
    const scenario = scenarioKey === 'churn' ? rawMock.churn_dataset : rawMock.sales_forecast;
    if (scenario) {
      setDashboardContract(scenario.dashboard);
      setAnalysisData(scenario.analysis);
      setPipelineProgress({
        dataset_id: scenario.dashboard.dataset_id,
        is_running: false,
        overall_progress: 100,
        current_stage: 'dashboard_assembly',
        stages: [
          { stage: 'discovery', label: 'Dataset Discovery & Fingerprinting', description: 'Semantic schema inference completed', status: 'completed', duration_sec: 1.1 },
          { stage: 'quality_audit', label: 'Data Quality & Leakage Audit', description: 'Integrity verified, ID features quarantined', status: 'completed', duration_sec: 0.9 },
          { stage: 'model_championship', label: 'Model Championship Benchmark', description: 'Candidate algorithms cross-validated', status: 'completed', duration_sec: 3.2 },
          { stage: 'insight_investigation', label: 'Multi-Perspective Investigation', description: 'Statistical claims extracted', status: 'completed', duration_sec: 2.0 },
          { stage: 'fact_verification', label: 'Cross-Examination & Verification', description: 'Claims checked against counterfactuals', status: 'completed', duration_sec: 1.4 },
          { stage: 'dashboard_assembly', label: 'Dashboard Contract Assembly', description: 'Machine-readable UI spec generated', status: 'completed', duration_sec: 0.4 }
        ],
        logs: [
          '[AIDA Engine] Dataset loaded and schema profiled.',
          '[Discovery] Inferred target candidate & column entities.',
          '[Quality] Quarantined target leakage and entity identifiers.',
          '[Championship] Stratified cross-validation completed across all models.',
          '[Investigation] High-confidence findings verified by agent panel.',
          '[Ready] Contract assembled and published to presentation layer.'
        ]
      });
    }
  };

  // Load contract from backend or fallback to demo
  const loadDashboardData = async () => {
    setIsLoading(true);
    try {
      if (isDemoMode || !activeDatasetId) {
        loadScenario(activeScenario);
      } else {
        const res = await fetchWithAuth(`${API_BASE_URL}/api/pipeline/dashboard/${activeDatasetId}`);
        if (res.ok) {
          const data: DashboardContract = await res.json();
          setDashboardContract(data);

          // Also fetch championship analysis
          const champRes = await fetchWithAuth(`${API_BASE_URL}/api/pipeline/championship/${activeDatasetId}`);
          if (champRes.ok) {
            setAnalysisData(await champRes.json());
          }

          // Fetch pipeline status
          const statusRes = await fetchWithAuth(`${API_BASE_URL}/api/pipeline/status/${activeDatasetId}`);
          if (statusRes.ok) {
            setPipelineProgress(await statusRes.json());
          }
        } else {
          // Fall back gracefully
          loadScenario(activeScenario);
        }
      }
    } catch (err) {
      console.warn("Backend pipeline fetch failed, falling back to mock contract:", err);
      loadScenario(activeScenario);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadDashboardData();
  }, [activeDatasetId, isDemoMode, activeScenario]);

  // Handler to trigger live pipeline run
  const handleRunPipeline = async () => {
    setIsTriggeringPipeline(true);
    const targetId = activeDatasetId || (activeScenario === 'churn' ? 'ds-churn-901' : 'ds-sales-502');

    try {
      const res = await fetchWithAuth(`${API_BASE_URL}/api/pipeline/run/${targetId}`, {
        method: 'POST'
      });
      if (res.ok) {
        const data = await res.json();
        if (data.progress) {
          setPipelineProgress(data.progress);
        }
      }
    } catch (e) {
      console.warn("Could not reach backend pipeline trigger, simulating locally", e);
    } finally {
      setIsTriggeringPipeline(false);
    }
  };

  const contract = dashboardContract || (mockData as any).churn_dataset.dashboard;

  const getKPIIcon = (iconName?: string) => {
    switch (iconName) {
      case 'Database': return <Database className="w-5 h-5 text-sky-500" />;
      case 'CheckCircle': return <CheckCircle className="w-5 h-5 text-emerald-500" />;
      case 'Trophy': return <Trophy className="w-5 h-5 text-amber-500" />;
      case 'AlertTriangle': return <AlertTriangle className="w-5 h-5 text-red-500" />;
      case 'Calendar': return <Calendar className="w-5 h-5 text-purple-500" />;
      default: return <BrainCircuit className="w-5 h-5 text-primary" />;
    }
  };

  return (
    <div className="space-y-6 max-w-7xl mx-auto pb-12">
      {/* Top Header & Demo Controls */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-card border border-border/80 rounded-2xl p-5 shadow-sm">
        <div>
          <div className="flex items-center gap-2">
            <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-primary/10 text-primary border border-primary/20">
              <Sparkles className="w-3.5 h-3.5" />
              AIDA Autonomous Intelligence
            </span>
            <span className="text-xs text-foreground/50 font-mono">
              Dataset: {contract.dataset_name}
            </span>
          </div>

          <h1 className="text-2xl sm:text-3xl font-bold tracking-tight text-foreground mt-1">
            Autonomous Insights Dashboard
          </h1>
          <p className="text-xs sm:text-sm text-foreground/60 mt-0.5">
            Dataset-agnostic automated profiling, multi-model championship, and fact-verified insights.
          </p>
        </div>

        {/* Demo Switcher & Pipeline Actions */}
        <div className="flex flex-wrap items-center gap-2.5">
          <div className="bg-muted/60 p-1 rounded-xl border border-border flex items-center gap-1">
            <button
              onClick={() => {
                setDemoMode(true);
                setActiveScenario('churn');
              }}
              className={clsx(
                "px-3 py-1.5 text-xs font-medium rounded-lg transition-all",
                isDemoMode && activeScenario === 'churn'
                  ? "bg-primary text-primary-foreground shadow-sm"
                  : "text-foreground/70 hover:text-foreground"
              )}
            >
              Demo: Churn (Classification)
            </button>
            <button
              onClick={() => {
                setDemoMode(true);
                setActiveScenario('sales');
              }}
              className={clsx(
                "px-3 py-1.5 text-xs font-medium rounded-lg transition-all",
                isDemoMode && activeScenario === 'sales'
                  ? "bg-primary text-primary-foreground shadow-sm"
                  : "text-foreground/70 hover:text-foreground"
              )}
            >
              Demo: Sales (Time Series)
            </button>
          </div>

          <button
            onClick={loadDashboardData}
            title="Refresh from Pipeline"
            className="p-2 rounded-lg border border-border bg-card hover:bg-muted text-foreground/70 transition-colors"
          >
            <RefreshCw className={clsx("w-4 h-4", isLoading && "animate-spin text-primary")} />
          </button>
        </div>
      </div>

      {/* Dynamic KPI Cards Row (from contract) */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {contract.kpis.map((kpi: KPICard) => (
          <div
            key={kpi.id}
            className="bg-card border border-border/80 hover:border-primary/40 rounded-xl p-4 shadow-sm transition-all flex flex-col justify-between"
          >
            <div className="flex items-center justify-between gap-2">
              <span className="text-xs font-medium text-foreground/60 tracking-tight">
                {kpi.label}
              </span>
              <div className="p-2 rounded-lg bg-muted/50">
                {getKPIIcon(kpi.icon_name)}
              </div>
            </div>

            <div className="mt-2">
              <div className="flex items-baseline gap-2">
                <span className="text-2xl font-bold tracking-tight text-foreground">
                  {kpi.value}
                </span>
                {kpi.change && (
                  <span
                    className={clsx(
                      "text-xs font-semibold px-1.5 py-0.5 rounded",
                      kpi.is_positive
                        ? "bg-emerald-500/10 text-emerald-600 dark:text-emerald-400"
                        : "bg-red-500/10 text-red-600 dark:text-red-400"
                    )}
                  >
                    {kpi.change}
                  </span>
                )}
              </div>

              {kpi.subtitle && (
                <p className="text-xs text-foreground/50 mt-1 truncate">
                  {kpi.subtitle}
                </p>
              )}
            </div>
          </div>
        ))}
      </div>

      {/* Pipeline Stage Tracker */}
      {pipelineProgress && (
        <PipelineProgress
          progress={pipelineProgress}
          onRunPipeline={handleRunPipeline}
          isTriggering={isTriggeringPipeline}
        />
      )}

      {/* Dataset Integrity & Leakage Warning Banner */}
      {contract.applicable_sections.data_quality && (
        <QualityLeakageBanner
          qualityReport={(mockData as any)[activeScenario === 'sales' ? 'sales_forecast' : 'churn_dataset']?.discovery?.quality_report}
          leakageWarnings={(mockData as any)[activeScenario === 'sales' ? 'sales_forecast' : 'churn_dataset']?.discovery?.leakage_report?.warnings}
        />
      )}

      {/* Auto-Generated Visualizations Grid */}
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-lg font-bold text-foreground tracking-tight flex items-center gap-2">
              <BarChart2 className="w-5 h-5 text-primary" />
              <span>Automated Structural Visualizations</span>
            </h2>
            <p className="text-xs text-foreground/60">
              Heuristically selected charts matching data distributions, temporal signals, and segment relationships.
            </p>
          </div>
          <span className="text-xs text-foreground/50 font-medium">
            {contract.charts.filter((c: PlotlyChartSpec) => c.applicable).length} Charts Displayed
          </span>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
          {contract.charts
            .filter((c: PlotlyChartSpec) => c.applicable)
            .map((chart: PlotlyChartSpec) => (
              <AutoChart key={chart.id} spec={chart} />
            ))}
        </div>
      </div>

      {/* Validated Insights & Multi-Perspective Investigation */}
      {contract.applicable_sections.insights_investigation && (
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-lg font-bold text-foreground tracking-tight flex items-center gap-2">
                <BrainCircuit className="w-5 h-5 text-emerald-500" />
                <span>Multi-Perspective Validated Insights</span>
              </h2>
              <p className="text-xs text-foreground/60">
                Agent-formulated assertions cross-examined by statistical critics and verified across candidate algorithms.
              </p>
            </div>
            <span className="text-xs text-foreground/50 font-medium">
              {contract.insights.length} Insights Identified
            </span>
          </div>

          <div className="space-y-4">
            {contract.insights.map((insight: InsightContract) => (
              <InsightCard key={insight.id} insight={insight} />
            ))}
          </div>
        </div>
      )}

      {/* Model Championship & Validation Governance */}
      {contract.applicable_sections.model_championship && analysisData && (
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-lg font-bold text-foreground tracking-tight flex items-center gap-2">
                <Trophy className="w-5 h-5 text-amber-500" />
                <span>Model Championship Benchmark</span>
              </h2>
              <p className="text-xs text-foreground/60">
                Multi-algorithm tournament with leak-free cross validation and error diagnostic breakdown.
              </p>
            </div>
          </div>

          <ModelChampionship analysis={analysisData} />
        </div>
      )}
    </div>
  );
}
