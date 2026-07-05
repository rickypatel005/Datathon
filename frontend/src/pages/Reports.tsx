import { fetchWithAuth, API_BASE_URL } from '../utils/apiClient';
import { useState, useEffect } from "react";
import { useStore } from '../store/useStore';
import { FileText, Database, Plus, Clock, CheckCircle2, XCircle, AlertCircle, RefreshCw } from 'lucide-react';
import { Link } from 'react-router-dom';
import ReactMarkdown from 'react-markdown';

interface AnalysisHistory {
  id: string;
  dataset_id: string;
  analysis_type: string;
  status: string;
  result?: {
    crew_report?: string;
    eda?: any;
    cleaning?: any;
  };
  summary?: string;
  created_at: string;
}

export function Reports() {
  const activeDatasetId = useStore(state => state.activeDatasetId);
  const [reports, setReports] = useState<AnalysisHistory[]>([]);
  const [selectedReportId, setSelectedReportId] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isGenerating, setIsGenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchReports = async () => {
    if (!activeDatasetId) return;
    setIsLoading(true);
    try {
      const res = await fetchWithAuth(`${API_BASE_URL}/api/datasets/${activeDatasetId}/analyses`);
      if (!res.ok) throw new Error('Failed to fetch reports');
      const data = await res.json();
      setReports(data);
      if (data.length > 0 && !selectedReportId) {
        setSelectedReportId(data[0].id);
      }
    } catch (err: any) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchReports();
    // Set up polling to update running reports
    const interval = setInterval(() => {
      fetchReports();
    }, 10000); // poll every 10 seconds
    return () => clearInterval(interval);
  }, [activeDatasetId]);

  const handleGenerateReport = async () => {
    if (!activeDatasetId) return;
    setIsGenerating(true);
    setError(null);
    try {
      const res = await fetchWithAuth(`${API_BASE_URL}/api/analyze`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          dataset_id: activeDatasetId,
          analysis_type: 'full'
        })
      });
      if (!res.ok) throw new Error('Failed to start analysis');
      const newAnalysis = await res.json();
      setReports([newAnalysis, ...reports]);
      setSelectedReportId(newAnalysis.id);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setIsGenerating(false);
    }
  };

  if (!activeDatasetId) {
    return (
      <div className="max-w-4xl mx-auto flex flex-col items-center justify-center min-h-[60vh] text-center space-y-6">
        <div className="w-20 h-20 bg-primary/10 rounded-full flex items-center justify-center text-primary">
          <Database className="w-10 h-10" />
        </div>
        <div>
          <h2 className="text-2xl font-bold mb-2">No Dataset Selected</h2>
          <p className="text-foreground/60 max-w-md mx-auto">
            Please select an active dataset from the Datasets tab before viewing or generating reports.
          </p>
        </div>
        <Link 
          to="/datasets" 
          className="bg-primary hover:bg-primary/90 text-primary-foreground px-6 py-2.5 rounded-lg font-medium transition-colors"
        >
          Go to Datasets
        </Link>
      </div>
    );
  }

  const selectedReport = reports.find(r => r.id === selectedReportId);

  return (
    <div className="space-y-6 max-w-7xl mx-auto h-[calc(100vh-8rem)] flex flex-col">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight flex items-center gap-3">
            <FileText className="w-8 h-8 text-primary" />
            AI Analysis Reports
          </h1>
          <p className="text-foreground/60 mt-1">Generate comprehensive data audits and AI-authored summaries.</p>
        </div>
        <button
          onClick={handleGenerateReport}
          disabled={isGenerating}
          className="bg-primary hover:bg-primary/90 text-primary-foreground px-4 py-2.5 rounded-lg font-medium transition-colors flex items-center gap-2 disabled:opacity-50"
        >
          {isGenerating ? <RefreshCw className="w-5 h-5 animate-spin" /> : <Plus className="w-5 h-5" />}
          Generate New Report
        </button>
      </div>

      {error && (
        <div className="bg-red-500/10 border border-red-500/20 text-red-500 p-4 rounded-xl flex items-start gap-3">
          <AlertCircle className="w-5 h-5 flex-shrink-0 mt-0.5" />
          <p>{error}</p>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6 flex-1 min-h-0">
        <div className="lg:col-span-1 bg-card border border-border rounded-xl flex flex-col overflow-hidden">
          <div className="p-4 border-b border-border bg-secondary/30">
            <h2 className="font-semibold">Report History</h2>
          </div>
          <div className="flex-1 overflow-y-auto p-2 space-y-2">
            {isLoading && reports.length === 0 ? (
              <div className="flex justify-center p-8">
                <div className="w-6 h-6 border-2 border-primary border-t-transparent rounded-full animate-spin"></div>
              </div>
            ) : reports.length === 0 ? (
              <div className="text-center p-6 text-foreground/50 text-sm">
                No reports found for this dataset. Click "Generate New Report" to start.
              </div>
            ) : (
              reports.map(report => (
                <div
                  key={report.id}
                  onClick={() => setSelectedReportId(report.id)}
                  className={`p-3 rounded-lg cursor-pointer transition-colors border ${
                    selectedReportId === report.id
                      ? 'bg-primary/10 border-primary/30'
                      : 'hover:bg-secondary/50 border-transparent'
                  }`}
                >
                  <div className="flex items-center justify-between mb-1">
                    <span className="font-medium text-sm capitalize">{report.analysis_type} Analysis</span>
                    {report.status === 'completed' && <CheckCircle2 className="w-4 h-4 text-green-500" />}
                    {report.status === 'running' && <RefreshCw className="w-4 h-4 text-blue-500 animate-spin" />}
                    {report.status === 'failed' && <XCircle className="w-4 h-4 text-red-500" />}
                    {report.status === 'pending' && <Clock className="w-4 h-4 text-foreground/40" />}
                  </div>
                  <div className="text-xs text-foreground/50">
                    {new Date(report.created_at).toLocaleString()}
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

        <div className="lg:col-span-3 bg-card border border-border rounded-xl flex flex-col overflow-hidden">
          {selectedReport ? (
            <div className="flex-1 overflow-y-auto p-8 prose prose-sm sm:prose-base dark:prose-invert max-w-none">
              {selectedReport.status === 'running' || selectedReport.status === 'pending' ? (
                <div className="flex flex-col items-center justify-center h-full text-foreground/50 space-y-4">
                  <div className="w-12 h-12 border-4 border-primary border-t-transparent rounded-full animate-spin"></div>
                  <p className="text-lg">The AI is analyzing your data. This may take a minute...</p>
                  <p className="text-sm italic">You can navigate away; it will run in the background.</p>
                </div>
              ) : selectedReport.status === 'failed' ? (
                <div className="flex flex-col items-center justify-center h-full text-red-500/80 space-y-4">
                  <XCircle className="w-16 h-16" />
                  <p className="text-lg font-semibold">Analysis Failed</p>
                  <p className="text-sm max-w-md text-center">{selectedReport.summary || "An unexpected error occurred."}</p>
                </div>
              ) : selectedReport.result?.crew_report ? (
                <div>
                  <ReactMarkdown>{selectedReport.result.crew_report}</ReactMarkdown>
                </div>
              ) : (
                <div className="flex flex-col items-center justify-center h-full text-foreground/50">
                  <p>No report content available.</p>
                </div>
              )}
            </div>
          ) : (
            <div className="flex-1 flex items-center justify-center text-foreground/40 text-center">
              <div>
                <FileText className="w-16 h-16 mb-4 opacity-50 mx-auto" />
                <p className="text-lg">Select a report from the history or generate a new one.</p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

