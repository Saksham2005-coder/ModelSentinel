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
    <div className="min-h-screen flex bg-background-base text-text-primary">
      {/* Left side: Branding & Visuals (Hidden on Mobile) */}
      <div className="hidden lg:flex lg:flex-1 relative bg-background-primary border-r border-border overflow-hidden">
        {/* Background Image with Overlay */}
        <div 
          className="absolute inset-0 bg-cover bg-center bg-no-repeat opacity-40 mix-blend-luminosity"
          style={{ backgroundImage: 'url(/assets/auth-bg.jpg)' }}
        />
        <div className="absolute inset-0 bg-gradient-to-t from-background-base via-background-base/80 to-transparent" />
        <div className="absolute inset-0 bg-gradient-to-r from-background-base/90 to-transparent" />
        
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
        <div className="lg:hidden absolute inset-0 z-0">
          <div 
            className="absolute inset-0 bg-cover bg-center opacity-20 mix-blend-luminosity"
            style={{ backgroundImage: 'url(/assets/auth-bg.jpg)' }}
          />
          <div className="absolute inset-0 bg-background-base/90" />
        </div>

        <div className="mx-auto w-full max-w-sm relative z-10">
          <div className="lg:hidden flex items-center space-x-3 mb-10">
            <div className="w-8 h-8 bg-brand rounded-lg flex items-center justify-center">
              <Activity className="text-slate-950 w-5 h-5" />
            </div>
            <span className="text-xl font-bold tracking-tight text-white">MODELSENTINEL</span>
          </div>

          <Link to="/login" className="inline-flex items-center text-sm font-medium text-text-secondary hover:text-text-primary transition-colors mb-6">
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back to Sign In
          </Link>

          <div>
            <h2 className="text-3xl font-semibold text-white tracking-tight">Forgot your password?</h2>
            <p className="mt-2 text-sm text-text-secondary">Enter your ModelSentinel account email and we'll help you regain access.</p>
          </div>

          <div className="mt-8">
            {isSubmitted ? (
              <div className="space-y-6">
                <div className="p-4 bg-blue-500/10 border border-blue-500/20 rounded-lg">
                  <p className="text-sm text-blue-400 text-center">
                    Password recovery email delivery is not configured in this environment.
                  </p>
                </div>
                <p className="text-sm text-text-secondary text-center">
                  Please contact your administrator to regain access to your workspace.
                </p>
              </div>
            ) : (
              <form onSubmit={handleSubmit} className="space-y-6">
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

                <button
                  type="submit"
                  disabled={isLoading}
                  className="w-full flex justify-center py-3 px-4 border border-transparent rounded-lg shadow-sm text-sm font-medium text-slate-950 bg-brand hover:bg-brand-hover focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-slate-900 focus:ring-brand disabled:opacity-50 disabled:cursor-not-allowed transition-all"
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
