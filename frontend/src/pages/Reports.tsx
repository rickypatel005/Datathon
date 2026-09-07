import { useState, useEffect } from "react";
import { useStore } from '../store/useStore';
import mockData from '../mocks/mock_contracts.json';
import { AutoChart } from '../components/AutoChart';
import { InsightCard } from '../components/InsightCard';
import { QualityLeakageBanner } from '../components/QualityLeakageBanner';
import {
  Printer,
  Sparkles,
  Trophy,
  BrainCircuit,
  BarChart2,
  ShieldCheck,
  Layers
} from 'lucide-react';

export function Reports() {
  const { activeDatasetId, activeScenario } = useStore();
  const [reportData, setReportData] = useState<any>(null);

  useEffect(() => {
    // Load dataset contract for report
    const rawMock = mockData as any;
    const scenario = activeScenario === 'sales' ? rawMock.sales_forecast : rawMock.churn_dataset;
    setReportData(scenario);
  }, [activeDatasetId, activeScenario]);

  const scenario = reportData || (mockData as any).churn_dataset;
  const dashboard = scenario.dashboard;
  const discovery = scenario.discovery;
  const analysis = scenario.analysis;

  return (
    <div className="space-y-6 max-w-5xl mx-auto pb-16">
      {/* Top Header & Export Action */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-border pb-4 print:hidden">
        <div>
          <div className="flex items-center gap-2">
            <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-primary/10 text-primary border border-primary/20">
              <Sparkles className="w-3.5 h-3.5" />
              AIDA Executive Dossier
            </span>
            <span className="text-xs text-foreground/50">
              Generated for: {dashboard.dataset_name}
            </span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-bold tracking-tight text-foreground mt-1">
            Executive Intelligence Report
          </h1>
          <p className="text-xs sm:text-sm text-foreground/60 mt-0.5">
            Structured autonomous report containing evidence-backed insights, data quality audits, and validated machine learning models.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={() => window.print()}
            className="inline-flex items-center gap-1.5 px-4 py-2 rounded-xl bg-primary hover:bg-primary/90 text-primary-foreground text-xs font-semibold shadow transition-colors"
          >
            <Printer className="w-4 h-4" />
            <span>Export / Print PDF</span>
          </button>
        </div>
      </div>

      {/* Printable Report Document Sheet */}
      <div className="bg-card border border-border/80 rounded-2xl p-6 sm:p-10 shadow-sm space-y-8 print:border-none print:shadow-none print:p-0">
        
        {/* Document Title Header */}
        <div className="border-b border-border/80 pb-6">
          <div className="flex items-center justify-between text-xs text-foreground/50 mb-2">
            <span>AIDA Autonomous Analyst &bull; Confidential Assessment</span>
            <span>Date: {new Date(dashboard.generated_at).toLocaleDateString()}</span>
          </div>
          <h2 className="text-2xl font-black tracking-tight text-foreground">
            {dashboard.dataset_name}: Comprehensive Findings & Modeling Strategy
          </h2>
          <p className="text-sm text-foreground/70 mt-1 leading-relaxed">
            This autonomous executive dossier profiles dataset structure, isolates data leakage, evaluates candidate algorithms with rigorous cross-validation, and cross-examines analytical claims with statistical critics.
          </p>
        </div>

        {/* Section 1: Executive KPI Summary */}
        <div className="space-y-3">
          <h3 className="text-xs font-bold uppercase tracking-wider text-primary flex items-center gap-1.5">
            <Layers className="w-4 h-4" />
            <span>1. Executive Scorecard</span>
          </h3>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
            {dashboard.kpis.map((kpi: any) => (
              <div key={kpi.id} className="p-3.5 rounded-xl bg-muted/40 border border-border/60">
                <span className="text-[11px] text-foreground/60 block">{kpi.label}</span>
                <p className="text-xl font-black text-foreground mt-0.5">{kpi.value}</p>
                {kpi.subtitle && (
                  <span className="text-[10px] text-foreground/50 mt-1 block truncate">
                    {kpi.subtitle}
                  </span>
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Section 2: Data Quality & Preprocessing Actions */}
        <div className="space-y-3">
          <h3 className="text-xs font-bold uppercase tracking-wider text-emerald-500 flex items-center gap-1.5">
            <ShieldCheck className="w-4 h-4" />
            <span>2. Data Integrity & Leakage Governance</span>
          </h3>
          <QualityLeakageBanner
            qualityReport={discovery.quality_report}
            leakageWarnings={discovery.leakage_report.warnings}
          />
        </div>

        {/* Section 3: Verified Analytical Insights */}
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-xs font-bold uppercase tracking-wider text-sky-500 flex items-center gap-1.5">
              <BrainCircuit className="w-4 h-4" />
              <span>3. Validated Business Insights</span>
            </h3>
            <span className="text-xs text-foreground/50 font-medium">
              {dashboard.insights.length} Evidence-Backed Findings
            </span>
          </div>

          <div className="space-y-4">
            {dashboard.insights.map((insight: any) => (
              <InsightCard key={insight.id} insight={insight} defaultExpanded={true} />
            ))}
          </div>
        </div>

        {/* Section 4: Key Structural Charts */}
        <div className="space-y-4 page-break-before">
          <h3 className="text-xs font-bold uppercase tracking-wider text-purple-500 flex items-center gap-1.5">
            <BarChart2 className="w-4 h-4" />
            <span>4. Evidence Visualizations</span>
          </h3>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {dashboard.charts.slice(0, 2).map((chart: any) => (
              <AutoChart key={chart.id} spec={chart} />
            ))}
          </div>
        </div>

        {/* Section 5: Model Championship & Governance */}
        <div className="space-y-3">
          <h3 className="text-xs font-bold uppercase tracking-wider text-amber-500 flex items-center gap-1.5">
            <Trophy className="w-4 h-4" />
            <span>5. Model Championship Benchmark</span>
          </h3>
          <div className="bg-muted/30 border border-border/80 rounded-xl p-4 text-xs space-y-3">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-border/60 pb-3">
              <div>
                <span className="text-foreground/50 uppercase text-[10px]">Production Selected Algorithm</span>
                <p className="text-base font-bold text-foreground">{analysis.champion_model}</p>
              </div>
              <div className="text-right">
                <span className="text-foreground/50 uppercase text-[10px]">Validation Protocol</span>
                <p className="font-semibold text-foreground">{analysis.validation_strategy.method}</p>
              </div>
            </div>

            <p className="text-foreground/80 leading-relaxed">
              Models were evaluated with strict holdout isolation. The champion achieved a primary metric of{' '}
              <strong>
                {dashboard.championship_summary.primary_metric_name} ={' '}
                {dashboard.championship_summary.primary_metric_value}
              </strong>{' '}
              across {dashboard.championship_summary.total_models_evaluated} competing architectures.
            </p>
          </div>
        </div>

        {/* Sign-off footer */}
        <div className="border-t border-border/80 pt-4 flex items-center justify-between text-xs text-foreground/40">
          <span>AIDA Autonomous Intelligence Agent Suite</span>
          <span>System Verified &bull; ISO-Compliant Analytic Process</span>
        </div>
      </div>
    </div>
  );
}
