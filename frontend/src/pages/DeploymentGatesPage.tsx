import { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { DeploymentApi, Deployment } from '@/services/api/deployments';
import { PullRequestApi, PullRequest } from '@/services/api/pull_requests';
import { IncidentApi, Incident } from '@/services/api/incidents';
import { Badge } from '@/components/ui/Badge';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/Table';
import { Loader2, Rocket } from 'lucide-react';

export function DeploymentGatesPage() {
  const navigate = useNavigate();
  const [deployments, setDeployments] = useState<Deployment[]>([]);
  const [pullRequests, setPullRequests] = useState<Record<string, PullRequest>>({});
  const [incidents, setIncidents] = useState<Record<string, Incident>>({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchData = useCallback(async () => {
    setLoading(true);
    try {
      const [deps, prs, incs] = await Promise.all([
        DeploymentApi.getDeployments(),
        PullRequestApi.getPullRequests(),
        IncidentApi.getIncidents()
      ]);
      setDeployments(deps);
      
      const prMap: Record<string, PullRequest> = {};
      prs.forEach(pr => { prMap[pr.id] = pr; });
      setPullRequests(prMap);

      const incMap: Record<string, Incident> = {};
      incs.forEach(inc => { incMap[inc.id] = inc; });
      setIncidents(incMap);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to fetch deployments');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const metrics = {
    eligible: deployments.filter(d => d.status === 'ELIGIBLE').length,
    blocked: deployments.filter(d => d.status === 'BLOCKED').length,
    waitingForCi: deployments.filter(d => d.gate_result?.ci_passed === false).length,
    waitingForApproval: deployments.filter(d => d.gate_result?.human_approved === false).length,
    total: deployments.length,
  };

  const getStatusBadge = (status: string) => {
    if (status === 'ELIGIBLE') return <Badge variant="success">{status}</Badge>;
    if (status === 'BLOCKED') return <Badge variant="danger">{status}</Badge>;
    return <Badge variant="default">{status}</Badge>;
  };

  const getGateCell = (passed: boolean | undefined) => {
    if (passed === undefined) return <span className="text-text-muted text-xs">--</span>;
    return passed ? <span className="text-status-success text-xs font-bold mr-2">PASS</span> : <span className="text-status-danger text-xs font-bold mr-2">FAIL</span>;
  };

  return (
    <div className="flex flex-col gap-8">
      <div>
        <h1 className="text-3xl font-bold tracking-tight text-text-primary">Deployment Gates</h1>
        <p className="text-text-secondary mt-1">Review operational deployment eligibility for patches.</p>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
        {Object.entries(metrics).map(([key, value]) => (
          <div key={key} className="bg-surface border border-border rounded-lg p-4 flex flex-col">
            <span className="text-sm text-text-secondary capitalize">{key.replace(/([A-Z])/g, ' $1').trim()}</span>
            <span className="text-2xl font-bold text-text-primary mt-1">{value}</span>
          </div>
        ))}
      </div>

      {error && <div className="text-status-danger p-4 bg-status-danger/10 rounded-lg">{error}</div>}

      <div className="rounded-xl border border-border bg-surface overflow-hidden">
        {loading ? (
          <div className="p-12 flex justify-center text-text-secondary">
            <Loader2 className="h-8 w-8 animate-spin" />
          </div>
        ) : deployments.length === 0 ? (
          <div className="p-12 text-center text-text-secondary">
            <Rocket className="h-8 w-8 mx-auto mb-4 text-text-muted" />
            <h3 className="text-lg font-medium text-text-primary">No deployment gates yet.</h3>
            <p className="mt-2">Deployment eligibility will appear after a pull request enters the delivery workflow.</p>
          </div>
        ) : (
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Incident</TableHead>
                <TableHead>Pull Request</TableHead>
                <TableHead>Validation</TableHead>
                <TableHead>Regression</TableHead>
                <TableHead>CI</TableHead>
                <TableHead>Approval</TableHead>
                <TableHead>Gate Result</TableHead>
                <TableHead>Updated</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {deployments.map((dep) => {
                const pr = pullRequests[dep.pull_request_id];
                const inc = incidents[dep.incident_id];
                const g = dep.gate_result;

                return (
                  <TableRow 
                    key={dep.id} 
                    className="cursor-pointer hover:bg-surface-hover"
                    onClick={() => navigate(`/deployment-gates/${dep.id}`)}
                  >
                    <TableCell>
                      {inc ? (
                        <>
                          <div className="font-medium text-text-primary">{inc.incident_key}</div>
                          <div className="text-xs text-text-secondary truncate max-w-[150px]">{inc.title}</div>
                        </>
                      ) : 'Unknown'}
                    </TableCell>
                    <TableCell className="font-mono text-xs text-brand">
                      {pr ? pr.branch_name : dep.pull_request_id.substring(0,8)}
                    </TableCell>
                    <TableCell>{getGateCell(g?.validation_passed)}</TableCell>
                    <TableCell>{getGateCell(g?.regression_passed)}</TableCell>
                    <TableCell>{getGateCell(g?.ci_passed)}</TableCell>
                    <TableCell>{getGateCell(g?.human_approved)}</TableCell>
                    <TableCell>
                      <div className="flex flex-col">
                        {getStatusBadge(dep.status)}
                        {dep.status === 'BLOCKED' && dep.block_reason && (
                          <span className="text-xs text-status-danger mt-1 truncate max-w-[150px]">{dep.block_reason}</span>
                        )}
                      </div>
                    </TableCell>
                    <TableCell className="text-sm text-text-secondary">
                      {new Date(dep.created_at).toLocaleString()}
                    </TableCell>
                  </TableRow>
                );
              })}
            </TableBody>
          </Table>
        )}
      </div>
    </div>
  );
}
