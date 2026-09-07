import React from 'react';

export const BarChart = ({ categories = [], series = [], height = 220, yLabel = "Value" }) => {
  if (!categories || categories.length === 0 || !series || series.length === 0) {
    return (
      <div style={{ height, display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#64748b' }}>
        No chart data available
      </div>
    );
  }

  const values = series[0]?.data || [];
  const maxVal = Math.max(...values.map(v => Number(v) || 0), 0.01);
  const chartHeight = height - 50;

  return (
    <div style={{ width: '100%', height }}>
      <svg width="100%" height={height} style={{ overflow: 'visible' }}>
        {/* Y Axis line */}
        <line x1="40" y1="10" x2="40" y2={chartHeight + 10} stroke="#334155" strokeWidth="1" />
        {/* X Axis line */}
        <line x1="40" y1={chartHeight + 10} x2="98%" y2={chartHeight + 10} stroke="#334155" strokeWidth="1" />

        {/* Bars */}
        {categories.map((cat, idx) => {
          const val = Number(values[idx]) || 0;
          const barH = (val / maxVal) * (chartHeight - 15);
          const barWidth = Math.min(48, Math.max(16, (800 / categories.length) - 16));
          const xPos = 60 + idx * ((100 - 15) / categories.length) * 7.5;

          return (
            <g key={idx}>
              <rect
                x={`${xPos}%`}
                y={chartHeight + 10 - barH}
                width={`${barWidth}px`}
                height={barH}
                rx="4"
                fill={series[0]?.color || '#6366f1'}
                opacity="0.88"
                style={{ transition: 'all 0.3s ease' }}
              >
                <title>{`${cat}: ${val}`}</title>
              </rect>
              <text
                x={`${xPos}%`}
                y={chartHeight + 26}
                fill="#94a3b8"
                fontSize="11"
                textAnchor="start"
                style={{ fontFamily: 'var(--font-mono)' }}
              >
                {cat.length > 12 ? cat.substring(0, 10) + '..' : cat}
              </text>
              <text
                x={`${xPos}%`}
                y={chartHeight + 5 - barH}
                fill="#f8fafc"
                fontSize="10"
                fontWeight="bold"
                style={{ fontFamily: 'var(--font-mono)' }}
              >
                {typeof val === 'number' ? (val % 1 !== 0 ? val.toFixed(3) : val) : val}
              </text>
            </g>
          );
        })}
      </svg>
    </div>
  );
};

export const ConfusionMatrixGrid = ({ matrix = [], labels = [] }) => {
  if (!matrix || matrix.length === 0) {
    return <div style={{ color: '#64748b' }}>No confusion matrix available.</div>;
  }

  const flattened = matrix.flat();
  const maxVal = Math.max(...flattened, 1);

  return (
    <div style={{ display: 'inline-block', background: 'rgba(15, 23, 42, 0.4)', padding: '16px', borderRadius: '12px' }}>
      <div style={{ display: 'flex', marginBottom: '8px', marginLeft: '90px' }}>
        <div style={{ fontSize: '11px', color: '#94a3b8', fontWeight: 600, letterSpacing: '0.05em' }}>
          PREDICTED CLASS
        </div>
      </div>
      <div style={{ display: 'flex', marginLeft: '90px', gap: '8px', marginBottom: '6px' }}>
        {labels.map((lbl, idx) => (
          <div key={idx} style={{ width: '70px', textAlign: 'center', fontSize: '11px', color: '#cbd5e1', fontWeight: 600, fontFamily: 'var(--font-mono)' }}>
            {lbl}
          </div>
        ))}
      </div>

      {matrix.map((row, rIdx) => (
        <div key={rIdx} style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
          <div style={{ width: '80px', textAlign: 'right', fontSize: '11px', color: '#cbd5e1', fontWeight: 600, fontFamily: 'var(--font-mono)' }}>
            {labels[rIdx] || `C${rIdx}`}
          </div>
          {row.map((cellVal, cIdx) => {
            const intensity = Math.min(1.0, Math.max(0.1, cellVal / maxVal));
            const isCorrect = rIdx === cIdx;
            const bg = isCorrect
              ? `rgba(16, 185, 129, ${0.15 + intensity * 0.7})`
              : cellVal > 0 ? `rgba(244, 63, 94, ${0.15 + intensity * 0.6})` : 'rgba(255,255,255,0.02)';

            return (
              <div
                key={cIdx}
                style={{
                  width: '70px',
                  height: '52px',
                  background: bg,
                  border: isCorrect ? '1px solid rgba(16, 185, 129, 0.4)' : '1px solid rgba(255,255,255,0.06)',
                  borderRadius: '6px',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  color: isCorrect ? '#ecfdf5' : '#fff',
                  fontWeight: 700,
                  fontSize: '14px',
                  fontFamily: 'var(--font-mono)',
                }}
              >
                {cellVal}
              </div>
            );
          })}
        </div>
      ))}
      <div style={{ fontSize: '10px', color: '#64748b', marginTop: '10px', textAlign: 'center' }}>
        Diagonal cells indicate accurate predictions; off-diagonal cells represent misclassifications.
      </div>
    </div>
  );
};
