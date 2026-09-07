import React, { useState } from 'react';
import type { QualityReport, LeakageWarning } from '../types/contracts';
import {
  ShieldAlert,
  ShieldCheck,
  CheckCircle2,
  AlertTriangle,
  ChevronDown,
  ChevronUp,
  Sparkles
} from 'lucide-react';
import clsx from 'clsx';

interface QualityLeakageBannerProps {
  qualityReport?: QualityReport;
  leakageWarnings?: LeakageWarning[];
}

export const QualityLeakageBanner: React.FC<QualityLeakageBannerProps> = ({
  qualityReport,
  leakageWarnings = []
}) => {
  const [showCleaningAudit, setShowCleaningAudit] = useState(false);

  const hasLeakage = leakageWarnings.length > 0;
  const score = qualityReport?.overall_score ?? 92.0;

  return (
    <div className="bg-card border border-border/80 rounded-xl p-5 shadow-sm space-y-3">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        {/* Left: Quality Score & Status */}
        <div className="flex items-center gap-3.5">
          <div
            className={clsx(
              "w-12 h-12 rounded-xl flex items-center justify-center flex-shrink-0 border",
              score >= 90
                ? "bg-emerald-500/10 text-emerald-500 border-emerald-500/20"
                : (score >= 75 ? "bg-amber-500/10 text-amber-500 border-amber-500/20" : "bg-red-500/10 text-red-500 border-red-500/20")
            )}
          >
            {score >= 90 ? <ShieldCheck className="w-6 h-6" /> : <ShieldAlert className="w-6 h-6" />}
          </div>

          <div>
            <div className="flex items-center gap-2">
              <span className="text-xs font-semibold uppercase tracking-wider text-foreground/50">
                Dataset Integrity Audit
              </span>
              <span
                className={clsx(
                  "text-[10px] font-bold px-2 py-0.5 rounded-full border",
                  score >= 90
                    ? "bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border-emerald-500/20"
                    : "bg-amber-500/10 text-amber-600 border-amber-500/20"
                )}
              >
                {score >= 90 ? 'High Confidence' : 'Review Advised'}
              </span>
            </div>

            <h4 className="text-base font-bold text-foreground flex items-center gap-2 mt-0.5">
              <span>Overall Quality Health: {score.toFixed(1)}%</span>
            </h4>

            <p className="text-xs text-foreground/70 mt-0.5">
              {qualityReport?.total_rows?.toLocaleString() ?? '7,043'} rows &bull; {qualityReport?.total_cols ?? '21'} columns profiled &bull;{' '}
              {qualityReport?.missing_cells_total ? `${qualityReport.missing_cells_total} missing cells cleaned` : '0 missing cells'}
            </p>
          </div>
        </div>

        {/* Right: Quick Action / Status indicator */}
        <div className="flex items-center gap-2">
          {qualityReport?.cleaning_actions_taken && qualityReport.cleaning_actions_taken.length > 0 && (
            <button
              onClick={() => setShowCleaningAudit(!showCleaningAudit)}
              className="text-xs font-medium px-3 py-1.5 rounded-lg bg-muted/60 hover:bg-muted text-foreground/80 flex items-center gap-1.5 transition-colors border border-border/50"
            >
              <Sparkles className="w-3.5 h-3.5 text-primary" />
              <span>Cleaning Audit Trail ({qualityReport.cleaning_actions_taken.length})</span>
              {showCleaningAudit ? <ChevronUp className="w-3.5 h-3.5 ml-1" /> : <ChevronDown className="w-3.5 h-3.5 ml-1" />}
            </button>
          )}
        </div>
      </div>

      {/* Target Leakage Warnings Alert */}
      {hasLeakage && (
        <div className="bg-amber-500/10 border border-amber-500/25 rounded-lg p-3 text-xs space-y-1.5">
          <div className="flex items-center gap-2 text-amber-700 dark:text-amber-400 font-bold">
            <AlertTriangle className="w-4 h-4 flex-shrink-0" />
            <span>Target Leakage & Entity Identifier Alert</span>
          </div>
          {leakageWarnings.map((warn, i) => (
            <div key={i} className="pl-6 text-foreground/80">
              <span className="font-semibold text-foreground">{warn.column}</span>: {warn.reason}{' '}
              <span className="text-emerald-600 dark:text-emerald-400 font-medium">({warn.recommendation})</span>
            </div>
          ))}
        </div>
      )}

      {/* Cleaning Actions List */}
      {showCleaningAudit && qualityReport?.cleaning_actions_taken && (
        <div className="bg-muted/40 border border-border/60 rounded-lg p-3 text-xs space-y-1.5 pt-2">
          <span className="font-semibold text-foreground block mb-1">Autonomous Preprocessing Log:</span>
          {qualityReport.cleaning_actions_taken.map((action, idx) => (
            <div key={idx} className="flex items-start gap-2 text-foreground/80">
              <CheckCircle2 className="w-3.5 h-3.5 text-emerald-500 flex-shrink-0 mt-0.5" />
              <span>{action}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
