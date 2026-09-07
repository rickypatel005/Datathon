import { NavLink, useNavigate, useLocation } from 'react-router-dom';
import {
  FileText,
  Database,
  Settings,
  Plus,
  ChevronLeft,
  ChevronRight,
  GitFork,
  Lightbulb,
  Trophy,
  BarChart2,
  MessageSquare,
  LogOut,
  Moon,
  Sun,
  Layers
} from 'lucide-react';
import { useStore } from '../store/useStore';
import clsx from 'clsx';

export function Sidebar() {
  const {
    isSidebarOpen,
    toggleSidebar,
    logout,
    theme,
    setTheme,
  } = useStore();
  const navigate = useNavigate();
  const location = useLocation();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const isNewAnalysisActive = location.pathname === '/new-analysis';

  return (
    <div
      className={clsx(
        "h-screen bg-[#070d1e] border-r border-[#17233f] transition-all duration-300 flex flex-col relative z-50 select-none",
        isSidebarOpen ? "w-64" : "w-20"
      )}
    >
      {/* Brand Header */}
      <div className="h-16 px-4 flex items-center justify-between border-b border-[#17233f] bg-[#091124]">
        {isSidebarOpen ? (
          <div className="flex items-center gap-2.5 cursor-pointer" onClick={() => navigate('/')}>
            <div className="w-8 h-8 rounded-xl bg-gradient-to-tr from-[#3b82f6] to-[#6366f1] flex items-center justify-center text-white shadow-md shadow-indigo-500/25">
              <div className="w-2.5 h-2.5 rounded-full bg-white shadow-sm" />
            </div>
            <span className="font-black text-xl tracking-wider text-white">
              AIDA
            </span>
          </div>
        ) : (
          <div className="w-full flex justify-center cursor-pointer" onClick={() => navigate('/')}>
            <div className="w-8 h-8 rounded-xl bg-gradient-to-tr from-[#3b82f6] to-[#6366f1] flex items-center justify-center text-white shadow-md shadow-indigo-500/25">
              <div className="w-2.5 h-2.5 rounded-full bg-white shadow-sm" />
            </div>
          </div>
        )}
      </div>

      {/* Collapse/Expand Floating Button */}
      <button
        onClick={toggleSidebar}
        className="absolute -right-3 top-20 bg-[#121c33] border border-[#1e293b] rounded-full p-1 hover:bg-[#1e293b] transition-colors z-50 text-slate-300"
      >
        {isSidebarOpen ? <ChevronLeft className="w-3.5 h-3.5" /> : <ChevronRight className="w-3.5 h-3.5" />}
      </button>

      {/* Primary Top Action Button: "+ New Analysis" */}
      <div className="p-3">
        <button
          onClick={() => navigate('/new-analysis')}
          className={clsx(
            "w-full rounded-xl py-2.5 px-3 flex items-center justify-center gap-2 text-xs font-bold transition-all shadow-md",
            isNewAnalysisActive
              ? "bg-gradient-to-r from-[#6366f1] to-[#4f46e5] text-white shadow-indigo-500/30 ring-1 ring-indigo-400/50"
              : "bg-[#141d36] hover:bg-[#1b2749] text-indigo-300 border border-indigo-500/30 hover:text-white"
          )}
          title="New Analysis"
        >
          <Plus className="w-4 h-4 text-indigo-300 flex-shrink-0" />
          {isSidebarOpen && <span>New Analysis</span>}
        </button>
      </div>

      {/* Navigation Links */}
      <div className="flex-1 overflow-y-auto px-3 space-y-1">
        {/* Core items matching reference screens */}
        <NavLink
          to="/reports"
          className={({ isActive }) =>
            clsx(
              "flex items-center gap-3 px-3 py-2.5 rounded-xl transition-all text-xs font-semibold",
              isActive
                ? "bg-[#182344] text-white border border-indigo-500/30"
                : "text-slate-400 hover:bg-[#0f1830] hover:text-slate-200"
            )
          }
          title={!isSidebarOpen ? "Reports" : undefined}
        >
          <FileText className="w-4 h-4 flex-shrink-0 text-slate-400" />
          {isSidebarOpen && <span>Reports</span>}
        </NavLink>

        <NavLink
          to="/datasets"
          className={({ isActive }) =>
            clsx(
              "flex items-center gap-3 px-3 py-2.5 rounded-xl transition-all text-xs font-semibold",
              isActive
                ? "bg-[#182344] text-white border border-indigo-500/30"
                : "text-slate-400 hover:bg-[#0f1830] hover:text-slate-200"
            )
          }
          title={!isSidebarOpen ? "Datasets" : undefined}
        >
          <Database className="w-4 h-4 flex-shrink-0 text-slate-400" />
          {isSidebarOpen && <span>Datasets</span>}
        </NavLink>

        <div className="pt-2 pb-1 border-t border-[#17233f]/70 mt-2">
          {isSidebarOpen && (
            <span className="text-[10px] font-bold uppercase tracking-wider text-slate-500 px-3 block mb-1">
              Deep Analytics
            </span>
          )}

          <NavLink
            to="/"
            end
            className={({ isActive }) =>
              clsx(
                "flex items-center gap-3 px-3 py-2 rounded-xl transition-all text-xs font-medium",
                isActive
                  ? "bg-[#182344] text-white border border-indigo-500/30"
                  : "text-slate-400 hover:bg-[#0f1830] hover:text-slate-200"
              )
            }
            title={!isSidebarOpen ? "Overview" : undefined}
          >
            <Layers className="w-4 h-4 flex-shrink-0 text-slate-400" />
            {isSidebarOpen && <span>Overview Dashboard</span>}
          </NavLink>

          <NavLink
            to="/pipeline"
            className={({ isActive }) =>
              clsx(
                "flex items-center gap-3 px-3 py-2 rounded-xl transition-all text-xs font-medium",
                isActive
                  ? "bg-[#182344] text-white border border-indigo-500/30"
                  : "text-slate-400 hover:bg-[#0f1830] hover:text-slate-200"
              )
            }
            title={!isSidebarOpen ? "Investigation Pipeline" : undefined}
          >
            <GitFork className="w-4 h-4 flex-shrink-0 text-slate-400" />
            {isSidebarOpen && <span>Pipeline</span>}
          </NavLink>

          <NavLink
            to="/insights"
            className={({ isActive }) =>
              clsx(
                "flex items-center gap-3 px-3 py-2 rounded-xl transition-all text-xs font-medium",
                isActive
                  ? "bg-[#182344] text-white border border-indigo-500/30"
                  : "text-slate-400 hover:bg-[#0f1830] hover:text-slate-200"
              )
            }
            title={!isSidebarOpen ? "Insights Workspace" : undefined}
          >
            <Lightbulb className="w-4 h-4 flex-shrink-0 text-slate-400" />
            {isSidebarOpen && <span>Insights</span>}
          </NavLink>

          <NavLink
            to="/models"
            className={({ isActive }) =>
              clsx(
                "flex items-center gap-3 px-3 py-2 rounded-xl transition-all text-xs font-medium",
                isActive
                  ? "bg-[#182344] text-white border border-indigo-500/30"
                  : "text-slate-400 hover:bg-[#0f1830] hover:text-slate-200"
              )
            }
            title={!isSidebarOpen ? "Model Championship" : undefined}
          >
            <Trophy className="w-4 h-4 flex-shrink-0 text-slate-400" />
            {isSidebarOpen && <span>Model Arena</span>}
          </NavLink>

          <NavLink
            to="/visualizations"
            className={({ isActive }) =>
              clsx(
                "flex items-center gap-3 px-3 py-2 rounded-xl transition-all text-xs font-medium",
                isActive
                  ? "bg-[#182344] text-white border border-indigo-500/30"
                  : "text-slate-400 hover:bg-[#0f1830] hover:text-slate-200"
              )
            }
            title={!isSidebarOpen ? "Visualizations" : undefined}
          >
            <BarChart2 className="w-4 h-4 flex-shrink-0 text-slate-400" />
            {isSidebarOpen && <span>Visualizations</span>}
          </NavLink>

          <NavLink
            to="/chat"
            className={({ isActive }) =>
              clsx(
                "flex items-center gap-3 px-3 py-2 rounded-xl transition-all text-xs font-medium",
                isActive
                  ? "bg-[#182344] text-white border border-indigo-500/30"
                  : "text-slate-400 hover:bg-[#0f1830] hover:text-slate-200"
              )
            }
            title={!isSidebarOpen ? "AI Assistant" : undefined}
          >
            <MessageSquare className="w-4 h-4 flex-shrink-0 text-slate-400" />
            {isSidebarOpen && <span>AI Chat</span>}
          </NavLink>
        </div>
      </div>

      {/* Settings Link */}
      <div className="px-3 py-2 border-t border-[#17233f]/70">
        <NavLink
          to="/settings"
          className={({ isActive }) =>
            clsx(
              "flex items-center gap-3 px-3 py-2 rounded-xl transition-all text-xs font-medium",
              isActive
                ? "bg-[#182344] text-white"
                : "text-slate-400 hover:bg-[#0f1830] hover:text-slate-200"
            )
          }
          title={!isSidebarOpen ? "Settings" : undefined}
        >
          <Settings className="w-4 h-4 flex-shrink-0 text-slate-400" />
          {isSidebarOpen && <span>Settings</span>}
        </NavLink>
      </div>

      {/* Bottom Wave Graphic / Brand Statement Card */}
      {isSidebarOpen && (
        <div className="p-3">
          <div className="relative overflow-hidden rounded-2xl bg-gradient-to-b from-[#0e1933] to-[#0a1226] border border-[#1d2b4f] p-4 text-center shadow-inner">
            {/* Ambient subtle glowing waves */}
            <div className="absolute -bottom-6 -right-6 w-24 h-24 bg-indigo-600/10 rounded-full blur-xl pointer-events-none" />
            <div className="absolute -top-6 -left-6 w-24 h-24 bg-sky-600/10 rounded-full blur-xl pointer-events-none" />

            <p className="text-[11px] font-semibold text-slate-300 leading-snug tracking-tight">
              Turning Data into
            </p>
            <p className="text-[11px] font-bold text-transparent bg-clip-text bg-gradient-to-r from-indigo-400 via-sky-400 to-indigo-300 tracking-tight">
              Brighter Decisions
            </p>
          </div>
        </div>
      )}

      {/* Footer Controls: Theme & Logout */}
      <div className="p-3 border-t border-[#17233f] bg-[#091124] flex items-center justify-between">
        <div className="flex items-center gap-2">
          <button
            onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}
            className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-[#15203b] transition-colors"
            title="Toggle theme"
          >
            {theme === 'dark' ? <Sun className="w-3.5 h-3.5" /> : <Moon className="w-3.5 h-3.5" />}
          </button>
          <button
            onClick={handleLogout}
            className="p-1.5 rounded-lg text-slate-400 hover:text-red-400 hover:bg-red-500/10 transition-colors"
            title="Log out"
          >
            <LogOut className="w-3.5 h-3.5" />
          </button>
        </div>

        {isSidebarOpen && (
          <span className="text-[10px] font-mono text-slate-500">v2.4 AUTO</span>
        )}
      </div>
    </div>
  );
}
