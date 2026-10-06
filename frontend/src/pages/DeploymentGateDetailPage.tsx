import { useState, useEffect, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { DeploymentApi, Deployment } from '@/services/api/deployments';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { Loader2, ArrowLeft, Rocket, CheckCircle, XCircle, ShieldAlert } from 'lucide-react';

export function DeploymentGateDetailPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [deployment, setDeployment] = useState<Deployment | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchData = useCallback(async () => {
    if (!id) return;
    setLoading(true);
    try {
      const deps = await DeploymentApi.getDeployments();
      const dep = deps.find(d => d.id === id);
      if (!dep) {
        throw new Error('Deployment gate not found');
      }
      setDeployment(dep);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Unable to load deployment gate.');
    } finally {
      setLoading(false);
    }
  }, [id]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

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
        <h2 className="text-xl font-bold text-text-primary">Error Loading Deployment Gate</h2>
        <p className="text-text-secondary mt-2">{error || 'Deployment gate not found'}</p>
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

  return (
    <div className="flex flex-col gap-8 pb-12 max-w-4xl mx-auto">
      <div className="flex items-center gap-4">
        <Button variant="outline" size="sm" onClick={() => navigate('/deployments')}>
          <ArrowLeft className="h-4 w-4 mr-2" /> Back
        </Button>
        <div>
          <div className="flex items-center gap-3">
            <h1 className="text-2xl font-bold tracking-tight text-text-primary">Deployment Gate: {deployment.id.substring(0,8)}</h1>
            <Badge variant={deployment.status === 'ELIGIBLE' ? 'success' : 'danger'}>
              {deployment.status}
            </Badge>
          </div>
          <p className="text-text-secondary mt-1 font-mono text-sm">
            Commit: {deployment.commit_sha || 'N/A'}
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-surface border border-border rounded-xl p-6">
          <p className="text-sm text-text-secondary">Pull Request</p>
          <p className="font-mono text-lg text-brand mt-1">{deployment.pull_request_id.substring(0,8)}</p>
          <Button variant="outline" size="sm" className="mt-4 w-full" onClick={() => navigate(`/pull-requests/${deployment.pull_request_id}`)}>
            View Pull Request
          </Button>
        </div>
        <div className="bg-surface border border-border rounded-xl p-6">
          <p className="text-sm text-text-secondary">Incident</p>
          <p className="font-mono text-lg text-text-primary mt-1">{deployment.incident_id.substring(0,8)}</p>
          <Button variant="outline" size="sm" className="mt-4 w-full" onClick={() => navigate(`/incidents/${deployment.incident_id}`)}>
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

        <div className={`mt-8 p-6 rounded-lg border text-center ${deployment.status === 'ELIGIBLE' ? 'bg-status-success/10 border-status-success/30' : 'bg-status-danger/10 border-status-danger/30'}`}>
          <h2 className={`text-2xl font-black tracking-widest ${deployment.status === 'ELIGIBLE' ? 'text-status-success' : 'text-status-danger'}`}>
            {deployment.status === 'ELIGIBLE' ? 'DEPLOYMENT ELIGIBLE' : 'DEPLOYMENT BLOCKED'}
          </h2>
          {deployment.status === 'BLOCKED' && deployment.block_reason && (
            <p className="text-status-danger font-medium mt-4 p-3 bg-background-base rounded border border-status-danger/20 inline-block">
              {deployment.block_reason}
            </p>
          )}
        </div>
      </div>
    </div>
  );
}
