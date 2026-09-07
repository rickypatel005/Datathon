import React, { useState } from 'react';
import type { InsightContract } from '../types/contracts';
import {
  CheckCircle2,
  AlertCircle,
  HelpCircle,
  XCircle,
  ChevronDown,
  ChevronUp,
  ShieldCheck,
  Scale,
  BrainCircuit
} from 'lucide-react';
import clsx from 'clsx';

interface InsightCardProps {
  insight: InsightContract;
  defaultExpanded?: boolean;
}

const getStatusBadge = (status: InsightContract['status']) => {
  switch (status) {
    case 'verified':
      return {
        label: 'Verified Finding',
        icon: CheckCircle2,
        classes: 'bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border-emerald-500/20'
      };
    case 'challenged':
      return {
        label: 'Challenged by Critic',
        icon: AlertCircle,
        classes: 'bg-amber-500/10 text-amber-600 dark:text-amber-400 border-amber-500/20'
      };
    case 'rejected':
      return {
        label: 'Refuted / Rejected',
        icon: XCircle,
        classes: 'bg-red-500/10 text-red-600 dark:text-red-400 border-red-500/20'
      };
    case 'investigating':
    default:
      return {
        label: 'Under Investigation',
        icon: HelpCircle,
        classes: 'bg-sky-500/10 text-sky-600 dark:text-sky-400 border-sky-500/20'
      };
  }
};

const getImpactBadge = (impact: InsightContract['business_impact']) => {
  switch (impact) {
    case 'high':
      return 'bg-red-500/10 text-red-600 dark:text-red-400 border-red-500/20 font-semibold';
    case 'medium':
      return 'bg-amber-500/10 text-amber-600 dark:text-amber-400 border-amber-500/20 font-medium';
    case 'low':
      return 'bg-slate-500/10 text-slate-600 dark:text-slate-400 border-slate-500/20';
  }
};

