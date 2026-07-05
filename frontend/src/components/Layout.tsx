import { useEffect } from "react";
import { Sidebar } from './Sidebar';
import { Outlet } from 'react-router-dom';
import { useStore } from '../store/useStore';
import { fetchWithAuth, API_BASE_URL } from '../utils/apiClient';

export function Layout() {
  const user = useStore(state => state.user);
  const token = useStore(state => state.token);
  const setUser = useStore(state => state.setUser);

  useEffect(() => {
    if (token && !user) {
      fetchWithAuth(`${API_BASE_URL}/api/users/me`)
        .then(res => {
          if (res.ok) return res.json();
          throw new Error('Failed to fetch user');
        })
        .then(data => {
          console.log('Fetched user data:', data);
          setUser(data);
        })
        .catch(err => console.error('Layout user fetch error:', err));
    }
  }, [token, user, setUser]);

  const initial = user?.username ? user.username.charAt(0).toUpperCase() : '?';
  const displayName = user?.username || 'Loading...';

  return (
    <div className="flex h-screen overflow-hidden bg-background">
      <Sidebar />
      <div className="flex-1 flex flex-col h-full overflow-hidden">
        <header className="h-16 border-b border-border flex items-center justify-between px-6 bg-card/50 backdrop-blur-sm z-10">
          <div className="font-medium">
            {user ? `Welcome, ${user.username}` : 'Welcome to DataMind AI'}
          </div>
          <div className="flex items-center gap-3">
            <span className="text-sm font-medium text-foreground/70">{displayName}</span>
            <div className="w-9 h-9 rounded-full bg-gradient-to-br from-primary to-accent flex items-center justify-center text-white font-bold text-sm uppercase shadow-md shadow-primary/20">
              {initial}
            </div>
          </div>
        </header>
        <main className="flex-1 overflow-y-auto p-6 relative">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
