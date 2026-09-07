import React, { useState } from 'react';
import type { PipelineProgress as PipelineProgressType } from '../types/contracts';
import {
  CheckCircle2,
  Clock,
  AlertCircle,
  Terminal,
  Loader2,
  ChevronDown,
  ChevronUp,
  Play
} from 'lucide-react';
import clsx from 'clsx';

interface PipelineProgressProps {
  progress: PipelineProgressType;
  onRunPipeline?: () => void;
  isTriggering?: boolean;
}

export const PipelineProgress: React.FC<PipelineProgressProps> = ({
  progress,
  onRunPipeline,
  isTriggering = false
}) => {
  const [showLogs, setShowLogs] = useState(false);

  return (
    <div className="bg-card border border-border rounded-xl p-5 shadow-sm space-y-4">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-border/80 pb-3">
        <div>
          <div className="flex items-center gap-2">
            <span className="text-xs font-bold uppercase tracking-wider text-primary">
              Autonomous Pipeline Stepper
            </span>
            <span className={clsx(
              "text-[10px] font-bold px-2 py-0.5 rounded-full border",
              progress.is_running
                ? "bg-sky-500/10 text-sky-600 border-sky-500/20 animate-pulse"
                : "bg-emerald-500/10 text-emerald-600 border-emerald-500/20"
            )}>
              {progress.is_running ? 'Pipeline Active' : 'Pipeline Ready'}
            </span>
          </div>
          <h3 className="text-base font-bold text-foreground mt-0.5">
            AIDA 6-Stage Execution Lifecycle
          </h3>
        </div>

        <div className="flex items-center gap-2">
          {onRunPipeline && (
            <button
              onClick={onRunPipeline}
              disabled={isTriggering || progress.is_running}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-primary hover:bg-primary/90 text-primary-foreground font-semibold text-xs shadow transition-colors disabled:opacity-50"
            >
              {isTriggering || progress.is_running ? (
                <>
                  <Loader2 className="w-3.5 h-3.5 animate-spin" />
                  <span>Analyzing...</span>
                </>
              ) : (
                <>
                  <Play className="w-3.5 h-3.5 fill-current" />
                  <span>Run AIDA Pipeline</span>
                </>
              )}
            </button>
          )}

          <button
            onClick={() => setShowLogs(!showLogs)}
            className="inline-flex items-center gap-1 px-2.5 py-1.5 rounded-lg border border-border bg-muted/40 hover:bg-muted text-xs text-foreground/70 transition-colors"
          >
            <Terminal className="w-3.5 h-3.5 text-foreground/60" />
            <span>Logs</span>
            {showLogs ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />}
          </button>
        </div>
      </div>

      {/* Progress Bar */}
      <div className="space-y-1.5">
        <div className="flex justify-between text-xs font-medium text-foreground/70">
          <span>Overall Stage Progress</span>
          <span>{progress.overall_progress}%</span>
        </div>
        <div className="w-full h-2 bg-foreground/10 rounded-full overflow-hidden">
          <div
            className="h-full bg-gradient-to-r from-primary via-emerald-400 to-sky-400 rounded-full transition-all duration-500"
            style={{ width: `${progress.overall_progress}%` }}
          />
        </div>
      </div>

      {/* 6 Stage Timeline Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2.5 pt-1">
        {progress.stages.map((stage, idx) => {
          const isCompleted = stage.status === 'completed';
          const isRunning = stage.status === 'running';
          const isFailed = stage.status === 'failed';

          return (
            <div
              key={stage.stage}
              className={clsx(
                "p-3 rounded-lg border text-xs transition-all",
                isCompleted && "bg-emerald-500/5 border-emerald-500/20",
                isRunning && "bg-sky-500/5 border-sky-500/30 ring-1 ring-sky-500/30 animate-pulse",
                isFailed && "bg-red-500/5 border-red-500/30",
                !isCompleted && !isRunning && !isFailed && "bg-muted/30 border-border/60 opacity-60"
              )}
            >
              <div className="flex items-center justify-between mb-1">
                <span className="text-[10px] font-bold text-foreground/40 uppercase">
                  Stage {idx + 1}
                </span>
                {isCompleted && <CheckCircle2 className="w-4 h-4 text-emerald-500" />}
                {isRunning && <Loader2 className="w-4 h-4 text-sky-500 animate-spin" />}
                {isFailed && <AlertCircle className="w-4 h-4 text-red-500" />}
                {!isCompleted && !isRunning && !isFailed && (
                  <Clock className="w-3.5 h-3.5 text-foreground/30" />
                )}
              </div>

              <h4 className="font-semibold text-foreground tracking-tight">{stage.label}</h4>
              <p className="text-[11px] text-foreground/60 mt-0.5 line-clamp-2">{stage.description}</p>
              {stage.duration_sec && (
                <span className="text-[10px] text-foreground/40 mt-1 inline-block">
                  Duration: {stage.duration_sec}s
                </span>
              )}
            </div>
          );
        })}
      </div>

      {/* Live Logs Drawer */}
      {showLogs && (
        <div className="bg-slate-950 text-slate-200 rounded-lg p-3 font-mono text-[11px] space-y-1 max-h-40 overflow-y-auto border border-slate-800">
          <div className="text-slate-400 text-[10px] uppercase font-bold border-b border-slate-800 pb-1 mb-1">
            Autonomous Pipeline Stream:
          </div>
          {progress.logs.map((log, i) => (
            <div key={i} className="leading-relaxed text-slate-300">
              {log}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
