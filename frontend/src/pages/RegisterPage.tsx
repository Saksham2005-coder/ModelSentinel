import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { fetchApi } from '@/services/api/client';
import { Eye, EyeOff, Activity, ShieldCheck, Zap, Search } from 'lucide-react';

export function RegisterPage() {
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);
  const [devToken, setDevToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');

    if (password !== confirmPassword) {
      setError('Passwords do not match.');
      setIsLoading(false);
      return;
    }

    if (password.length < 8) {
      setError('Password must be at least 8 characters.');
      setIsLoading(false);
      return;
    }

    try {
      const response = await fetchApi<{dev_verification_token?: string}>('/auth/register', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email,
          password,
          full_name: name
        })
      });

      if (response.dev_verification_token) {
        setDevToken(response.dev_verification_token);
      }
      setSuccess(true);
    } catch (err: unknown) {
      if (err instanceof Error) {
        // Backend returns "The user with this email already exists in the system." for duplicate
        setError(err.message);
      } else {
        setError('Unable to connect to ModelSentinel. Please try again.');
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex bg-background-base text-text-primary">
      {/* Left side: Branding & Visuals (Hidden on Mobile) */}
      <div className="hidden lg:flex lg:flex-1 relative bg-background-primary border-r border-border overflow-hidden">
        {/* Modern Ambient Gradient Background */}
        <div className="absolute inset-0 bg-[#0a0a0a]">
          <div className="absolute top-0 right-0 w-[80%] h-[80%] rounded-full bg-brand/10 blur-[120px] mix-blend-screen pointer-events-none" />
          <div className="absolute bottom-0 left-0 w-[60%] h-[60%] rounded-full bg-blue-500/10 blur-[120px] mix-blend-screen pointer-events-none" />
          <div className="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSI0IiBoZWlnaHQ9IjQiPgo8cmVjdCB3aWR0aD0iNCIgaGVpZ2h0PSI0IiBmaWxsPSIjZmZmIiBmaWxsLW9wYWNpdHk9IjAuMDUiLz4KPC9zdmc+')] opacity-20" />
        </div>
        
        {/* Atmospheric Accent */}
        <div className="absolute top-1/4 -left-32 w-96 h-96 bg-brand/10 rounded-full blur-3xl pointer-events-none" />

        <div className="relative z-10 p-16 flex flex-col h-full justify-between">
          <div>
            <div className="flex items-center space-x-3 mb-12">
              <div className="w-10 h-10 bg-brand rounded-lg flex items-center justify-center shadow-lg shadow-amber-500/20">
                <Activity className="text-slate-950 w-6 h-6" />
              </div>
              <span className="text-2xl font-bold tracking-tight text-white">MODELSENTINEL</span>
            </div>

            <h1 className="text-4xl md:text-5xl font-medium text-white mb-6 leading-tight tracking-tight">
              ML reliability engineering,<br />
              <span className="text-text-secondary">from detection to verified recovery.</span>
            </h1>
          </div>

          <div className="space-y-6 max-w-sm">
            <div className="flex items-center space-x-4 text-text-secondary">
              <Activity className="w-5 h-5 text-brand" />
              <span className="text-sm font-medium tracking-wide uppercase">Monitor</span>
            </div>
            <div className="flex items-center space-x-4 text-text-secondary">
              <Search className="w-5 h-5 text-brand" />
              <span className="text-sm font-medium tracking-wide uppercase">Investigate</span>
            </div>
            <div className="flex items-center space-x-4 text-text-secondary">
              <Zap className="w-5 h-5 text-brand" />
              <span className="text-sm font-medium tracking-wide uppercase">Remediate</span>
            </div>
            <div className="flex items-center space-x-4 text-text-secondary">
              <ShieldCheck className="w-5 h-5 text-brand" />
              <span className="text-sm font-medium tracking-wide uppercase">Verify</span>
            </div>
          </div>
        </div>
      </div>

      {/* Right side: Auth Card */}
      <div className="flex-1 flex flex-col justify-center py-12 px-4 sm:px-6 lg:px-20 xl:px-24 relative overflow-hidden">
        {/* Mobile background */}
        <div className="lg:hidden absolute inset-0 z-0 bg-[#0a0a0a]">
          <div className="absolute top-[-20%] right-[-20%] w-[80%] h-[80%] rounded-full bg-brand/10 blur-[100px] pointer-events-none" />
        </div>

        <div className="mx-auto w-full max-w-sm relative z-10">
          <div className="lg:hidden flex items-center space-x-3 mb-10">
            <div className="w-8 h-8 bg-brand rounded-lg flex items-center justify-center">
              <Activity className="text-slate-950 w-5 h-5" />
            </div>
            <span className="text-xl font-bold tracking-tight text-white">MODELSENTINEL</span>
          </div>

          <div>
            <h2 className="text-3xl font-semibold text-white tracking-tight">Create your account</h2>
            <p className="mt-2 text-sm text-text-secondary">Set up your ModelSentinel workspace credentials.</p>
          </div>

          <div className="mt-8">
            {success ? (
              <div className="p-6 bg-background-primary border border-border-strong rounded-lg text-center space-y-4">
                <div className="w-12 h-12 bg-brand/20 text-brand rounded-full flex items-center justify-center mx-auto mb-4">
                  <ShieldCheck className="w-6 h-6" />
                </div>
                <h3 className="text-lg font-medium text-white">Check your email</h3>
                <p className="text-sm text-text-primary">We've sent a verification link to your email address.</p>
                
                {devToken && (
                  <div className="mt-4 p-4 bg-background-secondary rounded-lg text-left">
                    <p className="text-xs text-brand font-semibold mb-2">DEVELOPMENT MODE:</p>
                    <p className="text-sm text-text-primary mb-2">Verification link generated successfully.</p>
                    <a 
                      href={`/verify-email?token=${devToken}`}
                      className="text-xs text-blue-400 hover:text-blue-300 break-all"
                    >
                      {window.location.origin}/verify-email?token={devToken}
                    </a>
                  </div>
                )}

                <div className="pt-4">
                  <Link to="/login" className="inline-flex justify-center py-2 px-4 border border-transparent rounded-lg shadow-sm text-sm font-medium text-black bg-brand hover:bg-brand-hover focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-brand focus:ring-offset-slate-900 transition-colors">
                    Back to Sign In
                  </Link>
                </div>
              </div>
            ) : (
              <form onSubmit={handleSubmit} className="space-y-6">
                {error && (
                  <div className="p-4 bg-red-500/10 border border-red-500/20 rounded-lg">
                    <p className="text-sm text-red-400">{error}</p>
                  </div>
                )}

                <div className="space-y-4">
                  <div>
                    <label htmlFor="name" className="block text-sm font-medium text-text-primary mb-1">
                      Full Name
                    </label>
                    <input
                      id="name"
                      name="name"
                      type="text"
                      autoComplete="name"
                      required
                      value={name}
                      onChange={(e) => setName(e.target.value)}
                      className="appearance-none block w-full px-4 py-3 bg-background-primary border border-border-strong rounded-lg text-text-primary placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-brand/50 focus:border-brand transition-colors sm:text-sm"
                      placeholder="Jane Doe"
                    />
                  </div>

                  <div>
                    <label htmlFor="email" className="block text-sm font-medium text-text-primary mb-1">
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
                      className="appearance-none block w-full px-4 py-3 bg-background-primary border border-border-strong rounded-lg text-text-primary placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-brand/50 focus:border-brand transition-colors sm:text-sm"
                      placeholder="name@company.com"
                    />
                  </div>

                  <div>
                    <label htmlFor="password" className="block text-sm font-medium text-text-primary mb-1">
                      Password
                    </label>
                    <div className="relative">
                      <input
                        id="password"
                        name="password"
                        type={showPassword ? 'text' : 'password'}
                        autoComplete="new-password"
                        required
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        className="appearance-none block w-full px-4 py-3 bg-background-primary border border-border-strong rounded-lg text-text-primary placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-brand/50 focus:border-brand transition-colors sm:text-sm"
                        placeholder="••••••••"
                      />
                      <button
                        type="button"
                        onClick={() => setShowPassword(!showPassword)}
                        className="absolute inset-y-0 right-0 pr-3 flex items-center text-text-muted hover:text-text-primary focus:outline-none"
                        aria-label={showPassword ? "Hide password" : "Show password"}
                      >
                        {showPassword ? (
                          <EyeOff className="h-5 w-5" aria-hidden="true" />
                        ) : (
                          <Eye className="h-5 w-5" aria-hidden="true" />
                        )}
                      </button>
                    </div>
                    <p className="mt-2 text-xs text-text-muted">
                      Minimum 8 characters. Use a dedicated ModelSentinel password.
                    </p>
                  </div>

                  <div>
                    <label htmlFor="confirm-password" className="block text-sm font-medium text-text-primary mb-1">
                      Confirm Password
                    </label>
                    <div className="relative">
                      <input
                        id="confirm-password"
                        name="confirm-password"
                        type={showConfirmPassword ? 'text' : 'password'}
                        autoComplete="new-password"
                        required
                        value={confirmPassword}
                        onChange={(e) => setConfirmPassword(e.target.value)}
                        className="appearance-none block w-full px-4 py-3 bg-background-primary border border-border-strong rounded-lg text-text-primary placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-brand/50 focus:border-brand transition-colors sm:text-sm"
                        placeholder="••••••••"
                      />
                      <button
                        type="button"
                        onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                        className="absolute inset-y-0 right-0 pr-3 flex items-center text-text-muted hover:text-text-primary focus:outline-none"
                        aria-label={showConfirmPassword ? "Hide password" : "Show password"}
                      >
                        {showConfirmPassword ? (
                          <EyeOff className="h-5 w-5" aria-hidden="true" />
                        ) : (
                          <Eye className="h-5 w-5" aria-hidden="true" />
                        )}
                      </button>
                    </div>
                  </div>
                </div>

                <button
                  type="submit"
                  disabled={isLoading}
                  className="w-full flex justify-center py-3 px-4 border border-transparent rounded-lg shadow-sm text-sm font-medium text-slate-950 bg-brand hover:bg-brand-hover focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-slate-900 focus:ring-brand disabled:opacity-50 disabled:cursor-not-allowed transition-all"
                >
                  {isLoading ? 'Creating account...' : 'Create Account'}
                </button>
              </form>
            )}

            <div className="mt-8 pt-8 border-t border-border flex justify-center">
              <p className="text-sm text-text-secondary">
                Already have an account?{' '}
                <Link to="/login" className="font-medium text-brand hover:text-brand-hover transition-colors">
                  Sign In
                </Link>
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
