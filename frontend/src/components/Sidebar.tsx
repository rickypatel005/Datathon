import { NavLink, useNavigate } from 'react-router-dom';
import {
  LayoutDashboard,
  Database,
  GitFork,
  Lightbulb,
  Trophy,
  BarChart2,
  FileText,
  MessageSquare,
  LogOut,
  ChevronLeft,
  ChevronRight,
  FileSpreadsheet,
  Moon,
  Sun
} from 'lucide-react';
import { useStore } from '../store/useStore';
import clsx from 'clsx';

const navItems = [
  { icon: LayoutDashboard, label: 'Overview', path: '/', badge: null },
  { icon: Database, label: 'Datasets', path: '/datasets', badge: '2' },
  { icon: GitFork, label: 'Investigation Pipeline', path: '/pipeline', badge: '6/6' },
  { icon: Lightbulb, label: 'Insights Workspace', path: '/insights', badge: '3 Validated' },
  { icon: Trophy, label: 'Model Championship', path: '/models', badge: 'LGBM' },
  { icon: BarChart2, label: 'Visualizations', path: '/visualizations', badge: 'Auto' },
  { icon: FileText, label: 'Executive Report', path: '/reports', badge: 'Ready' },
  { icon: MessageSquare, label: 'AI Assistant', path: '/chat', badge: 'Live' },
];

export function Sidebar() {
  const {
    isSidebarOpen,
    toggleSidebar,
    logout,
    theme,
    setTheme,
    dashboardContract,
    activeScenario,
    setActiveScenario,
    setDemoMode
  } = useStore();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const datasetName = dashboardContract?.dataset_name || (activeScenario === 'sales' ? 'retail_daily_sales.csv' : 'customer_churn.csv');

  return (
    <div
      className={clsx(
        "h-screen bg-surface-container-lowest border-r border-border transition-all duration-300 flex flex-col relative z-50 select-none",
        isSidebarOpen ? "w-72" : "w-20"
      )}
    >
      {/* Brand Header */}
      <div className="h-16 px-4 flex items-center justify-between border-b border-border/80 bg-surface-container-low/60">
        {isSidebarOpen ? (
          <div className="flex items-center justify-between w-full">
            <div className="flex items-center gap-2.5">
              <div className="w-8 h-8 rounded-lg bg-gradient-to-tr from-primary to-secondary flex items-center justify-center text-primary-foreground font-black text-sm shadow-md shadow-primary/20">
                AI
              </div>
              <div className="flex items-baseline gap-1.5">
                <span className="font-bold text-lg tracking-tight text-on-surface">
                  AIDA
                </span>
                <span className="text-[10px] font-mono uppercase px-1.5 py-0.2 rounded bg-surface-container-high text-secondary font-semibold">
                  v2.4 AUTO
                </span>
              </div>
            </div>
          </div>
        ) : (
          <div className="w-full flex justify-center">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-tr from-primary to-secondary flex items-center justify-center text-primary-foreground font-black text-sm">
              AI
            </div>
          </div>
        )}
      </div>

      {/* Collapse/Expand Floating Button */}
      <button
        onClick={toggleSidebar}
        className="absolute -right-3 top-20 bg-surface-container-high border border-border rounded-full p-1 hover:bg-primary/20 transition-colors z-50 text-on-surface"
      >
        {isSidebarOpen ? <ChevronLeft className="w-3.5 h-3.5" /> : <ChevronRight className="w-3.5 h-3.5" />}
      </button>

      {/* Active Dataset Inspection Card */}
      {isSidebarOpen && (
        <div className="p-3">
          <div className="p-3 rounded-xl bg-surface-container-low border border-border/70 space-y-2">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-1.5 min-w-0">
                <FileSpreadsheet className="w-4 h-4 text-secondary flex-shrink-0" />
                <span className="font-mono text-xs text-on-surface font-semibold truncate">
                  {datasetName}
                </span>
              </div>
              <span className="w-2 h-2 rounded-full bg-secondary animate-ping shrink-0" />
            </div>

            <div className="font-mono text-[10px] text-on-surface-variant flex items-center gap-1">
              <span>{activeScenario === 'sales' ? '730 rows · 12 cols' : '7,043 rows · 21 cols'}</span>
              <span>&bull;</span>
              <span className="text-emerald-400 font-medium">Q94.2/100</span>
            </div>

            <div className="flex items-center justify-between pt-1">
              <span className="px-1.5 py-0.5 rounded bg-surface-container text-tertiary font-mono text-[9px] font-semibold uppercase">
                {activeScenario === 'sales' ? 'Time Series' : 'Classification'}
              </span>
              <button
                onClick={() => {
                  setDemoMode(true);
                  setActiveScenario(activeScenario === 'churn' ? 'sales' : 'churn');
                }}
                className="text-[10px] text-on-surface-variant hover:text-secondary flex items-center gap-1 transition-colors"
              >
                <span>Switch Scenario</span>
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Navigation Links */}
      <div className="flex-1 overflow-y-auto py-2 px-2.5 space-y-1">
        {navItems.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            className={({ isActive }) =>
              clsx(
                "flex items-center justify-between px-3 py-2 rounded-xl transition-all text-xs font-medium",
                isActive
                  ? "bg-primary text-white shadow-sm shadow-primary/20 font-semibold"
                  : "text-on-surface-variant hover:bg-surface-container hover:text-on-surface"
              )
            }
            title={!isSidebarOpen ? item.label : undefined}
          >
            <div className="flex items-center gap-2.5 min-w-0">
              <item.icon className="w-4 h-4 flex-shrink-0" />
              {isSidebarOpen && <span className="truncate">{item.label}</span>}
            </div>
            {isSidebarOpen && item.badge && (
              <span className="text-[10px] font-mono px-1.5 py-0.5 rounded-full bg-surface-container-high/80 text-secondary font-semibold">
                {item.badge}
              </span>
            )}
          </NavLink>
        ))}
      </div>

      {/* Telemetry & User Footer */}
      <div className="p-3 border-t border-border/80 bg-surface-container-low/40 space-y-2">
        {isSidebarOpen && (
          <div className="p-2 rounded-lg bg-surface-container-lowest font-mono text-[10px] text-on-surface-variant flex items-center justify-between">
            <span className="flex items-center gap-1">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-500" />
              Engine: Ready
            </span>
            <span>RAM: 1.4 GB</span>
          </div>
        )}

        <div className="flex items-center justify-between gap-2 pt-1">
          <div className="flex items-center gap-2 min-w-0">
            <div className="w-7 h-7 rounded-full bg-primary flex items-center justify-center font-bold text-xs text-white shrink-0 shadow-sm">
              SC
            </div>
            {isSidebarOpen && (
              <div className="min-w-0">
                <p className="text-xs font-semibold text-on-surface truncate">Dr. Sarah Chen</p>
                <p className="font-mono text-[10px] text-on-surface-variant truncate">Lead Analyst</p>
              </div>
            )}
          </div>

          <div className="flex items-center gap-1">
            <button
              onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}
              className="p-1.5 rounded-lg text-on-surface-variant hover:text-on-surface hover:bg-surface-container transition-colors"
              title="Toggle Theme"
            >
              {theme === 'dark' ? <Sun className="w-3.5 h-3.5" /> : <Moon className="w-3.5 h-3.5" />}
            </button>
            <button
              onClick={handleLogout}
              className="p-1.5 rounded-lg text-red-400 hover:text-red-300 hover:bg-red-500/10 transition-colors"
              title="Log out"
            >
              <LogOut className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
