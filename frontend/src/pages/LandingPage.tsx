import { Button } from '@/components/ui/Button';
import { BrainCircuit, Play, CheckSquare, Activity, Search, Zap, ShieldCheck } from 'lucide-react';
import { Link } from 'react-router-dom';

export function LandingPage() {
  return (
    <div 
      className="min-h-screen bg-background-base flex flex-col relative overflow-hidden"
      style={{
        backgroundImage: 'url(/assets/landing-bg.jpg)',
        backgroundSize: 'cover',
        backgroundPosition: 'center',
        backgroundRepeat: 'no-repeat'
      }}
    >
      <div className="absolute inset-0 bg-background-base/80 md:bg-background-base/60 backdrop-blur-sm md:backdrop-blur-none z-0" />
      
      <header className="flex items-center justify-between p-6 max-w-7xl mx-auto w-full relative z-10">
        <div className="flex items-center gap-2 text-brand font-bold text-xl">
          <div className="w-8 h-8 bg-brand rounded-lg flex items-center justify-center">
            <BrainCircuit className="h-5 w-5 text-black" />
          </div>
          <span className="text-white">ModelSentinel</span>
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

      <main className="flex-1 flex flex-col justify-center pt-16 md:pt-24 max-w-7xl mx-auto w-full px-6 relative z-10">
        <div className="grid md:grid-cols-2 gap-12 items-center flex-1">
          <div className="flex flex-col gap-6">
            <h1 className="text-5xl md:text-[64px] font-bold tracking-tight text-white leading-[1.1]">
              From<br />
              Model Failures to<br />
              <span className="text-brand">Reliable Systems</span>
            </h1>
            <p className="text-lg text-text-secondary max-w-xl leading-relaxed font-medium">
              ModelSentinel detects ML issues, finds the root cause, generates validated fixes, and helps you prevent them.
            </p>
            <div className="flex items-center gap-4 pt-4">
              <Button variant="primary" size="lg" className="rounded-lg px-6 whitespace-nowrap gap-2 bg-[#f59e0b] hover:bg-[#d97706] text-black font-bold border-none" asChild>
                <Link to="/dashboard">Get Started &rarr;</Link>
              </Button>
              <Button variant="outline" size="lg" className="rounded-lg px-6 whitespace-nowrap gap-2 border-white/20 text-white hover:bg-surface hover:text-white bg-black/40 backdrop-blur-md">
                <Play className="h-4 w-4 text-white" />
                Watch Demo
              </Button>
            </div>
          </div>
          
          <div className="relative hidden md:block aspect-square w-full max-w-lg mx-auto">
            <div className="relative h-full w-full">
              {/* Abstract Representation of the 3D stack from image */}
              <div className="absolute top-[5%] left-[-10%] glass-panel p-3 rounded-2xl flex items-center gap-4 shadow-[0_0_15px_rgba(245,158,11,0.3)] transition-all w-56 border border-brand/50 bg-black/70 backdrop-blur-md">
                 <div className="w-10 h-10 flex items-center justify-center bg-brand/10 rounded-full border border-brand/50 text-brand"><Activity size={18} /></div>
                 <div className="flex flex-col">
                   <span className="font-bold text-white text-sm">Detect</span>
                   <span className="text-xs text-text-secondary">Performance drop</span>
                 </div>
              </div>
              
              <div className="absolute top-[25%] right-[0%] glass-panel p-3 rounded-2xl flex items-center gap-4 shadow-[0_0_15px_rgba(245,158,11,0.3)] transition-all w-56 border border-brand/50 bg-black/70 backdrop-blur-md">
                 <div className="w-10 h-10 flex items-center justify-center bg-brand/10 rounded-full border border-brand/50 text-brand"><Search size={18} /></div>
                 <div className="flex flex-col">
                   <span className="font-bold text-white text-sm">Investigate</span>
                   <span className="text-xs text-text-secondary">Root cause</span>
                 </div>
              </div>
              
              <div className="absolute top-[45%] left-[-20%] glass-panel p-3 rounded-2xl flex items-center gap-4 shadow-[0_0_15px_rgba(16,185,129,0.3)] transition-all w-56 border border-[#10b981]/50 bg-black/70 backdrop-blur-md">
                 <div className="w-10 h-10 flex items-center justify-center bg-[#10b981]/10 rounded-full border border-[#10b981]/50 text-[#10b981]"><Zap size={18} /></div>
                 <div className="flex flex-col">
                   <span className="font-bold text-white text-sm">Fix</span>
                   <span className="text-xs text-text-secondary">Generate patch</span>
                 </div>
              </div>
              
              <div className="absolute top-[65%] right-[-10%] glass-panel p-3 rounded-2xl flex items-center gap-4 shadow-[0_0_15px_rgba(16,185,129,0.3)] transition-all w-56 border border-[#10b981]/50 bg-black/70 backdrop-blur-md">
                 <div className="w-10 h-10 flex items-center justify-center bg-[#10b981]/10 rounded-full border border-[#10b981]/50 text-[#10b981]"><CheckSquare size={18} /></div>
                 <div className="flex flex-col">
                   <span className="font-bold text-white text-sm">Validate</span>
                   <span className="text-xs text-text-secondary">Test & evaluate</span>
                 </div>
              </div>
              
              <div className="absolute top-[85%] left-[-5%] glass-panel p-3 rounded-2xl flex items-center gap-4 shadow-[0_0_15px_rgba(245,158,11,0.3)] transition-all w-56 border border-brand/50 bg-black/70 backdrop-blur-md">
                 <div className="w-10 h-10 flex items-center justify-center bg-brand/10 rounded-full border border-brand/50 text-brand"><ShieldCheck size={18} /></div>
                 <div className="flex flex-col">
                   <span className="font-bold text-white text-sm">Prevent</span>
                   <span className="text-xs text-text-secondary">Add regression test</span>
                 </div>
              </div>
            </div>
          </div>
        </div>

        {/* Feature Row / Tech Stack */}
        <div className="w-full pb-8 pt-8 mt-12 border-t border-white/10 z-20">
          <p className="text-sm text-text-secondary font-medium mb-4">Built for Modern ML Teams</p>
          <div className="flex flex-wrap gap-8 items-center opacity-70 hover:opacity-100 transition-all duration-500 text-white">
            <span className="font-semibold text-lg flex items-center gap-2"><div className="w-4 h-4 rounded-full bg-slate-300"></div> scikit-learn</span>
            <span className="font-semibold text-lg flex items-center gap-2"><div className="w-4 h-4 bg-orange-600 rounded-sm"></div> PyTorch</span>
            <span className="font-semibold text-lg flex items-center gap-2"><div className="w-4 h-4 bg-orange-500 rounded-sm"></div> TensorFlow</span>
            <span className="font-semibold text-lg flex items-center gap-2"><div className="w-4 h-4 bg-teal-500 rounded-full"></div> FastAPI</span>
            <span className="font-semibold text-lg flex items-center gap-2"><div className="w-4 h-4 bg-blue-500 rounded-sm"></div> docker</span>
            <span className="font-bold text-xl flex items-center gap-2 text-[#ff9900]">aws</span>
          </div>
        </div>
      </main>
    </div>
  );
}
