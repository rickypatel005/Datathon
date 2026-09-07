import React from 'react';
import { BarChart } from './SvgCharts';

export const ModelLabView = ({ modelChampionship = {} }) => {
  const {
    task_type = 'classification',
    validation_strategy = 'CrossValidation',
    folds = 5,
    primary_metric = 'score',
    champion_model_name = 'None',
    champion_score = null,
    selection_rationale = '',
    leaderboard = [],
    ensemble_result = {},
  } = modelChampionship;

  const chartCategories = leaderboard.map(r => r.model_name);
  const chartValues = leaderboard.map(r => r.primary_metric_score);

  return (
    <div style={{ maxWidth: '1440px', margin: '0 auto', padding: '28px' }}>
      {/* Page Title & Protocol */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '24px', flexWrap: 'wrap', gap: '16px' }}>
        <div>
          <div style={{ fontSize: '11px', color: 'var(--primary)', fontWeight: 700, letterSpacing: '0.05em', textTransform: 'uppercase', marginBottom: '4px' }}>
            EMPIRICAL MODEL TOURNAMENT
          </div>
          <h2 style={{ fontSize: '24px' }}>Model Championship & Cross-Validation</h2>
        </div>

        <div style={{ display: 'flex', gap: '12px', flexWrap: 'wrap' }}>
          <div className="glass-panel" style={{ padding: '8px 16px', borderRadius: '8px' }}>
            <span style={{ fontSize: '11px', color: 'var(--text-muted)' }}>Task: </span>
            <strong style={{ fontSize: '12px', color: '#fff', textTransform: 'capitalize' }}>{task_type}</strong>
          </div>
          <div className="glass-panel" style={{ padding: '8px 16px', borderRadius: '8px' }}>
            <span style={{ fontSize: '11px', color: 'var(--text-muted)' }}>Validation: </span>
            <strong style={{ fontSize: '12px', color: '#fff' }}>{validation_strategy} ({folds} Folds)</strong>
          </div>
          <div className="glass-panel" style={{ padding: '8px 16px', borderRadius: '8px' }}>
            <span style={{ fontSize: '11px', color: 'var(--text-muted)' }}>Metric: </span>
            <strong style={{ fontSize: '12px', color: '#fff', textTransform: 'uppercase' }}>{primary_metric}</strong>
          </div>
        </div>
      </div>

      {/* Champion Model Callout Card */}
      <div className="glass-panel" style={{ padding: '28px', border: '1px solid rgba(16, 185, 129, 0.3)', background: 'linear-gradient(135deg, rgba(16, 185, 129, 0.08), rgba(15, 23, 42, 0.8))', marginBottom: '28px' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '16px' }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '8px' }}>
              <span style={{ fontSize: '24px' }}>🏆</span>
              <h3 style={{ fontSize: '20px', color: '#fff' }}>Champion Model: {champion_model_name}</h3>
              <span className="badge badge-verified">EMPIRICALLY VALIDATED</span>
            </div>
            <p style={{ color: '#cbd5e1', fontSize: '14px', maxWidth: '680px', lineHeight: 1.5 }}>
              {selection_rationale || 'The champion was selected empirically using cross-validation. Zero LLM or subjective opinion involved.'}
            </p>
          </div>

          <div style={{ textAlign: 'right', background: 'rgba(0, 0, 0, 0.3)', padding: '16px 24px', borderRadius: '12px', border: '1px solid rgba(255, 255, 255, 0.05)' }}>
            <div style={{ fontSize: '11px', color: '#94a3b8', textTransform: 'uppercase', fontWeight: 700 }}>Mean CV {primary_metric}</div>
            <div style={{ fontSize: '32px', fontWeight: 800, color: '#34d399', fontFamily: 'var(--font-mono)' }}>
              {champion_score !== null ? champion_score.toFixed(4) : 'N/A'}
            </div>
          </div>
        </div>
      </div>

      {/* Visual Leaderboard Comparison Chart */}
      {leaderboard.length > 0 && (
        <div className="glass-panel" style={{ padding: '24px', marginBottom: '28px' }}>
          <h4 style={{ fontSize: '16px', marginBottom: '6px' }}>Cross-Validation Performance Comparison</h4>
          <div style={{ fontSize: '12px', color: 'var(--text-muted)', marginBottom: '16px' }}>
            Empirical evaluation across all candidate model architectures under identical cross-validation folds.
          </div>
          <BarChart
            categories={chartCategories}
            series={[{ name: primary_metric, data: chartValues, color: '#6366f1' }]}
            height={220}
            yLabel={primary_metric}
          />
        </div>
      )}

      {/* Leaderboard Table */}
      <div className="glass-panel" style={{ padding: '24px', marginBottom: '28px', overflowX: 'auto' }}>
        <h4 style={{ fontSize: '16px', marginBottom: '16px' }}>Candidate Models Leaderboard</h4>
        <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '13px' }}>
          <thead>
            <tr style={{ borderBottom: '1px solid #334155', color: '#94a3b8', textTransform: 'uppercase', fontSize: '11px' }}>
              <th style={{ padding: '12px 16px' }}>Rank</th>
              <th style={{ padding: '12px 16px' }}>Model Architecture</th>
              <th style={{ padding: '12px 16px' }}>{primary_metric} (Mean)</th>
              <th style={{ padding: '12px 16px' }}>Fold Scores</th>
              <th style={{ padding: '12px 16px' }}>Secondary Metrics</th>
              <th style={{ padding: '12px 16px' }}>Status</th>
            </tr>
          </thead>
          <tbody>
            {leaderboard.map((row) => (
              <tr
                key={row.model_name}
                style={{
                  borderBottom: '1px solid rgba(255, 255, 255, 0.05)',
                  background: row.is_champion ? 'rgba(16, 185, 129, 0.05)' : 'transparent',
                }}
              >
                <td style={{ padding: '12px 16px', fontFamily: 'var(--font-mono)', fontWeight: 700 }}>
                  {row.is_champion ? '🏆 #1' : `#${row.rank}`}
                </td>
                <td style={{ padding: '12px 16px', fontWeight: 600, color: '#fff' }}>
                  {row.model_name}
                </td>
                <td style={{ padding: '12px 16px', fontFamily: 'var(--font-mono)', fontWeight: 700, color: row.is_champion ? '#34d399' : '#cbd5e1' }}>
                  {row.primary_metric_score.toFixed(4)}
                </td>
                <td style={{ padding: '12px 16px', fontFamily: 'var(--font-mono)', fontSize: '11px', color: '#94a3b8' }}>
                  [{row.fold_scores.join(', ')}]
                </td>
                <td style={{ padding: '12px 16px', fontFamily: 'var(--font-mono)', fontSize: '11px', color: '#cbd5e1' }}>
                  {Object.entries(row.secondary_metrics || {}).map(([k, v]) => `${k}: ${v}`).join(' | ')}
                </td>
                <td style={{ padding: '12px 16px' }}>
                  <span className="badge badge-verified" style={{ fontSize: '10px' }}>{row.status}</span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Controlled Ensemble Experiment Section */}
      {ensemble_result && ensemble_result.ensemble_score && (
        <div className="glass-panel" style={{ padding: '24px' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '12px' }}>
            <h4 style={{ fontSize: '16px' }}>Controlled Ensemble Experiment</h4>
            <span className={ensemble_result.improves_champion ? 'badge badge-verified' : 'badge badge-neutral'}>
              {ensemble_result.improves_champion ? 'ENSEMBLE IMPROVED' : 'SINGLE CHAMPION RETAINED'}
            </span>
          </div>
          <p style={{ fontSize: '13px', color: '#cbd5e1', marginBottom: '14px' }}>
            {ensemble_result.reason || 'AIDA tested an out-of-fold top-model ensemble blend under identical cross-validation folds.'}
          </p>
          <div style={{ display: 'flex', gap: '20px', fontSize: '12px', fontFamily: 'var(--font-mono)' }}>
            <div>Champion Score: <strong style={{ color: '#fff' }}>{ensemble_result.champion_score?.toFixed(4)}</strong></div>
            <div>Ensemble Score: <strong style={{ color: '#fff' }}>{ensemble_result.ensemble_score?.toFixed(4)}</strong></div>
            <div>Delta: <strong style={{ color: ensemble_result.improves_champion ? '#34d399' : '#94a3b8' }}>{ensemble_result.delta?.toFixed(4)}</strong></div>
          </div>
        </div>
      )}
    </div>
  );
};
