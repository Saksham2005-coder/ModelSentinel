/* eslint-disable @typescript-eslint/no-explicit-any */
import { useState, useEffect, useCallback } from 'react';
import { useParams, Link } from 'react-router-dom';
import { IncidentApi, IncidentDetail, IncidentEvent } from '@/services/api/incidents';
import { ModelsApi, Model } from '@/services/api/models';
import { PullRequestApi, PullRequest } from '@/services/api/pull_requests';
import { DeploymentApi, Deployment } from '@/services/api/deployments';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { Loader2, ArrowLeft, Clock, AlertTriangle, ShieldAlert, CheckCircle, BrainCircuit, ShieldCheck, Link as LinkIcon, Activity } from 'lucide-react';
import { ReliabilityApi, CausalGraph } from '@/services/api/reliability';
import { SimpleGraphRenderer } from '@/components/reliability/CausalGraphModal';
import { workflowsApi, WorkflowRun } from '@/services/api/workflows';
import { fetchApi } from '@/services/api/client';
import { CopyButton } from '@/components/ui/CopyButton';
import { LoadingState } from '@/components/ui/LoadingState';
import { useToast } from '@/contexts/ToastContext';

export function IncidentDetailPage() {
  const { incidentId } = useParams<{ incidentId: string }>();
  const [incident, setIncident] = useState<IncidentDetail | null>(null);
  const [model, setModel] = useState<Model | null>(null);
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const { addToast } = useToast();
  
  const [similar, setSimilar] = useState<any[]>([]);
  const [eligibility, setEligibility] = useState<{eligible: boolean, reason: string} | null>(null);
  
  const [pullRequests, setPullRequests] = useState<PullRequest[]>([]);
  const [deployments, setDeployments] = useState<Deployment[]>([]);
  const [causalGraph, setCausalGraph] = useState<CausalGraph | null>(null);
  const [causalGraphLoading, setCausalGraphLoading] = useState(false);
  const [workflows, setWorkflows] = useState<WorkflowRun[]>([]);

  const [activeTab, setActiveTab] = useState('Overview');

  const fetchIncident = useCallback(async () => {
    if (!incidentId) return;
    try {
      setLoading(true);
      const inc = await IncidentApi.getIncident(incidentId);
      setIncident(inc);
      const mod = await ModelsApi.getModel(inc.model_id);
      setModel(mod);
      
      // Fetch similar incidents
      fetchApi<any[]>(`/incidents/${incidentId}/similar`)
        .then(data => setSimilar(data || []))
        .catch(() => setSimilar([]));

      PullRequestApi.getPullRequests().then(prs => {
        setPullRequests(prs.filter(pr => pr.incident_id === incidentId));
      }).catch(console.error);

      DeploymentApi.getDeployments().then(deps => {
        setDeployments(deps.filter(dep => dep.incident_id === incidentId));
      }).catch(console.error);

      workflowsApi.listWorkflows().then(wfs => {
        setWorkflows(wfs.filter(wf => wf.entity_type === 'incident' && wf.entity_id === incidentId));
      }).catch(console.error);
        
      // Fetch eligibility if resolved
      if (inc.status === 'resolved') {
        fetchApi<{eligible: boolean, reason: string}>(`/incidents/${incidentId}/memory/eligibility`)
          .then(data => setEligibility(data))
          .catch(() => setEligibility(null));
      }
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Failed to fetch incident details';
      setError(msg);
      addToast('error', msg);
    } finally {
      setLoading(false);
    }
  }, [incidentId, addToast]);

  useEffect(() => {
    fetchIncident();
  }, [fetchIncident]);

  useEffect(() => {
    if (activeTab === 'Reliability Timeline' && incidentId && model) {
      setCausalGraphLoading(true);
      ReliabilityApi.getIncidentGraphByIncidentId(model.id, incidentId)
        .then(graph => setCausalGraph(graph))
        .catch(console.error)
        .finally(() => setCausalGraphLoading(false));
    }
  }, [activeTab, incidentId, model]);

  const handleAction = async (action: 'acknowledge' | 'startInvestigation' | 'resolve' | 'suppress' | 'learn') => {
    if (!incidentId) return;
    setActionLoading(true);
    try {
      if (action === 'acknowledge') {
        await IncidentApi.acknowledge(incidentId);
        addToast('success', 'Incident acknowledged.');
      }
      if (action === 'startInvestigation') {
        window.location.href = `/incidents/${incidentId}/investigation`;
        return;
      }
      if (action === 'resolve') {
        await IncidentApi.resolve(incidentId, 'Resolved via UI');
        addToast('success', 'Incident resolved.');
      }
      if (action === 'suppress') {
        await IncidentApi.suppress(incidentId);
        addToast('info', 'Incident suppressed.');
      }
      if (action === 'learn') {
        const data = await fetchApi<any>(`/incidents/${incidentId}/memory`, {
          method: 'POST',
          body: JSON.stringify({
            title: `Resolved: ${incident?.title}`,
            resolution_summary: 'Fix restored model performance successfully'
          })
        });
        if (data) {
          // Create regression test automatically
          await fetchApi(`/memories/${data.id}/regression-case`, {
            method: 'POST',
            body: JSON.stringify({})
          });
          addToast('success', 'Learned from incident and created regression test.');
        }
      }
      await fetchIncident();
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : `Failed to ${action} incident`;
      setError(msg);
      addToast('error', msg);
    } finally {
      setActionLoading(false);
    }
  };

  const handleStartWorkflow = async () => {
    if (!incidentId || !incident) return;
    setActionLoading(true);
    try {
      const wf = await workflowsApi.createWorkflow(`Recovery ${incident.id.substring(0,8)}`, 'INCIDENT_RECOVERY', 'incident', incidentId);
      await workflowsApi.startWorkflow(wf.id);
      addToast('success', 'Recovery workflow started.');
      await fetchIncident();
      window.location.href = `/workflows/${wf.id}`;
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Failed to start workflow';
      setError(msg);
      addToast('error', msg);
      setActionLoading(false);
    }
  };

  if (loading) return <LoadingState text="Loading incident details..." className="py-20" />;
  if (error) return <div className="p-8 text-status-danger">{error}</div>;
  if (!incident) return <div className="p-8">Incident not found</div>;

  if (!incident) return <div className="p-8">Incident not found</div>;

  const tabs = ['Overview', 'Investigation', 'Proposed Fix', 'Validation', 'Timeline', 'Reliability Timeline', 'Workflows'];

  return (
    <div className="flex flex-col gap-8">
      <div>
        <Link to="/incidents" className="inline-flex items-center text-sm text-text-secondary hover:text-text-primary mb-4">
          <ArrowLeft className="w-4 h-4 mr-1" /> Back to Incidents
        </Link>
        <div className="flex flex-col md:flex-row md:items-start justify-between gap-4">
          <div>
            <div className="flex items-center gap-3 mb-2">
              <h1 className="text-2xl font-semibold tracking-tight tracking-tight text-text-primary flex items-center gap-2">
                Incident <span className="font-mono text-xl text-text-secondary">#{incident.id.substring(0,8)}</span>
                <CopyButton value={incident.id} label="Copy incident ID" />
              </h1>
              <Badge variant={incident.severity === 'critical' ? 'danger' : 'warning'} className="uppercase">
                {incident.severity}
              </Badge>
              <Badge variant="default" className="uppercase">{incident.status.replace('_', ' ')}</Badge>
            </div>
            <div className="text-text-secondary flex items-center gap-2">
              <span className="font-medium text-text-primary">{model?.name || 'Unknown Model'}</span>
              <span>•</span>
              <span>Detected: {new Date(incident.detected_at).toLocaleString()}</span>
            </div>
          </div>
          
          <div className="flex gap-2">
            {incident.status === 'detected' && (
              <Button variant="outline" onClick={() => handleAction('acknowledge')} disabled={actionLoading}>
                Acknowledge
              </Button>
            )}
            {['detected', 'acknowledged'].includes(incident.status) && (
              <Button onClick={() => handleAction('startInvestigation')} disabled={actionLoading}>
                Start Investigation
              </Button>
            )}
            {workflows.length === 0 && (
              <Button variant="outline" onClick={handleStartWorkflow} disabled={actionLoading} className="border-brand text-brand hover:bg-brand hover:text-text-primary">
                Start Recovery Workflow
              </Button>
            )}
            {!['resolved', 'suppressed'].includes(incident.status) && (
              <>
                <Button variant="outline" onClick={() => handleAction('suppress')} disabled={actionLoading}>
                  Suppress
                </Button>
                <Button variant="primary" className="bg-status-success hover:bg-status-success/90 text-text-primary" onClick={() => handleAction('resolve')} disabled={actionLoading}>
                  <CheckCircle className="w-4 h-4 mr-2" />
                  Resolve
                </Button>
              </>
            )}
            {incident.status === 'resolved' && eligibility?.eligible && (
               <Button onClick={() => handleAction('learn')} disabled={actionLoading} className="bg-status-warning hover:bg-status-warning/90 text-background-base text-text-primary">
                 <BrainCircuit className="w-4 h-4 mr-2" />
                 Learn From This Incident
               </Button>
            )}
            {incident.status === 'resolved' && eligibility && !eligibility.eligible && eligibility.reason.includes("already exists") && (
               <Button disabled className="bg-brand/20 text-brand border-brand/50" variant="outline">
                 <ShieldCheck className="w-4 h-4 mr-2" />
                 Regression Coverage Created
               </Button>
            )}
          </div>
        </div>
      </div>

      <div className="flex gap-6 border-b border-border">
        {tabs.map(t => (
          <button
            key={t}
            className={`pb-3 text-sm font-medium transition-colors border-b-2 ${
              activeTab === t ? 'border-brand text-brand' : 'border-transparent text-text-secondary hover:text-text-primary'
            }`}
            onClick={() => {
              if (t === 'Investigation') {
                window.location.href = `/incidents/${incidentId}/investigation`;
              } else if (t === 'Proposed Fix') {
                window.location.href = `/incidents/${incidentId}/fix`;
              } else if (t === 'Validation') {
                window.location.href = `/incidents/${incidentId}/validation`;
              } else {
                setActiveTab(t);
              }
            }}
          >
            {t}
          </button>
        ))}
      </div>

      {activeTab === 'Overview' && (
        <div className="space-y-8 animate-in fade-in duration-500">
          <div className="p-6 border border-border rounded-xl bg-surface">
            <h2 className="text-lg font-semibold mb-2">Summary</h2>
            <p className="text-text-secondary">{incident.summary || incident.title}</p>
          </div>

          {similar.length > 0 && (
            <div>
              <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
                <BrainCircuit className="w-5 h-5 text-brand" />
                Historical Resolution Intelligence
              </h2>
              <div className="grid grid-cols-1 gap-4">
                {similar.map((s, idx) => (
                  <div key={idx} className="p-4 border border-border rounded-xl bg-surface flex flex-col gap-3">
                    <div className="flex justify-between items-start">
                      <div>
                        <div className="flex items-center gap-3 mb-1">
                          <Link to={`/incidents/${s.incident_id}`} className="font-medium hover:underline text-text-primary text-lg">
                            {s.title}
                          </Link>
                          <Badge variant="warning" className="border-brand/50 text-brand bg-brand/10">
                            {s.similarity_score}% Match
                          </Badge>
                          {s.resolution?.effectiveness_score > 0 && (
                            <Badge variant={s.resolution.effectiveness_score > 70 ? "success" : "warning"} className="ml-2">
                              {s.resolution.effectiveness_score} Effectiveness
                            </Badge>
                          )}
                        </div>
                        <p className="text-sm text-text-secondary">
                          <span className="font-medium">Previous Fix:</span> {s.resolution?.summary || s.resolution_summary || "N/A"}
                        </p>
                      </div>
                    </div>
                    
                    <div>
                      <p className="text-xs font-semibold text-text-muted uppercase tracking-wider mb-2">Why it matched</p>
                      <div className="text-xs text-text-secondary flex flex-wrap gap-2">
                        {s.similarity_reasons && s.similarity_reasons.map((r: string, i: number) => (
                          <span key={i} className="bg-surface border border-border px-2 py-1 rounded-md">{r}</span>
                        ))}
                      </div>
                    </div>
                    
                    <div>
                       <p className="text-xs font-semibold text-text-muted uppercase tracking-wider mb-2 flex items-center gap-1">
                         <LinkIcon className="w-3 h-3" /> Provenance
                       </p>
                       <div className="flex gap-4 text-sm">
                         <Link to={`/incidents/${s.incident_id}`} className="text-brand hover:underline flex items-center gap-1">
                           Original Incident
                         </Link>
                         <Link to={`/incidents/${s.incident_id}?tab=Validation`} className="text-brand hover:underline flex items-center gap-1">
                           Validation Report
                         </Link>
                       </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          <div>
            <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
              <ShieldAlert className="w-5 h-5 text-status-warning" />
              Key Signals
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {incident.signals.map(s => (
                <div key={s.id} className="p-4 border border-border rounded-xl bg-surface">
                  <div className="text-xs text-text-muted uppercase tracking-wider mb-1 font-semibold">{s.source_type.replace('_', ' ')}</div>
                  <div className="font-medium mb-2">{s.signal_name}</div>
                  <div className="flex items-baseline gap-2 mb-2">
                    <span className="text-2xl font-semibold tracking-tight">{s.observed_value !== null ? s.observed_value?.toFixed(4) : 'N/A'}</span>
                    {s.threshold !== null && (
                      <span className="text-sm text-text-secondary">
                        (Threshold: {s.comparison} {s.threshold})
                      </span>
                    )}
                  </div>
                  <p className="text-sm text-text-secondary">{s.explanation}</p>
                </div>
              ))}
            </div>
          </div>
          
          {incident.evidence && (
            <div>
              <h2 className="text-xl font-semibold mb-4">Evidence Snapshot</h2>
              <div className="p-4 border border-border rounded-xl bg-surface overflow-auto max-h-96">
                <pre className="text-xs text-text-secondary">
                  {JSON.stringify(incident.evidence.snapshot, null, 2)}
                </pre>
              </div>
            </div>
          )}
        </div>
      )}

      {activeTab === 'Timeline' && (
        <div className="space-y-6">
          <h2 className="text-xl font-semibold flex items-center gap-2">
            <Clock className="w-5 h-5" />
            Incident Timeline
          </h2>
          <div className="border-l-2 border-border ml-3 space-y-8 py-4">
            {/* Standard Events */}
            {incident.events.map((e: IncidentEvent) => (
              <div key={e.id} className="relative pl-8">
                <div className="absolute -left-[9px] top-1 h-4 w-4 rounded-full border-2 border-surface bg-brand" />
                <div className="text-sm text-text-muted mb-1">{new Date(e.created_at).toLocaleString()}</div>
                <div className="font-medium text-text-primary capitalize">{e.event_type.replace('_', ' ')}</div>
                <p className="text-text-secondary mt-1">{e.message}</p>
              </div>
            ))}
            
            {/* Phase 10 Synthesized Events */}
            {pullRequests.map(pr => (
              <div key={pr.id} className="relative pl-8">
                <div className="absolute -left-[9px] top-1 h-4 w-4 rounded-full border-2 border-surface bg-brand" />
                <div className="text-sm text-text-muted mb-1">{new Date(pr.created_at).toLocaleString()}</div>
                <div className="font-medium text-text-primary">Pull Request Created</div>
                <p className="text-text-secondary mt-1">
                  Branch <span className="font-mono text-xs">{pr.branch_name}</span> generated for patch validation.
                </p>
                <Link to={`/pull-requests/${pr.id}`} className="text-brand text-sm hover:underline mt-1 inline-block">View Pull Request</Link>
              </div>
            ))}
            {deployments.map(dep => (
              <div key={dep.id} className="relative pl-8">
                <div className="absolute -left-[9px] top-1 h-4 w-4 rounded-full border-2 border-surface bg-purple-500" />
                <div className="text-sm text-text-muted mb-1">{new Date(dep.updated_at || dep.created_at).toLocaleString()}</div>
                <div className="font-medium text-text-primary">Deployment Status: {dep.status}</div>
                <p className="text-text-secondary mt-1">
                  Current State: <Badge variant={['ELIGIBLE', 'HEALTHY'].includes(dep.status) ? 'success' : ['BLOCKED', 'FAILED'].includes(dep.status) ? 'danger' : 'warning'}>{dep.status}</Badge>
                </p>
                {dep.environment && <p className="text-xs text-text-secondary mt-1">Environment: {dep.environment}</p>}
                {dep.block_reason && <p className="text-status-danger text-sm mt-1">{dep.block_reason}</p>}
                <Link to={`/deployment-gates/${dep.id}`} className="text-brand text-sm hover:underline mt-1 inline-block">View Deployment Details</Link>
              </div>
            ))}
          </div>
        </div>
      )}

      {activeTab === 'Reliability Timeline' && (
        <div className="space-y-6">
          <h2 className="text-xl font-semibold flex items-center gap-2">
            <Activity className="w-5 h-5 text-brand" />
            Causal Incident Graph
          </h2>
          <div className="p-8 border border-border rounded-xl bg-surface flex justify-center overflow-auto max-h-[800px] bg-[url('data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSI0MCIgaGVpZ2h0PSI0MCI+CjxyZWN0IHdpZHRoPSI0MCIgaGVpZ2h0PSI0MCIgZmlsbD0ibm9uZSIvPgo8Y2lyY2xlIGN4PSIyMCIgY3k9IjIwIiByPSIxIiBmaWxsPSJyZ2JhKDI1NSwgMjU1LCAyNTUsIDAuMDUpIi8+Cjwvc3ZnPg==')]">
            {causalGraphLoading ? (
              <div className="flex justify-center items-center h-64 text-text-secondary"><Loader2 className="h-8 w-8 animate-spin" /></div>
            ) : causalGraph && causalGraph.nodes.length > 0 ? (
              <SimpleGraphRenderer graph={causalGraph} />
            ) : (
              <div className="text-text-muted">No causal connections found for this incident.</div>
            )}
          </div>
        </div>
      )}

      {activeTab === 'Workflows' && (
        <div className="space-y-6">
          <h2 className="text-xl font-semibold flex items-center gap-2">
            <Activity className="w-5 h-5 text-brand" />
            Reliability Workflows
          </h2>
          {workflows.length === 0 ? (
             <div className="p-16 border border-border border-dashed rounded-xl flex flex-col items-center justify-center text-center">
                <AlertTriangle className="h-10 w-10 text-text-muted mb-4" />
                <h3 className="text-lg font-medium text-text-primary mb-2">No active workflows</h3>
                <Button onClick={handleStartWorkflow} disabled={actionLoading} className="mt-4 bg-brand hover:bg-brand/90 text-text-primary">
                  Start Recovery Workflow
                </Button>
             </div>
          ) : (
            <div className="space-y-4">
              {workflows.map(wf => (
                <div key={wf.id} className="p-4 border border-border rounded-xl bg-surface flex justify-between items-center">
                  <div>
                    <h3 className="font-medium text-text-primary">{wf.name}</h3>
                    <p className="text-sm text-text-secondary">Status: {wf.status} | ID: {wf.id}</p>
                  </div>
                  <Link to={`/workflows/${wf.id}`} className="px-4 py-2 bg-background-secondary text-text-primary rounded-lg hover:bg-background-elevated transition-colors">
                    View Workflow
                  </Link>
                </div>
              ))}
            </div>
          )}
        </div>
      )}


    </div>
  );
}
