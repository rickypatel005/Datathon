import React, { useState } from 'react';
import type { AnalysisContract } from '../types/contracts';
import {
  Trophy,
  Award,
  Clock,
  AlertOctagon
} from 'lucide-react';
import clsx from 'clsx';

interface ModelChampionshipProps {
  analysis: AnalysisContract;
}

export const ModelChampionship: React.FC<ModelChampionshipProps> = ({ analysis }) => {
  const [selectedTab, setSelectedTab] = useState<'leaderboard' | 'features' | 'errors'>('leaderboard');

  const { models, feature_importance, error_analysis, validation_strategy, task_type } = analysis;

  const champion = models.find((m) => m.is_champion) || models[0];

  return (
    <div className="bg-card border border-border rounded-xl p-6 shadow-sm space-y-6">
      {/* Header & Champion Showcase Banner */}
      <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4 border-b border-border/80 pb-5">
        <div>
          <div className="flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-amber-500 mb-1">
            <Trophy className="w-4 h-4" />
            <span>Automated Model Championship</span>
          </div>
          <h3 className="text-xl font-bold text-foreground tracking-tight">
            Algorithmic Benchmark & Validation Governance
          </h3>
          <p className="text-xs text-foreground/70 mt-1">
            Task: <span className="font-semibold text-foreground uppercase">{task_type.replace('_', ' ')}</span> &bull; Protocol: <span className="font-medium text-foreground">{validation_strategy.method}</span>
          </p>
        </div>

        {champion && (
          <div className="bg-gradient-to-r from-amber-500/10 via-primary/10 to-transparent border border-amber-500/30 rounded-xl p-3.5 flex items-center gap-3.5">
            <div className="w-10 h-10 rounded-full bg-amber-500/20 text-amber-500 flex items-center justify-center flex-shrink-0 shadow-inner">
              <Award className="w-6 h-6" />
            </div>
            <div>
              <div className="flex items-center gap-1.5">
                <span className="text-[10px] font-bold text-amber-600 dark:text-amber-400 uppercase tracking-wider">Champion Selected</span>
                <span className="bg-emerald-500/20 text-emerald-600 dark:text-emerald-400 text-[10px] font-semibold px-1.5 py-0.2 rounded">Production Candidate</span>
              </div>
              <p className="font-bold text-sm text-foreground">{champion.model_name}</p>
              <div className="flex items-center gap-3 text-xs text-foreground/70 mt-0.5">
                <span>CV Score: <strong className="text-foreground">{champion.cv_mean.toFixed(3)}</strong> ±{champion.cv_std.toFixed(3)}</span>
                <span>Train Time: <strong className="text-foreground">{champion.training_time_sec}s</strong></span>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Navigation Tabs */}
      <div className="flex items-center gap-2 border-b border-border">
        <button
          onClick={() => setSelectedTab('leaderboard')}
          className={clsx(
            "px-4 py-2 text-xs font-semibold border-b-2 transition-colors",
            selectedTab === 'leaderboard'
              ? "border-primary text-primary"
              : "border-transparent text-foreground/60 hover:text-foreground"
          )}
        >
          Model Leaderboard ({models.length})
        </button>

        <button
          onClick={() => setSelectedTab('features')}
          className={clsx(
            "px-4 py-2 text-xs font-semibold border-b-2 transition-colors",
            selectedTab === 'features'
              ? "border-primary text-primary"
              : "border-transparent text-foreground/60 hover:text-foreground"
          )}
        >
          Feature Importance ({feature_importance?.length || 0})
        </button>

        <button
          onClick={() => setSelectedTab('errors')}
          className={clsx(
            "px-4 py-2 text-xs font-semibold border-b-2 transition-colors",
            selectedTab === 'errors'
              ? "border-primary text-primary"
              : "border-transparent text-foreground/60 hover:text-foreground"
          )}
        >
          Error & Residual Breakdown
        </button>
      </div>

      {/* Tab 1: Leaderboard */}
      {selectedTab === 'leaderboard' && (
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs border-collapse">
            <thead>
              <tr className="border-b border-border/80 text-foreground/50 uppercase tracking-wider font-semibold">
                <th className="py-2.5 px-3">Rank & Model</th>
                <th className="py-2.5 px-3">Algorithm</th>
                <th className="py-2.5 px-3">Primary Metric</th>
                <th className="py-2.5 px-3">CV Mean (± Std)</th>
                <th className="py-2.5 px-3">Fit Time</th>
                <th className="py-2.5 px-3">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border/40">
              {models.map((model, idx) => {
                const primaryMetricVal = model.metrics.roc_auc ?? model.metrics.r2_score ?? model.metrics.accuracy ?? model.metrics.mae ?? 0;
                const metricName = model.metrics.roc_auc ? 'ROC-AUC' : (model.metrics.r2_score ? 'R²' : (model.metrics.mae ? 'MAE' : 'Accuracy'));

                return (
                  <tr
                    key={model.model_id}
                    className={clsx(
                      "hover:bg-muted/30 transition-colors",
                      model.is_champion ? "bg-amber-500/5 font-medium" : ""
                    )}
                  >
                    <td className="py-3 px-3">
                      <div className="flex items-center gap-2">
                        {model.is_champion ? (
                          <span className="w-5 h-5 rounded-full bg-amber-500/20 text-amber-500 flex items-center justify-center font-bold text-[10px]">
                            1
                          </span>
                        ) : (
                          <span className="w-5 h-5 rounded-full bg-foreground/10 text-foreground/60 flex items-center justify-center font-bold text-[10px]">
                            {idx + 1}
                          </span>
                        )}
                        <span className="font-semibold text-foreground">{model.model_name}</span>
                      </div>
                    </td>

                    <td className="py-3 px-3 text-foreground/70 font-mono text-[11px]">
                      {model.algorithm}
                    </td>

                    <td className="py-3 px-3">
                      <span className="font-bold text-foreground">
                        {typeof primaryMetricVal === 'number' ? primaryMetricVal.toFixed(3) : primaryMetricVal}
                      </span>
                      <span className="text-[10px] text-foreground/50 ml-1">({metricName})</span>
                    </td>

                    <td className="py-3 px-3 text-foreground/80">
                      <div className="flex items-center gap-1.5">
                        <span>{model.cv_mean.toFixed(3)}</span>
                        <span className="text-foreground/40 text-[10px]">&plusmn;{model.cv_std.toFixed(3)}</span>
                      </div>
                    </td>

                    <td className="py-3 px-3 text-foreground/70">
                      <div className="flex items-center gap-1">
                        <Clock className="w-3 h-3 text-foreground/40" />
                        <span>{model.training_time_sec}s</span>
                      </div>
                    </td>

                    <td className="py-3 px-3">
                      {model.is_champion ? (
                        <span className="inline-flex items-center gap-1 bg-amber-500/10 text-amber-600 dark:text-amber-400 border border-amber-500/20 text-[10px] font-bold px-2 py-0.5 rounded-full">
                          <Trophy className="w-3 h-3" /> Winner
                        </span>
                      ) : (
                        <span className="inline-flex items-center text-foreground/50 text-[10px] px-2 py-0.5 rounded">
                          Evaluated
                        </span>
                      )}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}

      {/* Tab 2: Feature Importance */}
      {selectedTab === 'features' && (
        <div className="space-y-3">
          <p className="text-xs text-foreground/70">
            Relative SHAP / Gini feature attribution calculated for <strong>{champion?.model_name}</strong>:
          </p>
          <div className="space-y-2">
            {feature_importance?.map((feat) => (
              <div key={feat.feature} className="flex items-center gap-3">
                <span className="text-xs font-medium text-foreground w-48 truncate text-right font-mono">
                  {feat.feature}
                </span>
                <div className="flex-1 h-3 bg-foreground/10 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-gradient-to-r from-primary to-sky-400 rounded-full"
                    style={{ width: `${Math.min(100, Math.round(feat.importance * 100 * 2.5))}%` }}
                  />
                </div>
                <span className="text-xs font-bold text-foreground w-12 text-left">
                  {(feat.importance * 100).toFixed(1)}%
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Tab 3: Error Analysis */}
      {selectedTab === 'errors' && error_analysis && (
        <div className="space-y-4">
          {error_analysis.type === 'classification' && error_analysis.confusion_matrix && (
            <div className="bg-muted/30 p-4 rounded-xl border border-border/50">
              <h4 className="text-xs font-bold uppercase tracking-wider text-foreground/70 mb-3">
                Holdout Confusion Matrix ({error_analysis.confusion_matrix.labels.join(' vs ')})
              </h4>
              <div className="inline-grid grid-cols-2 gap-2 text-center text-xs">
                {error_analysis.confusion_matrix.matrix.map((row, rIdx) =>
                  row.map((val, cIdx) => (
                    <div
                      key={`${rIdx}-${cIdx}`}
                      className={clsx(
                        "p-3 rounded-lg border flex flex-col items-center justify-center min-w-[120px]",
                        rIdx === cIdx
                          ? "bg-emerald-500/10 border-emerald-500/20 text-emerald-600 dark:text-emerald-400"
                          : "bg-red-500/10 border-red-500/20 text-red-600 dark:text-red-400"
                      )}
                    >
                      <span className="text-base font-bold">{val}</span>
                      <span className="text-[10px] opacity-70">
                        {rIdx === cIdx ? 'True ' : 'False '}
                        {error_analysis.confusion_matrix!.labels[cIdx]}
                      </span>
                    </div>
                  ))
                )}
              </div>
            </div>
          )}

          {error_analysis.worst_performing_segments && (
            <div>
              <h4 className="text-xs font-bold uppercase tracking-wider text-foreground/70 mb-2 flex items-center gap-1.5">
                <AlertOctagon className="w-3.5 h-3.5 text-amber-500" />
                Vulnerable Subsegments (Highest Error Rate)
              </h4>
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-2">
                {error_analysis.worst_performing_segments.map((seg, idx) => (
                  <div key={idx} className="bg-background/80 border border-border rounded-lg p-3">
                    <span className="text-[10px] text-foreground/50 uppercase">{seg.feature}</span>
                    <p className="text-sm font-semibold text-foreground">{seg.segment}</p>
                    <div className="flex items-center justify-between text-xs mt-1">
                      <span className="text-red-500 font-bold">{(seg.error_rate * 100).toFixed(1)}% Error</span>
                      <span className="text-foreground/50">{seg.sample_count} samples</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
