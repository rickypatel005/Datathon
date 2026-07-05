import { fetchWithAuth, API_BASE_URL } from '../utils/apiClient';
import React, { useEffect, useState, useRef } from 'react';
import { UploadCloud, FileText, Database, Calendar, HardDrive, Trash2 } from 'lucide-react';
import { useStore } from '../store/useStore';

interface Dataset {
  id: string;
  name: string;
  file_type: string;
  file_size: number;
  row_count: number;
  column_count: number;
  status: string;
  created_at: string;
}

export function Datasets() {
  const [datasets, setDatasets] = useState<Dataset[]>([]);
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [previewData, setPreviewData] = useState<any>(null);
  const [isLoadingPreview, setIsLoadingPreview] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);
  
  const setActiveDatasetId = useStore(state => state.setActiveDatasetId);
  const activeDatasetId = useStore(state => state.activeDatasetId);

  const fetchDatasets = async () => {
    try {
      const res = await fetchWithAuth(`${API_BASE_URL}/api/datasets`);
      if (!res.ok) throw new Error('Failed to fetch datasets');
      const data = await res.json();
      setDatasets(data);
    } catch (err: any) {
      setError(err.message);
    }
  };

  const fetchPreview = async (id: string) => {
    setIsLoadingPreview(true);
    try {
      const res = await fetchWithAuth(`${API_BASE_URL}/api/datasets/${id}/preview`);
      if (!res.ok) throw new Error('Failed to fetch preview');
      const data = await res.json();
      setPreviewData(data);
    } catch (err: any) {
      console.error(err);
    } finally {
      setIsLoadingPreview(false);
    }
  };

  useEffect(() => {
    fetchDatasets();
  }, []);

  useEffect(() => {
    if (activeDatasetId) {
      fetchPreview(activeDatasetId);
    } else {
      setPreviewData(null);
    }
  }, [activeDatasetId]);

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setIsUploading(true);
    setError(null);
    const formData = new FormData();
    formData.append('file', file);

    try {
      const res = await fetchWithAuth(`${API_BASE_URL}/api/upload`, {
        method: 'POST',
        body: formData,
      });
      if (!res.ok) {
        const errData = await res.json().catch(() => ({}));
        throw new Error(errData.detail || 'Upload failed');
      }
      
      const newDataset = await res.json();
      setDatasets([...datasets, newDataset]);
      setActiveDatasetId(newDataset.id);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setIsUploading(false);
      if (fileInputRef.current) fileInputRef.current.value = '';
    }
  };

  const handleDelete = async (e: React.MouseEvent, id: string) => {
    e.stopPropagation(); // Prevent card click
    if (!window.confirm("Are you sure you want to delete this dataset? This will also delete any related analyses, chat histories, and ML models.")) {
      return;
    }
    
    try {
      const res = await fetchWithAuth(`${API_BASE_URL}/api/datasets/${id}`, {
        method: 'DELETE'
      });
      if (!res.ok) throw new Error('Failed to delete dataset');
      
      setDatasets(datasets.filter(d => d.id !== id));
      if (activeDatasetId === id) {
        setActiveDatasetId(null);
      }
    } catch (err: any) {
      setError(err.message);
    }
  };

  const formatSize = (bytes: number) => {
    if (!bytes) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return `${parseFloat((bytes / Math.pow(k, i)).toFixed(1))} ${sizes[i]}`;
  };

  return (
    <div className="space-y-6 max-w-6xl mx-auto">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Datasets</h1>
          <p className="text-foreground/60 mt-1">Manage and upload your data files for analysis.</p>
        </div>
        
        <div>
          <input 
            type="file" 
            ref={fileInputRef} 
            onChange={handleFileUpload} 
            accept=".csv,.xlsx,.xls,.json" 
            className="hidden" 
          />
          <button 
            onClick={() => fileInputRef.current?.click()}
            disabled={isUploading}
            className="bg-primary hover:bg-primary/90 text-primary-foreground px-4 py-2.5 rounded-lg font-medium transition-colors flex items-center justify-center gap-2 disabled:opacity-50"
          >
            <UploadCloud className="w-5 h-5" />
            {isUploading ? 'Uploading...' : 'Upload Dataset'}
          </button>
        </div>
      </div>

      {error && (
        <div className="bg-red-500/10 border border-red-500/20 text-red-500 p-4 rounded-xl">
          {error}
        </div>
      )}

      {datasets.length === 0 && !isUploading ? (
        <div className="bg-card border border-border rounded-xl p-12 flex flex-col items-center justify-center text-center">
          <div className="w-16 h-16 bg-primary/10 rounded-full flex items-center justify-center text-primary mb-4">
            <Database className="w-8 h-8" />
          </div>
          <h3 className="text-xl font-semibold mb-2">No datasets yet</h3>
          <p className="text-foreground/60 max-w-md">
            Upload your first dataset (CSV, Excel, JSON) to start analyzing, chatting, and building models.
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {datasets.map(dataset => (
            <div 
              key={dataset.id} 
              className={`bg-card border rounded-xl p-5 transition-all hover:shadow-md cursor-pointer ${activeDatasetId === dataset.id ? 'border-primary ring-1 ring-primary/20' : 'border-border'}`}
              onClick={() => setActiveDatasetId(dataset.id)}
            >
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center gap-3">
                  <div className="p-2.5 bg-blue-500/10 text-blue-500 rounded-lg">
                    <FileText className="w-6 h-6" />
                  </div>
                  <div>
                    <h3 className="font-semibold truncate max-w-[150px]" title={dataset.name}>{dataset.name}</h3>
                    <p className="text-xs text-foreground/50 uppercase font-medium mt-0.5">{dataset.file_type}</p>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  {activeDatasetId === dataset.id && (
                    <span className="bg-primary text-primary-foreground text-[10px] uppercase font-bold px-2 py-1 rounded-full">Active</span>
                  )}
                  <button 
                    onClick={(e) => handleDelete(e, dataset.id)}
                    className="p-1.5 text-foreground/40 hover:text-red-500 hover:bg-red-500/10 rounded-md transition-colors"
                    title="Delete dataset"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>
              
              <div className="space-y-2 text-sm text-foreground/70 bg-secondary/50 p-3 rounded-lg">
                <div className="flex items-center justify-between">
                  <span className="flex items-center gap-1.5"><HardDrive className="w-4 h-4" /> Size</span>
                  <span className="font-medium text-foreground">{formatSize(dataset.file_size)}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="flex items-center gap-1.5"><Database className="w-4 h-4" /> Shape</span>
                  <span className="font-medium text-foreground">{dataset.row_count} x {dataset.column_count}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="flex items-center gap-1.5"><Calendar className="w-4 h-4" /> Added</span>
                  <span className="font-medium text-foreground">{new Date(dataset.created_at).toLocaleDateString()}</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {activeDatasetId && (
        <div className="bg-card border border-border rounded-xl p-6 mt-8 shadow-sm">
          <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
            <Database className="w-5 h-5 text-primary" />
            Dataset Preview
          </h2>
          {isLoadingPreview ? (
            <div className="flex items-center justify-center p-12">
              <div className="w-8 h-8 border-4 border-primary border-t-transparent rounded-full animate-spin"></div>
            </div>
          ) : previewData ? (
            <div className="overflow-x-auto rounded-lg border border-border">
              <table className="w-full text-sm text-left">
                <thead className="text-xs uppercase bg-secondary/50 text-foreground/70">
                  <tr>
                    {previewData.columns.map((col: string) => (
                      <th key={col} className="px-4 py-3 font-semibold">{col}</th>
                    ))}
                  </tr>
                </thead>
                <tbody className="divide-y divide-border">
                  {previewData.head.map((row: any, i: number) => (
                    <tr key={i} className="hover:bg-secondary/20 transition-colors">
                      {previewData.columns.map((col: string) => (
                        <td key={col} className="px-4 py-2.5 whitespace-nowrap">
                          {row[col] !== null ? String(row[col]) : <span className="text-foreground/40 italic">null</span>}
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="text-center p-8 text-foreground/50">
              Failed to load preview data.
            </div>
          )}
        </div>
      )}
    </div>
  );
}

