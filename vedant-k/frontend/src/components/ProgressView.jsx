import React from 'react';

export const ProgressView = ({ progressData, filename }) => {
  const stages = progressData?.stages || [];
  const currentStage = progressData?.stage_number || progressData?.current_stage || 1;
  const totalStages = progressData?.total_stages || stages.length || 15;
  const progressPct = progressData?.percentage != null ? progressData.percentage : Math.min(100, Math.round((currentStage / totalStages) * 100));

  return (
    <div style={{ maxWidth: '820px', margin: '40px auto', padding: '0 20px' }}>
      <div className="glass-panel" style={{ padding: '36px' }}>
        {/* Progress Header */}
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '16px', flexWrap: 'wrap', gap: '12px' }}>
          <div>
            <div style={{ fontSize: '12px', color: 'var(--primary)', fontWeight: 700, letterSpacing: '0.05em', marginBottom: '4px' }}>
              AUTONOMOUS EXECUTION IN PROGRESS
            </div>
            <h2 style={{ fontSize: '22px' }}>Analyzing: {filename || 'Dataset'}</h2>
          </div>
          <div style={{ textAlign: 'right' }}>
            <div style={{ fontSize: '28px', fontWeight: 800, fontFamily: 'var(--font-mono)', color: 'var(--primary)' }}>
              {progressPct}%
            </div>
            <div style={{ fontSize: '11px', color: 'var(--text-muted)' }}>
              Stage {currentStage} of {totalStages}
            </div>
          </div>
        </div>

        {/* Global Progress Bar */}
        <div style={{ width: '100%', height: '8px', background: 'rgba(255, 255, 255, 0.08)', borderRadius: '9999px', overflow: 'hidden', marginBottom: '32px' }}>
          <div style={{
            width: `${progressPct}%`,
            height: '100%',
            background: 'linear-gradient(90deg, #6366f1, #06b6d4)',
            borderRadius: '9999px',
            transition: 'width 0.4s ease',
          }} />
        </div>

        {/* 15 Stage Timeline Grid */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(240px, 1fr))', gap: '12px' }}>
          {stages.map((st) => {
            const isCompleted = st.status === 'completed';
            const isRunning = st.status === 'running';
            const isFailed = st.status === 'failed';

            let icon = '○';
            let color = '#64748b';
            let bg = 'rgba(255, 255, 255, 0.02)';
            let borderColor = 'rgba(255, 255, 255, 0.05)';

            if (isCompleted) {
              icon = '✓';
              color = '#34d399';
              bg = 'rgba(16, 185, 129, 0.08)';
              borderColor = 'rgba(16, 185, 129, 0.2)';
            } else if (isRunning) {
              icon = '●';
              color = '#818cf8';
              bg = 'rgba(99, 102, 241, 0.12)';
              borderColor = 'rgba(99, 102, 241, 0.4)';
            } else if (isFailed) {
              icon = '✕';
              color = '#f43f5e';
              bg = 'rgba(244, 63, 94, 0.1)';
              borderColor = 'rgba(244, 63, 94, 0.3)';
            }

            return (
              <div
                key={st.id}
                style={{
                  padding: '12px 16px',
                  borderRadius: '10px',
                  background: bg,
                  border: `1px solid ${borderColor}`,
                  display: 'flex',
                  alignItems: 'center',
                  gap: '12px',
                  transition: 'all 0.2s',
                }}
              >
                <div style={{
                  width: '24px',
                  height: '24px',
                  borderRadius: '50%',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  fontSize: '12px',
                  fontWeight: 'bold',
                  color: color,
                  border: `1px solid ${color}`,
                }}>
                  {icon}
                </div>
                <div style={{ flex: 1 }}>
                  <div style={{ fontSize: '13px', fontWeight: 600, color: isRunning ? '#fff' : (isCompleted ? '#cbd5e1' : '#64748b') }}>
                    {st.name}
                  </div>
                  <div style={{ fontSize: '10px', color: color, textTransform: 'uppercase', fontWeight: 700 }}>
                    {st.status}
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};
