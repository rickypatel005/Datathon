import React, { useState } from 'react';

export const UploadView = ({ onUploadFile, onSelectSample, isUploading, sampleCatalog = [] }) => {
  const [dragActive, setDragActive] = useState(false);

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      onUploadFile(e.dataTransfer.files[0]);
    }
  };

  const handleFileInput = (e) => {
    if (e.target.files && e.target.files[0]) {
      onUploadFile(e.target.files[0]);
    }
  };

  return (
    <div style={{ maxWidth: '980px', margin: '40px auto', padding: '0 20px' }}>
      {/* Hero Header */}
      <div style={{ textAlign: 'center', marginBottom: '40px' }}>
        <div style={{ display: 'inline-block', padding: '4px 14px', borderRadius: '9999px', background: 'rgba(99, 102, 241, 0.12)', border: '1px solid rgba(99, 102, 241, 0.3)', color: '#818cf8', fontSize: '12px', fontWeight: 700, marginBottom: '16px' }}>
          AUTONOMOUS DATA SCIENTIST & ML BRAIN
        </div>
        <h1 style={{ fontSize: '38px', lineHeight: 1.2, marginBottom: '14px', background: 'linear-gradient(135deg, #fff 40%, #94a3b8)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
          Upload any dataset.<br />AIDA will validate, challenge, and explain it.
        </h1>
        <p style={{ color: 'var(--text-secondary)', fontSize: '16px', maxWidth: '620px', margin: '0 auto' }}>
          Zero manual configuration required. AIDA automatically audits data quality, detects leakage, benchmarks models, conducts error diagnostics, and generates verified insights.
        </p>
      </div>

      {/* Upload Zone */}
      <div
        className="glass-panel"
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
        style={{
          padding: '48px 30px',
          textAlign: 'center',
          cursor: 'pointer',
          border: dragActive ? '2px dashed var(--primary)' : '2px dashed var(--bg-card-border)',
          background: dragActive ? 'rgba(99, 102, 241, 0.08)' : 'var(--bg-card)',
          position: 'relative',
          marginBottom: '40px',
        }}
      >
        <input
          type="file"
          id="file-upload-input"
          accept=".csv,.xlsx,.xls"
          onChange={handleFileInput}
          style={{ position: 'absolute', top: 0, left: 0, width: '100%', height: '100%', opacity: 0, cursor: 'pointer' }}
          disabled={isUploading}
        />

        <div style={{ width: '64px', height: '64px', margin: '0 auto 20px', borderRadius: '16px', background: 'rgba(99, 102, 241, 0.1)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '28px' }}>
          📁
        </div>

        <h3 style={{ fontSize: '18px', marginBottom: '8px' }}>
          {dragActive ? 'Drop your dataset here' : 'Choose a file or drag & drop here'}
        </h3>
        <p style={{ color: 'var(--text-muted)', fontSize: '13px', marginBottom: '24px' }}>
          Supports CSV and Excel spreadsheets (.xlsx, .xls) up to 50MB
        </p>

        <button className="btn-primary" style={{ pointerEvents: 'none' }}>
          <span>Browse Dataset File</span>
        </button>
      </div>

      {/* 1-Click Judging Demos */}
      <div>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '16px' }}>
          <h4 style={{ fontSize: '16px', color: '#cbd5e1' }}>1-Click Hackathon Judging Datasets</h4>
          <span style={{ fontSize: '12px', color: 'var(--text-muted)' }}>Pre-configured empirical demonstrations</span>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '16px' }}>
          {sampleCatalog.map((sample) => (
            <div
              key={sample.sample_id}
              className="glass-panel"
              onClick={() => onSelectSample(sample.sample_id)}
              style={{
                padding: '20px',
                cursor: 'pointer',
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'space-between',
              }}
            >
              <div>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '8px' }}>
                  <span className="badge badge-high" style={{ fontSize: '9px' }}>{sample.task}</span>
                  <span style={{ fontSize: '11px', color: 'var(--text-muted)', fontFamily: 'var(--font-mono)' }}>{sample.rows} rows</span>
                </div>
                <h5 style={{ fontSize: '15px', marginBottom: '6px' }}>{sample.title}</h5>
                <p style={{ fontSize: '12px', color: 'var(--text-secondary)', lineHeight: 1.4, marginBottom: '16px' }}>
                  {sample.description}
                </p>
              </div>

              <div style={{ fontSize: '12px', fontWeight: 600, color: 'var(--primary)', display: 'flex', alignItems: 'center', gap: '6px' }}>
                Analyze Dataset <span>→</span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
