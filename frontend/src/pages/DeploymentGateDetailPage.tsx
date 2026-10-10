import { useState, useEffect, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { DeploymentApi, Deployment } from '@/services/api/deployments';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { Loader2, ArrowLeft, Rocket, CheckCircle, XCircle, ShieldAlert, Activity } from 'lucide-react';

export function DeploymentGateDetailPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [deployment, setDeployment] = useState<Deployment | null>(null);
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchData = useCallback(async () => {
    if (!id) return;
    setLoading(true);
    try {
      const dep = await DeploymentApi.getDeployment(id);
      if (!dep) {
        throw new Error('Deployment not found');
      }
      setDeployment(dep);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Unable to load deployment.');
    } finally {
      setLoading(false);
    }
  }, [id]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const handleRecordDeployment = async () => {
    if (!id) return;
    setActionLoading(true);
    try {
      await DeploymentApi.recordDeployment(id, 'production', 'Manual');
      await fetchData();
    } catch (err: unknown) {
      alert(err instanceof Error ? err.message : 'Error recording deployment');
    } finally {
      setActionLoading(false);
    }
  };

  const handleStartVerification = async () => {
    if (!id) return;
    setActionLoading(true);
    try {
      await DeploymentApi.startVerification(id);
      await fetchData();
    } catch (err: unknown) {
      alert(err instanceof Error ? err.message : 'Error starting verification');
    } finally {
      setActionLoading(false);
    }
  };

  const handleEvaluateHealth = async () => {
    if (!id) return;
    setActionLoading(true);
    try {
      await DeploymentApi.evaluateHealth(id);
      await fetchData();
    } catch (err: unknown) {
      alert(err instanceof Error ? err.message : 'Error evaluating health');
    } finally {
      setActionLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full">
        <Loader2 className="h-8 w-8 animate-spin text-text-secondary" />
      </div>
    );
  }

  if (error || !deployment) {
    return (
      <div className="p-8 text-center bg-surface border border-border rounded-xl">
        <ShieldAlert className="h-12 w-12 text-status-danger mx-auto mb-4" />
        <h2 className="text-xl font-bold text-text-primary">Error Loading Deployment</h2>
        <p className="text-text-secondary mt-2">{error || 'Deployment not found'}</p>
        <Button onClick={() => navigate('/deployments')} className="mt-6" variant="outline">
          Back to Deployments
        </Button>
      </div>
    );
  }

  const g = deployment.gate_result;

  const RequirementRow = ({ label, passed, required }: { label: string, passed?: boolean, required: boolean }) => (
    <div className="flex items-center justify-between p-4 border border-border bg-background-base rounded-lg mb-3">
      <div>
        <h4 className="font-medium text-text-primary">{label}</h4>
        <p className="text-xs text-text-secondary mt-1">
          Current: <span className="font-mono">{passed ? 'PASS' : (passed === false ? 'FAIL' : 'PENDING')}</span> | 
          Required: <span className="font-mono">{required ? 'PASS' : 'ANY'}</span>
        </p>
      </div>
      <div>
        {passed ? <CheckCircle className="h-6 w-6 text-status-success" /> : <XCircle className="h-6 w-6 text-status-danger" />}
      </div>
    </div>
  );

  const getStatusColor = (s: string) => {
    if (s === 'ELIGIBLE' || s === 'HEALTHY') return 'text-status-success';
    if (s === 'BLOCKED' || s === 'FAILED') return 'text-status-danger';
    if (s === 'DEGRADED') return 'text-status-warning';
    return 'text-brand';
  };

  const getStatusVariant = (s: string) => {
    if (s === 'ELIGIBLE' || s === 'HEALTHY') return 'success';
    if (s === 'BLOCKED' || s === 'FAILED') return 'danger';
    if (s === 'DEGRADED') return 'warning';
    if (s === 'VERIFYING' || s === 'DEPLOYED') return 'info';
    return 'default';
  };

  const isPostDeployment = ['DEPLOYED', 'VERIFYING', 'HEALTHY', 'DEGRADED', 'FAILED'].includes(deployment.status);

  return (
    <div className="flex flex-col gap-8 pb-12 max-w-4xl mx-auto">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Button variant="outline" size="sm" onClick={() => navigate('/deployments')}>
            <ArrowLeft className="h-4 w-4 mr-2" /> Back
          </Button>
          <div>
            <div className="flex items-center gap-3">
              <h1 className="text-2xl font-semibold tracking-tight tracking-tight text-text-primary">Deployment: {deployment.id.substring(0,8)}</h1>
              <Badge variant={getStatusVariant(deployment.status)}>
                {deployment.status}
              </Badge>
            </div>
            <p className="text-text-secondary mt-1 font-mono text-sm">
              Commit: {deployment.commit_sha || 'N/A'} {deployment.environment ? `| Env: ${deployment.environment}` : ''}
            </p>
          </div>
        </div>
        
        <div className="flex items-center gap-2">
          {deployment.status === 'ELIGIBLE' && (
            <Button onClick={handleRecordDeployment} disabled={actionLoading}>
              {actionLoading ? <Loader2 className="h-4 w-4 animate-spin" /> : 'Mark as Deployed'}
            </Button>
          )}
          {deployment.status === 'DEPLOYED' && (
            <Button onClick={handleStartVerification} disabled={actionLoading}>
              {actionLoading ? <Loader2 className="h-4 w-4 animate-spin" /> : 'Start Verification'}
            </Button>
          )}
          {deployment.status === 'VERIFYING' && (
            <Button onClick={handleEvaluateHealth} disabled={actionLoading}>
              {actionLoading ? <Loader2 className="h-4 w-4 animate-spin" /> : 'Evaluate Health'}
            </Button>
          )}
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-surface border border-border rounded-xl p-6">
          <p className="text-sm text-text-secondary">Pull Request</p>
          <p className="font-mono text-lg text-brand mt-1">{deployment.pull_request_id ? deployment.pull_request_id.substring(0,8) : 'N/A'}</p>
          <Button variant="outline" size="sm" className="mt-4 w-full" onClick={() => navigate(`/pull-requests/${deployment.pull_request_id}`)} disabled={!deployment.pull_request_id}>
            View Pull Request
          </Button>
        </div>
        <div className="bg-surface border border-border rounded-xl p-6">
          <p className="text-sm text-text-secondary">Incident</p>
          <p className="font-mono text-lg text-text-primary mt-1">{deployment.incident_id ? deployment.incident_id.substring(0,8) : 'N/A'}</p>
          <Button variant="outline" size="sm" className="mt-4 w-full" onClick={() => navigate(`/incidents/${deployment.incident_id}`)} disabled={!deployment.incident_id}>
            View Incident
          </Button>
        </div>
      </div>

      <div className="bg-surface border border-border rounded-xl p-6">
        <h3 className="text-lg font-bold text-text-primary mb-6 flex items-center gap-2">
          <Rocket className="h-5 w-5 text-brand" /> Deterministic Checklist
        </h3>

        <RequirementRow label="Patch Approval" passed={g?.patch_approved} required={true} />
        <RequirementRow label="Validation Checks" passed={g?.validation_passed} required={true} />
        <RequirementRow label="Regression Suite" passed={g?.regression_passed} required={true} />
        <RequirementRow label="Security Checks" passed={g?.security_passed} required={true} />
        <RequirementRow label="Continuous Integration (CI)" passed={g?.ci_passed} required={true} />
        <RequirementRow label="Human Approval" passed={g?.human_approved} required={true} />

        {deployment.policy_result && (
          <div className="mt-6 p-4 border border-border bg-background-base rounded-lg text-sm">
            <div className="flex items-center justify-between mb-2">
              <span className="font-semibold text-text-primary">Policy Evaluation: {deployment.policy_result.matched_policy || 'Default'}</span>
              <Badge variant={
                deployment.policy_result.result === 'ALLOW' ? 'success' :
                deployment.policy_result.result === 'BLOCK' ? 'danger' : 'warning'
              }>
                {deployment.policy_result.result}
              </Badge>
            </div>
            {deployment.policy_result.blocking_rules?.length > 0 && (
              <ul className="list-disc pl-4 mt-2 text-status-danger text-xs">
                {deployment.policy_result.blocking_rules.map((r: Record<string, unknown>, i: number) => (
                  <li key={i}>{String(r.type)}: expected {String(r.operator)} {String(r.required)}, got {String(r.actual)}</li>
                ))}
              </ul>
            )}
          </div>
        )}

        <div className={`mt-8 p-6 rounded-lg border text-center ${deployment.status === 'ELIGIBLE' ? 'bg-status-success/10 border-status-success/30' : 'bg-status-danger/10 border-status-danger/30'}`}>
          <h2 className={`text-2xl font-black tracking-widest ${getStatusColor(deployment.status)}`}>
            {deployment.status === 'ELIGIBLE' ? 'DEPLOYMENT ELIGIBLE' : 'DEPLOYMENT BLOCKED'}
          </h2>
          {deployment.status === 'BLOCKED' && deployment.block_reason && (
            <p className="text-status-danger font-medium mt-4 p-3 bg-background-base rounded border border-status-danger/20 inline-block">
              {deployment.block_reason}
            </p>
          )}
        </div>
      </div>

      {isPostDeployment && (
        <div className="bg-surface border border-border rounded-xl p-6">
          <h3 className="text-lg font-bold text-text-primary mb-6 flex items-center gap-2">
            <Activity className="h-5 w-5 text-brand" /> Post-Deployment Verification
          </h3>
          
          <div className="mb-6 p-4 bg-background-base border border-border rounded-lg">
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div>
                <p className="text-xs text-text-secondary">Deployed At</p>
                <p className="font-medium mt-1">{deployment.deployed_at ? new Date(deployment.deployed_at).toLocaleString() : 'N/A'}</p>
              </div>
              <div>
                <p className="text-xs text-text-secondary">Environment</p>
                <p className="font-medium mt-1">{deployment.environment || 'N/A'}</p>
              </div>
              <div>
                <p className="text-xs text-text-secondary">Source</p>
                <p className="font-medium mt-1">{deployment.deployment_source || 'N/A'}</p>
              </div>
              <div>
                <p className="text-xs text-text-secondary">Current Status</p>
                <p className={`font-bold mt-1 ${getStatusColor(deployment.status)}`}>{deployment.status}</p>
              </div>
            </div>
          </div>

          {deployment.verifications && deployment.verifications.length > 0 ? (
            <div className="space-y-4">
              <h4 className="font-medium text-text-primary">Verification Runs</h4>
              {deployment.verifications.map(v => (
                <div key={v.id} className="p-4 border border-border rounded-lg bg-background-base flex flex-col gap-2">
                  <div className="flex justify-between items-start">
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="font-mono text-sm">Run: {v.id.substring(0,8)}</span>
                        <Badge variant={getStatusVariant(v.status)}>{v.status}</Badge>
                      </div>
                      <p className="text-sm text-text-secondary mt-1">{v.summary}</p>
                    </div>
                    <div className="text-right text-xs text-text-secondary">
                      <div>Started: {new Date(v.started_at).toLocaleString()}</div>
                      {v.completed_at && <div>Completed: {new Date(v.completed_at).toLocaleString()}</div>}
                    </div>
                  </div>
                  {v.failure_reason && (
                    <div className="mt-2 p-3 bg-status-danger/10 border border-status-danger/30 rounded text-status-danger text-sm">
                      <strong>Failure Reason:</strong> {v.failure_reason}
                    </div>
                  )}
                  {v.observations && Object.keys(v.observations).length > 0 && (
                    <div className="mt-2 text-sm border-t border-border pt-2">
                      <p className="text-text-secondary mb-1">Observations:</p>
                      <pre className="p-2 bg-black/20 rounded font-mono text-xs overflow-auto max-h-32">
                        {JSON.stringify(v.observations, null, 2)}
                      </pre>
                    </div>
                  )}
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center p-8 bg-background-base border border-border rounded-lg">
              <p className="text-text-secondary">No verification runs started yet.</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
