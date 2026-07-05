import { API_BASE_URL } from '../utils/apiClient';
import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { BrainCircuit, Mail, Lock, User, ArrowRight, AlertCircle } from 'lucide-react';
import { useStore } from '../store/useStore';

export function Register() {
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  
  const setAuth = useStore(state => state.setAuth);
  const navigate = useNavigate();

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    if (password !== confirmPassword) {
      setError("Passwords do not match");
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const res = await fetch(`${API_BASE_URL}/api/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, email, password }),
      });

      if (!res.ok) {
        const errData = await res.json();
        throw new Error(errData.detail || 'Failed to register');
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

  return (
    <div className="min-h-screen bg-background flex flex-col items-center justify-center relative overflow-hidden">
      {/* Background decorations */}
      <div className="absolute top-[-20%] right-[-10%] w-[50%] h-[50%] bg-blue-500/20 blur-[120px] rounded-full pointer-events-none"></div>
      <div className="absolute bottom-[-20%] left-[-10%] w-[50%] h-[50%] bg-primary/20 blur-[120px] rounded-full pointer-events-none"></div>

      <div className="w-full max-w-md z-10 px-6 py-12">
        <div className="text-center mb-8">
          <div className="flex items-center justify-center gap-2 mb-4">
            <div className="bg-primary/10 p-3 rounded-2xl">
              <BrainCircuit className="w-8 h-8 text-primary" />
            </div>
            <span className="text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-[#1DB875] to-[#0EA5E9]">
              DataMind AI
            </span>
          </div>
          <h1 className="text-2xl font-semibold tracking-tight text-foreground">Create an account</h1>
          <p className="text-foreground/60 mt-2 text-sm">Join DataMind AI to analyze your data like a pro</p>
        </div>

        <div className="bg-card/40 backdrop-blur-xl border border-border/50 shadow-2xl rounded-3xl p-8 transition-all hover:border-primary/30">
          <form onSubmit={handleRegister} className="space-y-5">
            {error && (
              <div className="bg-red-500/10 border border-red-500/20 text-red-500 p-3 rounded-xl text-sm flex items-start gap-2 animate-in fade-in slide-in-from-top-2">
                <AlertCircle className="w-4 h-4 flex-shrink-0 mt-0.5" />
                <p>{error}</p>
              </div>
            )}

            <div className="space-y-1">
              <label className="text-sm font-medium text-foreground/80 pl-1">Username</label>
              <div className="relative group">
                <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none text-foreground/40 group-focus-within:text-primary transition-colors">
                  <User className="h-5 w-5" />
                </div>
                <input
                  type="text"
                  required
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  className="w-full bg-secondary/50 border border-border rounded-xl pl-11 pr-4 py-3 outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary/50 transition-all text-sm"
                  placeholder="johndoe"
                />
              </div>
            </div>

            <div className="space-y-1">
              <label className="text-sm font-medium text-foreground/80 pl-1">Email</label>
              <div className="relative group">
                <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none text-foreground/40 group-focus-within:text-primary transition-colors">
                  <Mail className="h-5 w-5" />
                </div>
                <input
                  type="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="w-full bg-secondary/50 border border-border rounded-xl pl-11 pr-4 py-3 outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary/50 transition-all text-sm"
                  placeholder="name@example.com"
                />
              </div>
            </div>

            <div className="space-y-1">
              <label className="text-sm font-medium text-foreground/80 pl-1">Password</label>
              <div className="relative group">
                <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none text-foreground/40 group-focus-within:text-primary transition-colors">
                  <Lock className="h-5 w-5" />
                </div>
                <input
                  type="password"
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full bg-secondary/50 border border-border rounded-xl pl-11 pr-4 py-3 outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary/50 transition-all text-sm"
                  placeholder="••••••••"
                />
              </div>
            </div>

            <div className="space-y-1">
              <label className="text-sm font-medium text-foreground/80 pl-1">Confirm Password</label>
              <div className="relative group">
                <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none text-foreground/40 group-focus-within:text-primary transition-colors">
                  <Lock className="h-5 w-5" />
                </div>
                <input
                  type="password"
                  required
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  className="w-full bg-secondary/50 border border-border rounded-xl pl-11 pr-4 py-3 outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary/50 transition-all text-sm"
                  placeholder="••••••••"
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={isLoading}
              className="w-full bg-primary hover:bg-primary/90 text-primary-foreground py-3 rounded-xl font-semibold transition-all disabled:opacity-50 mt-4 flex items-center justify-center gap-2 group shadow-lg shadow-primary/20 hover:shadow-primary/40 active:scale-[0.98]"
            >
              {isLoading ? (
                <div className="w-5 h-5 border-2 border-primary-foreground border-t-transparent rounded-full animate-spin"></div>
              ) : (
                <>
                  Create Account
                  <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
                </>
              )}
            </button>
          </form>

          <div className="mt-6 text-center text-sm text-foreground/60">
            Already have an account?{' '}
            <Link 
              to="/login" 
              className="text-primary hover:underline font-semibold"
            >
              Sign in
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
