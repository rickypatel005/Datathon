import { useState } from 'react';
import { useStore } from '../store/useStore';
import mockData from '../mocks/mock_contracts.json';
import { InsightCard } from '../components/InsightCard';
import type { InsightContract } from '../types/contracts';
import {
  Lightbulb,
  Search,
  CheckCircle2,
  AlertCircle
} from 'lucide-react';
import clsx from 'clsx';

export function Insights() {
  const { activeScenario, dashboardContract } = useStore();
  const [filterStatus, setFilterStatus] = useState<string>('all');
  const [searchQuery, setSearchQuery] = useState<string>('');

  const scenario = (mockData as any)[activeScenario === 'sales' ? 'sales_forecast' : 'churn_dataset'];
  const allInsights: InsightContract[] = dashboardContract?.insights || scenario.dashboard.insights;

  const filteredInsights = allInsights.filter((ins) => {
    const matchesStatus = filterStatus === 'all' || ins.status === filterStatus;
    const matchesSearch =
      ins.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      ins.claim.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesStatus && matchesSearch;
  });

  const verifiedCount = allInsights.filter((i) => i.status === 'verified').length;
  const challengedCount = allInsights.filter((i) => i.status === 'challenged').length;

  return (
    <div className="space-y-6 max-w-6xl mx-auto pb-12">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-border pb-4">
        <div>
          <div className="flex items-center gap-2">
            <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-tertiary/10 text-tertiary border border-tertiary/20">
              <Lightbulb className="w-3.5 h-3.5" />
              Insights Workspace
            </span>
            <span className="font-mono text-xs text-on-surface-variant">
              {allInsights.length} Evidence-Backed Findings
            </span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-bold tracking-tight text-on-surface mt-1">
            Multi-Perspective Validated Insights
          </h1>
          <p className="text-xs sm:text-sm text-on-surface-variant mt-0.5">
            Statistical assertions investigated by analytical agents, challenged by critics, and resolved with formal verification.
          </p>
        </div>
      </div>

      {/* Filter & Search Bar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 bg-surface-container-low p-3 rounded-xl border border-border/80">
        <div className="flex items-center gap-2">
          <button
            onClick={() => setFilterStatus('all')}
            className={clsx(
              "px-3 py-1.5 rounded-lg text-xs font-medium transition-colors",
              filterStatus === 'all'
                ? "bg-primary text-white font-semibold"
                : "text-on-surface-variant hover:text-on-surface hover:bg-surface-container"
            )}
          >
            All ({allInsights.length})
          </button>
          <button
            onClick={() => setFilterStatus('verified')}
            className={clsx(
              "px-3 py-1.5 rounded-lg text-xs font-medium transition-colors flex items-center gap-1.5",
              filterStatus === 'verified'
                ? "bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 font-semibold"
                : "text-on-surface-variant hover:text-on-surface hover:bg-surface-container"
            )}
          >
            <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
            <span>Verified ({verifiedCount})</span>
          </button>
          <button
            onClick={() => setFilterStatus('challenged')}
            className={clsx(
              "px-3 py-1.5 rounded-lg text-xs font-medium transition-colors flex items-center gap-1.5",
              filterStatus === 'challenged'
                ? "bg-amber-500/20 text-amber-400 border border-amber-500/30 font-semibold"
                : "text-on-surface-variant hover:text-on-surface hover:bg-surface-container"
            )}
          >
            <AlertCircle className="w-3.5 h-3.5 text-amber-400" />
            <span>Challenged ({challengedCount})</span>
          </button>
        </div>

        <div className="relative w-full sm:w-64">
          <Search className="w-3.5 h-3.5 absolute left-3 top-2.5 text-on-surface-variant" />
          <input
            type="text"
            placeholder="Search claims or metrics..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full bg-surface-container border border-border/80 rounded-lg pl-9 pr-3 py-1.5 text-xs text-on-surface placeholder:text-on-surface-variant/50 outline-none focus:border-primary"
          />
        </div>
      </div>

      {/* Insights Cards List */}
      <div className="space-y-4">
        {filteredInsights.length === 0 ? (
          <div className="text-center py-12 text-on-surface-variant text-xs">
            No insights found matching your criteria.
          </div>
        ) : (
          filteredInsights.map((insight) => (
            <InsightCard key={insight.id} insight={insight} defaultExpanded={true} />
          ))
        )}
      </div>
    </div>
  );
}
