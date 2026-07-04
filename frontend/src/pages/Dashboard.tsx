import { fetchWithAuth } from '../utils/apiClient';
import React, { useEffect, useState } from 'react';
import { UploadCloud, FileText, Activity, BrainCircuit, MessageSquare, Clock, CheckCircle2, XCircle } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

interface DashboardStats {
  total_datasets: number;
  analyses_run: number;
  models_trained: number;
  storage_used: string;
}

interface RecentActivity {
  id: string;
  activity_type: string;
  description: string;
  status: string;
  created_at: string;
}

export function Dashboard() {
  const navigate = useNavigate();
  const [stats, setStats] = useState<DashboardStats>({
    total_datasets: 0,
    analyses_run: 0,
    models_trained: 0,
    storage_used: '0 B'
  });
  const [activities, setActivities] = useState<RecentActivity[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        const [statsRes, activityRes] = await Promise.all([
          fetchWithAuth('http://127.0.0.1:8000/api/dashboard/stats'),
          fetchWithAuth('http://127.0.0.1:8000/api/dashboard/recent-activity')
        ]);
        
        if (statsRes.ok) {
          const statsData = await statsRes.json();
          setStats(statsData);
        }
        
        if (activityRes.ok) {
          const activityData = await activityRes.json();
          setActivities(activityData);
        }
      } catch (err) {
        console.error("Failed to fetch dashboard data", err);
      } finally {
        setIsLoading(false);
      }
    };
    fetchDashboardData();
  }, []);

  const getActivityIcon = (type: string) => {
    switch (type) {
      case 'dataset': return <FileText className="w-5 h-5 text-blue-500" />;
      case 'analysis': return <Activity className="w-5 h-5 text-green-500" />;
      case 'model': return <BrainCircuit className="w-5 h-5 text-purple-500" />;
      default: return <Activity className="w-5 h-5" />;
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'ready':
      case 'completed': return <CheckCircle2 className="w-4 h-4 text-green-500" />;
      case 'running':
      case 'training': return <div className="w-4 h-4 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" />;
      case 'failed':
      case 'error': return <XCircle className="w-4 h-4 text-red-500" />;
      default: return <Clock className="w-4 h-4 text-foreground/40" />;
    }
  };

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Dashboard</h1>
        <p className="text-foreground/60 mt-1">Overview of your data analysis workspace.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {[
          { title: 'Total Datasets', value: isLoading ? '...' : stats.total_datasets, icon: FileText, color: 'text-blue-400', bg: 'bg-blue-400/10' },
          { title: 'Analyses Run', value: isLoading ? '...' : stats.analyses_run, icon: Activity, color: 'text-green-400', bg: 'bg-green-400/10' },
          { title: 'Models Trained', value: isLoading ? '...' : stats.models_trained, icon: BrainCircuit, color: 'text-purple-400', bg: 'bg-purple-400/10' },
          { title: 'Storage Used', value: isLoading ? '...' : stats.storage_used, icon: UploadCloud, color: 'text-orange-400', bg: 'bg-orange-400/10' },
        ].map((stat, i) => (
          <div key={i} className="bg-card border border-border p-5 rounded-xl flex items-center gap-4 transition-all hover:shadow-md">
            <div className={`p-3 rounded-lg ${stat.bg} ${stat.color}`}>
              <stat.icon className="w-6 h-6" />
            </div>
            <div>
              <p className="text-sm text-foreground/60 font-medium">{stat.title}</p>
              <h3 className="text-2xl font-bold mt-0.5">{stat.value}</h3>
            </div>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 bg-card border border-border rounded-xl p-6 flex flex-col h-[400px]">
          <h2 className="text-xl font-semibold mb-4">Recent Activity</h2>
          
          {isLoading ? (
            <div className="flex-1 flex items-center justify-center">
              <div className="w-8 h-8 border-4 border-primary border-t-transparent rounded-full animate-spin"></div>
            </div>
          ) : activities.length === 0 ? (
            <div className="flex-1 flex flex-col items-center justify-center text-foreground/40 text-center">
              <Activity className="w-12 h-12 mb-3 opacity-20" />
              <p>No recent activity. Upload a dataset to get started.</p>
            </div>
          ) : (
            <div className="flex-1 overflow-y-auto space-y-3 pr-2">
              {activities.map((activity) => (
                <div key={activity.id} className="flex items-start gap-4 p-3 rounded-lg hover:bg-secondary/50 transition-colors border border-transparent hover:border-border">
                  <div className="mt-1">
                    {getActivityIcon(activity.activity_type)}
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="font-medium text-sm truncate">{activity.description}</p>
                    <div className="flex items-center gap-2 mt-1">
                      {getStatusIcon(activity.status)}
                      <span className="text-xs text-foreground/50 capitalize">{activity.status}</span>
                      <span className="text-xs text-foreground/30">•</span>
                      <span className="text-xs text-foreground/50">{new Date(activity.created_at).toLocaleString()}</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
        <div className="bg-card border border-border rounded-xl p-6">
          <h2 className="text-xl font-semibold mb-4">Quick Actions</h2>
          <div className="space-y-3">
            <button onClick={() => navigate('/datasets')} className="w-full bg-primary hover:bg-primary/90 text-primary-foreground py-2.5 rounded-lg font-medium transition-colors flex items-center justify-center gap-2">
              <UploadCloud className="w-5 h-5" />
              Upload Dataset
            </button>
            <button onClick={() => navigate('/chat')} className="w-full bg-secondary hover:bg-secondary/80 text-foreground py-2.5 rounded-lg border border-border transition-colors flex items-center justify-center gap-2">
              <MessageSquare className="w-5 h-5" />
              Ask AI Assistant
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

