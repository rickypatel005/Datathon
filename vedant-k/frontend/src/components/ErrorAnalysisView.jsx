import React from 'react';
import { ConfusionMatrixGrid } from './SvgCharts';

export const ErrorAnalysisView = ({ errorAnalysis = {} }) => {
  const {
    task_type = 'classification',
    status = 'SUCCESS',
    reason = '',
    confusion_matrix = null,
    class_labels = [],
    class_metrics = [],
    weak_classes = [],
    residual_summary = {},
    bias_diagnostic = {},
    heteroscedasticity = {},
    subgroup_slices = [],
    worst_predictions = [],
  } = errorAnalysis;

  if (status === 'NOT_APPLICABLE' || status === 'UNAVAILABLE') {
    return (
      <div style={{ maxWidth: '980px', margin: '60px auto', padding: '0 20px', textAlign: 'center' }}>
        <div className="glass-panel" style={{ padding: '48px 30px' }}>
          <div style={{ fontSize: '36px', marginBottom: '16px' }}>ℹ️</div>
          <h3 style={{ fontSize: '20px', marginBottom: '8px' }}>Error Diagnostics Not Applicable</h3>
          <p style={{ color: 'var(--text-secondary)', fontSize: '14px', maxWidth: '520px', margin: '0 auto' }}>
            {reason || 'Supervised error analysis and post-hoc diagnostics are not applicable for datasets without a designated supervised target.'}
          </p>
        </div>
      </div>
    );
  }

  const isClassification = task_type.toLowerCase() === 'classification';

  return (
    <div style={{ maxWidth: '1440px', margin: '0 auto', padding: '28px' }}>
      {/* Page Title */}
      <div style={{ marginBottom: '24px' }}>
        <div style={{ fontSize: '11px', color: 'var(--primary)', fontWeight: 700, letterSpacing: '0.05em', textTransform: 'uppercase', marginBottom: '4px' }}>
          POST-HOC FAILURE PATTERNS & SLICE DIAGNOSTICS
        </div>
        <h2 style={{ fontSize: '24px' }}>Error Analysis & Subgroup Weakness</h2>
      </div>

      {/* Classification View */}
      {isClassification && (
        <div>
          {/* Top Grid: Confusion Matrix & Weak Class Alerts */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(420px, 1fr))', gap: '24px', marginBottom: '28px' }}>
            {confusion_matrix && (
              <div className="glass-panel" style={{ padding: '24px' }}>
                <h4 style={{ fontSize: '16px', marginBottom: '6px' }}>Out-of-Fold Confusion Matrix</h4>
                <div style={{ fontSize: '12px', color: 'var(--text-muted)', marginBottom: '16px' }}>
                  Evaluated across out-of-fold cross-validation predictions.
                </div>
                <ConfusionMatrixGrid matrix={confusion_matrix} labels={class_labels} />
              </div>
            )}

            {/* Weak Classes Alert Card */}
            <div className="glass-panel" style={{ padding: '24px' }}>
              <h4 style={{ fontSize: '16px', marginBottom: '6px' }}>Class Performance Diagnostics</h4>
              <div style={{ fontSize: '12px', color: 'var(--text-muted)', marginBottom: '16px' }}>
                Per-class recall, precision, and identified weakness vulnerabilities.
              </div>

              {weak_classes && weak_classes.length > 0 ? (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', marginBottom: '16px' }}>
                  {weak_classes.map((wc, idx) => (
                    <div key={idx} style={{ padding: '12px 16px', background: 'rgba(244, 63, 94, 0.08)', border: '1px solid rgba(244, 63, 94, 0.25)', borderRadius: '8px' }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '4px' }}>
                        <strong style={{ color: '#fb7185', fontSize: '13px' }}>Weak Class: {wc.class}</strong>
                        <span className="badge badge-rejected" style={{ fontSize: '9px' }}>{wc.severity || 'MEDIUM'} SEVERITY</span>
                      </div>
                      <div style={{ fontSize: '12px', color: '#cbd5e1' }}>
                        Recall: <strong>{(wc.recall * 100).toFixed(1)}%</strong> | F1: <strong>{wc.f1}</strong> | Support: {wc.support} samples
                      </div>
                      <div style={{ fontSize: '11px', color: '#94a3b8', marginTop: '4px' }}>
                        {wc.evidence}
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div style={{ padding: '14px', background: 'rgba(16, 185, 129, 0.08)', border: '1px solid rgba(16, 185, 129, 0.2)', borderRadius: '8px', color: '#34d399', fontSize: '13px', marginBottom: '16px' }}>
                  ✓ No severely underperforming classes detected. Recall is balanced across categories.
                </div>
              )}

              {/* Per-class Metrics Table */}
              <div style={{ overflowX: 'auto' }}>
                <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '12px' }}>
                  <thead>
                    <tr style={{ borderBottom: '1px solid #334155', color: '#94a3b8', textAlign: 'left' }}>
                      <th style={{ padding: '8px' }}>Class</th>
                      <th style={{ padding: '8px' }}>Precision</th>
                      <th style={{ padding: '8px' }}>Recall</th>
                      <th style={{ padding: '8px' }}>F1-Score</th>
                      <th style={{ padding: '8px' }}>Support</th>
                    </tr>
                  </thead>
                  <tbody>
                    {class_metrics.map((cm) => (
                      <tr key={cm.class} style={{ borderBottom: '1px solid rgba(255, 255, 255, 0.04)' }}>
                        <td style={{ padding: '8px', fontWeight: 600, color: '#fff' }}>{cm.class}</td>
                        <td style={{ padding: '8px', fontFamily: 'var(--font-mono)' }}>{cm.precision}</td>
                        <td style={{ padding: '8px', fontFamily: 'var(--font-mono)' }}>{cm.recall}</td>
                        <td style={{ padding: '8px', fontFamily: 'var(--font-mono)' }}>{cm.f1}</td>
                        <td style={{ padding: '8px', fontFamily: 'var(--font-mono)' }}>{cm.support}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Regression View */}
      {!isClassification && residual_summary && (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(360px, 1fr))', gap: '24px', marginBottom: '28px' }}>
          {/* Residual Summary Card */}
          <div className="glass-panel" style={{ padding: '24px' }}>
            <h4 style={{ fontSize: '16px', marginBottom: '16px' }}>Residual Error Metrics</h4>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '14px', fontFamily: 'var(--font-mono)' }}>
              <div>
                <div style={{ fontSize: '11px', color: '#94a3b8' }}>RMSE</div>
                <div style={{ fontSize: '20px', fontWeight: 700, color: '#fff' }}>{residual_summary.rmse || 0.0}</div>
              </div>
              <div>
                <div style={{ fontSize: '11px', color: '#94a3b8' }}>MAE</div>
                <div style={{ fontSize: '20px', fontWeight: 700, color: '#fff' }}>{residual_summary.mae || 0.0}</div>
              </div>
              <div>
                <div style={{ fontSize: '11px', color: '#94a3b8' }}>Mean Residual</div>
                <div style={{ fontSize: '16px', fontWeight: 600, color: '#cbd5e1' }}>{residual_summary.mean_residual || 0.0}</div>
              </div>
              <div>
                <div style={{ fontSize: '11px', color: '#94a3b8' }}>Std Residual</div>
                <div style={{ fontSize: '16px', fontWeight: 600, color: '#cbd5e1' }}>{residual_summary.std_residual || 0.0}</div>
              </div>
            </div>
          </div>

          {/* Systematic Bias Diagnostic */}
          <div className="glass-panel" style={{ padding: '24px' }}>
            <h4 style={{ fontSize: '16px', marginBottom: '8px' }}>Systematic Bias Diagnostic</h4>
            <div style={{ marginBottom: '12px' }}>
              <span className={bias_diagnostic.bias_detected ? 'badge badge-rejected' : 'badge badge-verified'}>
                {bias_diagnostic.bias_detected ? 'BIAS DETECTED' : 'RESIDUALS UNBIASED'}
              </span>
            </div>
            <p style={{ fontSize: '13px', color: '#cbd5e1', lineHeight: 1.5, marginBottom: '8px' }}>
              {bias_diagnostic.description || 'Residuals are approximately centered around zero.'}
            </p>
            <div style={{ fontSize: '11px', color: 'var(--text-muted)' }}>
              {bias_diagnostic.disclaimer || 'Descriptive diagnostic only. Does not imply causation.'}
            </div>
          </div>
        </div>
      )}

      {/* Subgroup Slices Table (Applicable to Both) */}
      <div className="glass-panel" style={{ padding: '24px', overflowX: 'auto' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '16px' }}>
          <div>
            <h4 style={{ fontSize: '16px' }}>Subgroup Slice Analysis (Weak Slices)</h4>
            <div style={{ fontSize: '12px', color: 'var(--text-muted)' }}>
              Empirical evaluation of loss disparities across categorical slices and feature segments.
            </div>
          </div>
          <span className="badge badge-neutral">{subgroup_slices.length} Slices Evaluated</span>
        </div>

        {subgroup_slices && subgroup_slices.length > 0 ? (
          <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '13px' }}>
            <thead>
              <tr style={{ borderBottom: '1px solid #334155', color: '#94a3b8', textTransform: 'uppercase', fontSize: '11px' }}>
                <th style={{ padding: '10px 14px' }}>Feature</th>
                <th style={{ padding: '10px 14px' }}>Subgroup Slice</th>
                <th style={{ padding: '10px 14px' }}>Slice Error</th>
                <th style={{ padding: '10px 14px' }}>Baseline Error</th>
                <th style={{ padding: '10px 14px' }}>Disparity Ratio</th>
                <th style={{ padding: '10px 14px' }}>Sample Count</th>
                <th style={{ padding: '10px 14px' }}>Diagnosis</th>
              </tr>
            </thead>
            <tbody>
              {subgroup_slices.map((slice, idx) => {
                const isWeak = slice.status === 'WEAK_SLICE';
                return (
                  <tr key={idx} style={{ borderBottom: '1px solid rgba(255, 255, 255, 0.04)', background: isWeak ? 'rgba(244, 63, 94, 0.04)' : 'transparent' }}>
                    <td style={{ padding: '10px 14px', fontWeight: 600, color: '#fff' }}>{slice.feature}</td>
                    <td style={{ padding: '10px 14px', fontFamily: 'var(--font-mono)' }}>{slice.group}</td>
                    <td style={{ padding: '10px 14px', fontFamily: 'var(--font-mono)' }}>{slice.group_metric}</td>
                    <td style={{ padding: '10px 14px', fontFamily: 'var(--font-mono)', color: '#94a3b8' }}>{slice.baseline_metric}</td>
                    <td style={{ padding: '10px 14px', fontFamily: 'var(--font-mono)', fontWeight: 700, color: isWeak ? '#fb7185' : '#34d399' }}>
                      {slice.error_disparity_ratio ? `${slice.error_disparity_ratio}x` : '1.0x'}
                    </td>
                    <td style={{ padding: '10px 14px', fontFamily: 'var(--font-mono)' }}>{slice.sample_count}</td>
                    <td style={{ padding: '10px 14px' }}>
                      <span className={isWeak ? 'badge badge-rejected' : 'badge badge-neutral'} style={{ fontSize: '10px' }}>
                        {slice.status || 'NORMAL'}
                      </span>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        ) : (
          <div style={{ color: '#94a3b8', fontSize: '13px' }}>
            No weak subgroup slices detected in the feature space.
          </div>
        )}
      </div>
    </div>
  );
};