export const InsightCard: React.FC<InsightCardProps> = ({ insight, defaultExpanded = false }) => {
  const [isExpanded, setIsExpanded] = useState(defaultExpanded);
  const statusInfo = getStatusBadge(insight.status);
  const StatusIcon = statusInfo.icon;

  const agreePercent = Math.round(insight.model_agreement.agree_ratio * 100);

  return (
    <div className="bg-card border border-border/80 hover:border-primary/40 rounded-xl p-5 shadow-sm transition-all duration-200">
      {/* Top Meta Bar */}
      <div className="flex flex-wrap items-center justify-between gap-2.5 mb-3">
        <div className="flex items-center gap-2">
          <span className={clsx(
            "inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium border",
            statusInfo.classes
          )}>
            <StatusIcon className="w-3.5 h-3.5" />
            {statusInfo.label}
          </span>

          <span className={clsx(
            "inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs border uppercase tracking-wider",
            getImpactBadge(insight.business_impact)
          )}>
            {insight.business_impact} Impact
          </span>
        </div>

        <div className="flex items-center gap-3">
          {/* Confidence Meter */}
          <div className="flex items-center gap-1.5" title={`Statistical confidence score: ${insight.confidence_score}%`}>
            <ShieldCheck className="w-4 h-4 text-primary" />
            <div className="flex flex-col">
              <span className="text-[10px] text-foreground/50 uppercase tracking-wider leading-none">Confidence</span>
              <span className="text-xs font-bold text-foreground leading-tight">{insight.confidence_score}%</span>
            </div>
            <div className="w-12 h-1.5 bg-foreground/10 rounded-full overflow-hidden ml-1">
              <div
                className={clsx(
                  "h-full rounded-full transition-all duration-500",
                  insight.confidence_score >= 90 ? "bg-emerald-500" : (insight.confidence_score >= 75 ? "bg-amber-500" : "bg-red-500")
                )}
                style={{ width: `${insight.confidence_score}%` }}
              />
            </div>
          </div>

          {/* Model Agreement */}
          <div className="flex items-center gap-1.5 pl-2 border-l border-border" title={`${insight.model_agreement.agree_count} of ${insight.model_agreement.total_models} benchmarked algorithms confirm this finding`}>
            <BrainCircuit className="w-4 h-4 text-sky-500" />
            <div className="flex flex-col">
              <span className="text-[10px] text-foreground/50 uppercase tracking-wider leading-none">Model Consensus</span>
              <span className="text-xs font-bold text-foreground leading-tight">{agreePercent}% ({insight.model_agreement.agree_count}/{insight.model_agreement.total_models})</span>
            </div>
          </div>
        </div>
      </div>

      {/* Claim Title & Text */}
      <h4 className="text-base font-semibold text-foreground tracking-tight mb-2">
        {insight.title}
      </h4>
      <p className="text-sm text-foreground/80 leading-relaxed mb-4 bg-muted/30 p-3 rounded-lg border border-border/40">
        "{insight.claim}"
      </p>

      {/* Statistical Evidence Pills */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 mb-3">
        <div className="bg-background/80 border border-border/60 rounded-lg p-2 flex flex-col">
          <span className="text-[11px] text-foreground/50">{insight.evidence.metric_name}</span>
          <span className="text-sm font-bold text-foreground mt-0.5">{insight.evidence.metric_value}</span>
        </div>

        {insight.evidence.p_value !== undefined && (
          <div className="bg-background/80 border border-border/60 rounded-lg p-2 flex flex-col">
            <span className="text-[11px] text-foreground/50">p-value</span>
            <span className="text-sm font-bold text-emerald-600 dark:text-emerald-400 mt-0.5">
              {insight.evidence.p_value < 0.001 ? '< 0.001' : insight.evidence.p_value.toFixed(4)}
            </span>
          </div>
        )}

        {insight.evidence.effect_size !== undefined && (
          <div className="bg-background/80 border border-border/60 rounded-lg p-2 flex flex-col">
            <span className="text-[11px] text-foreground/50">Effect Size (d/r)</span>
            <span className="text-sm font-bold text-foreground mt-0.5">{insight.evidence.effect_size}</span>
          </div>
        )}

        <div className="bg-background/80 border border-border/60 rounded-lg p-2 flex flex-col">
          <span className="text-[11px] text-foreground/50">Sample Support</span>
          <span className="text-sm font-bold text-foreground mt-0.5">{insight.evidence.sample_size.toLocaleString()} rows</span>
        </div>
      </div>

      {/* Expandable Verification & Critique Details */}
      <div className="border-t border-border/50 pt-2.5 mt-2">
        <button
          onClick={() => setIsExpanded(!isExpanded)}
          className="flex items-center justify-between w-full text-xs font-medium text-foreground/70 hover:text-foreground transition-colors py-1"
        >
          <span className="flex items-center gap-1.5">
            <Scale className="w-3.5 h-3.5 text-primary" />
            <span>Auditing Trail & Verification Argument</span>
          </span>
          {isExpanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
        </button>

        {isExpanded && (
          <div className="mt-3 space-y-2.5 text-xs">
            <div className="p-3 bg-muted/40 rounded-lg border border-border/40">
              <span className="font-semibold text-foreground block mb-1">Analytical Methodology:</span>
              <span className="text-foreground/70 leading-relaxed">{insight.methodology}</span>
            </div>

            {insight.critic_counterargument && (
              <div className="p-3 bg-amber-500/5 border border-amber-500/20 rounded-lg">
                <span className="font-semibold text-amber-700 dark:text-amber-400 block mb-1">
                  Critic Challenge / Counterfactual Test:
                </span>
                <span className="text-foreground/80 leading-relaxed">{insight.critic_counterargument}</span>
              </div>
            )}

            {insight.verifier_resolution && (
              <div className="p-3 bg-emerald-500/5 border border-emerald-500/20 rounded-lg">
                <span className="font-semibold text-emerald-700 dark:text-emerald-400 block mb-1">
                  Fact-Verifier Resolution:
                </span>
                <span className="text-foreground/80 leading-relaxed">{insight.verifier_resolution}</span>
              </div>
            )}

            {insight.model_agreement.agreeing_models.length > 0 && (
              <div className="flex flex-wrap items-center gap-1.5 pt-1">
                <span className="text-foreground/50 text-[11px]">Consensus Models:</span>
                {insight.model_agreement.agreeing_models.map((model) => (
                  <span key={model} className="bg-primary/10 text-primary px-2 py-0.5 rounded text-[10px] font-medium">
                    {model}
                  </span>
                ))}
                {insight.model_agreement.diverging_models.map((model) => (
                  <span key={model} className="bg-red-500/10 text-red-500 px-2 py-0.5 rounded text-[10px] line-through">
                    {model}
                  </span>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};
