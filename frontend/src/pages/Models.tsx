import { fetchWithAuth, API_BASE_URL } from '../utils/apiClient';
import React, { useState, useEffect } from 'react';
import { useStore } from '../store/useStore';
import { BrainCircuit, Database, AlertCircle, Play, CheckCircle2, XCircle, Clock, Trophy, Sliders } from 'lucide-react';
import { Link } from 'react-router-dom';
import { ModelChampionship } from '../components/ModelChampionship';
import mockData from '../mocks/mock_contracts.json';
import type { AnalysisContract } from '../types/contracts';

export function Models() {
  const activeDatasetId = useStore(state => state.activeDatasetId);
  const setActiveDatasetId = useStore(state => state.setActiveDatasetId);
  const [columns, setColumns] = useState<string[]>([]);
  const [models, setModels] = useState<any[]>([]);
  const [datasets, setDatasets] = useState<any[]>([]);
  const [selectedModel, setSelectedModel] = useState<any | null>(null);
  
  // Form state
  const [modelType, setModelType] = useState('classification');
  const [algorithm, setAlgorithm] = useState('');
  const [targetColumn, setTargetColumn] = useState('');
  const [featureColumns] = useState<string[]>([]);
  
  const [isTraining, setIsTraining] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchModels = async () => {
    try {
      const res = await fetchWithAuth(`${API_BASE_URL}/api/models`);
      if (res.ok) {
        const data = await res.json();
        setModels(data);
      }
    } catch (err) {
      console.error("Failed to fetch models", err);
    }
  };

  const fetchDatasets = async () => {
    try {
      const res = await fetchWithAuth(`${API_BASE_URL}/api/datasets`);
      if (res.ok) {
        const data = await res.json();
        setDatasets(data);
      }
    } catch (err) {
      console.error("Failed to fetch datasets", err);
    }
  };

  useEffect(() => {
    fetchModels();
    fetchDatasets();
    // Poll for updates every 5 seconds if there are training models
    const interval = setInterval(() => {
      fetchModels();
    }, 5000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    if (!activeDatasetId) return;
    
    const fetchColumns = async () => {
      try {
        const res = await fetchWithAuth(`${API_BASE_URL}/api/datasets/${activeDatasetId}/preview`);
        if (res.ok) {
          const data = await res.json();
          setColumns(data.columns || []);
          if (data.columns && data.columns.length > 0) {
            setTargetColumn(data.columns[data.columns.length - 1]); // default to last column
          }
        }
      } catch (err) {
        console.error("Failed to fetch columns", err);
      }
    };
    
    fetchColumns();
  }, [activeDatasetId]);

  const handleTrain = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!activeDatasetId) return;
    
    setIsTraining(true);
    setError(null);

    try {
      const payload = {
        dataset_id: activeDatasetId,
        model_type: modelType,
        algorithm: algorithm || null,
        target_column: modelType !== 'clustering' ? targetColumn : null,
        feature_columns: featureColumns.length > 0 ? featureColumns : null,
      };

      const res = await fetchWithAuth(`${API_BASE_URL}/api/train-model`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      
      if (!res.ok) {
        const errData = await res.json();
        throw new Error(errData.detail || 'Failed to start training');
      }
      
      await fetchModels();
    } catch (err: any) {
      setError(err.message);
    } finally {
      setIsTraining(false);
    }
  };

  const getStatusIcon = (status: string) => {
    switch(status) {
      case 'ready': return <CheckCircle2 className="w-5 h-5 text-green-500" />;
      case 'failed': return <XCircle className="w-5 h-5 text-red-500" />;
      case 'training': return <Clock className="w-5 h-5 text-yellow-500 animate-pulse" />;
      default: return <Clock className="w-5 h-5 text-foreground/50" />;
    }
  };

  const [tabMode, setTabMode] = useState<'championship' | 'custom'>('championship');
  const [analysisContract, setAnalysisContract] = useState<AnalysisContract>(
    (mockData as any).churn_dataset.analysis
  );

  useEffect(() => {
    if (!activeDatasetId) return;
    const fetchChampionship = async () => {
      try {
        const res = await fetchWithAuth(`${API_BASE_URL}/api/pipeline/championship/${activeDatasetId}`);
        if (res.ok) {
          const data = await res.json();
          if (data && data.models) {
            setAnalysisContract(data);
          }
        }
      } catch (e) {
        console.warn('Could not fetch pipeline championship, using fallback', e);
      }
    };
    fetchChampionship();
  }, [activeDatasetId]);

  return (
    <div className="space-y-6 max-w-6xl mx-auto pb-12">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight flex items-center gap-3">
            <BrainCircuit className="w-8 h-8 text-primary" />
            Machine Learning Intelligence
          </h1>
          <p className="text-foreground/60 mt-1">Autonomous algorithmic benchmarking, champion selection, and model training.</p>
        </div>

        <div className="flex items-center gap-1.5 bg-muted/60 p-1 rounded-xl border border-border">
          <button
            onClick={() => setTabMode('championship')}
            className={`px-3.5 py-1.5 rounded-lg text-xs font-semibold flex items-center gap-1.5 transition-all ${
              tabMode === 'championship'
                ? 'bg-primary text-primary-foreground shadow-sm'
                : 'text-foreground/70 hover:text-foreground'
            }`}
          >
            <Trophy className="w-3.5 h-3.5" />
            <span>Model Championship</span>
          </button>
          <button
            onClick={() => setTabMode('custom')}
            className={`px-3.5 py-1.5 rounded-lg text-xs font-semibold flex items-center gap-1.5 transition-all ${
              tabMode === 'custom'
                ? 'bg-primary text-primary-foreground shadow-sm'
                : 'text-foreground/70 hover:text-foreground'
            }`}
          >
            <Sliders className="w-3.5 h-3.5" />
            <span>Manual Training Studio</span>
          </button>
        </div>
      </div>

      {tabMode === 'championship' ? (
        <ModelChampionship analysis={analysisContract} />
      ) : (
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-1 space-y-6">
          <div className="bg-card border border-border rounded-xl p-5">
            <h2 className="font-semibold mb-4 text-lg">Train New Model</h2>
            
            {datasets.length === 0 ? (
              <div className="text-center py-6">
                <Database className="w-10 h-10 mx-auto text-foreground/30 mb-3" />
                <p className="text-sm text-foreground/60 mb-4">No datasets available</p>
                <Link to="/datasets" className="text-sm text-primary hover:underline">Upload a Dataset</Link>
              </div>
            ) : (
              <form onSubmit={handleTrain} className="space-y-4">
                {error && (
                  <div className="bg-red-500/10 border border-red-500/20 text-red-500 p-3 rounded-lg text-sm flex items-start gap-2">
                    <AlertCircle className="w-4 h-4 flex-shrink-0 mt-0.5" />
                    <p>{error}</p>
                  </div>
                )}

                <div>
                  <label className="block text-sm font-medium mb-1 text-foreground/80">Dataset</label>
                  <select 
                    value={activeDatasetId || ''} 
                    onChange={e => setActiveDatasetId(e.target.value)}
                    className="w-full bg-secondary border border-border rounded-lg px-3 py-2 outline-none focus:ring-2 focus:ring-primary/50 text-sm"
                  >
                    <option value="" disabled>-- Select Dataset --</option>
                    {datasets.map(d => (
                      <option key={d.id} value={d.id}>{d.name}</option>
                    ))}
                  </select>
                </div>
                
                <div>
                  <label className="block text-sm font-medium mb-1 text-foreground/80">Model Type</label>
                  <select 
                    value={modelType} 
                    onChange={e => setModelType(e.target.value)}
                    className="w-full bg-secondary border border-border rounded-lg px-3 py-2 outline-none focus:ring-2 focus:ring-primary/50 text-sm"
                  >
                    <option value="classification">Classification</option>
                    <option value="regression">Regression</option>
                    <option value="clustering">Clustering</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium mb-1 text-foreground/80">Algorithm (Optional)</label>
                  <select 
                    value={algorithm} 
                    onChange={e => setAlgorithm(e.target.value)}
                    className="w-full bg-secondary border border-border rounded-lg px-3 py-2 outline-none focus:ring-2 focus:ring-primary/50 text-sm"
                  >
                    <option value="">Auto-select best</option>
                    {modelType === 'classification' && (
                      <>
                        <option value="random_forest">Random Forest</option>
                        <option value="logistic_regression">Logistic Regression</option>
                        <option value="svm">Support Vector Machine (SVM)</option>
                        <option value="decision_tree">Decision Tree</option>
                        <option value="gradient_boosting">Gradient Boosting</option>
                        <option value="knn">K-Nearest Neighbors (KNN)</option>
                        <option value="naive_bayes">Naive Bayes</option>
                        <option value="mlp">Neural Network (MLP)</option>
                      </>
                    )}
                    {modelType === 'regression' && (
                      <>
                        <option value="random_forest">Random Forest</option>
                        <option value="linear_regression">Linear Regression</option>
                        <option value="svr">Support Vector Regression (SVR)</option>
                        <option value="decision_tree">Decision Tree</option>
                        <option value="gradient_boosting">Gradient Boosting</option>
                        <option value="knn">K-Nearest Neighbors (KNN)</option>
                        <option value="ridge">Ridge Regression</option>
                        <option value="lasso">Lasso Regression</option>
                        <option value="mlp">Neural Network (MLP)</option>
                      </>
                    )}
                    {modelType === 'clustering' && (
                      <>
                        <option value="kmeans">K-Means</option>
                        <option value="dbscan">DBSCAN</option>
                        <option value="agglomerative">Agglomerative Clustering</option>
                        <option value="gaussian_mixture">Gaussian Mixture Model</option>
                      </>
                    )}
                  </select>
                </div>

                {modelType !== 'clustering' && (
                  <div>
                    <label className="block text-sm font-medium mb-1 text-foreground/80">Target Column</label>
                    <select 
                      value={targetColumn} 
                      onChange={e => setTargetColumn(e.target.value)}
                      className="w-full bg-secondary border border-border rounded-lg px-3 py-2 outline-none focus:ring-2 focus:ring-primary/50 text-sm"
                    >
                      <option value="">-- Select Target --</option>
                      {columns.map(col => (
                        <option key={col} value={col}>{col}</option>
                      ))}
                    </select>
                  </div>
                )}

                <button 
                  type="submit" 
                  disabled={isTraining || (modelType !== 'clustering' && !targetColumn)}
                  className="w-full bg-primary hover:bg-primary/90 text-primary-foreground py-2.5 rounded-lg font-medium transition-colors disabled:opacity-50 mt-4 flex items-center justify-center gap-2"
                >
                  {isTraining ? (
                    <>
                      <div className="w-4 h-4 border-2 border-primary-foreground border-t-transparent rounded-full animate-spin"></div>
                      Starting...
                    </>
                  ) : (
                    <>
                      <Play className="w-4 h-4" />
                      Train Model
                    </>
                  )}
                </button>
              </form>
            )}
          </div>
        </div>

        <div className="lg:col-span-2 space-y-4">
          <h2 className="font-semibold text-lg flex items-center justify-between">
            Your Models
            <span className="bg-secondary text-foreground/70 text-xs px-2 py-1 rounded-full">{models.length} Total</span>
          </h2>
          
          {models.length === 0 ? (
            <div className="bg-card border border-border rounded-xl p-8 flex flex-col items-center justify-center text-center">
              <BrainCircuit className="w-12 h-12 text-foreground/20 mb-3" />
              <h3 className="text-lg font-medium mb-1">No Models Trained</h3>
              <p className="text-foreground/60 max-w-sm">
                You haven't trained any machine learning models yet. Use the form on the left to start your first training job.
              </p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {models.map(model => (
                <div key={model.id} className="bg-card border border-border rounded-xl p-5 flex flex-col h-full hover:border-primary/50 transition-colors">
                  <div className="flex items-start justify-between mb-3">
                    <div>
                      <h3 className="font-medium text-foreground truncate" title={model.name}>{model.name}</h3>
                      <p className="text-xs text-foreground/60 capitalize">{model.model_type} • {model.algorithm || 'Auto'}</p>
                    </div>
                    {getStatusIcon(model.status)}
                  </div>
                  
                  <div className="flex-1">
                    {model.status === 'training' && (
                      <div className="text-sm text-foreground/60 flex items-center gap-2 mt-4">
                        <div className="w-3 h-3 border-2 border-primary border-t-transparent rounded-full animate-spin"></div>
                        Training in progress...
                      </div>
                    )}
                    
                    {model.status === 'failed' && (
                      <p className="text-sm text-red-500 mt-4">Training failed. Please check your data and parameters.</p>
                    )}
                    
                    {model.status === 'ready' && model.metrics && (
                      <div className="mt-4 space-y-2">
                        <div className="text-xs text-foreground/50 uppercase font-semibold mb-1">Metrics</div>
                        <div className="grid grid-cols-2 gap-2">
                          {Object.entries(model.metrics).slice(0, 4).map(([key, value]: any) => (
                            <div key={key} className="bg-secondary/50 rounded p-2">
                              <div className="text-xs text-foreground/60 capitalize">{key.replace('_', ' ')}</div>
                              <div className="font-medium text-sm">
                                {typeof value === 'number' ? (value > 1 ? value.toFixed(2) : value.toFixed(4)) : String(value)}
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                  
                  <div className="mt-4 pt-4 border-t border-border flex justify-between items-center text-xs text-foreground/50">
                    <span>{new Date(model.created_at).toLocaleDateString()}</span>
                    {model.status === 'ready' && (
                      <button 
                        onClick={() => setSelectedModel(model)}
                        className="text-primary hover:underline font-medium"
                      >
                        View Details
                      </button>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
      )}

      {selectedModel && (
        <div className="fixed inset-0 bg-background/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-card border border-border rounded-xl shadow-xl w-full max-w-2xl max-h-[80vh] flex flex-col">
            <div className="p-6 border-b border-border flex items-center justify-between">
              <div>
                <h2 className="text-xl font-bold">{selectedModel.name}</h2>
                <p className="text-sm text-foreground/60 capitalize">{selectedModel.model_type} • {selectedModel.algorithm || 'Auto'}</p>
              </div>
              <button 
                onClick={() => setSelectedModel(null)}
                className="text-foreground/50 hover:text-foreground"
              >
                <XCircle className="w-6 h-6" />
              </button>
            </div>
            <div className="p-6 overflow-y-auto space-y-6">
              
              <div>
                <h3 className="text-sm font-semibold text-foreground/50 uppercase tracking-wider mb-3">Model Configuration</h3>
                <div className="grid grid-cols-2 gap-4 text-sm bg-secondary/20 p-4 rounded-lg border border-border/50">
                  {selectedModel.target_column && (
                    <div>
                      <span className="text-foreground/60 block mb-0.5">Target Column</span>
                      <span className="font-medium bg-secondary px-2 py-0.5 rounded text-xs">{selectedModel.target_column}</span>
                    </div>
                  )}
                  <div>
                    <span className="text-foreground/60 block mb-0.5">Features Used</span>
                    <span className="font-medium">{selectedModel.feature_columns ? `${selectedModel.feature_columns.length} selected` : 'All available'}</span>
                  </div>
                  <div>
                    <span className="text-foreground/60 block mb-0.5">Status</span>
                    <span className="font-medium capitalize flex items-center gap-1.5">
                      <div className="scale-75 origin-left -ml-1">{getStatusIcon(selectedModel.status)}</div>
                      {selectedModel.status}
                    </span>
                  </div>
                  <div>
                    <span className="text-foreground/60 block mb-0.5">Created At</span>
                    <span className="font-medium">{new Date(selectedModel.created_at).toLocaleString()}</span>
                  </div>
                </div>
              </div>

              <div>
                <h3 className="text-sm font-semibold text-foreground/50 uppercase tracking-wider mb-3">All Metrics</h3>
                <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
                  {Object.entries(selectedModel.metrics || {})
                    .filter(([k]) => k !== 'feature_importance' && k !== 'confusion_matrix' && k !== 'cluster_sizes')
                    .map(([key, value]: any) => (
                    <div key={key} className="bg-secondary/50 rounded-lg p-3">
                      <div className="text-xs text-foreground/60 capitalize mb-1">{key.replace('_', ' ')}</div>
                      <div className="font-semibold text-lg">
                        {typeof value === 'number' ? (value > 1 ? value.toFixed(2) : value.toFixed(4)) : String(value)}
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {selectedModel.metrics?.feature_importance && (
                <div>
                  <h3 className="text-sm font-semibold text-foreground/50 uppercase tracking-wider mb-3">Feature Importance</h3>
                  <div className="bg-secondary/30 rounded-lg border border-border overflow-hidden">
                    {Object.entries(selectedModel.metrics.feature_importance).slice(0, 10).map(([feature, importance]: any) => (
                      <div key={feature} className="flex items-center px-4 py-2 border-b border-border last:border-0">
                        <div className="w-1/3 text-sm truncate pr-4" title={feature}>{feature}</div>
                        <div className="w-2/3 flex items-center gap-3">
                          <div className="flex-1 bg-secondary rounded-full h-2">
                            <div className="bg-primary h-2 rounded-full" style={{ width: `${Math.max(0, Math.min(100, importance * 100))}%` }}></div>
                          </div>
                          <div className="text-xs text-foreground/60 w-12 text-right">{(importance * 100).toFixed(1)}%</div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {selectedModel.metrics?.cluster_sizes && (
                <div>
                  <h3 className="text-sm font-semibold text-foreground/50 uppercase tracking-wider mb-3">Cluster Sizes</h3>
                  <div className="flex flex-wrap gap-2">
                    {Object.entries(selectedModel.metrics.cluster_sizes).map(([cluster, size]: any) => (
                      <div key={cluster} className="bg-secondary/50 rounded-lg px-3 py-2 text-sm">
                        <span className="font-medium mr-2">Cluster {cluster}:</span>
                        <span className="text-foreground/70">{String(size)} items</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {selectedModel.metrics?.confusion_matrix && (
                <div>
                  <h3 className="text-sm font-semibold text-foreground/50 uppercase tracking-wider mb-3">Confusion Matrix</h3>
                  <div className="bg-secondary/30 rounded-lg border border-border p-4 overflow-x-auto">
                    <table className="min-w-full text-center text-sm">
                      <tbody>
                        {selectedModel.metrics.confusion_matrix.map((row: number[], i: number) => (
                          <tr key={i}>
                            {row.map((val: number, j: number) => (
                              <td key={j} className="p-2 border border-border/50">{val}</td>
                            ))}
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}
              
            </div>
          </div>
        </div>
      )}

    </div>
  );
}

