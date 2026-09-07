import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useStore } from '../store/useStore';
import mockData from '../mocks/mock_contracts.json';
import { AutoChart } from '../components/AutoChart';
import { InsightCard } from '../components/InsightCard';
import { QualityLeakageBanner } from '../components/QualityLeakageBanner';
import {
  Search,
  Plus,
  ArrowRight,
  Printer,
  Sparkles,
  Trophy,
  BrainCircuit,
  BarChart2,
  ShieldCheck,
  Layers,
  CheckCircle2,
  FileSpreadsheet
} from 'lucide-react';

interface ReportItem {
  id: string;
  name: string;
  dateAnalyzed: string;
  records: string;
  columns: number;
  quality: string;
  status: 'Completed' | 'Processing';
  scenario: 'sales' | 'churn';
}

export function Reports() {
  const navigate = useNavigate();
  const { setActiveScenario, setDemoMode } = useStore();
  const [viewMode, setViewMode] = useState<'list' | 'dossier'>('list');
  const [searchQuery, setSearchQuery] = useState('');

  // Datasets matching Screen 8
  const reportsList: ReportItem[] = [
    {
      id: 'rep-1',
      name: 'Customer_Sales_Data',
      dateAnalyzed: '07 Sep 2026, 01:24 PM',
      records: '12,482',
      columns: 18,
      quality: '94.8%',
      status: 'Completed',
      scenario: 'sales'
    },
    {
      id: 'rep-2',
      name: 'Marketing_Campaigns',
      dateAnalyzed: '05 Sep 2026, 10:12 AM',
      records: '8,231',
      columns: 14,
      quality: '92.1%',
      status: 'Completed',
      scenario: 'churn'
    },
    {
      id: 'rep-3',
      name: 'Hospital_Records',
      dateAnalyzed: '03 Sep 2026, 04:45 PM',
      records: '5,642',
      columns: 22,
      quality: '90.3%',
      status: 'Completed',
      scenario: 'sales'
    }
  ];

  const filteredReports = reportsList.filter((r) =>
    r.name.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const handleSelectReport = (report: ReportItem) => {
    setActiveScenario(report.scenario);
    setDemoMode(true);
    navigate('/');
  };

  // Raw mock for executive dossier
  const rawMock = mockData as any;
  const scenario = rawMock.sales_forecast;
  const dashboard = scenario.dashboard;
  const discovery = scenario.discovery;
  const analysis = scenario.analysis;

  return (
    <div className="space-y-6 max-w-7xl mx-auto pb-16 animate-in fade-in duration-200">
      {/* ─────────────────────────────────────────────────────────────
          MODE 1: "YOUR REPORTS" (Screen 8 from Reference Image)
         ───────────────────────────────────────────────────────────── */}
      {viewMode === 'list' && (
        <div className="space-y-6">
          {/* Header Row */}
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-[#1e293b] pb-4">
            <div>
              <div className="flex items-center gap-2">
                <h1 className="text-2xl sm:text-3xl font-black text-white tracking-tight">
                  Your Reports
                </h1>
                <button
                  onClick={() => setViewMode('dossier')}
                  className="text-[11px] font-semibold text-indigo-400 hover:text-indigo-300 ml-2 px-2 py-0.5 rounded bg-indigo-500/10 border border-indigo-500/20"
                >
                  View Full Dossier
                </button>
              </div>
              <p className="text-xs text-slate-400 mt-1">
                View and manage all your analyzed datasets.
              </p>
            </div>

            {/* Controls: Search & New Analysis Button */}
            <div className="flex items-center gap-3">
              <div className="relative">
                <Search className="w-3.5 h-3.5 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
                <input
                  type="text"
                  placeholder="Search reports..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="bg-[#0e1629] border border-[#1e293b] focus:border-indigo-500 text-xs text-white pl-8 pr-3 py-2 rounded-xl focus:outline-none w-48 sm:w-60 shadow-inner"
                />
              </div>

              <button
                onClick={() => navigate('/new-analysis')}
                className="px-4 py-2 text-xs font-bold text-white bg-gradient-to-r from-[#6366f1] to-[#4f46e5] hover:from-[#5558e6] hover:to-[#4338ca] rounded-xl shadow-lg shadow-indigo-500/25 flex items-center gap-1.5 transition-all flex-shrink-0"
              >
                <Plus className="w-3.5 h-3.5" />
                <span>New Analysis</span>
              </button>
            </div>
          </div>

          {/* Reports Table (Screen 8) */}
          <div className="bg-[#0e1629] border border-[#1e293b] rounded-2xl overflow-hidden shadow-xl">
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead className="bg-[#091124] text-slate-400 font-semibold border-b border-[#1e293b]">
                  <tr>
                    <th className="py-3.5 px-5">Dataset Name</th>
                    <th className="py-3.5 px-4">Date Analyzed</th>
                    <th className="py-3.5 px-4">Records</th>
                    <th className="py-3.5 px-4">Columns</th>
                    <th className="py-3.5 px-4">Quality</th>
                    <th className="py-3.5 px-4">Status</th>
                    <th className="py-3.5 px-5 text-right">Action</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-[#1e293b] text-slate-200">
                  {filteredReports.map((report) => (
                    <tr
                      key={report.id}
                      onClick={() => handleSelectReport(report)}
                      className="hover:bg-[#121c33] cursor-pointer transition-colors group"
                    >
                      <td className="py-4 px-5">
                        <div className="flex items-center gap-2.5">
                          <div className="p-1.5 rounded-lg bg-indigo-500/10 text-indigo-400">
                            <FileSpreadsheet className="w-4 h-4" />
                          </div>
                          <span className="font-bold text-white group-hover:text-indigo-300 transition-colors">
                            {report.name}
                          </span>
                        </div>
                      </td>

                      <td className="py-4 px-4 text-slate-400 font-mono text-[11px]">
                        {report.dateAnalyzed}
                      </td>

                      <td className="py-4 px-4 font-mono font-medium">
                        {report.records}
                      </td>

                      <td className="py-4 px-4 font-mono font-medium">
                        {report.columns}
                      </td>

                      <td className="py-4 px-4">
                        <span className="font-bold text-emerald-400 font-mono">
                          {report.quality}
                        </span>
                      </td>

                      <td className="py-4 px-4">
                        <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[10px] font-bold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                          <CheckCircle2 className="w-3 h-3" />
                          <span>{report.status}</span>
                        </span>
                      </td>

                      <td className="py-4 px-5 text-right">
                        <div className="inline-flex items-center justify-center w-7 h-7 rounded-lg bg-[#16203a] group-hover:bg-indigo-600 group-hover:text-white text-slate-400 transition-all">
                          <ArrowRight className="w-3.5 h-3.5" />
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {filteredReports.length === 0 && (
              <div className="py-12 text-center text-slate-500 text-xs">
                No reports matching "{searchQuery}"
              </div>
            )}
          </div>
        </div>
      )}

      {/* ─────────────────────────────────────────────────────────────
          MODE 2: EXECUTIVE INTELLIGENCE DOSSIER (Printable Report)
         ───────────────────────────────────────────────────────────── */}
      {viewMode === 'dossier' && (
        <div className="space-y-6">
          {/* Top Header & Toggle Back */}
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-[#1e293b] pb-4 print:hidden">
            <div>
              <div className="flex items-center gap-2">
                <button
                  onClick={() => setViewMode('list')}
                  className="text-xs font-semibold text-slate-400 hover:text-white transition-colors"
                >
                  &larr; Back to Reports List
                </button>
                <span className="text-slate-600">&bull;</span>
                <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
                  <Sparkles className="w-3.5 h-3.5" />
                  AIDA Executive Dossier
                </span>
              </div>
              <h1 className="text-2xl sm:text-3xl font-black text-white tracking-tight mt-1">
                Executive Intelligence Report
              </h1>
              <p className="text-xs text-slate-400 mt-0.5">
                Structured autonomous report containing evidence-backed insights, data quality audits, and validated ML models.
              </p>
            </div>

            <div className="flex items-center gap-2">
              <button
                onClick={() => window.print()}
                className="inline-flex items-center gap-1.5 px-4 py-2 rounded-xl bg-gradient-to-r from-indigo-500 to-indigo-600 hover:from-indigo-600 hover:to-indigo-700 text-white text-xs font-bold shadow-lg shadow-indigo-500/20 transition-all"
              >
                <Printer className="w-4 h-4" />
                <span>Export / Print PDF</span>
              </button>
            </div>
          </div>

          {/* Printable Sheet */}
          <div className="bg-[#0e1629] border border-[#1e293b] rounded-2xl p-6 sm:p-10 shadow-xl space-y-8 print:border-none print:shadow-none print:p-0">
            {/* Document Title Header */}
            <div className="border-b border-[#1e293b] pb-6">
              <div className="flex items-center justify-between text-xs text-slate-400 mb-2">
                <span>AIDA Autonomous Analyst &bull; Confidential Assessment</span>
                <span>Date: {new Date(dashboard.generated_at).toLocaleDateString()}</span>
              </div>
              <h2 className="text-2xl font-black text-white tracking-tight">
                {dashboard.dataset_name}: Comprehensive Findings & Modeling Strategy
              </h2>
              <p className="text-xs sm:text-sm text-slate-300 mt-1 leading-relaxed">
                This autonomous executive dossier profiles dataset structure, isolates data leakage, evaluates candidate algorithms with rigorous cross-validation, and cross-examines analytical claims with statistical critics.
              </p>
            </div>

            {/* Scorecard */}
            <div className="space-y-3">
              <h3 className="text-xs font-bold uppercase tracking-wider text-indigo-400 flex items-center gap-1.5">
                <Layers className="w-4 h-4" />
                <span>1. Executive Scorecard</span>
              </h3>
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                {dashboard.kpis.map((kpi: any) => (
                  <div key={kpi.id} className="p-3.5 rounded-xl bg-[#091124] border border-[#1e293b]">
                    <span className="text-[11px] text-slate-400 block">{kpi.label}</span>
                    <p className="text-xl font-black text-white mt-0.5">{kpi.value}</p>
                    {kpi.subtitle && (
                      <span className="text-[10px] text-slate-400 mt-1 block truncate">
                        {kpi.subtitle}
                      </span>
                    )}
                  </div>
                ))}
              </div>
            </div>

            {/* Quality */}
            <div className="space-y-3">
              <h3 className="text-xs font-bold uppercase tracking-wider text-emerald-400 flex items-center gap-1.5">
                <ShieldCheck className="w-4 h-4" />
                <span>2. Data Integrity & Leakage Governance</span>
              </h3>
              <QualityLeakageBanner
                qualityReport={discovery.quality_report}
                leakageWarnings={discovery.leakage_report.warnings}
              />
            </div>

            {/* Insights */}
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <h3 className="text-xs font-bold uppercase tracking-wider text-sky-400 flex items-center gap-1.5">
                  <BrainCircuit className="w-4 h-4" />
                  <span>3. Validated Business Insights</span>
                </h3>
                <span className="text-xs text-slate-400 font-medium">
                  {dashboard.insights.length} Evidence-Backed Findings
                </span>
              </div>

              <div className="space-y-4">
                {dashboard.insights.map((insight: any) => (
                  <InsightCard key={insight.id} insight={insight} defaultExpanded={true} />
                ))}
              </div>
            </div>

            {/* Visualizations */}
            <div className="space-y-4">
              <h3 className="text-xs font-bold uppercase tracking-wider text-purple-400 flex items-center gap-1.5">
                <BarChart2 className="w-4 h-4" />
                <span>4. Evidence Visualizations</span>
              </h3>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                {dashboard.charts.slice(0, 2).map((chart: any) => (
                  <AutoChart key={chart.id} spec={chart} />
                ))}
              </div>
            </div>

            {/* Model Championship */}
            <div className="space-y-3">
              <h3 className="text-xs font-bold uppercase tracking-wider text-amber-400 flex items-center gap-1.5">
                <Trophy className="w-4 h-4" />
                <span>5. Model Championship Benchmark</span>
              </h3>
              <div className="bg-[#091124] border border-[#1e293b] rounded-xl p-4 text-xs space-y-3">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-[#1e293b] pb-3">
                  <div>
                    <span className="text-slate-400 uppercase text-[10px]">Production Selected Algorithm</span>
                    <p className="text-base font-bold text-white">{analysis.champion_model}</p>
                  </div>
                  <div className="text-right">
                    <span className="text-slate-400 uppercase text-[10px]">Validation Protocol</span>
                    <p className="font-semibold text-white">{analysis.validation_strategy.method}</p>
                  </div>
                </div>

                <p className="text-slate-300 leading-relaxed">
                  Models were evaluated with strict holdout isolation. The champion achieved a primary metric of{' '}
                  <strong className="text-white">
                    {dashboard.championship_summary.primary_metric_name} ={' '}
                    {dashboard.championship_summary.primary_metric_value}
                  </strong>{' '}
                  across {dashboard.championship_summary.total_models_evaluated} competing architectures.
                </p>
              </div>
            </div>

            {/* Sign-off footer */}
            <div className="border-t border-[#1e293b] pt-4 flex items-center justify-between text-xs text-slate-500">
              <span>AIDA Autonomous Intelligence Agent Suite</span>
              <span>System Verified &bull; ISO-Compliant Analytic Process</span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
