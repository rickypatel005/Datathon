import { useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  UploadCloud,
  Sparkles,
  CheckCircle2,
  Trash2,
  ArrowRight,
  BarChart2,
  TrendingUp,
  MessageSquare,
  Wand2,
  FileSpreadsheet
} from 'lucide-react';
import { AnalyzingProgress } from '../components/AnalyzingProgress';

interface SelectedFile {
  id: string;
  name: string;
  size: string;
  type: string;
}

export function NewAnalysis() {
  const navigate = useNavigate();
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);

  // Default queue matches the reference image
  const [files, setFiles] = useState<SelectedFile[]>([
    { id: 'f1', name: 'sales_data_2024.csv', size: '2.4 MB', type: 'CSV' },
    { id: 'f2', name: 'customers.xlsx', size: '1.1 MB', type: 'XLSX' },
    { id: 'f3', name: 'marketing_data.csv', size: '856 KB', type: 'CSV' }
  ]);

  const handleRemoveFile = (id: string) => {
    setFiles((prev) => prev.filter((f) => f.id !== id));
  };

  const handleClearAll = () => {
    setFiles([]);
  };

  const handleFileDrop = (e: React.DragEvent) => {
    e.preventDefault();
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      const newFiles: SelectedFile[] = Array.from(e.dataTransfer.files).map((f, i) => ({
        id: `drop-${Date.now()}-${i}`,
        name: f.name,
        size: `${(f.size / (1024 * 1024)).toFixed(1)} MB`,
        type: f.name.split('.').pop()?.toUpperCase() || 'DATA'
      }));
      setFiles((prev) => [...prev, ...newFiles]);
    }
  };

  const handleFileInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      const newFiles: SelectedFile[] = Array.from(e.target.files).map((f, i) => ({
        id: `upload-${Date.now()}-${i}`,
        name: f.name,
        size: `${(f.size / (1024 * 1024)).toFixed(1)} MB`,
        type: f.name.split('.').pop()?.toUpperCase() || 'DATA'
      }));
      setFiles((prev) => [...prev, ...newFiles]);
    }
  };

  const handleRunAnalysis = () => {
    if (files.length === 0) return;
    setIsAnalyzing(true);
  };

  const handleAnalysisComplete = () => {
    setIsAnalyzing(false);
    navigate('/');
  };

  if (isAnalyzing) {
    return <AnalyzingProgress onComplete={handleAnalysisComplete} />;
  }

  return (
    <div className="max-w-4xl mx-auto py-4 px-4 space-y-7 animate-in fade-in duration-200">
      {/* Top Header */}
      <div className="text-center space-y-2">
        <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-[#171f38] text-indigo-300 border border-indigo-500/20 shadow-sm">
          <Sparkles className="w-3.5 h-3.5 text-indigo-400" />
          <span>Turn Data into Decisions</span>
        </div>

        <h1 className="text-3xl sm:text-4xl font-black tracking-tight text-white">
          Automated Insight Analyst
        </h1>
        <p className="text-xs sm:text-sm text-slate-400">
          Upload your data. We'll find the story.
        </p>
      </div>

      {/* 4 Feature Pills Bar */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-2.5">
        <div className="bg-[#0f172a] border border-[#1e293b] rounded-xl py-2 px-3 flex items-center justify-center gap-2 text-xs text-slate-300 shadow-sm">
          <Wand2 className="w-3.5 h-3.5 text-sky-400" />
          <span className="font-medium">Automatic data cleaning</span>
        </div>
        <div className="bg-[#0f172a] border border-[#1e293b] rounded-xl py-2 px-3 flex items-center justify-center gap-2 text-xs text-slate-300 shadow-sm">
          <TrendingUp className="w-3.5 h-3.5 text-emerald-400" />
          <span className="font-medium">Find patterns & trends</span>
        </div>
        <div className="bg-[#0f172a] border border-[#1e293b] rounded-xl py-2 px-3 flex items-center justify-center gap-2 text-xs text-slate-300 shadow-sm">
          <BarChart2 className="w-3.5 h-3.5 text-purple-400" />
          <span className="font-medium">Beautiful visualizations</span>
        </div>
        <div className="bg-[#0f172a] border border-[#1e293b] rounded-xl py-2 px-3 flex items-center justify-center gap-2 text-xs text-slate-300 shadow-sm">
          <MessageSquare className="w-3.5 h-3.5 text-amber-400" />
          <span className="font-medium">Plain-language insights</span>
        </div>
      </div>

      {/* Big Drag and Drop Box */}
      <div
        onDragOver={(e) => e.preventDefault()}
        onDrop={handleFileDrop}
        onClick={() => fileInputRef.current?.click()}
        className="bg-[#0e1629]/70 border-2 border-dashed border-[#22304f] hover:border-indigo-500/50 rounded-2xl p-10 flex flex-col items-center justify-center text-center cursor-pointer transition-all hover:bg-[#121c33]/80 group shadow-lg"
      >
        <input
          ref={fileInputRef}
          type="file"
          multiple
          accept=".csv,.xlsx,.xls,.json,.txt"
          className="hidden"
          onChange={handleFileInputChange}
        />

        <div className="w-16 h-16 rounded-2xl bg-gradient-to-tr from-indigo-500/20 to-sky-500/20 border border-indigo-500/30 flex items-center justify-center text-indigo-400 mb-3 shadow-inner group-hover:scale-105 transition-transform">
          <UploadCloud className="w-8 h-8" />
        </div>

        <h3 className="text-base font-bold text-white tracking-tight">
          Drop your files here
        </h3>
        <p className="text-xs text-indigo-400 mt-0.5">
          or click to browse
        </p>
        <span className="text-[11px] text-slate-500 mt-2">
          Supports CSV, XLSX, JSON, TXT and more
        </span>
      </div>

      {/* Selected Files Queue */}
      {files.length > 0 && (
        <div className="space-y-3">
          <div className="flex items-center justify-between text-xs text-slate-400 px-1">
            <span className="font-semibold text-slate-300">{files.length} files selected</span>
            <button
              onClick={handleClearAll}
              type="button"
              className="text-slate-400 hover:text-white transition-colors"
            >
              Clear all
            </button>
          </div>

          <div className="space-y-2">
            {files.map((file) => (
              <div
                key={file.id}
                className="bg-[#0f172a] border border-[#1e293b] rounded-xl px-4 py-3 flex items-center justify-between text-xs shadow-sm hover:border-slate-700 transition-colors"
              >
                <div className="flex items-center gap-3 min-w-0">
                  <div className="p-2 rounded-lg bg-indigo-500/10 text-indigo-400">
                    <FileSpreadsheet className="w-4 h-4" />
                  </div>
                  <div className="min-w-0">
                    <p className="font-semibold text-white truncate">{file.name}</p>
                    <p className="text-[10px] text-slate-400 mt-0.5">
                      {file.type} &bull; {file.size}
                    </p>
                  </div>
                </div>

                <div className="flex items-center gap-3">
                  <div className="w-5 h-5 rounded-full bg-emerald-500/10 text-emerald-400 flex items-center justify-center">
                    <CheckCircle2 className="w-3.5 h-3.5" />
                  </div>
                  <button
                    onClick={() => handleRemoveFile(file.id)}
                    type="button"
                    className="text-slate-500 hover:text-red-400 p-1 transition-colors"
                    title="Remove file"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>
            ))}
          </div>

          {/* Large Gradient Run Analysis Button */}
          <div className="pt-2">
            <button
              onClick={handleRunAnalysis}
              type="button"
              className="w-full bg-gradient-to-r from-[#6366f1] via-[#4f46e5] to-[#3b82f6] hover:from-[#5558e6] hover:to-[#2563eb] text-white font-bold py-3.5 rounded-xl text-sm shadow-xl shadow-indigo-500/25 flex items-center justify-center gap-2 transition-all group"
            >
              <span>Run Analysis</span>
              <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
