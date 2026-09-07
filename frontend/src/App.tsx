import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { Layout } from './components/Layout';
import { Dashboard } from './pages/Dashboard';
import { Chat } from './pages/Chat';
import { Datasets } from './pages/Datasets';
import { Visualizations } from './pages/Visualizations';
import { Models } from './pages/Models';
import { Reports } from './pages/Reports';
import { Settings } from './pages/Settings';
import { Pipeline } from './pages/Pipeline';
import { Insights } from './pages/Insights';
import { Login } from './pages/Login';
import { Register } from './pages/Register';
import { NewAnalysis } from './pages/NewAnalysis';
import { useStore } from './store/useStore';
import { Navigate } from 'react-router-dom';

const ProtectedRoute = ({ children }: { children: React.ReactNode }) => {
  const token = useStore(state => state.token);
  if (!token) {
    return <Navigate to="/login" replace />;
  }
  return <>{children}</>;
};

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        
        <Route path="/" element={
          <ProtectedRoute>
            <Layout />
          </ProtectedRoute>
        }>
          <Route index element={<Dashboard />} />
          <Route path="new-analysis" element={<NewAnalysis />} />
          <Route path="pipeline" element={<Pipeline />} />
          <Route path="insights" element={<Insights />} />
          <Route path="chat" element={<Chat />} />
          <Route path="datasets" element={<Datasets />} />
          <Route path="visualizations" element={<Visualizations />} />
          <Route path="models" element={<Models />} />
          <Route path="reports" element={<Reports />} />
          <Route path="settings" element={<Settings />} />
          <Route path="*" element={<div className="p-4 text-center text-foreground/50 mt-10">404 - Page not found</div>} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;
