import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { CheckCircle, XCircle, AlertCircle, Clock, Loader2, PlayCircle, Info } from 'lucide-react';
import { fetchApi } from '@/services/api/client';

interface ValidationRun {
  id: string;
  status: string;
  verdict: string;
  summary: string;
  started_at: string;
  completed_at: string;
}

interface ValidationCheck {
  id: string;
  check_type: string;
  name: string;
  status: string;
  summary: string;
}

interface ValidationMetric {
  id: string;
  metric_name: string;
  baseline_value: number;
  current_value: number;
  patched_value: number;
  delta: number;
  status: string;
  segment_name: string;
}

export const ValidationWorkspacePage: React.FC = () => {
  const { incidentId } = useParams<{ incidentId: string }>();
  const [runs, setRuns] = useState<ValidationRun[]>([]);
  const [activeRunId, setActiveRunId] = useState<string | null>(null);
  const [checks, setChecks] = useState<ValidationCheck[]>([]);
  const [metrics, setMetrics] = useState<ValidationMetric[]>([]);
  const [loading, setLoading] = useState(false);
  const [triggering, setTriggering] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchValidationData();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [incidentId]);

  const fetchValidationData = async () => {
    setLoading(true);
    setError(null);
    try {
      // Find patch for this incident
      // For this demo, let's fetch the investigations, then patch
      const invResponse = await fetchApi(`/incidents/${incidentId}/investigations`) as Array<{id: string, status: string}>;
      const activeInv = invResponse.find(i => i.status === 'completed' || i.status === 'in_progress');
      if (!activeInv) {
        throw new Error('No active investigation found.');
      }
      const patchResponse = await fetchApi(`/investigations/${activeInv.id}/patches`) as Array<{id: string, status: string}>;
      const approvedPatch = patchResponse.find(p => p.status === 'approved' || p.status === 'merged');
      if (!approvedPatch) {
        throw new Error('No approved patch found for validation.');
      }

      const runsResponse = await fetchApi(`/patches/${approvedPatch.id}/validation`) as ValidationRun[];
      setRuns(runsResponse);
      
      if (runsResponse.length > 0) {
        setActiveRunId(runsResponse[0].id);
        await fetchRunDetails(runsResponse[0].id);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load validation data.');
    } finally {
      setLoading(false);
    }
  };

  const fetchRunDetails = async (runId: string) => {
    try {
      const checksData = await fetchApi(`/validation/${runId}/checks`) as ValidationCheck[];
      setChecks(checksData);
      const metricsData = await fetchApi(`/validation/${runId}/metrics`) as ValidationMetric[];
      setMetrics(metricsData);
    } catch (err) {
      console.error(err);
    }
  };

  const startValidation = async () => {
    setTriggering(true);
    setError(null);
    try {
      const invResponse = await fetchApi(`/incidents/${incidentId}/investigations`) as Array<{id: string, status: string}>;
      const activeInv = invResponse.find(i => i.status === 'completed' || i.status === 'in_progress');
      const patchResponse = await fetchApi(`/investigations/${activeInv?.id}/patches`) as Array<{id: string, status: string}>;
      const approvedPatch = patchResponse.find(p => p.status === 'approved' || p.status === 'merged');
      
      if (approvedPatch) {
        await fetchApi(`/patches/${approvedPatch.id}/validation`, {
          method: 'POST'
        });
      }
      setTimeout(() => {
        fetchValidationData();
      }, 2000); // Polling for demo
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to start validation');
    } finally {
      setTriggering(false);
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'passed':
      case 'recovered':
      case 'PASS':
        return <CheckCircle className="w-5 h-5 text-emerald-500" />;
      case 'failed':
      case 'regressed':
      case 'FAIL':
        return <XCircle className="w-5 h-5 text-rose-500" />;
      case 'warning':
      case 'PARTIAL':
        return <AlertCircle className="w-5 h-5 text-brand" />;
      case 'skipped':
      case 'INCONCLUSIVE':
        return <Info className="w-5 h-5 text-text-secondary" />;
      default:
        return <Clock className="w-5 h-5 text-indigo-400" />;
    }
  };

  if (loading && runs.length === 0) {
    return (
      <div className="flex justify-center items-center h-full">
        <Loader2 className="w-8 h-8 animate-spin text-text-secondary" />
      </div>
    );
  }

  const activeRun = runs.find(r => r.id === activeRunId);

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-700">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight tracking-tight text-text-primary text-text-primary">Validation Workspace</h1>
          <p className="text-text-muted mt-2">Isolated patch validation and ML recovery verification</p>
        </div>
        <Button onClick={startValidation} disabled={triggering} className="bg-indigo-600 hover:bg-indigo-700 text-text-primary">
          {triggering ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : <PlayCircle className="w-4 h-4 mr-2" />}
          Start Validation
        </Button>
      </div>

      {error && (
        <div className="bg-rose-50 dark:bg-rose-900/20 text-rose-600 p-4 rounded-lg flex items-center border border-rose-200 dark:border-rose-800">
          <AlertCircle className="w-5 h-5 mr-3 flex-shrink-0" />
          <p>{error}</p>
        </div>
      )}

      {!activeRun && !error && (
        <div className="text-center py-16 bg-slate-50 dark:bg-background-primary rounded-lg border border-slate-200 dark:border-border">
          <Info className="w-12 h-12 text-text-secondary mx-auto mb-4" />
          <h3 className="text-xl font-medium text-text-primary text-text-primary mb-2">No Validation Runs</h3>
          <p className="text-text-muted mb-6">Start a validation run to evaluate the approved patch.</p>
        </div>
      )}

      {activeRun && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 space-y-6">
            
            <Card className="border-slate-200 dark:border-border overflow-hidden shadow-sm">
              <CardHeader className="bg-slate-50/50 dark:bg-background-primary/50 border-b border-slate-100 dark:border-border">
                <div className="flex justify-between items-center">
                  <CardTitle className="text-lg">Final Verdict</CardTitle>
                  <div className="flex items-center gap-2">
                    {getStatusIcon(activeRun.verdict || activeRun.status)}
                    <span className="font-semibold text-text-primary text-text-primary">
                      {activeRun.verdict || activeRun.status.toUpperCase()}
                    </span>
                  </div>
                </div>
              </CardHeader>
              <CardContent className="pt-6">
                <p className="text-text-disabled dark:text-text-primary">{activeRun.summary || 'Validation is in progress...'}</p>
                {activeRun.verdict === 'FAIL' && (
                  <Button variant="outline" className="mt-4 text-rose-600 border-rose-200 hover:bg-rose-50">
                    Request Changes
                  </Button>
                )}
              </CardContent>
            </Card>

            <Card className="border-slate-200 dark:border-border shadow-sm">
              <CardHeader>
                <CardTitle className="text-lg">System Checks</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {checks.map(check => (
                    <div key={check.id} className="flex items-start justify-between p-4 bg-slate-50 dark:bg-background-primary rounded-lg border border-slate-100 dark:border-border">
                      <div className="flex items-start gap-4">
                        <div className="mt-0.5">{getStatusIcon(check.status)}</div>
                        <div>
                          <h4 className="font-medium text-text-primary text-text-primary">{check.name}</h4>
                          <p className="text-sm text-text-muted mt-1">{check.summary}</p>
                        </div>
                      </div>
                      <span className="text-xs uppercase font-semibold text-text-secondary">{check.status}</span>
                    </div>
                  ))}
                  {checks.length === 0 && (
                    <p className="text-text-muted italic text-sm text-center py-4">No checks completed yet.</p>
                  )}
                </div>
              </CardContent>
            </Card>

            <Card className="border-slate-200 dark:border-border shadow-sm">
              <CardHeader>
                <CardTitle className="text-lg">ML Recovery Evaluation</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="overflow-x-auto">
                  <table className="w-full text-sm text-left">
                    <thead className="text-xs text-text-muted uppercase bg-slate-50 dark:bg-background-primary border-b border-slate-200 dark:border-border">
                      <tr>
                        <th className="px-4 py-3 font-medium">Metric</th>
                        <th className="px-4 py-3 font-medium">Healthy (Ref)</th>
                        <th className="px-4 py-3 font-medium">Current</th>
                        <th className="px-4 py-3 font-medium">Patched</th>
                        <th className="px-4 py-3 font-medium">Status</th>
                      </tr>
                    </thead>
                    <tbody>
                      {metrics.filter(m => !m.segment_name).map(m => (
                        <tr key={m.id} className="border-b border-slate-100 dark:border-border last:border-0">
                          <td className="px-4 py-3 font-medium text-text-primary text-text-primary">{m.metric_name}</td>
                          <td className="px-4 py-3 text-text-muted">{m.baseline_value.toFixed(3) || '-'}</td>
                          <td className="px-4 py-3 text-rose-500">{m.current_value.toFixed(3) || '-'}</td>
                          <td className="px-4 py-3 font-medium text-emerald-600">{m.patched_value.toFixed(3)}</td>
                          <td className="px-4 py-3">
                            <div className="flex items-center gap-1.5">
                              {getStatusIcon(m.status)}
                              <span className="capitalize">{m.status}</span>
                            </div>
                          </td>
                        </tr>
                      ))}
                      {metrics.length === 0 && (
                        <tr>
                          <td colSpan={5} className="px-4 py-6 text-center text-text-muted italic">No ML evaluation metrics available.</td>
                        </tr>
                      )}
                    </tbody>
                  </table>
                </div>
              </CardContent>
            </Card>
          </div>

          <div className="space-y-6">
            <Card className="border-slate-200 dark:border-border shadow-sm">
              <CardHeader>
                <CardTitle className="text-lg">Validation History</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {runs.map((run, i) => (
                    <button
                      key={run.id}
                      onClick={() => { setActiveRunId(run.id); fetchRunDetails(run.id); }}
                      className={`w-full text-left p-3 rounded-lg border transition-colors ${
                        activeRunId === run.id 
                          ? 'bg-indigo-50 border-indigo-200 dark:bg-indigo-900/20 dark:border-indigo-800' 
                          : 'bg-white border-slate-200 hover:bg-slate-50 dark:bg-background-base dark:border-border'
                      }`}
                    >
                      <div className="flex justify-between items-center mb-1">
                        <span className="font-medium text-sm text-text-primary text-text-primary">Run #{runs.length - i}</span>
                        {getStatusIcon(run.verdict || run.status)}
                      </div>
                      <div className="text-xs text-text-muted">
                        {new Date(run.started_at).toLocaleString()}
                      </div>
                    </button>
                  ))}
                </div>
              </CardContent>
            </Card>
            
            <Card className="border-slate-200 dark:border-border shadow-sm">
              <CardHeader>
                <CardTitle className="text-lg">Acceptance Profile</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3 text-sm">
                  <div className="flex justify-between items-center pb-2 border-b border-slate-100 dark:border-border">
                    <span className="text-text-disabled dark:text-text-secondary">Profile</span>
                    <span className="font-medium text-text-primary text-text-primary">ML_DEFAULT</span>
                  </div>
                  <div className="flex justify-between items-center pb-2 border-b border-slate-100 dark:border-border">
                    <span className="text-text-disabled dark:text-text-secondary">Required Checks</span>
                    <span className="font-medium text-text-primary text-text-primary">Static, Tests, Security</span>
                  </div>
                  <div className="flex justify-between items-center pb-2 border-b border-slate-100 dark:border-border">
                    <span className="text-text-disabled dark:text-text-secondary">Primary Metric</span>
                    <span className="font-medium text-text-primary text-text-primary">F1 Score</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-text-disabled dark:text-text-secondary">Min. Recovery</span>
                    <span className="font-medium text-text-primary text-text-primary">&ge; 0.85</span>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      )}
    </div>
  );
};
