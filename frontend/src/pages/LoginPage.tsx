import React, { useState } from 'react';
import { useNavigate, useLocation, Link } from 'react-router-dom';
import { fetchApi } from '@/services/api/client';
import { useAuth, User } from '@/AuthContext';
import { Eye, EyeOff, Activity, ShieldCheck, Zap, Search } from 'lucide-react';

interface LocationState {
  from?: {
    pathname: string;
  };
}

interface LoginResponse {
  access_token: string;
  user?: Record<string, unknown>;
}

export function LoginPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  
  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const state = location.state as LocationState;
  const from = state?.from?.pathname || '/dashboard';

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');

    try {
      const formData = new URLSearchParams();
      formData.append('username', email);
      formData.append('password', password);

      const data = await fetchApi<LoginResponse>('/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: formData.toString()
      });

      login(data.access_token, (data.user as unknown as User) || { email, full_name: 'Unknown User', role: 'VIEWER' });
      navigate(from, { replace: true });
    } catch (err: unknown) {
      if (err instanceof Error) {
        setError('Email or password is incorrect.');
      } else {
        setError('Unable to connect to ModelSentinel. Please try again.');
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex bg-black text-text-primary">
      {/* Left side: Branding & Visuals (Hidden on Mobile) */}
      <div className="hidden lg:flex lg:flex-1 relative bg-black border-r border-border overflow-hidden">
        {/* Modern Ambient Gradient Background */}
        <div className="absolute inset-0 bg-[#0a0a0a]">
          <div className="absolute top-0 right-0 w-[80%] h-[80%] rounded-full bg-brand/10 blur-[120px] mix-blend-screen pointer-events-none" />
          <div className="absolute bottom-0 left-0 w-[60%] h-[60%] rounded-full bg-blue-500/10 blur-[120px] mix-blend-screen pointer-events-none" />
          <div className="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSI0IiBoZWlnaHQ9IjQiPgo8cmVjdCB3aWR0aD0iNCIgaGVpZ2h0PSI0IiBmaWxsPSIjZmZmIiBmaWxsLW9wYWNpdHk9IjAuMDUiLz4KPC9zdmc+')] opacity-20" />
        </div>
        
        {/* Atmospheric Accent */}
        <div className="absolute top-1/4 -left-32 w-96 h-96 bg-brand/20 rounded-full blur-[100px] pointer-events-none" />

        <div className="relative z-10 p-16 flex flex-col h-full justify-between">
          <div>
            <div className="flex items-center space-x-3 mb-12">
              <div className="w-10 h-10 bg-brand rounded-lg flex items-center justify-center shadow-lg shadow-brand/20">
                <Activity className="text-black w-6 h-6" />
              </div>
              <span className="text-2xl font-bold tracking-tight text-white uppercase">MODELSENTINEL</span>
            </div>

            <h1 className="text-3xl md:text-4xl font-bold text-white mb-6 leading-tight tracking-tight">
              ML reliability engineering,<br />
              <span className="text-text-secondary font-medium">from detection to verified recovery.</span>
            </h1>
          </div>

          <div className="space-y-6 max-w-sm">
            <div className="flex items-center space-x-4 text-text-secondary">
              <Activity className="w-5 h-5 text-brand" />
              <span className="text-sm font-bold tracking-wide uppercase text-white/80">Monitor</span>
            </div>
            <div className="flex items-center space-x-4 text-text-secondary">
              <Search className="w-5 h-5 text-brand" />
              <span className="text-sm font-bold tracking-wide uppercase text-white/80">Investigate</span>
            </div>
            <div className="flex items-center space-x-4 text-text-secondary">
              <Zap className="w-5 h-5 text-brand" />
              <span className="text-sm font-bold tracking-wide uppercase text-white/80">Remediate</span>
            </div>
            <div className="flex items-center space-x-4 text-text-secondary">
              <ShieldCheck className="w-5 h-5 text-brand" />
              <span className="text-sm font-bold tracking-wide uppercase text-white/80">Verify</span>
            </div>
          </div>
        </div>
      </div>

      {/* Right side: Auth Card */}
      <div className="flex-1 flex flex-col justify-center py-12 px-4 sm:px-6 lg:px-20 xl:px-24 relative overflow-hidden bg-black">
        {/* Mobile background */}
        <div className="lg:hidden absolute inset-0 z-0 bg-[#0a0a0a]">
          <div className="absolute top-[-20%] right-[-20%] w-[80%] h-[80%] rounded-full bg-brand/10 blur-[100px] pointer-events-none" />
        </div>

        <div className="mx-auto w-full max-w-sm relative z-10">
          <div className="lg:hidden flex items-center space-x-3 mb-10">
            <div className="w-8 h-8 bg-brand rounded flex items-center justify-center">
              <Activity className="text-black w-5 h-5" />
            </div>
            <span className="text-xl font-bold tracking-tight text-white uppercase">MODELSENTINEL</span>
          </div>

          <div>
            <h2 className="text-4xl font-bold text-white tracking-tight">Welcome back</h2>
            <p className="mt-3 text-sm text-text-secondary font-medium">Sign in to your ModelSentinel workspace.</p>
          </div>

          <div className="mt-10">
            <form onSubmit={handleSubmit} className="space-y-6">
              {error && (
                <div className="p-4 bg-red-500/10 border border-red-500/20 rounded-lg">
                  <p className="text-sm text-red-400">{error}</p>
                </div>
              )}

              <div className="space-y-5">
                <div>
                  <label htmlFor="email" className="block text-sm font-bold text-white mb-2">
                    Email
                  </label>
                  <input
                    id="email"
                    name="email"
                    type="email"
                    autoComplete="email"
                    required
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    className="appearance-none block w-full px-4 py-3 bg-white/5 border border-white/10 rounded-lg text-white placeholder-white/40 focus:outline-none focus:ring-2 focus:ring-brand focus:border-brand focus:bg-white/10 transition-all sm:text-sm font-medium"
                    placeholder="demo-admin@modelsentinel.com"
                  />
                </div>

                <div>
                  <label htmlFor="password" className="block text-sm font-bold text-white mb-2">
                    Password
                  </label>
                  <div className="relative">
                    <input
                      id="password"
                      name="password"
                      type={showPassword ? 'text' : 'password'}
                      autoComplete="current-password"
                      required
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      className="appearance-none block w-full px-4 py-3 bg-white/5 border border-white/10 rounded-lg text-white placeholder-white/40 focus:outline-none focus:ring-2 focus:ring-brand focus:border-brand focus:bg-white/10 transition-all sm:text-sm font-medium"
                      placeholder="••••••••"
                    />
                    <button
                      type="button"
                      onClick={() => setShowPassword(!showPassword)}
                      className="absolute inset-y-0 right-0 pr-3 flex items-center text-slate-400 hover:text-slate-600 focus:outline-none"
                      aria-label={showPassword ? "Hide password" : "Show password"}
                    >
                      {showPassword ? (
                        <EyeOff className="h-5 w-5" aria-hidden="true" />
                      ) : (
                        <Eye className="h-5 w-5" aria-hidden="true" />
                      )}
                    </button>
                  </div>
                  <p className="mt-2 text-xs text-text-secondary leading-relaxed">
                    Use your ModelSentinel account password. This is separate from your email or GitHub password.
                  </p>
                </div>
              </div>

              <div className="flex items-center justify-end">
                <div className="text-sm">
                  <Link to="/forgot-password" className="font-semibold text-brand hover:text-brand-hover transition-colors">
                    Forgot password?
                  </Link>
                </div>
              </div>

              <button
                type="submit"
                disabled={isLoading}
                className="w-full flex justify-center py-3 px-4 border border-transparent rounded-lg shadow-sm text-sm font-bold text-black bg-[#f59e0b] hover:bg-[#d97706] focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-black focus:ring-brand disabled:opacity-50 disabled:cursor-not-allowed transition-all"
              >
                {isLoading ? 'Signing in...' : 'Sign In'}
              </button>
            </form>

            <div className="mt-8 pt-8 border-t border-border flex justify-center">
              <p className="text-sm text-text-secondary">
                Don't have an account?{' '}
                <Link to="/register" className="font-medium text-brand hover:text-brand-hover transition-colors">
                  Create account
                </Link>
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
