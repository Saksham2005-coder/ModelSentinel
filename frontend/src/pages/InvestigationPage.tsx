import { useState, useEffect, useCallback } from 'react';
import { useParams, Link } from 'react-router-dom';
import { InvestigationsApi, InvestigationDetail } from '@/services/api/investigations';
import { IncidentApi, IncidentDetail } from '@/services/api/incidents';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { Loader2, ArrowLeft, Play, AlertCircle, CheckCircle, ShieldAlert, FileText, Activity, Clock, BrainCircuit, Link as LinkIcon } from 'lucide-react';
import { fetchApi } from '@/services/api/client';

interface RelevantFile {
  file_path: string;
  relevance: string;
  reasons: string[];
}

interface RepoContext {
  error?: string;
  relevant_files?: RelevantFile[];
}

interface SimilarIncident {
  incident_id: string;
  incident_key: string;
  title: string;
  similarity_score: number;
  similarity_reasons?: string[];
  resolution?: {
    id: string;
    summary: string;
    effectiveness_score: number;
    validation_status: string;
  };
  resolution_summary?: string;
}

export function InvestigationPage() {
  const { incidentId } = useParams<{ incidentId: string }>();
  const [incident, setIncident] = useState<IncidentDetail | null>(null);
  const [investigation, setInvestigation] = useState<InvestigationDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedHypothesis, setSelectedHypothesis] = useState<string | null>(null);
  const [repoContext, setRepoContext] = useState<RepoContext | null>(null);
  const [similar, setSimilar] = useState<SimilarIncident[]>([]);

  const fetchData = useCallback(async () => {
    if (!incidentId) return;
    try {
      if (!incident) setLoading(true);
      const inc = await IncidentApi.getIncident(incidentId);
      setIncident(inc);
      const invs = await InvestigationsApi.getInvestigations(incidentId);
      if (invs.length > 0) {
        const detail = await InvestigationsApi.getInvestigation(invs[0].id);
        setInvestigation(detail);
      }
      
      try {
        const repoData = await fetchApi<RepoContext>(`/incidents/${incidentId}/repository-context`);
        setRepoContext(repoData);
      } catch (e) {
        console.error("Failed to fetch repository context", e);
      }
      
      try {
        const simData = await fetchApi<SimilarIncident[]>(`/incidents/${incidentId}/similar`);
        setSimilar(simData || []);
      } catch (e) {
        console.error("Failed to fetch similar incidents", e);
      }
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to fetch data');
    } finally {
      setLoading(false);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [incidentId]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  useEffect(() => {
    // Basic SSE polling equivalent if running
    if (investigation?.status === 'running') {
      const interval = setInterval(() => {
        InvestigationsApi.getInvestigation(investigation.id).then(setInvestigation).catch(console.error);
      }, 2000);
      return () => clearInterval(interval);
    }
  }, [investigation?.status, investigation?.id]);

  const handleStart = async () => {
    if (!incidentId) return;
    try {
      let invId = investigation?.id;
      if (!invId) {
        const newInv = await InvestigationsApi.createInvestigation(incidentId);
        invId = newInv.id;
      }
      await InvestigationsApi.startInvestigation(invId);
      fetchData();
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to start investigation');
    }
  };

  if (loading) return <div className="p-12 flex justify-center"><Loader2 className="h-8 w-8 animate-spin text-brand" /></div>;
  if (error) return <div className="p-8 text-status-danger">{error}</div>;
  if (!incident) return <div className="p-8">Incident not found</div>;

  return (
    <div className="flex flex-col h-[calc(100vh-8rem)]">
      <div className="mb-4">
        <Link to={`/incidents/${incidentId || ''}`} className="inline-flex items-center text-sm text-text-secondary hover:text-text-primary mb-2">
          <ArrowLeft className="w-4 h-4 mr-1" /> Back to Incident {incidentId ? incidentId.substring(0,8) : ''}
        </Link>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <h1 className="text-2xl font-semibold tracking-tight">AI Investigation</h1>
            <Badge variant={investigation?.status === 'completed' ? 'success' : investigation?.status === 'running' ? 'warning' : 'default'}>
              {investigation?.status.toUpperCase() || 'NOT STARTED'}
            </Badge>
          </div>
          {(!investigation || investigation.status === 'queued' || investigation.status === 'failed' || investigation.status === 'completed') && (
            <Button onClick={handleStart} variant="primary" className="gap-2">
              <Play className="w-4 h-4" />
              {investigation?.status === 'completed' ? 'Re-run Investigation' : 'Start Investigation'}
            </Button>
          )}
        </div>
      </div>

      <div className="flex flex-1 gap-6 overflow-hidden">
        {/* LEFT: Incident Context */}
        <div className="w-1/4 flex flex-col gap-4 overflow-y-auto border border-border rounded-xl bg-surface p-4">
          <h2 className="font-semibold text-lg border-b border-border pb-2">Incident Context</h2>
          <div>
            <div className="text-sm text-text-muted mb-1">Title</div>
            <div className="font-medium text-text-primary">{incident.title}</div>
          </div>
          <div>
            <div className="text-sm text-text-muted mb-1">Severity</div>
            <Badge variant={incident.severity === 'critical' ? 'danger' : 'warning'}>{incident.severity}</Badge>
          </div>
          <div>
            <div className="text-sm text-text-muted mb-1">Category</div>
            <div className="capitalize">{incident.category.replace('_', ' ')}</div>
          </div>
          <div>
            <h3 className="font-medium mb-2 mt-4 flex items-center gap-2"><ShieldAlert className="w-4 h-4" /> Triggering Signals</h3>
            <div className="space-y-3">
              {incident.signals.map(s => (
                <div key={s.id} className="p-2 border border-border rounded bg-surface-50 text-sm">
                  <div className="font-medium">{s.signal_name}</div>
                  <div className="text-xs text-text-secondary mt-1">Value: {s.observed_value?.toFixed(3)} (Threshold: {s.threshold})</div>
                </div>
              ))}
            </div>
          </div>
          
          {repoContext && !repoContext.error && (
            <div className="mt-4 pt-4 border-t border-border">
              <h3 className="font-medium mb-3 flex items-center gap-2 text-brand">
                <FileText className="w-4 h-4" /> Code Relevance
              </h3>
              {(repoContext.relevant_files?.length ?? 0) > 0 ? (
                <div className="space-y-3">
                  {repoContext.relevant_files!.map((file: RelevantFile, i: number) => (
                    <div key={i} className="p-2 border border-border-strong rounded bg-background-secondary/50 text-xs">
                      <div className="font-mono font-medium text-text-primary mb-1 truncate" title={file.file_path}>
                        {file.file_path.split('/').pop()}
                      </div>
                      <div className="flex gap-1 mb-1">
                        <Badge variant={file.relevance === 'High' ? 'danger' : file.relevance === 'Medium' ? 'warning' : 'default'} className="text-[9px] px-1 py-0 h-4">
                          {file.relevance} Relevancy
                        </Badge>
                      </div>
                      <div className="text-text-secondary mt-2 space-y-1">
                        {file.reasons.map((r: string, j: number) => (
                          <div key={j} className="flex gap-1 items-start">
                            <span className="text-brand mt-0.5">•</span>
                            <span>{r}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-sm text-text-muted italic">No direct code relevance found.</div>
              )}
            </div>
          )}
          
          {similar.length > 0 && (
            <div className="mt-4 pt-4 border-t border-border">
              <h3 className="font-medium mb-3 flex items-center gap-2 text-brand">
                <BrainCircuit className="w-4 h-4" /> Historical Context
              </h3>
              <div className="space-y-3">
                {similar.slice(0, 3).map((s, idx) => (
                  <div key={idx} className="p-3 border border-border rounded bg-surface-50 text-xs flex flex-col gap-2">
                    <div className="flex justify-between items-start">
                      <Link to={`/incidents/${s.incident_id}`} className="font-medium text-text-primary hover:underline" title={s.title}>
                        {s.title.substring(0, 40)}{s.title.length > 40 ? '...' : ''}
                      </Link>
                      <Badge variant="warning" className="text-[10px] px-1 py-0 h-4 border-brand/50 text-brand bg-brand/10">
                        {s.similarity_score}%
                      </Badge>
                    </div>
                    {s.resolution && s.resolution.effectiveness_score > 0 && (
                      <div className="flex items-center gap-1 mt-1">
                        <Badge variant={(s.resolution?.effectiveness_score ?? 0) > 70 ? "success" : "warning"} className="text-[10px] px-1 py-0 h-4">
                          {s.resolution?.effectiveness_score ?? 0} Effectiveness
                        </Badge>
                      </div>
                    )}
                    <div className="text-text-secondary mt-1">
                      <span className="font-medium text-text-muted">Fix:</span> {s.resolution?.summary || s.resolution_summary || "N/A"}
                    </div>
                    <div className="flex flex-wrap gap-1 mt-1">
                      {s.similarity_reasons && s.similarity_reasons.slice(0, 2).map((r: string, i: number) => (
                         <span key={i} className="bg-surface border border-border px-1 py-0.5 rounded text-[10px] text-text-muted">{r.replace(/^\+\d+\s/, '')}</span>
                      ))}
                    </div>
                    <div className="flex gap-2 text-[10px] mt-1 border-t border-border pt-1">
                      <Link to={`/incidents/${s.incident_id}`} className="text-brand hover:underline flex items-center gap-1">
                        <LinkIcon className="w-3 h-3" /> Incident
                      </Link>
                      <Link to={`/incidents/${s.incident_id}?tab=Validation`} className="text-brand hover:underline flex items-center gap-1">
                        <LinkIcon className="w-3 h-3" /> Validation
                      </Link>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* CENTER: Timeline & Hypotheses */}
        <div className="w-2/4 flex flex-col gap-4 overflow-y-auto border border-border rounded-xl bg-surface p-4">
          <h2 className="font-semibold text-lg border-b border-border pb-2">Investigation Workspace</h2>
          
          {!investigation ? (
            <div className="flex-1 flex flex-col items-center justify-center text-text-secondary">
              <Activity className="w-12 h-12 mb-4 opacity-50" />
              <p>No investigation found for this incident.</p>
              <Button onClick={handleStart} className="mt-4">Start Investigation</Button>
            </div>
          ) : (
            <>
              {investigation.summary && (
                <div className="p-4 bg-brand/10 border border-brand/20 rounded-lg">
                  <h3 className="font-semibold text-brand mb-1">Most Supported Explanation</h3>
                  <p className="text-sm">{investigation.summary}</p>
                </div>
              )}

              {investigation.hypotheses.length > 0 && (
                <div className="space-y-3 mt-4">
                  <h3 className="font-semibold flex items-center gap-2">Hypotheses Considered</h3>
                  {investigation.hypotheses.map(h => (
                    <div 
                      key={h.id} 
                      onClick={() => setSelectedHypothesis(h.id)}
                      className={`p-4 border rounded-lg cursor-pointer transition-colors ${selectedHypothesis === h.id ? 'border-brand bg-brand/5' : 'border-border bg-surface-50 hover:border-text-muted'}`}
                    >
                      <div className="flex justify-between items-start mb-2">
                        <div className="font-medium">{h.title}</div>
                        <Badge variant={h.status === 'supported' ? 'success' : h.status === 'rejected' ? 'danger' : 'warning'}>{h.status}</Badge>
                      </div>
                      <p className="text-sm text-text-secondary mb-3">{h.description}</p>
                      <div className="flex gap-4 text-xs">
                        <span className="flex items-center gap-1">
                          <CheckCircle className="w-3 h-3 text-status-success" /> {h.evidence_items.filter(e => e.relationship_type === 'supports').length} Supporting
                        </span>
                        <span className="flex items-center gap-1">
                          <AlertCircle className="w-3 h-3 text-status-danger" /> {h.evidence_items.filter(e => e.relationship_type === 'contradicts').length} Contradicting
                        </span>
                        <span className="text-text-muted">Strength: {h.evidence_strength}</span>
                      </div>
                    </div>
                  ))}
                </div>
              )}

              <div className="mt-8 border-t border-border pt-4">
                <h3 className="font-semibold mb-4 flex items-center gap-2"><Clock className="w-4 h-4" /> Timeline</h3>
                <div className="space-y-4 ml-2 border-l-2 border-border pl-4">
                  {investigation.events.map(e => (
                    <div key={e.id} className="relative">
                      <div className="absolute -left-[21px] top-1 h-2.5 w-2.5 rounded-full bg-brand" />
                      <div className="text-xs text-text-muted">{new Date(e.created_at).toLocaleTimeString()}</div>
                      <div className="font-medium text-sm">{e.title}</div>
                      <div className="text-xs text-text-secondary mt-0.5">{e.message}</div>
                    </div>
                  ))}
                </div>
              </div>
            </>
          )}
        </div>

        {/* RIGHT: Evidence */}
        <div className="w-1/4 flex flex-col gap-4 overflow-y-auto border border-border rounded-xl bg-surface p-4">
          <h2 className="font-semibold text-lg border-b border-border pb-2 flex items-center gap-2"><FileText className="w-4 h-4" /> Evidence</h2>
          
          {!selectedHypothesis ? (
            <div className="flex-1 flex items-center justify-center text-sm text-text-secondary text-center p-4">
              Select a hypothesis to view its linked evidence.
            </div>
          ) : (
            <div className="space-y-4">
              {investigation?.hypotheses.find(h => h.id === selectedHypothesis)?.evidence_items.map(ev => (
                <div key={ev.id} className="p-3 border border-border rounded-lg bg-surface-50 text-sm">
                  <div className="flex justify-between items-start mb-2">
                    <span className="font-medium text-text-primary">{ev.title}</span>
                    <Badge variant={ev.relationship_type === 'supports' ? 'success' : ev.relationship_type === 'contradicts' ? 'danger' : 'default'} className="text-[10px] px-1.5 py-0">
                      {ev.relationship_type.toUpperCase()}
                    </Badge>
                  </div>
                  <div className="text-xs text-text-secondary mb-2">{ev.explanation}</div>
                  <div className="p-2 bg-surface border border-border rounded font-mono text-xs overflow-x-auto text-text-muted">
                    {JSON.stringify(ev.value_json, null, 2)}
                  </div>
                  <div className="text-[10px] text-text-muted mt-2 uppercase tracking-wide">
                    Source: {ev.source_type}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
