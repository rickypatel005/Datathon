import React, { useState } from 'react';

export const InsightsView = ({ insights = [], rejectedInsights = [] }) => {
  const [selectedInsight, setSelectedInsight] = useState(null);
  const [activeTab, setActiveTab] = useState('verified'); // 'verified' | 'rejected'

  const getConfidenceBadgeClass = (conf) => {
    switch (conf?.toUpperCase()) {
      case 'HIGH': return 'badge-high';
      case 'MEDIUM': return 'badge-medium';
      case 'LOW': return 'badge-low';
      default: return 'badge-neutral';
    }
  };

  return (
    <div style={{ maxWidth: '1440px', margin: '0 auto', padding: '28px' }}>
      {/* Header & Filter Toggle */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '24px', flexWrap: 'wrap', gap: '16px' }}>
        <div>
          <div style={{ fontSize: '11px', color: 'var(--primary)', fontWeight: 700, letterSpacing: '0.05em', textTransform: 'uppercase', marginBottom: '4px' }}>
            AUTONOMOUS INVESTIGATION FINDINGS
          </div>
          <h2 style={{ fontSize: '24px' }}>Verified Analytical Insights</h2>
        </div>

        <div style={{ display: 'flex', gap: '8px', background: 'rgba(255, 255, 255, 0.04)', padding: '4px', borderRadius: '10px' }}>
          <button
            onClick={() => setActiveTab('verified')}
            style={{
              padding: '6px 16px',
              borderRadius: '8px',
              border: 'none',
              background: activeTab === 'verified' ? 'var(--primary)' : 'transparent',
              color: '#fff',
              fontWeight: 600,
              fontSize: '12px',
              cursor: 'pointer',
            }}
          >
            Verified Insights ({insights.length})
          </button>
          <button
            onClick={() => setActiveTab('rejected')}
            style={{
              padding: '6px 16px',
              borderRadius: '8px',
              border: 'none',
              background: activeTab === 'rejected' ? 'rgba(244, 63, 94, 0.2)' : 'transparent',
              color: activeTab === 'rejected' ? '#fb7185' : 'var(--text-muted)',
              fontWeight: 600,
              fontSize: '12px',
              cursor: 'pointer',
            }}
          >
            Critic Rejected ({rejectedInsights.length})
          </button>
        </div>
      </div>

      {/* Verified Insights Cards Grid */}
      {activeTab === 'verified' && (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(420px, 1fr))', gap: '20px' }}>
          {insights.map((ins) => (
            <div
              key={ins.insight_id}
              className="glass-panel"
              onClick={() => setSelectedInsight(ins)}
              style={{
                padding: '24px',
                cursor: 'pointer',
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'space-between',
              }}
            >
              <div>
                {/* Meta Badges */}
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '14px' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <span style={{ width: '26px', height: '26px', borderRadius: '6px', background: 'rgba(99, 102, 241, 0.2)', color: '#818cf8', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 800, fontSize: '12px', fontFamily: 'var(--font-mono)' }}>
                      #{ins.rank || 1}
                    </span>
                    <span className="badge badge-verified">VERIFIED</span>
                    <span className={`badge ${getConfidenceBadgeClass(ins.confidence)}`}>
                      {ins.confidence} CONFIDENCE
                    </span>
                  </div>
                  <span style={{ fontSize: '11px', color: 'var(--text-muted)', fontFamily: 'var(--font-mono)' }}>
                    {ins.method?.replace(/_/g, ' ')}
                  </span>
                </div>

                {/* Claim */}
                <h4 style={{ fontSize: '16px', lineHeight: 1.5, marginBottom: '16px', color: '#f8fafc' }}>
                  {ins.claim}
                </h4>

                {/* Evidence Metrics Highlight */}
                <div style={{ background: 'rgba(0, 0, 0, 0.25)', border: '1px solid rgba(255, 255, 255, 0.04)', borderRadius: '8px', padding: '12px 16px', marginBottom: '16px' }}>
                  <div style={{ fontSize: '10px', textTransform: 'uppercase', color: 'var(--text-muted)', fontWeight: 700, letterSpacing: '0.05em', marginBottom: '6px' }}>
                    EMPIRICAL EVIDENCE
                  </div>
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: '12px' }}>
                    {Object.entries(ins.evidence_highlights || {}).slice(0, 4).map(([k, v]) => (
                      <div key={k} style={{ fontSize: '12px', color: '#cbd5e1' }}>
                        <span style={{ color: '#94a3b8' }}>{k.replace(/_/g, ' ')}: </span>
                        <strong style={{ fontFamily: 'var(--font-mono)', color: '#fff' }}>
                          {typeof v === 'number' ? (v % 1 !== 0 ? v.toFixed(4) : v) : String(v)}
                        </strong>
                      </div>
                    ))}
                  </div>
                </div>
              </div>

              {/* Card Footer: View Provenance */}
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', borderTop: '1px solid rgba(255, 255, 255, 0.06)', paddingTop: '12px' }}>
                <span style={{ fontSize: '11px', color: 'var(--text-muted)' }}>
                  Source: {ins.source_paths?.[0] || 'AnalysisContract'}
                </span>
                <span style={{ fontSize: '12px', color: 'var(--primary)', fontWeight: 600 }}>
                  View Provenance Chain →
                </span>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Rejected Insights Tab (Proof of Adversarial Scrutiny) */}
      {activeTab === 'rejected' && (
        <div>
          <div style={{ padding: '14px 20px', background: 'rgba(244, 63, 94, 0.08)', border: '1px solid rgba(244, 63, 94, 0.2)', borderRadius: '10px', marginBottom: '20px', fontSize: '13px', color: '#fecdd3' }}>
            🛡️ <strong>Hard Numerical Verification Gate in Action:</strong> These candidate hypotheses were generated during exploration but rejected or challenged by the adversarial critic or verifier due to small sample size, trivial effect size, or lack of rigorous statistical significance.
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
            {rejectedInsights.map((rej, idx) => (
              <div key={idx} className="glass-panel" style={{ padding: '20px', borderColor: 'rgba(244, 63, 94, 0.15)' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '8px' }}>
                  <span className="badge badge-rejected">{rej.status || 'REJECTED'}</span>
                  <span style={{ fontSize: '12px', color: '#94a3b8', fontFamily: 'var(--font-mono)' }}>Candidate ID: {rej.candidate_id}</span>
                </div>
                <div style={{ fontSize: '14px', color: '#e2e8f0', marginBottom: '10px', fontWeight: 600 }}>
                  {rej.claim}
                </div>
                <div style={{ fontSize: '12px', color: '#fda4af', background: 'rgba(244, 63, 94, 0.06)', padding: '8px 12px', borderRadius: '6px' }}>
                  <strong>Rejection Reason:</strong> {rej.rejection_reason || 'Failed strict numerical verification gate.'}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Provenance Detail Modal */}
      {selectedInsight && (
        <div style={{
          position: 'fixed',
          top: 0, left: 0, right: 0, bottom: 0,
          background: 'rgba(0, 0, 0, 0.75)',
          backdropFilter: 'blur(8px)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 1000,
          padding: '20px',
        }}>
          <div className="glass-panel" style={{
            maxWidth: '720px',
            width: '100%',
            maxHeight: '90vh',
            overflowY: 'auto',
            padding: '32px',
            border: '1px solid rgba(99, 102, 241, 0.3)',
          }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '20px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <span className="badge badge-verified">VERIFIED INSIGHT</span>
                <span className={`badge ${getConfidenceBadgeClass(selectedInsight.confidence)}`}>
                  {selectedInsight.confidence}
                </span>
                <span style={{ fontSize: '12px', color: '#94a3b8', fontFamily: 'var(--font-mono)' }}>Rank #{selectedInsight.rank || 1}</span>
              </div>
              <button
                onClick={() => setSelectedInsight(null)}
                style={{ background: 'transparent', border: 'none', color: '#94a3b8', fontSize: '20px', cursor: 'pointer' }}
              >
                ✕
              </button>
            </div>

            <h3 style={{ fontSize: '18px', lineHeight: 1.5, marginBottom: '24px' }}>
              {selectedInsight.claim}
            </h3>

            {/* Complete Provenance Chain Visualization */}
            <div style={{ marginBottom: '28px' }}>
              <div style={{ fontSize: '11px', textTransform: 'uppercase', color: 'var(--primary)', fontWeight: 700, letterSpacing: '0.05em', marginBottom: '14px' }}>
                AUTONOMOUS PROVENANCE CHAIN (WHY AIDA BELIEVES THIS)
              </div>

              <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                {(selectedInsight.provenance_chain || []).map((step, idx) => (
                  <div key={idx} style={{
                    padding: '12px 16px',
                    background: 'rgba(255, 255, 255, 0.03)',
                    border: '1px solid rgba(255, 255, 255, 0.08)',
                    borderRadius: '8px',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '14px',
                  }}>
                    <div style={{ width: '28px', height: '28px', borderRadius: '50%', background: 'rgba(99, 102, 241, 0.15)', color: '#818cf8', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 700, fontSize: '11px' }}>
                      {idx + 1}
                    </div>
                    <div style={{ flex: 1 }}>
                      <div style={{ fontSize: '13px', fontWeight: 600, color: '#f8fafc' }}>{step.step}</div>
                      <div style={{ fontSize: '12px', color: '#94a3b8', fontFamily: 'var(--font-mono)' }}>{step.detail}</div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Critic Evaluation Section */}
            {selectedInsight.critic_summary && (
              <div style={{ marginBottom: '24px', padding: '16px', background: 'rgba(99, 102, 241, 0.06)', borderRadius: '8px', border: '1px solid rgba(99, 102, 241, 0.2)' }}>
                <div style={{ fontSize: '11px', fontWeight: 700, color: '#818cf8', textTransform: 'uppercase', marginBottom: '6px' }}>
                  Adversarial Critic Evaluation
                </div>
                <div style={{ fontSize: '13px', color: '#cbd5e1' }}>
                  {selectedInsight.critic_summary}
                </div>
              </div>
            )}

            <button className="btn-primary" style={{ width: '100%', justifyContent: 'center' }} onClick={() => setSelectedInsight(null)}>
              Close Insight Detail
            </button>
          </div>
        </div>
      )}
    </div>
  );
};
