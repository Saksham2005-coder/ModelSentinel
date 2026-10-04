import { Button } from '@/components/ui/Button';
import { BrainCircuit, Play, AlertCircle, CheckSquare } from 'lucide-react';
import { Link } from 'react-router-dom';

export function LandingPage() {
  return (
    <div className="min-h-screen bg-background-base flex flex-col">
      <header className="flex items-center justify-between p-6 max-w-7xl mx-auto w-full">
        <div className="flex items-center gap-2 text-brand font-bold text-xl">
          <BrainCircuit className="h-6 w-6" />
          <span className="text-text-primary">ModelSentinel</span>
        </div>
        <nav className="hidden md:flex items-center gap-8 text-sm font-medium text-text-secondary">
          <a href="#" className="hover:text-text-primary transition-colors">Product</a>
          <a href="#" className="hover:text-text-primary transition-colors">Solutions</a>
          <a href="#" className="hover:text-text-primary transition-colors">Resources</a>
          <a href="#" className="hover:text-text-primary transition-colors">Pricing</a>
        </nav>
        <div className="flex items-center gap-4">
          <Button variant="ghost" asChild>
            <Link to="/login">Sign in</Link>
          </Button>
          <Button variant="primary" asChild>
            <Link to="/dashboard">Get Started</Link>
          </Button>
        </div>
      </header>

      <main className="flex-1 flex items-center pt-16 md:pt-24 max-w-7xl mx-auto w-full px-6">
        <div className="grid md:grid-cols-2 gap-12 items-center">
          <div className="flex flex-col gap-6">
            <h1 className="text-5xl md:text-6xl font-bold tracking-tight text-text-primary leading-[1.1]">
              From Model Failures<br />
              <span className="text-brand">to Reliable Systems</span>
            </h1>
            <p className="text-lg text-text-secondary max-w-lg leading-relaxed">
              ModelSentinel detects ML issues, finds the root cause, generates validated fixes, and helps prevent them.
            </p>
            <div className="flex items-center gap-4 pt-4">
              <Button variant="primary" size="lg" asChild>
                <Link to="/dashboard">Get Started</Link>
              </Button>
              <Button variant="outline" size="lg" className="gap-2">
                <Play className="h-4 w-4" />
                Watch Demo
              </Button>
            </div>
            
            <div className="mt-12 pt-8 border-t border-border">
              <p className="text-sm text-text-muted font-medium mb-6 uppercase tracking-wider">Built for Modern ML Teams</p>
              <div className="flex flex-wrap gap-6 items-center opacity-60 grayscale hover:grayscale-0 transition-all duration-500">
                <span className="font-semibold text-lg">scikit-learn</span>
                <span className="font-semibold text-lg">PyTorch</span>
                <span className="font-semibold text-lg">TensorFlow</span>
                <span className="font-semibold text-lg">FastAPI</span>
                <span className="font-semibold text-lg">Docker</span>
              </div>
            </div>
          </div>
          
          <div className="relative hidden md:block aspect-square w-full max-w-lg mx-auto">
            <div className="absolute inset-0 bg-brand/20 blur-[100px] rounded-full mix-blend-screen" />
            <div className="relative h-full w-full border border-border-strong rounded-3xl bg-surface/50 p-8 backdrop-blur-xl flex flex-col items-center justify-center gap-8 shadow-2xl">
              <div className="w-full flex justify-between items-center opacity-50">
                <div className="w-24 h-1 bg-border rounded-full" />
                <div className="w-24 h-1 bg-brand rounded-full shadow-[0_0_10px_rgba(245,158,11,0.5)]" />
                <div className="w-24 h-1 bg-border rounded-full" />
              </div>
              <div className="flex items-center justify-center w-32 h-32 rounded-full border border-brand/50 bg-brand/10 shadow-[0_0_30px_rgba(245,158,11,0.2)]">
                <BrainCircuit className="h-12 w-12 text-brand" />
              </div>
              <div className="grid grid-cols-2 gap-4 w-full">
                <div className="p-4 rounded-xl bg-surface border border-border flex flex-col gap-2">
                  <div className="w-8 h-8 rounded bg-status-danger/20 flex items-center justify-center">
                    <AlertCircle className="h-4 w-4 text-status-danger" />
                  </div>
                  <span className="text-sm font-medium">Incident Detected</span>
                </div>
                <div className="p-4 rounded-xl bg-surface border border-border flex flex-col gap-2">
                  <div className="w-8 h-8 rounded bg-status-success/20 flex items-center justify-center">
                    <CheckSquare className="h-4 w-4 text-status-success" />
                  </div>
                  <span className="text-sm font-medium">Fix Validated</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
