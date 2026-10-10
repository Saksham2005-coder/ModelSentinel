import { Button } from '@/components/ui/Button';
import { Activity, Play, ChevronRight, Search, Zap, CheckSquare, ShieldCheck, AlertTriangle } from 'lucide-react';
import { Link } from 'react-router-dom';

export function LandingPage() {
  return (
    <div className="min-h-screen bg-[#f8f9fc] flex flex-col relative overflow-hidden font-sans">
      
      {/* 
        ========================================================
        BACKGROUND EFFECTS
        ========================================================
      */}
      {/* Deep Space Right Side */}
      <div className="absolute top-0 right-0 w-3/5 h-full bg-gradient-to-bl from-indigo-950 via-purple-900 to-transparent z-0" style={{ clipPath: 'polygon(20% 0, 100% 0, 100% 100%, 0% 100%)' }} />
      
      {/* Glowing Energy Waves */}
      <div className="absolute top-[-20%] right-[-10%] w-[70%] h-[70%] rounded-[100%] bg-gradient-to-tr from-orange-500 via-pink-500 to-purple-600 blur-[120px] mix-blend-screen opacity-60 z-0" />
      <div className="absolute bottom-[-20%] right-[10%] w-[60%] h-[60%] rounded-[100%] bg-gradient-to-tr from-yellow-400 via-orange-500 to-red-500 blur-[140px] mix-blend-screen opacity-50 z-0" />
      <div className="absolute top-[20%] left-[20%] w-[40%] h-[40%] rounded-[100%] bg-blue-400 blur-[150px] mix-blend-multiply opacity-20 z-0" />
      
      {/* 
        ========================================================
        HEADER
        ========================================================
      */}
      <header className="flex items-center justify-between p-6 max-w-7xl mx-auto w-full relative z-20">
        <div className="flex items-center gap-2 text-xl font-bold tracking-tight">
          <div className="w-8 h-8 bg-gradient-to-br from-orange-400 to-orange-600 rounded-md flex items-center justify-center shadow-lg">
            <Activity className="h-5 w-5 text-white" strokeWidth={3} />
          </div>
          <span className="text-slate-900">Model<span className="text-orange-500">Sentinel</span></span>
        </div>
        
        <nav className="hidden md:flex items-center gap-8 text-sm font-semibold text-slate-700">
          <a href="#" className="hover:text-slate-900 transition-colors">Product</a>
          <a href="#" className="hover:text-slate-900 transition-colors">Solutions</a>
          <a href="#" className="hover:text-slate-900 transition-colors">Resources</a>
          <a href="#" className="hover:text-slate-900 transition-colors">Pricing</a>
        </nav>
        
        <div className="flex items-center gap-4">
          <Button variant="ghost" className="text-white hover:text-slate-200 font-semibold" asChild>
            <Link to="/login">Sign in</Link>
          </Button>
          <Button className="bg-gradient-to-r from-orange-400 to-red-500 hover:from-orange-500 hover:to-red-600 text-white font-bold border-none shadow-lg shadow-orange-500/30 px-6 rounded-full" asChild>
            <Link to="/register">Get Started</Link>
          </Button>
        </div>
      </header>

      {/* 
        ========================================================
        MAIN CONTENT
        ========================================================
      */}
      <main className="flex-1 flex flex-col md:flex-row items-center pt-8 md:pt-16 max-w-[1400px] mx-auto w-full px-6 relative z-10">
        
        {/* LEFT COLUMN: Typography & CTAs */}
        <div className="w-full md:w-5/12 flex flex-col gap-6 relative z-20 pl-4 md:pl-12">
          
          <div className="flex items-center gap-2 text-xs font-bold tracking-[0.2em] text-slate-400 uppercase">
            <span>Monitor</span> <span className="w-1 h-1 bg-slate-300 rounded-full" /> 
            <span>Detect</span> <span className="w-1 h-1 bg-slate-300 rounded-full" /> 
            <span>Investigate</span> <span className="w-1 h-1 bg-slate-300 rounded-full" /> 
            <span>Prevent</span>
          </div>

          <h1 className="text-[3.5rem] md:text-[4.5rem] font-extrabold tracking-tight text-slate-900 leading-[1.05]">
            From <br />
            Model Failures to <br />
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-orange-400 via-red-500 to-pink-500 drop-shadow-sm">Reliable Systems</span>
          </h1>
          
          <p className="text-lg text-slate-500 max-w-lg leading-relaxed font-medium mt-2">
            ModelSentinel detects ML issues, finds the root cause, generates validated fixes, and helps you prevent them.
          </p>
          
          <div className="flex items-center gap-4 pt-4">
            <Button size="lg" className="rounded-full px-8 h-14 whitespace-nowrap gap-2 bg-gradient-to-r from-orange-400 to-pink-500 hover:from-orange-500 hover:to-pink-600 text-white font-bold text-base border-none shadow-xl shadow-orange-500/20 transition-all hover:scale-105" asChild>
              <Link to="/register">Get Started &rarr;</Link>
            </Button>
            <Button variant="outline" size="lg" className="rounded-full px-8 h-14 whitespace-nowrap gap-3 border-none bg-white text-slate-800 font-bold shadow-xl shadow-slate-200/50 hover:bg-slate-50 hover:scale-105 transition-all text-base">
              <div className="w-6 h-6 rounded-full bg-pink-100 flex items-center justify-center">
                <Play className="h-3 w-3 text-pink-600 ml-0.5" fill="currentColor" />
              </div>
              Watch Demo
            </Button>
          </div>

          {/* Tech Stack Pills */}
          <div className="mt-16">
            <p className="text-xs font-bold tracking-widest text-slate-500 uppercase mb-4">Built for Modern ML Teams</p>
            <div className="flex items-center gap-4 bg-white/70 backdrop-blur-md px-6 py-4 rounded-full shadow-lg shadow-slate-200/50 border border-white max-w-max">
              <span className="font-bold text-sm flex items-center gap-2 text-slate-700">
                <div className="w-5 h-5 rounded-full bg-blue-500 shadow-sm border border-white"></div> scikit-learn
              </span>
              <span className="w-px h-4 bg-slate-300"></span>
              <span className="font-bold text-sm flex items-center gap-2 text-slate-700">
                <div className="w-5 h-5 bg-orange-600 rounded-sm shadow-sm border border-white"></div> PyTorch
              </span>
              <span className="w-px h-4 bg-slate-300"></span>
              <span className="font-bold text-sm flex items-center gap-2 text-slate-700">
                <div className="w-5 h-5 bg-orange-400 rounded-sm shadow-sm border border-white"></div> TensorFlow
              </span>
              <span className="w-px h-4 bg-slate-300"></span>
              <span className="font-bold text-sm flex items-center gap-2 text-slate-700">
                <div className="w-5 h-5 bg-teal-500 rounded-full shadow-sm border border-white"></div> FastAPI
              </span>
              <span className="w-px h-4 bg-slate-300"></span>
              <span className="font-bold text-sm flex items-center gap-2 text-slate-700">
                <div className="w-5 h-5 bg-blue-600 rounded-sm shadow-sm border border-white"></div> docker
              </span>
            </div>
          </div>
        </div>
        
        {/* RIGHT COLUMN: 3D Scene Visualization */}
        <div className="w-full md:w-7/12 relative h-[700px] hidden md:block perspective-[2000px]">
          
          {/* Main Tilted Dashboard */}
          <div 
            className="absolute top-1/2 left-1/2 w-[850px] h-[550px] bg-slate-900/90 backdrop-blur-xl border border-white/10 rounded-2xl shadow-[0_30px_100px_rgba(0,0,0,0.5)] flex overflow-hidden"
            style={{
              transform: 'translate(-40%, -50%) rotateY(-20deg) rotateX(12deg) rotateZ(5deg)',
              transformStyle: 'preserve-3d',
              boxShadow: '-20px 40px 100px rgba(0,0,0,0.6), inset 0 1px 1px rgba(255,255,255,0.2)'
            }}
          >
            {/* Dashboard Sidebar */}
            <div className="w-48 border-r border-white/10 p-4 flex flex-col gap-2">
              <div className="flex items-center gap-2 mb-6">
                <Activity className="text-orange-500 w-5 h-5" />
                <span className="text-white font-bold text-sm">ModelSentinel</span>
              </div>
              
              <div className="bg-white/10 rounded-lg p-2 flex items-center gap-3 text-white text-xs font-medium">
                <div className="w-4 h-4 rounded bg-orange-500/20 flex items-center justify-center"><Activity size={12} className="text-orange-500" /></div>
                Overview
              </div>
              <div className="p-2 flex items-center gap-3 text-slate-400 text-xs font-medium hover:text-white transition-colors">
                <Activity size={14} /> Monitoring
              </div>
              <div className="p-2 flex items-center gap-3 text-slate-400 text-xs font-medium hover:text-white transition-colors">
                <AlertTriangle size={14} /> Incidents
              </div>
              <div className="p-2 flex items-center gap-3 text-slate-400 text-xs font-medium hover:text-white transition-colors">
                <Search size={14} /> Investigations
              </div>
            </div>

            {/* Dashboard Main Area */}
            <div className="flex-1 p-6 flex flex-col gap-4">
              {/* Top Stats */}
              <div className="flex gap-4">
                <div className="flex-1 bg-white/5 border border-white/10 rounded-xl p-4 flex items-center gap-4">
                  <div className="w-10 h-10 rounded-full border-2 border-emerald-500 flex items-center justify-center">
                    <span className="text-emerald-500 font-bold text-xs">18</span>
                  </div>
                  <div>
                    <div className="text-[10px] text-slate-400 uppercase">Healthy Models</div>
                    <div className="text-white font-bold text-sm">18 of 24</div>
                  </div>
                </div>
                <div className="flex-1 bg-white/5 border border-white/10 rounded-xl p-4 flex items-center gap-4">
                  <div className="w-10 h-10 rounded-full border-2 border-red-500 flex items-center justify-center bg-red-500/10">
                    <AlertTriangle className="text-red-500 w-4 h-4" />
                  </div>
                  <div>
                    <div className="text-[10px] text-slate-400 uppercase">Active Incidents</div>
                    <div className="text-white font-bold text-sm">3 Critical</div>
                  </div>
                </div>
                <div className="flex-1 bg-white/5 border border-white/10 rounded-xl p-4">
                  <div className="text-[10px] text-slate-400 uppercase">Mean Time to Fix</div>
                  <div className="text-white font-bold text-xl mt-1">21 <span className="text-xs text-emerald-500 font-normal">↓ 42%</span></div>
                </div>
              </div>
              
              {/* Big Chart */}
              <div className="flex-1 bg-white/5 border border-white/10 rounded-xl p-4 flex flex-col relative overflow-hidden">
                <div className="text-xs font-bold text-white mb-4">Model Performance Trend</div>
                {/* Fake Chart Grid */}
                <div className="absolute inset-x-4 top-12 bottom-4 flex flex-col justify-between">
                  <div className="border-t border-white/5 w-full"></div>
                  <div className="border-t border-white/5 w-full"></div>
                  <div className="border-t border-white/5 w-full"></div>
                  <div className="border-t border-white/5 w-full"></div>
                </div>
                {/* Fake SVG Chart Lines */}
                <svg className="w-full h-full absolute inset-0 pt-12 pb-4 px-4 overflow-visible" preserveAspectRatio="none">
                  <path d="M 0 100 C 50 120, 100 40, 150 60 S 250 150, 300 80 S 400 40, 450 120 S 550 50, 600 90" fill="none" stroke="url(#orange-grad)" strokeWidth="3" filter="drop-shadow(0 4px 6px rgba(249,115,22,0.5))" />
                  <path d="M 0 140 C 80 160, 120 90, 180 110 S 280 40, 320 70 S 420 160, 480 140 S 560 60, 600 120" fill="none" stroke="#ec4899" strokeWidth="2" strokeDasharray="4 4" />
                  <defs>
                    <linearGradient id="orange-grad" x1="0" y1="0" x2="1" y2="0">
                      <stop offset="0%" stopColor="#f59e0b" />
                      <stop offset="100%" stopColor="#ef4444" />
                    </linearGradient>
                  </defs>
                  
                  {/* Alert marker */}
                  <circle cx="300" cy="80" r="6" fill="#ef4444" className="animate-pulse" />
                  <line x1="300" y1="80" x2="300" y2="200" stroke="#ef4444" strokeWidth="1" strokeDasharray="2 2" />
                </svg>
              </div>

              {/* Bottom Small Widgets */}
              <div className="h-32 flex gap-4">
                <div className="flex-1 bg-white/5 border border-white/10 rounded-xl p-4 flex flex-col justify-end gap-1">
                  <div className="text-[10px] text-slate-400 uppercase absolute top-4 left-4">Anomaly Detection</div>
                  <div className="flex items-end gap-1 h-12">
                    {[3, 5, 2, 8, 4, 9, 3, 2, 7, 10, 4, 3, 2].map((h, i) => (
                      <div key={i} className={`flex-1 rounded-t-sm ${h > 7 ? 'bg-red-500' : 'bg-orange-500'}`} style={{ height: `${h * 10}%` }}></div>
                    ))}
                  </div>
                </div>
                <div className="flex-1 bg-white/5 border border-white/10 rounded-xl p-4 flex items-center justify-center relative">
                   <div className="text-[10px] text-slate-400 uppercase absolute top-4 left-4">Incident Types</div>
                   {/* Fake Donut Chart */}
                   <div className="w-16 h-16 rounded-full border-4 border-blue-500 border-r-pink-500 border-b-orange-500"></div>
                </div>
              </div>

            </div>
          </div>

          {/* FLOATING ACTION CARDS */}
          
          {/* Detect Card */}
          <div className="absolute top-[5%] right-[35%] w-64 bg-white/95 backdrop-blur-xl border border-white/50 rounded-2xl p-4 shadow-[0_20px_40px_rgba(0,0,0,0.15)] flex items-center justify-between z-30 transform hover:scale-105 hover:-translate-y-1 transition-all cursor-default">
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 bg-orange-50 rounded-full flex items-center justify-center text-orange-500 border border-orange-100 shadow-sm">
                <Activity size={20} strokeWidth={2.5} />
              </div>
              <div className="flex flex-col">
                <span className="font-extrabold text-slate-900 text-base">Detect</span>
                <span className="text-xs text-slate-500 font-medium">Performance drop</span>
              </div>
            </div>
            <div className="w-8 h-8 rounded-full bg-red-50 flex items-center justify-center text-red-500">
              <AlertTriangle size={14} strokeWidth={3} />
            </div>
          </div>

          {/* Investigate Card */}
          <div className="absolute top-[25%] right-[5%] w-64 bg-slate-100/90 backdrop-blur-xl border border-white/50 rounded-2xl p-4 shadow-[0_20px_40px_rgba(0,0,0,0.2)] flex items-center justify-between z-30 transform translate-z-[50px] hover:scale-105 transition-all cursor-default">
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 bg-white rounded-full flex items-center justify-center text-purple-600 border border-purple-100 shadow-sm">
                <Search size={20} strokeWidth={2.5} />
              </div>
              <div className="flex flex-col">
                <span className="font-extrabold text-slate-900 text-base">Investigate</span>
                <span className="text-xs text-slate-500 font-medium">Root cause</span>
              </div>
            </div>
            <ChevronRight className="text-slate-400 w-5 h-5" />
          </div>

          {/* Fix Card */}
          <div className="absolute top-[60%] left-[5%] w-60 bg-white/95 backdrop-blur-xl border border-white/50 rounded-2xl p-4 shadow-[0_20px_40px_rgba(0,0,0,0.15)] flex items-center justify-between z-30 transform hover:scale-105 transition-all cursor-default">
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 bg-emerald-50 rounded-full flex items-center justify-center text-emerald-500 border border-emerald-100 shadow-sm">
                <Zap size={20} strokeWidth={2.5} />
              </div>
              <div className="flex flex-col">
                <span className="font-extrabold text-slate-900 text-base">Fix</span>
                <span className="text-xs text-slate-500 font-medium">Generate patch</span>
              </div>
            </div>
            <ChevronRight className="text-slate-400 w-5 h-5" />
          </div>

          {/* Validate Card */}
          <div className="absolute top-[75%] right-[2%] w-60 bg-slate-100/95 backdrop-blur-xl border border-white/50 rounded-2xl p-4 shadow-[0_20px_40px_rgba(0,0,0,0.2)] flex items-center justify-between z-30 transform hover:scale-105 transition-all cursor-default">
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 bg-white rounded-full flex items-center justify-center text-emerald-500 border border-emerald-100 shadow-sm">
                <CheckSquare size={20} strokeWidth={2.5} />
              </div>
              <div className="flex flex-col">
                <span className="font-extrabold text-slate-900 text-base">Validate</span>
                <span className="text-xs text-slate-500 font-medium">Test & evaluate</span>
              </div>
            </div>
            <ChevronRight className="text-slate-400 w-5 h-5" />
          </div>

          {/* Prevent Card */}
          <div className="absolute bottom-[2%] left-[30%] w-64 bg-white/95 backdrop-blur-xl border border-white/50 rounded-2xl p-4 shadow-[0_20px_40px_rgba(0,0,0,0.15)] flex items-center justify-between z-30 transform hover:scale-105 transition-all cursor-default">
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 bg-orange-50 rounded-full flex items-center justify-center text-orange-500 border border-orange-100 shadow-sm">
                <ShieldCheck size={20} strokeWidth={2.5} />
              </div>
              <div className="flex flex-col">
                <span className="font-extrabold text-slate-900 text-base">Prevent</span>
                <span className="text-xs text-slate-500 font-medium">Add regression test</span>
              </div>
            </div>
            <ChevronRight className="text-slate-400 w-5 h-5" />
          </div>

        </div>
      </main>
    </div>
  );
}
