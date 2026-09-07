import React from 'react';

export const Header = ({
  currentView,
  setCurrentView,
  onSelectView,
  datasetName,
  taskType,
  qualityScore,
  onNewUpload,
  onNewAnalysis,
  hasActiveAnalysis = true,
}) => {
  const setView = setCurrentView || onSelectView;
  const handleNew = onNewUpload || onNewAnalysis;
  const navItems = [
    { id: 'overview', label: 'Executive Overview', icon: '📊' },
    { id: 'insights', label: 'Verified Insights', icon: '✨' },
    { id: 'models', label: 'Model Lab', icon: '🏆' },
    { id: 'errors', label: 'Error Diagnostics', icon: '🔍' },
    { id: 'quality', label: 'Quality & Leakage', icon: '🛡️' },
    { id: 'report', label: 'Executive Report', icon: '📑' },
  ];

  return (
    <header style={{
      borderBottom: '1px solid var(--bg-card-border)',
      background: 'rgba(9, 13, 22, 0.9)',
      backdropFilter: 'blur(16px)',
      position: 'sticky',
      top: 0,
      zIndex: 100,
      padding: '12px 28px',
    }}>
      <div style={{ maxWidth: '1440px', margin: '0 auto', display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '16px' }}>
        {/* Brand */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
          <div style={{
            width: '38px',
            height: '38px',
            borderRadius: '10px',
            background: 'linear-gradient(135deg, #6366f1, #06b6d4)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontWeight: 800,
            fontSize: '18px',
            color: '#fff',
            boxShadow: '0 0 16px var(--primary-glow)',
          }}>
            A
          </div>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <span style={{ fontSize: '18px', fontWeight: 800, letterSpacing: '-0.02em', color: '#fff' }}>AIDA</span>
              <span style={{ fontSize: '10px', padding: '2px 6px', background: 'rgba(99, 102, 241, 0.2)', color: '#818cf8', borderRadius: '4px', fontWeight: 700 }}>v1.0 ENGINE</span>
            </div>
            <div style={{ fontSize: '11px', color: 'var(--text-muted)' }}>Autonomous Intelligence & Data Analyst</div>
          </div>

          {datasetName && (
            <div style={{ marginLeft: '16px', paddingLeft: '16px', borderLeft: '1px solid #334155', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <span style={{ fontSize: '13px', fontWeight: 600, color: '#cbd5e1' }}>{datasetName}</span>
              {taskType && (
                <span className="badge badge-high" style={{ fontSize: '10px' }}>{taskType}</span>
              )}
            </div>
          )}
        </div>

        {/* Navigation Tabs */}
        {hasActiveAnalysis && (
          <nav style={{ display: 'flex', gap: '6px', overflowX: 'auto' }}>
            {navItems.map((item) => {
              const isActive = currentView === item.id;
              return (
                <button
                  key={item.id}
                  id={`nav-tab-${item.id}`}
                  onClick={() => setView && setView(item.id)}
                  style={{
                    background: isActive ? 'rgba(99, 102, 241, 0.15)' : 'transparent',
                    color: isActive ? '#818cf8' : 'var(--text-secondary)',
                    border: isActive ? '1px solid rgba(99, 102, 241, 0.3)' : '1px solid transparent',
                    padding: '8px 14px',
                    borderRadius: '8px',
                    fontSize: '13px',
                    fontWeight: 600,
                    cursor: 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '6px',
                    transition: 'all 0.15s ease',
                  }}
                >
                  <span>{item.icon}</span>
                  <span>{item.label}</span>
                </button>
              );
            })}
          </nav>
        )}

        {/* Action Button */}
        <div>
          <button
            id="btn-nav-new-dataset"
            className="btn-secondary"
            onClick={handleNew}
            style={{ fontSize: '12px', padding: '7px 14px' }}
          >
            Upload New Dataset
          </button>
        </div>
      </div>
    </header>
  );
};

export default Header;

