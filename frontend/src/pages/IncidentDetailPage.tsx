/* eslint-disable @typescript-eslint/no-explicit-any */
import { useState, useEffect, useCallback } from 'react';
import { useParams, Link } from 'react-router-dom';
import { IncidentApi, IncidentDetail, IncidentEvent } from '@/services/api/incidents';
import { ModelsApi, Model } from '@/services/api/models';
import { PullRequestApi, PullRequest } from '@/services/api/pull_requests';
import { DeploymentApi, Deployment } from '@/services/api/deployments';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { Loader2, ArrowLeft, Clock, AlertTriangle, ShieldAlert, CheckCircle, BrainCircuit, ShieldCheck, Link as LinkIcon } from 'lucide-react';

export function IncidentDetailPage() {
  const { incidentId } = useParams<{ incidentId: string }>();
  const [incident, setIncident] = useState<IncidentDetail | null>(null);
  const [model, setModel] = useState<Model | null>(null);
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  const [similar, setSimilar] = useState<any[]>([]);
  const [eligibility, setEligibility] = useState<{eligible: boolean, reason: string} | null>(null);
  
  const [pullRequests, setPullRequests] = useState<PullRequest[]>([]);
  const [deployments, setDeployments] = useState<Deployment[]>([]);

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
      fetch(`http://localhost:8000/api/v1/incidents/${incidentId}/similar`)
        .then(res => res.json())
        .then(data => setSimilar(data || []))
        .catch(() => setSimilar([]));

      PullRequestApi.getPullRequests().then(prs => {
        setPullRequests(prs.filter(pr => pr.incident_id === incidentId));
      }).catch(console.error);

      DeploymentApi.getDeployments().then(deps => {
        setDeployments(deps.filter(dep => dep.incident_id === incidentId));
      }).catch(console.error);
        
      // Fetch eligibility if resolved
      if (inc.status === 'resolved') {
        fetch(`http://localhost:8000/api/v1/incidents/${incidentId}/memory/eligibility`)
          .then(res => res.json())
          .then(data => setEligibility(data))
          .catch(() => setEligibility(null));
      }
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to fetch incident details');
    } finally {
      setLoading(false);
    }
  }, [incidentId]);

  useEffect(() => {
    fetchIncident();
  }, [fetchIncident]);

  const handleAction = async (action: 'acknowledge' | 'startInvestigation' | 'resolve' | 'suppress' | 'learn') => {
    if (!incidentId) return;
    setActionLoading(true);
    try {
      if (action === 'acknowledge') await IncidentApi.acknowledge(incidentId);
      if (action === 'startInvestigation') {
        window.location.href = `/incidents/${incidentId}/investigation`;
        return;
      }
      if (action === 'resolve') await IncidentApi.resolve(incidentId, 'Resolved via UI');
      if (action === 'suppress') await IncidentApi.suppress(incidentId);
      if (action === 'learn') {
        const memRes = await fetch(`http://localhost:8000/api/v1/incidents/${incidentId}/memory`, {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify({
            title: `Resolved: ${incident?.title}`,
            resolution_summary: 'Fix restored model performance successfully'
          })
        });
        if (memRes.ok) {
          const data = await memRes.json();
          // Create regression test automatically
          await fetch(`http://localhost:8000/api/v1/memories/${data.id}/regression-case`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({})
          });
        }
      }
      await fetchIncident();
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : `Failed to ${action} incident`);
    } finally {
      setActionLoading(false);
    }
  };

  if (loading) return <div className="p-12 flex justify-center"><Loader2 className="h-8 w-8 animate-spin text-text-secondary" /></div>;
  if (error) return <div className="p-8 text-status-danger">{error}</div>;
  if (!incident) return <div className="p-8">Incident not found</div>;

  const tabs = ['Overview', 'Investigation', 'Root Cause', 'Proposed Fix', 'Validation', 'Delivery', 'Timeline'];

  return (
    <div className="flex flex-col gap-8">
      <div>
        <Link to="/incidents" className="inline-flex items-center text-sm text-text-secondary hover:text-text-primary mb-4">
          <ArrowLeft className="w-4 h-4 mr-1" /> Back to Incidents
        </Link>
        <div className="flex flex-col md:flex-row md:items-start justify-between gap-4">
          <div>
            <div className="flex items-center gap-3 mb-2">
              <h1 className="text-3xl font-bold tracking-tight text-text-primary">
                Incident <span className="font-mono text-xl text-text-secondary">#{incident.id.substring(0,8)}</span>
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
            {!['resolved', 'suppressed'].includes(incident.status) && (
              <>
                <Button variant="outline" onClick={() => handleAction('suppress')} disabled={actionLoading}>
                  Suppress
                </Button>
                <Button variant="primary" className="bg-status-success hover:bg-status-success/90 text-white" onClick={() => handleAction('resolve')} disabled={actionLoading}>
                  <CheckCircle className="w-4 h-4 mr-2" />
                  Resolve
                </Button>
              </>
            )}
            {incident.status === 'resolved' && eligibility?.eligible && (
               <Button onClick={() => handleAction('learn')} disabled={actionLoading} className="bg-amber-600 hover:bg-amber-700 text-white">
                 <BrainCircuit className="w-4 h-4 mr-2" />
                 Learn From This Incident
               </Button>
            )}
            {incident.status === 'resolved' && eligibility && !eligibility.eligible && eligibility.reason.includes("already exists") && (
               <Button disabled className="bg-amber-500/20 text-amber-500 border-amber-500/50" variant="outline">
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
          <div className="p-6 border border-border rounded-xl bg-surface-50">
            <h2 className="text-lg font-semibold mb-2">Summary</h2>
            <p className="text-text-secondary">{incident.summary || incident.title}</p>
          </div>

          {similar.length > 0 && (
            <div>
              <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
                <LinkIcon className="w-5 h-5 text-amber-500" />
                Similar Incidents
              </h2>
              <div className="grid grid-cols-1 gap-4">
                {similar.map((s, idx) => (
                  <div key={idx} className="p-4 border border-border rounded-xl bg-surface flex justify-between items-center">
                    <div>
                      <div className="flex items-center gap-3 mb-1">
                        <Link to={`/incidents/${s.incident_id}`} className="font-medium hover:underline text-text-primary">
                          {s.title}
                        </Link>
                        <Badge variant="warning" className="border-amber-500/50 text-amber-500 bg-amber-500/10">
                          {s.similarity_score}% Match
                        </Badge>
                      </div>
                      <p className="text-sm text-text-secondary">
                        <span className="font-medium">Previous Fix:</span> {s.resolution_summary || "N/A"}
                      </p>
                      <div className="mt-2 text-xs text-text-muted flex gap-2">
                        {s.reasons.map((r: string, i: number) => (
                          <span key={i} className="bg-surface-50 px-2 py-1 rounded-md">{r}</span>
                        ))}
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
                    <span className="text-2xl font-bold">{s.observed_value !== null ? s.observed_value?.toFixed(4) : 'N/A'}</span>
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
              <div className="p-4 border border-border rounded-xl bg-surface-50 overflow-auto max-h-96">
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
                <div className="absolute -left-[9px] top-1 h-4 w-4 rounded-full border-2 border-surface bg-amber-500" />
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
                <div className="text-sm text-text-muted mb-1">{new Date(dep.created_at).toLocaleString()}</div>
                <div className="font-medium text-text-primary">Deployment Gate Evaluated</div>
                <p className="text-text-secondary mt-1">
                  Status: <Badge variant={dep.status === 'ELIGIBLE' ? 'success' : 'danger'}>{dep.status}</Badge>
                </p>
                {dep.block_reason && <p className="text-status-danger text-sm mt-1">{dep.block_reason}</p>}
                <Link to={`/deployment-gates/${dep.id}`} className="text-brand text-sm hover:underline mt-1 inline-block">View Gate Details</Link>
              </div>
            ))}
          </div>
        </div>
      )}

      {['Investigation', 'Root Cause', 'Proposed Fix', 'Validation', 'Delivery'].includes(activeTab) && (
        <div className="p-16 border border-border border-dashed rounded-xl flex flex-col items-center justify-center text-center">
          <AlertTriangle className="h-10 w-10 text-text-muted mb-4" />
          <h3 className="text-lg font-medium text-text-primary mb-2">
            {activeTab === 'Investigation' && 'Investigation not started'}
            {activeTab === 'Root Cause' && 'Root cause analysis not yet available'}
            {activeTab === 'Proposed Fix' && 'No fix has been generated'}
            {activeTab === 'Validation' && 'No validation run'}
            {activeTab === 'Delivery' && (pullRequests.length > 0 ? (
              <div className="flex flex-col gap-4 mt-4">
                 <Link to={`/pull-requests/${pullRequests[0].id}`} className="px-4 py-2 bg-brand text-white rounded-md hover:bg-brand/90 transition-colors">Go to Pull Request</Link>
              </div>
            ) : 'No delivery artifacts available')}
          </h3>
          <p className="text-text-secondary max-w-sm">
            {activeTab !== 'Delivery' && 'This capability will be enabled in future phases of the incident lifecycle.'}
          </p>
        </div>
      )}
    </div>
  );
}
