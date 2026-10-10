import React, { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import { PatchesApi, PatchChangeIntelligence } from '@/services/api/patches';
import { 
  AlertTriangle, 
  Search, 
  Activity, 
  Box, 
  Database,
  ShieldAlert,
  Clock,
  Layers,
  FileCode,
  FileText
} from 'lucide-react';
import { cn } from '@/lib/utils';

export function ChangeIntelligencePage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const patchId = searchParams.get('patchId') || '';
  
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [data, setData] = useState<PatchChangeIntelligence | null>(null);
  const [searchVal, setSearchVal] = useState(patchId);

  useEffect(() => {
    if (patchId) {
      loadData(patchId);
    }
  }, [patchId]);

  const loadData = async (id: string) => {
    setLoading(true);
    setError(null);
    try {
      const res = await PatchesApi.getChangeIntelligence(id);
      setData(res);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load change intelligence');
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchVal.trim()) {
      setSearchParams({ patchId: searchVal.trim() });
    }
  };

  return (
    <div className="flex flex-col h-full bg-background-base text-text-primary">
      <header className="flex flex-col gap-4 p-6 border-b border-border/60 bg-background-primary/50">
        <div>
          <h1 className="text-2xl font-semibold text-text-primary flex items-center gap-2">
            <Activity className="w-6 h-6 text-brand" />
            Change Intelligence
          </h1>
          <p className="text-sm text-text-secondary mt-1">
            Deep ML-aware impact analysis and historical correlation for proposed repository changes.
          </p>
        </div>
        
        <form onSubmit={handleSearch} className="flex gap-3 max-w-xl">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-text-muted" />
            <input 
              type="text"
              placeholder="Enter Patch ID to analyze..."
              value={searchVal}
              onChange={e => setSearchVal(e.target.value)}
              className="w-full bg-background-primary border border-border-strong rounded-md py-2 pl-9 pr-4 text-sm focus:outline-none focus:border-brand focus:ring-1 focus:ring-brand"
            />
          </div>
          <button 
            type="submit"
            disabled={loading || !searchVal.trim()}
            className="bg-status-warning hover:bg-status-warning/90 text-background-base disabled:opacity-50 text-text-primary px-4 py-2 rounded-md text-sm font-medium transition-colors"
          >
            Analyze
          </button>
        </form>
      </header>

      <div className="flex-1 overflow-auto p-6">
        {loading && (
          <div className="flex justify-center items-center h-48">
            <div className="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-brand"></div>
          </div>
        )}

        {error && (
          <div className="bg-red-500/10 border border-red-500/20 text-red-400 p-4 rounded-md flex items-start gap-3">
            <AlertTriangle className="w-5 h-5 mt-0.5 flex-shrink-0" />
            <div>
              <h3 className="font-medium text-red-300">Analysis Failed</h3>
              <p className="text-sm mt-1">{error}</p>
            </div>
          </div>
        )}

        {!loading && !error && !data && patchId && (
          <div className="text-center py-12 text-text-muted">
            No intelligence data found for this patch.
          </div>
        )}

        {!loading && !error && !data && !patchId && (
          <div className="flex flex-col items-center justify-center py-20 text-text-muted space-y-4">
            <Activity className="w-16 h-16 text-slate-700" />
            <p>Enter a patch ID above to view ML-aware change intelligence.</p>
          </div>
        )}

        {data && (
          <div className="space-y-6 max-w-6xl mx-auto pb-12">
            
            {/* Top Stats */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="bg-background-primary border border-border rounded-lg p-5 flex items-center justify-between">
                <div>
                  <h3 className="text-text-secondary text-sm font-medium mb-1">Risk Score</h3>
                  <div className="flex items-baseline gap-2">
                    <span className={cn(
                      "text-3xl font-bold",
                      data.risk_score >= 70 ? "text-red-400" :
                      data.risk_score >= 40 ? "text-brand-hover" : "text-status-success"
                    )}>
                      {data.risk_score}
                    </span>
                    <span className="text-text-muted text-sm">/ 100</span>
                  </div>
                </div>
                <ShieldAlert className={cn(
                  "w-10 h-10 opacity-20",
                  data.risk_score >= 70 ? "text-red-500" :
                  data.risk_score >= 40 ? "text-brand" : "text-status-success"
                )} />
              </div>
              
              <div className="bg-background-primary border border-border rounded-lg p-5 flex items-center justify-between">
                <div>
                  <h3 className="text-text-secondary text-sm font-medium mb-1">Blast Radius</h3>
                  <div className="flex items-center gap-2">
                    <span className={cn(
                      "text-2xl font-bold tracking-wide",
                      data.blast_radius === 'HIGH' ? "text-red-400" :
                      data.blast_radius === 'MEDIUM' ? "text-brand-hover" : "text-status-success"
                    )}>
                      {data.blast_radius}
                    </span>
                  </div>
                </div>
                <Activity className="w-10 h-10 text-text-muted opacity-20" />
              </div>
            </div>

            {/* Changed Files */}
            <div className="bg-background-primary border border-border rounded-lg overflow-hidden">
              <div className="px-5 py-4 border-b border-border bg-background-primary/50">
                <h2 className="text-lg font-medium text-text-primary flex items-center gap-2">
                  <FileCode className="w-5 h-5 text-brand" />
                  Changed Files
                </h2>
              </div>
              <div className="p-5">
                {data.changed_files.length > 0 ? (
                  <div className="space-y-4">
                    {data.changed_files.map((cf, idx) => (
                      <div key={idx} className="bg-background-base border border-border/60 rounded-md p-4">
                        <div className="flex items-start justify-between">
                          <div className="font-mono text-sm text-blue-300 font-medium">
                            {cf.path}
                          </div>
                          <span className="text-xs bg-background-secondary text-text-primary px-2 py-0.5 rounded border border-border-strong">
                            {cf.ml_category}
                          </span>
                        </div>
                        {cf.symbols_changed.length > 0 && (
                          <div className="mt-3 text-sm">
                            <span className="text-text-muted text-xs uppercase tracking-wider mb-1 block">Modified Symbols</span>
                            <div className="flex flex-wrap gap-2">
                              {cf.symbols_changed.map(sym => (
                                <span key={sym} className="font-mono text-xs text-status-warning/80 bg-status-warning-soft px-2 py-1 rounded border border-status-warning/30">
                                  {sym}
                                </span>
                              ))}
                            </div>
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-sm text-text-muted">No file changes detected.</p>
                )}
              </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Dependency Impact */}
              <div className="bg-background-primary border border-border rounded-lg flex flex-col">
                <div className="px-5 py-4 border-b border-border bg-background-primary/50">
                  <h2 className="text-lg font-medium text-text-primary flex items-center gap-2">
                    <Layers className="w-5 h-5 text-status-success" />
                    Dependency Impact
                  </h2>
                </div>
                <div className="p-5 flex-1 overflow-auto max-h-80">
                  {data.affected_dependencies.length > 0 ? (
                    <div className="flex flex-col gap-2">
                      {data.affected_dependencies.map((dep, i) => (
                        <div key={i} className="flex items-center gap-3 text-sm text-text-primary">
                          <div className="w-1.5 h-1.5 rounded-full bg-slate-600 flex-shrink-0" />
                          <span className="font-mono text-text-secondary">{dep}</span>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <p className="text-sm text-text-muted">No downstream dependencies detected.</p>
                  )}
                </div>
              </div>

              {/* ML Impact & Models */}
              <div className="flex flex-col gap-6">
                <div className="bg-background-primary border border-border rounded-lg">
                  <div className="px-5 py-4 border-b border-border bg-background-primary/50">
                    <h2 className="text-lg font-medium text-text-primary flex items-center gap-2">
                      <Box className="w-5 h-5 text-cyan-400" />
                      ML Impact Categories
                    </h2>
                  </div>
                  <div className="p-5">
                    {data.ml_impact.length > 0 ? (
                      <div className="flex flex-wrap gap-2">
                        {data.ml_impact.map((mi, i) => (
                          <div key={i} className="px-3 py-1.5 bg-background-secondary/50 border border-border-strong/50 rounded-md">
                            <div className="text-sm font-medium text-text-primary">{mi.component}</div>
                            <div className="text-xs text-text-secondary mt-0.5">{mi.reason}</div>
                          </div>
                        ))}
                      </div>
                    ) : (
                      <p className="text-sm text-text-muted">No ML components identified.</p>
                    )}
                  </div>
                </div>

                <div className="bg-background-primary border border-border rounded-lg flex-1">
                  <div className="px-5 py-4 border-b border-border bg-background-primary/50">
                    <h2 className="text-lg font-medium text-text-primary flex items-center gap-2">
                      <Database className="w-5 h-5 text-purple-400" />
                      Affected Models
                    </h2>
                  </div>
                  <div className="p-5">
                    {data.affected_models.length > 0 ? (
                      <div className="space-y-3">
                        {data.affected_models.map((am, i) => (
                          <div key={i} className="flex items-center justify-between p-3 bg-background-base border border-border rounded-md">
                            <span className="text-sm font-medium text-text-primary">{am.model_id}</span>
                            <span className="text-xs text-text-secondary bg-background-primary px-2 py-1 rounded border border-border-strong">
                              v: {am.version_id.slice(0, 8)}
                            </span>
                          </div>
                        ))}
                      </div>
                    ) : (
                      <p className="text-sm text-text-muted">No directly affected models found.</p>
                    )}
                  </div>
                </div>
              </div>
            </div>

            {/* Historical Evidence */}
            <div className="bg-background-primary border border-border rounded-lg overflow-hidden">
              <div className="px-5 py-4 border-b border-border bg-background-primary/50">
                <h2 className="text-lg font-medium text-text-primary flex items-center gap-2">
                  <Clock className="w-5 h-5 text-orange-400" />
                  Historical Evidence
                </h2>
              </div>
              <div className="p-5">
                {data.historical_evidence.length > 0 ? (
                  <div className="space-y-3">
                    {data.historical_evidence.map((he, i) => (
                      <div key={i} className="flex items-start gap-4 p-4 bg-background-base border border-border/60 rounded-md">
                        <div className={cn(
                          "px-2 py-1 text-xs font-semibold rounded border",
                          he.evidence === "DIRECT EVIDENCE" ? "bg-red-500/10 border-red-500/20 text-red-400" :
                          he.evidence === "HISTORICAL CORRELATION" ? "bg-brand/10 border-brand/20 text-brand-hover" :
                          "bg-blue-500/10 border-blue-500/20 text-blue-400"
                        )}>
                          {he.evidence}
                        </div>
                        <div>
                          <div className="text-sm font-medium text-text-primary">{he.type.replace('_', ' ').toUpperCase()}</div>
                          <div className="text-sm text-text-secondary mt-1">{he.description}</div>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-sm text-text-muted">No historical incidents or failed patches found for these components.</p>
                )}
              </div>
            </div>

            {/* Risk Factors & Recommendations */}
            <div className="bg-background-primary border border-border rounded-lg overflow-hidden">
              <div className="px-5 py-4 border-b border-border bg-background-primary/50">
                <h2 className="text-lg font-medium text-text-primary flex items-center gap-2">
                  <FileText className="w-5 h-5 text-text-secondary" />
                  Deterministic Risk Factors & Recommendation
                </h2>
              </div>
              <div className="p-5 grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <h3 className="text-sm font-medium text-text-secondary mb-3 uppercase tracking-wider">Score Calculation</h3>
                  {data.risk_factors.length > 0 ? (
                    <ul className="space-y-2">
                      {data.risk_factors.map((rf, i) => {
                        const isPlus = rf.startsWith('+');
                        return (
                          <li key={i} className="text-sm flex items-start gap-2">
                            <span className={cn(
                              "font-mono font-medium",
                              isPlus ? "text-brand-hover" : "text-status-success"
                            )}>
                              {rf.split(' ')[0]}
                            </span>
                            <span className="text-text-primary">{rf.substring(rf.indexOf(' ') + 1)}</span>
                          </li>
                        )
                      })}
                    </ul>
                  ) : (
                    <p className="text-sm text-text-muted">Base risk only.</p>
                  )}
                </div>
                <div>
                  <h3 className="text-sm font-medium text-text-secondary mb-3 uppercase tracking-wider">Engineering Review</h3>
                  <div className="bg-blue-900/20 border border-blue-800/50 rounded-md p-4 text-sm text-blue-200/90 leading-relaxed">
                    {data.risk_score >= 70 ? (
                      <>
                        <strong className="text-blue-300 block mb-2">High Scrutiny Required</strong>
                        This change affects critical ML components or has strong historical correlation with past failures. 
                        Ensure thorough regression testing across all affected models before proceeding.
                      </>
                    ) : data.risk_score >= 40 ? (
                      <>
                        <strong className="text-blue-300 block mb-2">Moderate Review Recommended</strong>
                        Changes affect core data pipelines or have multiple downstream dependencies. Validate data schemas and verify unaffected downstream symbols.
                      </>
                    ) : (
                      <>
                        <strong className="text-blue-300 block mb-2">Standard Review</strong>
                        Changes are localized and do not indicate direct impact on core inference logic or historical failures. Standard CI checks should suffice.
                      </>
                    )}
                  </div>
                </div>
              </div>
            </div>

          </div>
        )}
      </div>
    </div>
  );
}
