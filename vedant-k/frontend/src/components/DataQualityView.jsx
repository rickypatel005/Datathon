import React from 'react';

export const DataQualityView = ({ dataQuality = {} }) => {
  const {
    row_count = 0,
    column_count = 0,
    memory_mb = 0.0,
    column_types = {},
    missing_value_summary = {},
    duplicate_rows = 0,
    constant_columns = [],
    leakage_risks = [],
    routing_decisions = {},
    target_candidates = [],
  } = dataQuality;

  const typeCounts = Object.values(column_types).reduce((acc, t) => {
    acc[t] = (acc[t] || 0) + 1;
    return acc;
  }, {});

  return (
    <div style={{ maxWidth: '1440px', margin: '0 auto', padding: '28px' }}>
      {/* Page Title */}
      <div style={{ marginBottom: '24px' }}>
        <div style={{ fontSize: '11px', color: 'var(--primary)', fontWeight: 700, letterSpacing: '0.05em', textTransform: 'uppercase', marginBottom: '4px' }}>
          DATA INTEGRITY & LEAKAGE AUDIT
        </div>
        <h2 style={{ fontSize: '24px' }}>Schema Discovery & Quality Audit</h2>
      </div>

      {/* Dataset Profile KPIs */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px', marginBottom: '28px' }}>
        <div className="glass-panel" style={{ padding: '20px' }}>
          <div style={{ fontSize: '11px', color: 'var(--text-muted)', fontWeight: 600 }}>ROW COUNT</div>
          <div style={{ fontSize: '24px', fontWeight: 800, color: '#fff', fontFamily: 'var(--font-mono)' }}>{row_count.toLocaleString()}</div>
        </div>
        <div className="glass-panel" style={{ padding: '20px' }}>
          <div style={{ fontSize: '11px', color: 'var(--text-muted)', fontWeight: 600 }}>FEATURE COUNT</div>
          <div style={{ fontSize: '24px', fontWeight: 800, color: '#fff', fontFamily: 'var(--font-mono)' }}>{column_count}</div>
        </div>
        <div className="glass-panel" style={{ padding: '20px' }}>
          <div style={{ fontSize: '11px', color: 'var(--text-muted)', fontWeight: 600 }}>MEMORY FOOTPRINT</div>
          <div style={{ fontSize: '24px', fontWeight: 800, color: '#fff', fontFamily: 'var(--font-mono)' }}>{memory_mb.toFixed(2)} MB</div>
        </div>
        <div className="glass-panel" style={{ padding: '20px' }}>
          <div style={{ fontSize: '11px', color: 'var(--text-muted)', fontWeight: 600 }}>DUPLICATE ROWS</div>
          <div style={{ fontSize: '24px', fontWeight: 800, color: duplicate_rows > 0 ? '#fb7185' : '#34d399', fontFamily: 'var(--font-mono)' }}>
            {duplicate_rows}
          </div>
        </div>
      </div>

      {/* Grid: Column Types & Task Routing */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(420px, 1fr))', gap: '24px', marginBottom: '28px' }}>
        {/* Column Types Breakdown */}
        <div className="glass-panel" style={{ padding: '24px' }}>
          <h4 style={{ fontSize: '16px', marginBottom: '14px' }}>Column Data Types</h4>
          <div style={{ display: 'flex', gap: '12px', marginBottom: '16px' }}>
            {Object.entries(typeCounts).map(([type, count]) => (
              <div key={type} style={{ padding: '8px 14px', background: 'rgba(255, 255, 255, 0.03)', border: '1px solid rgba(255, 255, 255, 0.08)', borderRadius: '8px' }}>
                <span style={{ fontSize: '11px', color: '#94a3b8', textTransform: 'capitalize' }}>{type}: </span>
                <strong style={{ fontSize: '13px', color: '#fff' }}>{count}</strong>
              </div>
            ))}
          </div>

          <div style={{ maxHeight: '240px', overflowY: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '12px' }}>
              <thead>
                <tr style={{ borderBottom: '1px solid #334155', color: '#94a3b8', textAlign: 'left' }}>
                  <th style={{ padding: '8px' }}>Column</th>
                  <th style={{ padding: '8px' }}>Inferred Type</th>
                  <th style={{ padding: '8px' }}>Missing Values</th>
                </tr>
              </thead>
              <tbody>
                {Object.entries(column_types).map(([col, type]) => {
                  const missCount = missing_value_summary[col] || 0;
                  return (
                    <tr key={col} style={{ borderBottom: '1px solid rgba(255, 255, 255, 0.04)' }}>
                      <td style={{ padding: '8px', color: '#fff', fontWeight: 600 }}>{col}</td>
                      <td style={{ padding: '8px' }}><span className="badge badge-neutral" style={{ fontSize: '9px' }}>{type}</span></td>
                      <td style={{ padding: '8px', color: missCount > 0 ? '#fb7185' : '#34d399', fontFamily: 'var(--font-mono)' }}>
                        {missCount}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>

        {/* Task Routing Decisions */}
        <div className="glass-panel" style={{ padding: '24px' }}>
          <h4 style={{ fontSize: '16px', marginBottom: '8px' }}>Intelligent Task Routing</h4>
          <div style={{ fontSize: '12px', color: 'var(--text-muted)', marginBottom: '16px' }}>
            AIDA automatically routes analytics based on target candidate heuristics and schema fingerprint.
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', marginBottom: '16px' }}>
            {Object.entries(routing_decisions).map(([task, enabled]) => (
              <div key={task} style={{
                padding: '10px 14px',
                borderRadius: '8px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                background: enabled ? 'rgba(99, 102, 241, 0.08)' : 'rgba(255, 255, 255, 0.02)',
                border: enabled ? '1px solid rgba(99, 102, 241, 0.25)' : '1px solid rgba(255, 255, 255, 0.04)',
              }}>
                <span style={{ fontSize: '13px', fontWeight: 600, color: enabled ? '#fff' : '#64748b', textTransform: 'capitalize' }}>
                  {task.replace(/_/g, ' ')}
                </span>
                <span className={enabled ? 'badge badge-high' : 'badge badge-neutral'} style={{ fontSize: '9px' }}>
                  {enabled ? 'ACTIVE' : 'INACTIVE'}
                </span>
              </div>
            ))}
          </div>

          <div style={{ fontSize: '12px', color: '#cbd5e1' }}>
            <strong>Target Candidates: </strong>
            <span style={{ fontFamily: 'var(--font-mono)', color: 'var(--primary)' }}>
              {target_candidates.length > 0 ? target_candidates.join(', ') : 'None detected (Unsupervised)'}
            </span>
          </div>
        </div>
      </div>

      {/* Data Leakage Audit Table */}
      <div className="glass-panel" style={{ padding: '24px' }}>
        <h4 style={{ fontSize: '16px', marginBottom: '6px' }}>Leakage & Contamination Protections</h4>
        <div style={{ fontSize: '12px', color: 'var(--text-muted)', marginBottom: '16px' }}>
          Identifiers and zero-variance columns flagged and isolated to prevent out-of-fold data leakage.
        </div>

        {leakage_risks && leakage_risks.length > 0 ? (
          <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '13px' }}>
            <thead>
              <tr style={{ borderBottom: '1px solid #334155', color: '#94a3b8', textTransform: 'uppercase', fontSize: '11px' }}>
                <th style={{ padding: '10px 14px' }}>Feature</th>
                <th style={{ padding: '10px 14px' }}>Risk Assessment</th>
                <th style={{ padding: '10px 14px' }}>Severity</th>
                <th style={{ padding: '10px 14px' }}>Mitigation Action</th>
              </tr>
            </thead>
            <tbody>
              {leakage_risks.map((risk, idx) => (
                <tr key={idx} style={{ borderBottom: '1px solid rgba(255, 255, 255, 0.04)' }}>
                  <td style={{ padding: '10px 14px', fontWeight: 600, color: '#fff' }}>{risk.feature}</td>
                  <td style={{ padding: '10px 14px', color: '#cbd5e1' }}>{risk.risk_type.replace(/_/g, ' ')}</td>
                  <td style={{ padding: '10px 14px' }}>
                    <span className={risk.severity === 'HIGH' ? 'badge badge-rejected' : 'badge badge-low'} style={{ fontSize: '9px' }}>
                      {risk.severity}
                    </span>
                  </td>
                  <td style={{ padding: '10px 14px', color: '#94a3b8' }}>{risk.action}</td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <div style={{ padding: '14px', background: 'rgba(16, 185, 129, 0.08)', borderRadius: '8px', color: '#34d399', fontSize: '13px' }}>
            ✓ No leakage threats detected. Dataset feature inputs are clean.
          </div>
        )}
      </div>
    </div>
  );
};
