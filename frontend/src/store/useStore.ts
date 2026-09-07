import { create } from 'zustand';
import type { DashboardContract, PipelineProgress } from '../types/contracts';

interface User {
  id: string;
  email: string;
  username: string;
  role: string;
}

interface Dataset {
  id: string;
  name: string;
  status: string;
}

interface AppState {
  user: User | null;
  token: string | null;
  datasets: Dataset[];
  activeDatasetId: string | null;
  setUser: (user: User | null) => void;
  setAuth: (user: User | null, token: string | null) => void;
  logout: () => void;
  setDatasets: (datasets: Dataset[]) => void;
  setActiveDatasetId: (id: string | null) => void;
  isSidebarOpen: boolean;
  toggleSidebar: () => void;
  theme: 'light' | 'dark' | 'system';
  setTheme: (theme: 'light' | 'dark' | 'system') => void;

  // AIDA Autonomous Pipeline & Contract State
  isDemoMode: boolean;
  setDemoMode: (isDemo: boolean) => void;
  activeScenario: 'churn' | 'sales';
  setActiveScenario: (scenario: 'churn' | 'sales') => void;
  dashboardContract: DashboardContract | null;
  setDashboardContract: (contract: DashboardContract | null) => void;
  pipelineProgress: PipelineProgress | null;
  setPipelineProgress: (progress: PipelineProgress | null) => void;
}

// Helper to apply theme to document
const applyTheme = (theme: 'light' | 'dark' | 'system') => {
  const root = window.document.documentElement;
  root.classList.remove('light', 'dark');
  
  if (theme === 'system') {
    const systemTheme = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
    root.classList.add(systemTheme);
  } else {
    root.classList.add(theme);
  }
};

// Initialize theme from localStorage or system preference
const savedTheme = (localStorage.getItem('app-theme') as 'light' | 'dark' | 'system') || 'system';
applyTheme(savedTheme);

export const useStore = create<AppState>((set) => ({
  user: null,
  token: localStorage.getItem('datamind-token'),
  datasets: [],
  activeDatasetId: null,
  setUser: (user) => set({ user }),
  setAuth: (user, token) => {
    if (token) {
      localStorage.setItem('datamind-token', token);
    } else {
      localStorage.removeItem('datamind-token');
    }
    set({ user, token });
  },
  logout: () => {
    localStorage.removeItem('datamind-token');
    set({ user: null, token: null, datasets: [], activeDatasetId: null });
  },
  setDatasets: (datasets) => set({ datasets }),
  setActiveDatasetId: (id) => set({ activeDatasetId: id }),
  isSidebarOpen: true,
  toggleSidebar: () => set((state) => ({ isSidebarOpen: !state.isSidebarOpen })),
  theme: savedTheme,
  setTheme: (theme) => {
    localStorage.setItem('app-theme', theme);
    applyTheme(theme);
    set({ theme });
  },

  // AIDA Defaults
  isDemoMode: false,
  setDemoMode: (isDemoMode) => set({ isDemoMode }),
  activeScenario: 'churn',
  setActiveScenario: (activeScenario) => set({ activeScenario }),
  dashboardContract: null,
  setDashboardContract: (dashboardContract) => set({ dashboardContract }),
  pipelineProgress: null,
  setPipelineProgress: (pipelineProgress) => set({ pipelineProgress }),
}));

