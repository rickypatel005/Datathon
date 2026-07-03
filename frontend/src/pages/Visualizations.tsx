import { fetchWithAuth } from '../utils/apiClient';
import React, { useState, useEffect } from 'react';
import Plot from 'react-plotly.js';
import { useStore } from '../store/useStore';
import { BarChart2, Database, AlertCircle } from 'lucide-react';
import { Link } from 'react-router-dom';

export function Visualizations() {
  const activeDatasetId = useStore(state => state.activeDatasetId);
  const [columns, setColumns] = useState<string[]>([]);
  const [chartType, setChartType] = useState('scatter');
  const [xColumn, setXColumn] = useState('');
  const [yColumn, setYColumn] = useState('');
  const [colorColumn, setColorColumn] = useState('');
  
  const [chartData, setChartData] = useState<any>(null);
  const [insights, setInsights] = useState<string | null>(null);
  const [isGenerating, setIsGenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!activeDatasetId) return;
    
    // Fetch preview to get column names
    const fetchColumns = async () => {
      try {
        const res = await fetchWithAuth(`http://localhost:8000/api/datasets/${activeDatasetId}/preview`);
        if (!res.ok) throw new Error('Failed to fetch dataset info');
        const data = await res.json();
        setColumns(data.columns || []);
        if (data.columns && data.columns.length > 0) {
          setXColumn(data.columns[0]);
          if (data.columns.length > 1) {
            setYColumn(data.columns[1]);
          }
        }
      } catch (err: any) {
        setError("Could not load columns. Ensure dataset exists.");
      }
    };
    
    fetchColumns();
    setChartData(null);
    setInsights(null);
  }, [activeDatasetId]);

  const handleGenerate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!activeDatasetId) return;
    
    setIsGenerating(true);
    setError(null);
    setChartData(null);
    setInsights(null);

    try {
      const payload = {
        dataset_id: activeDatasetId,
        chart_type: chartType,
        x_column: xColumn || null,
        y_column: yColumn || null,
        color_column: colorColumn || null
      };

      const res = await fetchWithAuth('http://localhost:8000/api/visualize', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      
      if (!res.ok) {
        const errData = await res.json();
        throw new Error(errData.detail || 'Failed to generate visualization');
      }
      
      const data = await res.json();
      setChartData(data.chart_data);
      setInsights(data.insights);
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
            Please select an active dataset from the Datasets tab before generating visualizations.
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

  return (
    <div className="space-y-6 max-w-6xl mx-auto">
      <div>
        <h1 className="text-3xl font-bold tracking-tight flex items-center gap-3">
          <BarChart2 className="w-8 h-8 text-primary" />
          Visualizations
        </h1>
        <p className="text-foreground/60 mt-1">Generate dynamic charts and explore patterns in your data.</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        <div className="lg:col-span-1 bg-card border border-border rounded-xl p-5 h-fit">
          <h2 className="font-semibold mb-4 text-lg">Configure Chart</h2>
          <form onSubmit={handleGenerate} className="space-y-4">
            <div>
              <label className="block text-sm font-medium mb-1 text-foreground/80">Chart Type</label>
              <select 
                value={chartType} 
                onChange={e => setChartType(e.target.value)}
                className="w-full bg-secondary border border-border rounded-lg px-3 py-2 outline-none focus:ring-2 focus:ring-primary/50 text-sm text-foreground"
              >
                <option value="scatter">Scatter Plot</option>
                <option value="bar">Bar Chart</option>
                <option value="line">Line Chart</option>
                <option value="histogram">Histogram</option>
                <option value="countplot">Count Plot</option>
                <option value="boxplot">Box Plot</option>
                <option value="pie">Pie Chart</option>
                <option value="heatmap">Correlation Heatmap</option>
              </select>
            </div>

            {chartType !== 'heatmap' && (
              <>
                <div>
                  <label className="block text-sm font-medium mb-1 text-foreground/80">X-Axis Column</label>
                  <select 
                    value={xColumn} 
                    onChange={e => setXColumn(e.target.value)}
                    className="w-full bg-secondary border border-border rounded-lg px-3 py-2 outline-none focus:ring-2 focus:ring-primary/50 text-sm text-foreground"
                  >
                    <option value="">-- Select Column --</option>
                    {columns.map(col => (
                      <option key={col} value={col}>{col}</option>
                    ))}
                  </select>
                </div>

                {!['histogram', 'pie', 'countplot'].includes(chartType) && (
                  <div>
                    <label className="block text-sm font-medium mb-1 text-foreground/80">Y-Axis Column</label>
                    <select 
                      value={yColumn} 
                      onChange={e => setYColumn(e.target.value)}
                      className="w-full bg-secondary border border-border rounded-lg px-3 py-2 outline-none focus:ring-2 focus:ring-primary/50 text-sm text-foreground"
                    >
                      <option value="">-- Select Column --</option>
                      {columns.map(col => (
                        <option key={col} value={col}>{col}</option>
                      ))}
                    </select>
                  </div>
                )}

                {['scatter'].includes(chartType) && (
                  <div>
                    <label className="block text-sm font-medium mb-1 text-foreground/80">Color Grouping (Optional)</label>
                    <select 
                      value={colorColumn} 
                      onChange={e => setColorColumn(e.target.value)}
                      className="w-full bg-secondary border border-border rounded-lg px-3 py-2 outline-none focus:ring-2 focus:ring-primary/50 text-sm text-foreground"
                    >
                      <option value="">-- None --</option>
                      {columns.map(col => (
                        <option key={col} value={col}>{col}</option>
                      ))}
                    </select>
                  </div>
                )}
              </>
            )}

            <button 
              type="submit" 
              disabled={isGenerating || columns.length === 0}
              className="w-full bg-primary hover:bg-primary/90 text-primary-foreground py-2.5 rounded-lg font-medium transition-colors disabled:opacity-50 mt-2"
            >
              {isGenerating ? 'Generating...' : 'Generate Chart'}
            </button>
          </form>
        </div>

        <div className="lg:col-span-3 bg-card border border-border rounded-xl min-h-[500px] flex flex-col p-4">
          {error && (
            <div className="bg-red-500/10 border border-red-500/20 text-red-500 p-4 rounded-xl mb-4 flex items-start gap-3">
              <AlertCircle className="w-5 h-5 flex-shrink-0 mt-0.5" />
              <p className="text-sm">{error}</p>
            </div>
          )}

          {!chartData && !isGenerating && !error && (
            <div className="flex-1 flex flex-col items-center justify-center text-foreground/40 text-center">
              <BarChart2 className="w-16 h-16 mb-4 opacity-50" />
              <p className="text-lg">Configure your chart on the left and click Generate.</p>
            </div>
          )}

          {isGenerating && (
            <div className="flex-1 flex flex-col items-center justify-center">
              <div className="w-10 h-10 border-4 border-primary border-t-transparent rounded-full animate-spin mb-4"></div>
              <p className="text-foreground/60 animate-pulse">Generating your visualization...</p>
            </div>
          )}

          {chartData && !isGenerating && (
            <div className="flex-1 w-full h-full flex flex-col">
              <div className="flex-1 min-h-[400px] relative w-full rounded-lg overflow-hidden border border-border/50">
                <Plot
                  data={chartData.data || []}
                  layout={{
                    ...chartData.layout,
                    autosize: true,
                    paper_bgcolor: 'rgba(0,0,0,0)',
                    plot_bgcolor: 'rgba(0,0,0,0)',
                    font: { color: 'inherit' },
                    margin: { t: 50, r: 20, l: 50, b: 50 }
                  }}
                  useResizeHandler={true}
                  style={{ width: '100%', height: '100%' }}
                  config={{ responsive: true, displayModeBar: true }}
                />
              </div>
              
              {insights && (
                <div className="mt-6 bg-secondary/30 rounded-xl p-4 border border-border/50">
                  <h3 className="font-semibold flex items-center gap-2 mb-2">
                    <span className="w-2 h-2 rounded-full bg-primary"></span>
                    Key Insights
                  </h3>
                  <p className="text-foreground/80 text-sm leading-relaxed">
                    {insights}
                  </p>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

