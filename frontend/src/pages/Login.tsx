import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Mail, Lock, ArrowRight, AlertCircle, Sparkles } from 'lucide-react';
import { useStore } from '../store/useStore';
import { API_BASE_URL } from '../utils/apiClient';

export function Login() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  
  const setAuth = useStore(state => state.setAuth);
  const navigate = useNavigate();

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError(null);

    try {
      const res = await fetch(`${API_BASE_URL}/api/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password }),
      });

      if (!res.ok) {
        const errData = await res.json();
        throw new Error(errData.detail || 'Failed to login');
      }

      const data = await res.json();
      setAuth(data.user, data.access_token);
      navigate('/');
    } catch (err: any) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  const handleDemoAccess = async () => {
    try {
      const res = await fetch(`${API_BASE_URL}/api/demo-login`, {
        method: 'POST'
      });
      if (res.ok) {
        const data = await res.json();
        setAuth(data.user, data.access_token);
        navigate('/');
        return;
      }
    } catch (e) {
      console.warn('Backend demo-login fetch failed, using fallback token', e);
    }

    // Fallback demo session with recognized demo-token
    setAuth(
      {
        id: 'usr-demo-01',
        email: 'dr.chen@aida.ai',
        username: 'Dr. Sarah Chen',
        role: 'Lead Data Scientist'
      },
      'demo-token-aida-jwt-999'
    );
    navigate('/');
  };

  return (
    <div className="min-h-screen bg-[#0b1326] text-[#dae2fd] flex flex-col items-center justify-center relative overflow-hidden px-4">
      {/* Subtle telemetry background glows */}
      <div className="absolute top-[-15%] left-[-10%] w-[500px] h-[500px] bg-[#6366f1]/10 blur-[130px] rounded-full pointer-events-none" />
      <div className="absolute bottom-[-15%] right-[-10%] w-[500px] h-[500px] bg-[#7bd0ff]/10 blur-[130px] rounded-full pointer-events-none" />

      <div className="w-full max-w-md z-10">
        {/* Brand Header */}
        <div className="text-center mb-6">
          <div className="inline-flex items-center gap-2 mb-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-primary to-secondary flex items-center justify-center text-white font-black text-lg shadow-lg shadow-primary/30">
              AI
            </div>
            <span className="font-bold text-2xl tracking-tight text-on-surface">
              AIDA
            </span>
          </div>

          <div className="flex items-center justify-center gap-2 mb-1">
            <span className="px-2 py-0.5 rounded-full bg-surface-container-high text-secondary font-mono text-[10px] font-semibold uppercase tracking-wider">
              Precision Scientific Observability
            </span>
          </div>
          <h1 className="text-xl font-bold tracking-tight text-on-surface mt-2">
            Autonomous Data Investigation
          </h1>
          <p className="text-xs text-on-surface-variant mt-1">
            Enterprise authentication & session token verification
          </p>
        </div>

        {/* Card Box */}
        <div className="bg-[#131b2e] border border-[#222a3d] rounded-2xl p-6 sm:p-8 shadow-2xl space-y-5">
          {error && (
            <div className="bg-red-500/10 border border-red-500/20 text-red-400 p-3 rounded-xl text-xs flex items-start gap-2">
              <AlertCircle className="w-4 h-4 flex-shrink-0 mt-0.5" />
              <p>{error}</p>
            </div>
          )}

          <form onSubmit={handleLogin} className="space-y-4">
            <div>
              <label className="block text-xs font-semibold text-on-surface-variant mb-1.5 uppercase tracking-wider font-mono">
                Corporate Identity (Email)
              </label>
              <div className="relative">
                <Mail className="w-4 h-4 absolute left-3 top-3 text-on-surface-variant/60" />
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="analyst@enterprise.com"
                  className="w-full bg-[#171f33] border border-[#2d3449] rounded-xl pl-9 pr-3 py-2 text-xs text-on-surface placeholder:text-on-surface-variant/40 outline-none focus:border-primary transition-colors"
                  required
                />
              </div>
            </div>

            <div>
              <div className="flex items-center justify-between mb-1.5">
                <label className="block text-xs font-semibold text-on-surface-variant uppercase tracking-wider font-mono">
                  Access Key (Password)
                </label>
              </div>
              <div className="relative">
                <Lock className="w-4 h-4 absolute left-3 top-3 text-on-surface-variant/60" />
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••••••"
                  className="w-full bg-[#171f33] border border-[#2d3449] rounded-xl pl-9 pr-3 py-2 text-xs text-on-surface placeholder:text-on-surface-variant/40 outline-none focus:border-primary transition-colors"
                  required
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={isLoading}
              className="w-full bg-primary hover:bg-primary/90 text-white font-semibold py-2.5 rounded-xl text-xs shadow-lg shadow-primary/20 transition-all flex items-center justify-center gap-2 disabled:opacity-50"
            >
              {isLoading ? (
                <span>Verifying credentials...</span>
              ) : (
                <>
                  <span>Sign In to Console</span>
                  <ArrowRight className="w-3.5 h-3.5" />
                </>
              )}
            </button>
          </form>

          {/* Quick Demo Access Button */}
          <div className="pt-2 border-t border-[#222a3d]">
            <button
              onClick={handleDemoAccess}
              type="button"
              className="w-full bg-[#171f33] hover:bg-[#222a3d] border border-primary/30 text-secondary font-semibold py-2.5 rounded-xl text-xs transition-colors flex items-center justify-center gap-2 shadow-sm"
            >
              <Sparkles className="w-3.5 h-3.5 text-secondary" />
              <span>Instant Guest Analyst Access</span>
            </button>
            <p className="text-[10px] text-center text-on-surface-variant/60 mt-2 font-mono">
              Bypasses login for live Datathon demonstration
            </p>
          </div>
        </div>

        {/* Footer */}
        <div className="text-center mt-6 text-xs text-on-surface-variant/60">
          <span>Don't have an account? </span>
          <Link to="/register" className="text-primary hover:underline font-semibold">
            Request Analyst Provisioning
          </Link>
        </div>
      </div>
    </div>
  );
}
