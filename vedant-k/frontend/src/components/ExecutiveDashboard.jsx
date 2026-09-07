import React from 'react';
import { BarChart, ConfusionMatrixGrid } from './SvgCharts';

export const ExecutiveDashboard = ({ dashboardSpec, onNavigateTab }) => {
  if (!dashboardSpec) return null;

  const {
    kpis = [],
    executive_summary = {},
    charts = [],
    model_championship = {},
    insights = [],
  } = dashboardSpec;

  const benchmarksChart = charts.find(c => c.chart_id === 'chart_model_benchmarks');
  const corrsChart = charts.find(c => c.chart_id === 'chart_correlations');
  const slicesChart = charts.find(c => c.chart_id === 'chart_weak_slices');

  return (
    <div style={{ maxWidth: '1440px', margin: '0 auto', padding: '28px' }}>
      {/* KPI Cards Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px', marginBottom: '28px' }}>
        {kpis.map((kpi) => (
          <div key={kpi.id} className="glass-panel" style={{ padding: '20px' }}>
            <div style={{ fontSize: '11px', color: 'var(--text-muted)', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '6px' }}>
              {kpi.label}
            </div>
            <div style={{ fontSize: '26px', fontWeight: 800, color: '#fff', fontFamily: 'var(--font-mono)', marginBottom: '4px' }}>
              {kpi.value}
            </div>
            <div style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>
              {kpi.subtext}
            </div>
          </div>
        ))}
      </div>

      {/* Executive Overview & Top Findings Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(420px, 1fr))', gap: '24px', marginBottom: '28px' }}>
        {/* Synthesis Box */}
        <div className="glass-panel" style={{ padding: '28px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '12px' }}>
            <span style={{ fontSize: '18px' }}>🧠</span>
            <h3 style={{ fontSize: '18px' }}>Autonomous Executive Synthesis</h3>
          </div>
          <p style={{ color: '#cbd5e1', fontSize: '14px', lineHeight: 1.6, marginBottom: '20px' }}>
            {executive_summary.overview}
          </p>

          <h4 style={{ fontSize: '13px', textTransform: 'uppercase', letterSpacing: '0.05em', color: '#94a3b8', marginBottom: '10px' }}>
            Key Validated Takeaways
          </h4>
          <ul style={{ listStyle: 'none', display: 'flex', flexDirection: 'column', gap: '8px' }}>
            {(executive_summary.key_takeaways || []).map((point, idx) => (
              <li key={idx} style={{ fontSize: '13px', color: '#e2e8f0', display: 'flex', alignItems: 'flex-start', gap: '10px' }}>
                <span style={{ color: 'var(--primary)', fontWeight: 'bold' }}>•</span>
                <span>{point}</span>
              </li>
            ))}
          </ul>
        </div>

        {/* Actionable Recommendations */}
        <div className="glass-panel" style={{ padding: '28px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '12px' }}>
            <span style={{ fontSize: '18px' }}>🎯</span>
            <h3 style={{ fontSize: '18px' }}>Domain Recommendations & Warnings</h3>
          </div>

          <div style={{ marginBottom: '20px' }}>
            <h4 style={{ fontSize: '12px', textTransform: 'uppercase', letterSpacing: '0.05em', color: '#34d399', marginBottom: '8px' }}>
              Actionable Guidance
            </h4>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
              {(executive_summary.recommendations || []).map((rec, idx) => (
                <div key={idx} style={{ padding: '10px 14px', background: 'rgba(16, 185, 129, 0.08)', border: '1px solid rgba(16, 185, 129, 0.2)', borderRadius: '8px', fontSize: '12px', color: '#d1fae5' }}>
                  {rec}
                </div>
              ))}
            </div>
          </div>

          {(executive_summary.warnings && executive_summary.warnings.length > 0) && (
            <div>
              <h4 style={{ fontSize: '12px', textTransform: 'uppercase', letterSpacing: '0.05em', color: '#fb7185', marginBottom: '8px' }}>
                Data Integrity Warnings
              </h4>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                {executive_summary.warnings.map((warn, idx) => (
                  <div key={idx} style={{ padding: '8px 12px', background: 'rgba(244, 63, 94, 0.08)', border: '1px solid rgba(244, 63, 94, 0.2)', borderRadius: '8px', fontSize: '12px', color: '#ffe4e6' }}>
                    ⚠️ Constant/zero-variance column excluded: {warn}
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Visual Analytics Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(420px, 1fr))', gap: '24px' }}>
        {/* Model Championship Quick Card */}
        {benchmarksChart && (
          <div className="glass-panel" style={{ padding: '24px' }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '16px' }}>
              <div>
                <h4 style={{ fontSize: '16px' }}>{benchmarksChart.title}</h4>
                <div style={{ fontSize: '12px', color: 'var(--text-muted)' }}>{benchmarksChart.description}</div>
              </div>
              <button
                className="btn-secondary"
                style={{ fontSize: '11px', padding: '4px 10px' }}
                onClick={() => onNavigateTab('models')}
              >
                Model Lab →
              </button>
            </div>
            <BarChart
              categories={benchmarksChart.categories}
              series={benchmarksChart.series}
              height={200}
              yLabel={benchmarksChart.y_axis_label}
            />
          </div>
        )}

        {/* Subgroup Slices / Correlations Chart */}
        {slicesChart ? (
          <div className="glass-panel" style={{ padding: '24px' }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '16px' }}>
              <div>
                <h4 style={{ fontSize: '16px' }}>{slicesChart.title}</h4>
                <div style={{ fontSize: '12px', color: 'var(--text-muted)' }}>{slicesChart.description}</div>
              </div>
              <button
                className="btn-secondary"
                style={{ fontSize: '11px', padding: '4px 10px' }}
                onClick={() => onNavigateTab('errors')}
              >
                Error Analysis →
              </button>
            </div>
            <BarChart
              categories={slicesChart.categories}
              series={slicesChart.series}
              height={200}
              yLabel="Disparity Ratio"
            />
          </div>
        ) : corrsChart ? (
          <div className="glass-panel" style={{ padding: '24px' }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '16px' }}>
              <div>
                <h4 style={{ fontSize: '16px' }}>{corrsChart.title}</h4>
                <div style={{ fontSize: '12px', color: 'var(--text-muted)' }}>{corrsChart.description}</div>
              </div>
            </div>
            <BarChart
              categories={corrsChart.categories}
              series={corrsChart.series}
              height={200}
              yLabel="Correlation"
            />
          </div>
        ) : null}
      </div>
    </div>
  );
};
