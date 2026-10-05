import { useState, useEffect, useCallback } from 'react';
import { useParams, Link } from 'react-router-dom';
import { IncidentApi, IncidentDetail, IncidentEvent } from '@/services/api/incidents';
import { ModelsApi, Model } from '@/services/api/models';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { Loader2, ArrowLeft, Clock, AlertTriangle, ShieldAlert, CheckCircle } from 'lucide-react';

export function IncidentDetailPage() {
  const { incidentId } = useParams<{ incidentId: string }>();
  const [incident, setIncident] = useState<IncidentDetail | null>(null);
  const [model, setModel] = useState<Model | null>(null);
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  const [activeTab, setActiveTab] = useState('Overview');

  const fetchIncident = useCallback(async () => {
    if (!incidentId) return;
    try {
      setLoading(true);
      const inc = await IncidentApi.getIncident(incidentId);
      setIncident(inc);
      const mod = await ModelsApi.getModel(inc.model_id);
      setModel(mod);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to fetch incident details');
    } finally {
      setLoading(false);
    }
  }, [incidentId]);

  useEffect(() => {
    fetchIncident();
  }, [fetchIncident]);

  const handleAction = async (action: 'acknowledge' | 'startInvestigation' | 'resolve' | 'suppress') => {
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

  const tabs = ['Overview', 'Investigation', 'Root Cause', 'Proposed Fix', 'Validation', 'Timeline'];

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
        <div className="space-y-8">
          <div className="p-6 border border-border rounded-xl bg-surface-50">
            <h2 className="text-lg font-semibold mb-2">Summary</h2>
            <p className="text-text-secondary">{incident.summary || incident.title}</p>
          </div>

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
            {incident.events.map((e: IncidentEvent) => (
              <div key={e.id} className="relative pl-8">
                <div className="absolute -left-[9px] top-1 h-4 w-4 rounded-full border-2 border-surface bg-brand" />
                <div className="text-sm text-text-muted mb-1">{new Date(e.created_at).toLocaleString()}</div>
                <div className="font-medium text-text-primary capitalize">{e.event_type.replace('_', ' ')}</div>
                <p className="text-text-secondary mt-1">{e.message}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {['Investigation', 'Root Cause', 'Proposed Fix', 'Validation'].includes(activeTab) && (
        <div className="p-16 border border-border border-dashed rounded-xl flex flex-col items-center justify-center text-center">
          <AlertTriangle className="h-10 w-10 text-text-muted mb-4" />
          <h3 className="text-lg font-medium text-text-primary mb-2">
            {activeTab === 'Investigation' && 'Investigation not started'}
            {activeTab === 'Root Cause' && 'Root cause analysis not yet available'}
            {activeTab === 'Proposed Fix' && 'No fix has been generated'}
            {activeTab === 'Validation' && 'No validation run'}
          </h3>
          <p className="text-text-secondary max-w-sm">
            This capability will be enabled in future phases of the incident lifecycle.
          </p>
        </div>
      )}
    </div>
  );
}
