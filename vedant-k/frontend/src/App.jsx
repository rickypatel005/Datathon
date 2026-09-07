import React, { useState, useEffect } from "react";
import Header from "./components/Header";
import { UploadView } from "./components/UploadView";
import { ProgressView } from "./components/ProgressView";
import { ExecutiveDashboard } from "./components/ExecutiveDashboard";
import { InsightsView } from "./components/InsightsView";
import { ModelLabView } from "./components/ModelLabView";
import { ErrorAnalysisView } from "./components/ErrorAnalysisView";
import { DataQualityView } from "./components/DataQualityView";
import ReportView from "./components/ReportView";

const API_BASE = "";

export default function App() {
  const [currentView, setCurrentView] = useState("overview");
  const [analysisId, setAnalysisId] = useState(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [progressData, setProgressData] = useState(null);
  const [dashboardSpec, setDashboardSpec] = useState(null);
  const [sampleDatasets, setSampleDatasets] = useState([]);
  const [errorMsg, setErrorMsg] = useState(null);

  // Fetch sample datasets list on initial load
  useEffect(() => {
    fetch(`${API_BASE}/api/sample-datasets`)
      .then((res) => {
        if (res.ok) return res.json();
        return [];
      })
      .then((data) => {
        if (Array.isArray(data)) {
          setSampleDatasets(data);
        }
      })
      .catch((err) => console.log("Sample datasets fetch note:", err.message));
  }, []);

  // Polling hook for progress tracking
  useEffect(() => {
    let timer = null;

    if (isAnalyzing && analysisId) {
      const pollProgress = async () => {
        try {
          const res = await fetch(`${API_BASE}/api/analysis/${analysisId}/progress`);
          if (!res.ok) {
            throw new Error(`Failed to check progress: ${res.statusText}`);
          }
          const data = await res.json();
          setProgressData(data);

          if (data.error) {
            setIsAnalyzing(false);
            setErrorMsg(data.error);
            return;
          }

          if (data.completed) {
            setIsAnalyzing(false);
            // Fetch the completed dashboard spec
            const dashRes = await fetch(`${API_BASE}/api/analysis/${analysisId}/dashboard`);
            if (dashRes.ok) {
              const spec = await dashRes.json();
              setDashboardSpec(spec);
              setCurrentView("overview");
            } else {
              setErrorMsg("Analysis completed, but failed to load dashboard specification.");
            }
            return;
          }

          // Continue polling
          timer = setTimeout(pollProgress, 600);
        } catch (err) {
          console.error("Progress poll error:", err);
          timer = setTimeout(pollProgress, 1200);
        }
      };

      pollProgress();
    }

    return () => {
      if (timer) clearTimeout(timer);
    };
  }, [isAnalyzing, analysisId]);

  // Handle CSV file upload
  const handleUpload = async (file) => {
    setErrorMsg(null);
    setDashboardSpec(null);
    setIsAnalyzing(true);
    setProgressData({
      stage_number: 1,
      total_stages: 15,
      stage_name: "Uploading Dataset",
      stage_description: "Streaming dataset bytes to authoritative analytical core...",
      percentage: 5,
      completed: false,
    });

    try {
      const formData = new FormData();
      formData.append("file", file);

      const res = await fetch(`${API_BASE}/api/analyze`, {
        method: "POST",
        body: formData,
      });

      if (!res.ok) {
        const errJson = await res.json().catch(() => ({ detail: res.statusText }));
        throw new Error(errJson.detail || "Analysis request failed");
      }

      const data = await res.json();
      setAnalysisId(data.analysis_id);
    } catch (err) {
      setIsAnalyzing(false);
      setErrorMsg(err.message || "Network error occurred during upload.");
    }
  };

  // Handle sample dataset click
  const handleSelectSample = async (sampleId) => {
    setErrorMsg(null);
    setDashboardSpec(null);
    setIsAnalyzing(true);
    setProgressData({
      stage_number: 1,
      total_stages: 15,
      stage_name: "Initializing Benchmark Dataset",
      stage_description: "Generating benchmark dataset with real analytical signals...",
      percentage: 5,
      completed: false,
    });

    try {
      const res = await fetch(`${API_BASE}/api/analyze-sample/${sampleId}`, {
        method: "POST",
      });

      if (!res.ok) {
        const errJson = await res.json().catch(() => ({ detail: res.statusText }));
        throw new Error(errJson.detail || "Sample analysis failed to trigger");
      }

      const data = await res.json();
      setAnalysisId(data.analysis_id);
    } catch (err) {
      setIsAnalyzing(false);
      setErrorMsg(err.message || "Failed to trigger sample analysis.");
    }
  };

  // Reset to upload view
  const handleReset = () => {
    setAnalysisId(null);
    setIsAnalyzing(false);
    setProgressData(null);
    setDashboardSpec(null);
    setErrorMsg(null);
    setCurrentView("overview");
  };

  return (
    <div className="min-h-screen flex flex-col bg-background text-primary selection:bg-accent/30 selection:text-white">
      {/* Top Navigation Header */}
      <Header
        currentView={currentView}
        onSelectView={setCurrentView}
        hasActiveAnalysis={Boolean(dashboardSpec)}
        datasetName={dashboardSpec?.dataset_name || "Active Session"}
        qualityScore={dashboardSpec?.data_quality?.overall_score}
        onNewAnalysis={handleReset}
      />

      {/* Main Content Area */}
      <main className="flex-1 max-w-7xl w-full mx-auto p-4 md:p-6 lg:p-8">
        {errorMsg && (
          <div className="mb-6 p-4 rounded-xl bg-danger/10 border border-danger/30 flex items-center justify-between animate-fadeIn">
            <div className="flex items-center gap-3">
              <span className="text-xl">⚠️</span>
              <div>
                <h4 className="font-bold text-danger text-sm">Pipeline Execution Error</h4>
                <p className="text-xs text-secondary mt-0.5">{errorMsg}</p>
              </div>
            </div>
            <button
              onClick={() => setErrorMsg(null)}
              className="btn btn-secondary text-xs px-3 py-1"
            >
              Dismiss
            </button>
          </div>
        )}

        {/* View 1: Upload / Dataset Selection (when no analysis is active) */}
        {!dashboardSpec && !isAnalyzing && (
          <UploadView
            onUpload={handleUpload}
            sampleDatasets={sampleDatasets}
            onSelectSample={handleSelectSample}
            isAnalyzing={isAnalyzing}
          />
        )}

        {/* View 2: Multi-stage real-time progress tracker */}
        {isAnalyzing && (
          <div className="py-12">
            <ProgressView progress={progressData} />
          </div>
        )}

        {/* View 3: Dashboard tabs (when analysis completes) */}
        {dashboardSpec && !isAnalyzing && (
          <div className="animate-fadeIn">
            {currentView === "overview" && (
              <ExecutiveDashboard
                dashboardSpec={dashboardSpec}
                onNavigateTab={setCurrentView}
              />
            )}

            {currentView === "insights" && (
              <InsightsView
                insights={dashboardSpec.insights || []}
              />
            )}

            {currentView === "models" && (
              <ModelLabView
                modelChampionship={dashboardSpec.model_championship || {}}
              />
            )}

            {currentView === "errors" && (
              <ErrorAnalysisView
                errorAnalysis={dashboardSpec.error_analysis || {}}
              />
            )}

            {currentView === "quality" && (
              <DataQualityView
                dataQuality={dashboardSpec.data_quality || {}}
              />
            )}

            {currentView === "report" && (
              <ReportView
                dashboardSpec={dashboardSpec}
              />
            )}
          </div>
        )}
      </main>

      {/* Global Footer */}
      <footer className="border-t border-border/40 py-6 px-4 text-center text-xs text-muted">
        <div className="flex items-center justify-center gap-2">
          <span>AIDA • Autonomous Intelligence & Data Analyst</span>
          <span>•</span>
          <span className="font-mono text-accent">Phase 4.0 Verified</span>
          <span>•</span>
          <span>Strict Deterministic Intelligence</span>
        </div>
      </footer>
    </div>
  );
}
