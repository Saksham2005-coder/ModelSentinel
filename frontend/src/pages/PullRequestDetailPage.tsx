import { useState, useEffect, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { PullRequestApi, PullRequest } from '@/services/api/pull_requests';
import { IncidentApi, Incident } from '@/services/api/incidents';
import { DeploymentApi, Deployment } from '@/services/api/deployments';
import { changeRiskService, ChangeRiskAssessment } from '@/services/api/changeRisk';
import { fetchApi } from '@/services/api/client';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { Loader2, ArrowLeft, GitPullRequest, GitBranch, ShieldAlert, CheckCircle, XCircle, Rocket } from 'lucide-react';

interface ExternalCheck {
  id: string;
  name: string;
  provider: string;
  conclusion: string;
  status: string;
}

export function PullRequestDetailPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [pr, setPr] = useState<PullRequest | null>(null);
  const [incident, setIncident] = useState<Incident | null>(null);
  const [deployment, setDeployment] = useState<Deployment | null>(null);
  const [riskAssessment, setRiskAssessment] = useState<ChangeRiskAssessment | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [checks, setChecks] = useState<ExternalCheck[]>([]);

  const fetchData = useCallback(async () => {
    if (!id) return;
    setLoading(true);
    try {
      const prData = await PullRequestApi.getPullRequest(id);
      setPr(prData);
      
      const incData = await IncidentApi.getIncident(prData.incident_id);
      setIncident(incData);

      try {
        const risk = await changeRiskService.getAssessmentForPatch(prData.patch_proposal_id);
        setRiskAssessment(risk);
      } catch (e) {
        console.warn("Could not load risk assessment");
      }

      try {
        const res = await fetchApi<ExternalCheck[]>(`/pull-requests/${id}/checks`);
        setChecks(res);
      } catch (e) {
        console.warn("Could not load CI checks");
      }

      const deps = await DeploymentApi.getDeployments();
      const dep = deps.find(d => d.pull_request_id === prData.id);
      if (dep) {
        setDeployment(dep);
      }
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Unable to load pull request.');
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

  if (error || !pr) {
    return (
      <div className="p-8 text-center bg-surface border border-border rounded-xl">
        <ShieldAlert className="h-12 w-12 text-status-danger mx-auto mb-4" />
        <h2 className="text-xl font-bold text-text-primary">Error Loading Pull Request</h2>
        <p className="text-text-secondary mt-2">{error || 'Pull request not found'}</p>
        <Button onClick={() => navigate('/pull-requests')} className="mt-6" variant="outline">
          Back to Pull Requests
        </Button>
      </div>
    );
  }

  const g = deployment?.gate_result;

  return (
    <div className="flex flex-col gap-8 pb-12">
      <div className="flex items-center gap-4">
        <Button variant="outline" size="sm" onClick={() => navigate('/pull-requests')}>
          <ArrowLeft className="h-4 w-4 mr-2" /> Back
        </Button>
        <div>
          <div className="flex items-center gap-3">
            <h1 className="text-2xl font-bold tracking-tight text-text-primary">Pull Request: {pr.id.substring(0,8)}</h1>
            <Badge variant={pr.status === 'PASSED' ? 'success' : pr.status === 'FAILED' ? 'danger' : 'info'}>
              {pr.status}
            </Badge>
          </div>
          <p className="text-text-secondary mt-1 flex items-center gap-2">
            <GitBranch className="h-4 w-4" /> {pr.branch_name}
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="col-span-2 flex flex-col gap-6">
          {/* PR Overview */}
          <section className="bg-surface border border-border rounded-xl p-6">
            <h3 className="text-lg font-bold text-text-primary mb-4 flex items-center gap-2">
              <GitPullRequest className="h-5 w-5 text-brand" /> Overview
            </h3>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <p className="text-sm text-text-secondary">Incident ID</p>
                <p className="font-medium">{pr.incident_id.substring(0,8)}</p>
              </div>
              <div>
                <p className="text-sm text-text-secondary">Branch</p>
                <p className="font-mono text-sm">{pr.branch_name}</p>
              </div>
              <div>
                <p className="text-sm text-text-secondary">Commit SHA</p>
                <p className="font-mono text-sm">{pr.commit_sha || 'Pending'}</p>
              </div>
              <div>
                <p className="text-sm text-text-secondary">External URL</p>
                {pr.external_pr_url ? (
                  <a href={pr.external_pr_url} target="_blank" rel="noreferrer" className="text-brand hover:underline font-mono text-sm">
                    View on GitHub
                  </a>
                ) : (
                  <p className="text-text-muted">Not linked</p>
                )}
              </div>
            </div>
          </section>

          {/* Validation & CI */}
          <section className="bg-surface border border-border rounded-xl p-6">
            <h3 className="text-lg font-bold text-text-primary mb-4">CI Checks</h3>
            <div className="flex flex-col gap-3">
              <div className="flex items-center justify-between p-3 border border-border rounded bg-background-base">
                <span className="font-medium text-text-primary">Validation Status</span>
                {g?.validation_passed === true ? <Badge variant="success">PASS</Badge> : <Badge variant="danger">FAIL</Badge>}
              </div>
              <div className="flex items-center justify-between p-3 border border-border rounded bg-background-base">
                <span className="font-medium text-text-primary">Regression Status</span>
                {g?.regression_passed === true ? <Badge variant="success">PASS</Badge> : <Badge variant="danger">FAIL</Badge>}
              </div>
              <div className="flex items-center justify-between p-3 border border-border rounded bg-background-base">
                <span className="font-medium text-text-primary">Internal CI Pipeline</span>
                {g?.ci_passed === true ? <Badge variant="success">PASS</Badge> : <Badge variant="danger">FAIL</Badge>}
              </div>
            </div>
            
            {checks.length > 0 && (
              <div className="mt-6">
                <h4 className="text-sm font-semibold text-text-secondary mb-3">External Provider Checks</h4>
                <div className="flex flex-col gap-2">
                  {checks.map(c => (
                    <div key={c.id} className="flex items-center justify-between p-3 border border-border rounded bg-background-base text-sm">
                      <div className="flex flex-col">
                        <span className="font-medium">{c.name}</span>
                        <span className="text-xs text-text-muted">{c.provider}</span>
                      </div>
                      <Badge variant={
                        c.conclusion === 'SUCCESS' ? 'success' :
                        (c.conclusion === 'FAILURE' || c.conclusion === 'CANCELLED') ? 'danger' : 'info'
                      }>
                        {c.conclusion || c.status}
                      </Badge>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </section>
        </div>

        <div className="flex flex-col gap-6">
          {/* Deployment Gate */}
          <section className={`border rounded-xl p-6 ${deployment?.status === 'ELIGIBLE' ? 'bg-status-success/10 border-status-success/30' : 'bg-status-danger/10 border-status-danger/30'}`}>
            <h3 className="text-lg font-bold mb-4 flex items-center gap-2">
              <Rocket className="h-5 w-5" /> Deployment Gate
            </h3>
            
            <div className="flex flex-col gap-2 mb-6 text-sm">
              <div className="flex items-center justify-between">
                <span>Patch Approved</span>
                {g?.patch_approved ? <CheckCircle className="h-4 w-4 text-status-success" /> : <XCircle className="h-4 w-4 text-status-danger" />}
              </div>
              <div className="flex items-center justify-between">
                <span>Validation Passed</span>
                {g?.validation_passed ? <CheckCircle className="h-4 w-4 text-status-success" /> : <XCircle className="h-4 w-4 text-status-danger" />}
              </div>
              <div className="flex items-center justify-between">
                <span>Regression Passed</span>
                {g?.regression_passed ? <CheckCircle className="h-4 w-4 text-status-success" /> : <XCircle className="h-4 w-4 text-status-danger" />}
              </div>
              <div className="flex items-center justify-between">
                <span>CI Passed</span>
                {g?.ci_passed ? <CheckCircle className="h-4 w-4 text-status-success" /> : <XCircle className="h-4 w-4 text-status-danger" />}
              </div>
              <div className="flex items-center justify-between">
                <span>Human Approval</span>
                {g?.human_approved ? <CheckCircle className="h-4 w-4 text-status-success" /> : <XCircle className="h-4 w-4 text-status-danger" />}
              </div>
            </div>

            {deployment?.policy_result && (
              <div className="mt-4 pt-4 border-t border-border/50 text-sm">
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

            <div className="pt-4 border-t border-border/50">
              <p className={`font-bold text-lg text-center ${deployment?.status === 'ELIGIBLE' ? 'text-status-success' : 'text-status-danger'}`}>
                {deployment?.status === 'ELIGIBLE' ? 'DEPLOYMENT ELIGIBLE' : 'DEPLOYMENT BLOCKED'}
              </p>
              {deployment?.status === 'BLOCKED' && deployment.block_reason && (
                <p className="text-xs text-status-danger text-center mt-2 font-medium">
                  {deployment.block_reason}
                </p>
              )}
            </div>
            
            <Button className="w-full mt-4" variant="outline" onClick={() => navigate(`/deployment-gates/${deployment?.id}`)} disabled={!deployment}>
              View Full Gate Details
            </Button>
          </section>

          {/* Change Risk */}
          {riskAssessment && (
            <section className="bg-surface border border-border rounded-xl p-6">
              <h3 className="text-lg font-bold text-text-primary mb-4 flex items-center gap-2">
                <ShieldAlert className="h-5 w-5 text-brand" /> Change Risk
              </h3>
              <div className="flex items-center gap-4 mb-4">
                <div className="text-2xl font-bold text-text-primary">{riskAssessment.risk_score}</div>
                <Badge variant={
                  riskAssessment.risk_level === 'CRITICAL' ? 'danger' :
                  riskAssessment.risk_level === 'HIGH' ? 'danger' :
                  riskAssessment.risk_level === 'MODERATE' ? 'warning' : 'success'
                }>
                  {riskAssessment.risk_level} RISK
                </Badge>
              </div>
              <div className="space-y-4 text-sm">
                <div>
                  <span className="text-text-secondary block mb-1">Blast Radius</span>
                  <div className="grid grid-cols-2 gap-2">
                    <div className="bg-background-base p-2 rounded text-center">
                      <div className="text-text-muted text-xs">Files</div>
                      <div className="font-medium">{riskAssessment.blast_radius.files.length}</div>
                    </div>
                    <div className="bg-background-base p-2 rounded text-center">
                      <div className="text-text-muted text-xs">Models</div>
                      <div className="font-medium">{riskAssessment.blast_radius.models.length}</div>
                    </div>
                  </div>
                </div>
                <div>
                  <span className="text-text-secondary block mb-1">Risk Factors</span>
                  <ul className="text-text-primary space-y-1">
                    {riskAssessment.factors.map((f, i) => (
                      <li key={i} className="truncate text-xs" title={f.factor}>• {f.factor} (+{f.contribution})</li>
                    ))}
                  </ul>
                </div>
              </div>
            </section>
          )}

          {/* Incident Context */}
          <section className="bg-surface border border-border rounded-xl p-6">
            <h3 className="text-lg font-bold text-text-primary mb-4">Incident Context</h3>
            {incident ? (
              <div className="flex flex-col gap-3">
                <div>
                  <p className="text-xs text-text-secondary">Key</p>
                  <p className="font-mono text-sm">{incident.incident_key}</p>
                </div>
                <div>
                  <p className="text-xs text-text-secondary">Title</p>
                  <p className="text-sm">{incident.title}</p>
                </div>
                <div>
                  <p className="text-xs text-text-secondary">Severity</p>
                  <Badge variant="warning">{incident.severity}</Badge>
                </div>
                <Button variant="outline" size="sm" className="mt-2" onClick={() => navigate(`/incidents/${incident.id}`)}>
                  View Incident
                </Button>
              </div>
            ) : (
              <p className="text-sm text-text-muted">Loading incident context...</p>
            )}
          </section>
        </div>
      </div>
    </div>
  );
}
