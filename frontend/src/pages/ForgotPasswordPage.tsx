import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { Activity, ShieldCheck, Zap, Search, ArrowLeft } from 'lucide-react';

export function ForgotPasswordPage() {
  const [email, setEmail] = useState('');
  const [isSubmitted, setIsSubmitted] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);

    // Simulate network delay to make the fake request feel real
    setTimeout(() => {
      setIsLoading(false);
      setIsSubmitted(true);
    }, 1000);
  };

  return (
    <div className="min-h-screen flex bg-slate-950 text-slate-200">
      {/* Left side: Branding & Visuals (Hidden on Mobile) */}
      <div className="hidden lg:flex lg:flex-1 relative bg-slate-900 border-r border-slate-800 overflow-hidden">
        {/* Background Image with Overlay */}
        <div 
          className="absolute inset-0 bg-cover bg-center bg-no-repeat opacity-40 mix-blend-luminosity"
          style={{ backgroundImage: 'url(/assets/auth-bg.jpg)' }}
        />
        <div className="absolute inset-0 bg-gradient-to-t from-slate-950 via-slate-950/80 to-transparent" />
        <div className="absolute inset-0 bg-gradient-to-r from-slate-950/90 to-transparent" />
        
        {/* Atmospheric Accent */}
        <div className="absolute top-1/4 -left-32 w-96 h-96 bg-amber-500/10 rounded-full blur-3xl pointer-events-none" />

        <div className="relative z-10 p-16 flex flex-col h-full justify-between">
          <div>
            <div className="flex items-center space-x-3 mb-12">
              <div className="w-10 h-10 bg-amber-500 rounded-lg flex items-center justify-center shadow-lg shadow-amber-500/20">
                <Activity className="text-slate-950 w-6 h-6" />
              </div>
              <span className="text-2xl font-bold tracking-tight text-white">MODELSENTINEL</span>
            </div>

            <h1 className="text-4xl md:text-5xl font-medium text-white mb-6 leading-tight tracking-tight">
              ML reliability engineering,<br />
              <span className="text-slate-400">from detection to verified recovery.</span>
            </h1>
          </div>

          <div className="space-y-6 max-w-sm">
            <div className="flex items-center space-x-4 text-slate-400">
              <Activity className="w-5 h-5 text-amber-500" />
              <span className="text-sm font-medium tracking-wide uppercase">Monitor</span>
            </div>
            <div className="flex items-center space-x-4 text-slate-400">
              <Search className="w-5 h-5 text-amber-500" />
              <span className="text-sm font-medium tracking-wide uppercase">Investigate</span>
            </div>
            <div className="flex items-center space-x-4 text-slate-400">
              <Zap className="w-5 h-5 text-amber-500" />
              <span className="text-sm font-medium tracking-wide uppercase">Remediate</span>
            </div>
            <div className="flex items-center space-x-4 text-slate-400">
              <ShieldCheck className="w-5 h-5 text-amber-500" />
              <span className="text-sm font-medium tracking-wide uppercase">Verify</span>
            </div>
          </div>
        </div>
      </div>

      {/* Right side: Auth Card */}
      <div className="flex-1 flex flex-col justify-center py-12 px-4 sm:px-6 lg:px-20 xl:px-24 relative overflow-hidden">
        {/* Mobile background */}
        <div className="lg:hidden absolute inset-0 z-0">
          <div 
            className="absolute inset-0 bg-cover bg-center opacity-20 mix-blend-luminosity"
            style={{ backgroundImage: 'url(/assets/auth-bg.jpg)' }}
          />
          <div className="absolute inset-0 bg-slate-950/90" />
        </div>

        <div className="mx-auto w-full max-w-sm relative z-10">
          <div className="lg:hidden flex items-center space-x-3 mb-10">
            <div className="w-8 h-8 bg-amber-500 rounded-lg flex items-center justify-center">
              <Activity className="text-slate-950 w-5 h-5" />
            </div>
            <span className="text-xl font-bold tracking-tight text-white">MODELSENTINEL</span>
          </div>

          <Link to="/login" className="inline-flex items-center text-sm font-medium text-slate-400 hover:text-slate-200 transition-colors mb-6">
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back to Sign In
          </Link>

          <div>
            <h2 className="text-3xl font-semibold text-white tracking-tight">Forgot your password?</h2>
            <p className="mt-2 text-sm text-slate-400">Enter your ModelSentinel account email and we'll help you regain access.</p>
          </div>

          <div className="mt-8">
            {isSubmitted ? (
              <div className="space-y-6">
                <div className="p-4 bg-blue-500/10 border border-blue-500/20 rounded-lg">
                  <p className="text-sm text-blue-400 text-center">
                    Password recovery email delivery is not configured in this environment.
                  </p>
                </div>
                <p className="text-sm text-slate-400 text-center">
                  Please contact your administrator to regain access to your workspace.
                </p>
              </div>
            ) : (
              <form onSubmit={handleSubmit} className="space-y-6">
                <div>
                  <label htmlFor="email" className="block text-sm font-medium text-slate-300 mb-1">
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
                    className="appearance-none block w-full px-4 py-3 bg-slate-900 border border-slate-700 rounded-lg text-slate-200 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-amber-500/50 focus:border-amber-500 transition-colors sm:text-sm"
                    placeholder="name@company.com"
                  />
                </div>

                <button
                  type="submit"
                  disabled={isLoading}
                  className="w-full flex justify-center py-3 px-4 border border-transparent rounded-lg shadow-sm text-sm font-medium text-slate-950 bg-amber-500 hover:bg-amber-400 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-slate-900 focus:ring-amber-500 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
                >
                  {isLoading ? 'Processing...' : 'Continue'}
                </button>
              </form>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
