import React from 'react';
import Plot from 'react-plotly.js';
import type { PlotlyChartSpec } from '../types/contracts';
import { BarChart3, TrendingUp, ScatterChart, PieChart, Layers } from 'lucide-react';

interface AutoChartProps {
  spec: PlotlyChartSpec;
  className?: string;
}

const getCategoryIcon = (category?: string) => {
  switch (category) {
    case 'time_series':
      return <TrendingUp className="w-4 h-4 text-emerald-500" />;
    case 'correlation':
      return <ScatterChart className="w-4 h-4 text-sky-500" />;
    case 'distribution':
      return <BarChart3 className="w-4 h-4 text-purple-500" />;
    case 'category_comparison':
      return <PieChart className="w-4 h-4 text-amber-500" />;
    default:
      return <Layers className="w-4 h-4 text-primary" />;
  }
};

const getCategoryLabel = (category?: string) => {
  switch (category) {
    case 'time_series':
      return 'Time Series Trend';
    case 'correlation':
      return 'Correlation Analysis';
    case 'distribution':
      return 'Distribution Profile';
    case 'category_comparison':
      return 'Segment Comparison';
    default:
      return 'Automated Chart';
  }
};

export const AutoChart: React.FC<AutoChartProps> = ({ spec, className = '' }) => {
  if (!spec || !spec.data || spec.data.length === 0) {
    return (
      <div className={`bg-card border border-border rounded-xl p-6 flex flex-col items-center justify-center text-foreground/50 min-h-[320px] ${className}`}>
        <BarChart3 className="w-10 h-10 mb-2 opacity-40" />
        <p className="text-sm font-medium">Chart data unavailable</p>
      </div>
    );
  }

  // Ensure transparent background and dynamic layout styling
  const layout = {
    autosize: true,
    paper_bgcolor: 'rgba(0,0,0,0)',
    plot_bgcolor: 'rgba(0,0,0,0)',
    font: {
      family: 'Inter, system-ui, -apple-system, sans-serif',
      color: 'currentColor',
      size: 11
    },
    hoverlabel: {
      bgcolor: '#1e293b',
      bordercolor: '#334155',
      font: { color: '#f8fafc', size: 12 }
    },
    ...spec.layout,
    margin: spec.layout?.margin || { t: 30, r: 20, l: 45, b: 45 }
  };

  return (
    <div className={`bg-card border border-border/80 rounded-xl p-4 shadow-sm flex flex-col hover:border-border transition-all duration-200 ${className}`}>
      <div className="flex items-start justify-between gap-3 mb-2">
        <div>
          <div className="flex items-center gap-1.5 text-xs font-semibold uppercase tracking-wider text-foreground/60 mb-1">
            {getCategoryIcon(spec.category)}
            <span>{getCategoryLabel(spec.category)}</span>
          </div>
          <h3 className="font-semibold text-base text-foreground tracking-tight">{spec.title}</h3>
          {spec.description && (
            <p className="text-xs text-foreground/70 mt-0.5 leading-relaxed">{spec.description}</p>
          )}
        </div>
      </div>

      <div className="flex-1 w-full min-h-[280px] relative mt-2">
        <Plot
          data={spec.data}
          layout={layout}
          config={{
            responsive: true,
            displayModeBar: false,
            ...spec.config
          }}
          useResizeHandler={true}
          style={{ width: '100%', height: '100%', minHeight: '280px' }}
        />
      </div>
    </div>
  );
};
