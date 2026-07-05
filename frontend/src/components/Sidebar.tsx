import { NavLink, useNavigate } from 'react-router-dom';
import datamindLogo from '../assets/datamind-logo.png';
import {
  LayoutDashboard,
  Database,
  MessageSquare,
  BarChart2,
  BrainCircuit,
  FileText,
  Settings,
  LogOut,
  ChevronLeft,
  ChevronRight
} from 'lucide-react';
import { useStore } from '../store/useStore';
import clsx from 'clsx';

const navItems = [
  { icon: LayoutDashboard, label: 'Dashboard', path: '/' },
  { icon: Database, label: 'Datasets', path: '/datasets' },
  { icon: MessageSquare, label: 'AI Chat', path: '/chat' },
  { icon: BarChart2, label: 'Visualizations', path: '/visualizations' },
  { icon: BrainCircuit, label: 'ML Models', path: '/models' },
  { icon: FileText, label: 'Reports', path: '/reports' },
];

export function Sidebar() {
  const { isSidebarOpen, toggleSidebar, logout } = useStore();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <div className={clsx(
      "h-screen bg-card border-r border-border transition-all duration-300 flex flex-col relative",
      isSidebarOpen ? "w-64" : "w-20"
    )}>
      <div className="p-4 flex items-center justify-between border-b border-border h-16">
        {isSidebarOpen && (
          <div className="flex items-center gap-2.5">
            <img src={datamindLogo} alt="DataMind AI" className="w-8 h-8 object-contain rounded-md" />
            <span className="font-bold text-lg tracking-tight bg-gradient-to-r from-[#1DB875] to-[#0EA5E9] bg-clip-text text-transparent">DataMind AI</span>
          </div>
        )}
        {!isSidebarOpen && (
          <div className="w-full flex justify-center">
            <img src={datamindLogo} alt="DataMind AI" className="w-8 h-8 object-contain rounded-md" />
          </div>
        )}
      </div>

      <button
        onClick={toggleSidebar}
        className="absolute -right-3 top-20 bg-card border border-border rounded-full p-1 hover:bg-primary/20 transition-colors z-10"
      >
        {isSidebarOpen ? <ChevronLeft className="w-4 h-4" /> : <ChevronRight className="w-4 h-4" />}
      </button>

      <div className="flex-1 overflow-y-auto py-4 px-3 flex flex-col gap-2">
        {navItems.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            className={({ isActive }) => clsx(
              "flex items-center gap-3 px-3 py-2.5 rounded-lg transition-colors",
              isActive
                ? "bg-primary/10 text-primary font-medium"
                : "text-foreground/70 hover:bg-foreground/5 hover:text-foreground"
            )}
            title={!isSidebarOpen ? item.label : undefined}
          >
            <item.icon className="w-5 h-5 flex-shrink-0" />
            {isSidebarOpen && <span>{item.label}</span>}
          </NavLink>
        ))}
      </div>

      <div className="p-4 border-t border-border flex flex-col gap-2">
        <NavLink
          to="/settings"
          className={({ isActive }) => clsx(
            "flex items-center gap-3 px-3 py-2.5 rounded-lg transition-colors",
            isActive
              ? "bg-primary/10 text-primary font-medium"
              : "text-foreground/70 hover:bg-foreground/5 hover:text-foreground"
          )}
          title={!isSidebarOpen ? "Settings" : undefined}
        >
          <Settings className="w-5 h-5 flex-shrink-0" />
          {isSidebarOpen && <span>Settings</span>}
        </NavLink>
        
        <button
          onClick={handleLogout}
          className="flex items-center gap-3 px-3 py-2.5 rounded-lg transition-colors text-red-500 hover:bg-red-500/10 w-full text-left"
          title={!isSidebarOpen ? "Log out" : undefined}
        >
          <LogOut className="w-5 h-5 flex-shrink-0" />
          {isSidebarOpen && <span>Log out</span>}
        </button>
      </div>
    </div>
  );
}
