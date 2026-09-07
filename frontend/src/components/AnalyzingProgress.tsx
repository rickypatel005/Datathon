import { useEffect, useState } from 'react';
import { CheckCircle2, Sparkles } from 'lucide-react';
import clsx from 'clsx';

interface AnalyzingProgressProps {
  onComplete: () => void;
}

export function AnalyzingProgress({ onComplete }: AnalyzingProgressProps) {
  const [percent, setPercent] = useState(15);
  const [activeStep, setActiveStep] = useState(0);

  const steps = [
    { title: 'Understanding dataset structure' },
    { title: 'Detecting column types' },
    { title: 'Cleaning data (missing values, duplicates, formatting)' },
    { title: 'Finding patterns (correlations, clusters, outliers)' },
    { title: 'Generating visualizations' },
    { title: 'Preparing insights' }
  ];

  useEffect(() => {
    const timer = setInterval(() => {
      setPercent((prev) => {
        if (prev >= 100) {
          clearInterval(timer);
          setTimeout(() => {
            onComplete();
          }, 600);
          return 100;
        }
        const next = prev + 17;
        const stepIdx = Math.min(steps.length - 1, Math.floor((next / 100) * steps.length));
        setActiveStep(stepIdx);
        return Math.min(100, next);
      });
    }, 600);

    return () => clearInterval(timer);
  }, [onComplete]);

  // Circular gauge math (radius = 54, strokeWidth = 8, circumference = 2 * PI * 54 = ~339.29)
  const radius = 54;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (percent / 100) * circumference;

  return (
    <div className="flex flex-col items-center justify-center max-w-xl mx-auto py-8 px-4 text-center space-y-7 animate-in fade-in duration-300">
      <div className="space-y-2">
        <h2 className="text-2xl sm:text-3xl font-bold tracking-tight text-white">
          Analyzing your data
        </h2>
        <p className="text-xs sm:text-sm text-slate-400 max-w-md mx-auto leading-relaxed">
          Sit back! AIDA is automatically understanding, cleaning and finding insights from your dataset.
        </p>
      </div>

      {/* Circular Progress Gauge */}
      <div className="relative w-36 h-36 flex items-center justify-center">
        <svg className="w-full h-full -rotate-90 transform" viewBox="0 0 128 128">
          {/* Background track */}
          <circle
            cx="64"
            cy="64"
            r={radius}
            className="text-[#131b2e]"
            strokeWidth="8"
            stroke="currentColor"
            fill="transparent"
          />
          {/* Animated gradient progress ring */}
          <circle
            cx="64"
            cy="64"
            r={radius}
            className="transition-all duration-500 ease-out"
            strokeWidth="8"
            strokeDasharray={circumference}
            strokeDashoffset={strokeDashoffset}
            strokeLinecap="round"
            stroke="url(#progressGradient)"
            fill="transparent"
          />
          <defs>
            <linearGradient id="progressGradient" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor="#38bdf8" />
              <stop offset="100%" stopColor="#6366f1" />
            </linearGradient>
          </defs>
        </svg>
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span className="text-3xl font-black text-white tracking-tight">{percent}%</span>
        </div>
      </div>

      {/* 6 Step Checklist */}
      <div className="w-full max-w-md bg-[#0f172a]/60 border border-[#1e293b] rounded-2xl p-5 space-y-3 text-left shadow-lg">
        {steps.map((step, idx) => {
          const isDone = idx < activeStep;
          const isCurrent = idx === activeStep;
          return (
            <div key={idx} className="flex items-center gap-3 text-xs">
              {isDone ? (
                <div className="w-4 h-4 rounded-full bg-emerald-500/20 text-emerald-400 flex items-center justify-center flex-shrink-0">
                  <CheckCircle2 className="w-3.5 h-3.5" />
                </div>
              ) : isCurrent ? (
                <div className="w-4 h-4 rounded-full border-2 border-sky-400 border-t-transparent animate-spin flex-shrink-0" />
              ) : (
                <div className="w-4 h-4 rounded-full border border-slate-600 flex-shrink-0" />
              )}
              <span
                className={clsx(
                  "transition-colors",
                  isDone && "text-slate-300",
                  isCurrent && "text-sky-300 font-semibold",
                  !isDone && !isCurrent && "text-slate-500"
                )}
              >
                {step.title}
              </span>
            </div>
          );
        })}
      </div>

      {/* Bottom Sparkle Quote Box */}
      <div className="bg-[#111c35]/60 border border-[#1e293b] rounded-xl px-5 py-2.5 flex items-center gap-2 text-xs text-indigo-300 shadow-sm">
        <Sparkles className="w-3.5 h-3.5 text-indigo-400 flex-shrink-0" />
        <span className="italic">"From raw data to real insights, automatically."</span>
      </div>
    </div>
  );
}
