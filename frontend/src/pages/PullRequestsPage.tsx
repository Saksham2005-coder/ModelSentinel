import { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { PullRequestApi, PullRequest } from '@/services/api/pull_requests';
import { IncidentApi, Incident } from '@/services/api/incidents';
import { DeploymentApi, Deployment } from '@/services/api/deployments';
import { Badge } from '@/components/ui/Badge';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/Table';
import { Loader2, GitPullRequest } from 'lucide-react';

export function PullRequestsPage() {
  const navigate = useNavigate();
  const [pullRequests, setPullRequests] = useState<PullRequest[]>([]);
  const [incidents, setIncidents] = useState<Record<string, Incident>>({});
  const [deployments, setDeployments] = useState<Record<string, Deployment>>({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchData = useCallback(async () => {
    setLoading(true);
    try {
      const [prs, incs, deps] = await Promise.all([
        PullRequestApi.getPullRequests(),
        IncidentApi.getIncidents(),
        DeploymentApi.getDeployments()
      ]);
      setPullRequests(prs);
      
      const incMap: Record<string, Incident> = {};
      incs.forEach(inc => { incMap[inc.id] = inc; });
      setIncidents(incMap);
      
      const depMap: Record<string, Deployment> = {};
      deps.forEach(dep => { depMap[dep.pull_request_id] = dep; });
      setDeployments(depMap);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to fetch pull requests');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const metrics = {
    total: pullRequests.length,
    ready: pullRequests.filter(pr => pr.status === 'CREATED').length,
    checking: pullRequests.filter(pr => pr.status === 'PENDING').length,
    passed: pullRequests.filter(pr => pr.status === 'PASSED').length,
    blocked: pullRequests.filter(pr => pr.status === 'FAILED').length,
    merged: pullRequests.filter(pr => pr.status === 'MERGED').length,
  };

  const getStatusBadge = (status: string) => {
    const s = status.toUpperCase();
    if (s === 'PASSED' || s === 'MERGED') return <Badge variant="success">{status}</Badge>;
    if (s === 'FAILED' || s === 'BLOCKED') return <Badge variant="danger">{status}</Badge>;
    if (s === 'PENDING') return <Badge variant="warning">{status}</Badge>;
    return <Badge variant="info">{status}</Badge>;
  };
  
  const getSubStatus = (passed?: boolean) => {
    if (passed === undefined) return <span className="text-text-muted">--</span>;
    return passed ? <span className="text-status-success text-xs font-bold">PASS</span> : <span className="text-status-danger text-xs font-bold">FAIL</span>;
  };

  return (
    <div className="flex flex-col gap-8">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight tracking-tight text-text-primary">Pull Requests</h1>
        <p className="text-text-secondary mt-1">Manage validated patches through the delivery workflow.</p>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-6 gap-4">
        {Object.entries(metrics).map(([key, value]) => (
          <div key={key} className="bg-surface border border-border rounded-lg p-4 flex flex-col">
            <span className="text-sm text-text-secondary capitalize">{key}</span>
            <span className="text-2xl font-semibold tracking-tight text-text-primary mt-1">{value}</span>
          </div>
        ))}
      </div>

      {error && <div className="text-status-danger p-4 bg-status-danger/10 rounded-lg">{error}</div>}

      <div className="rounded-xl border border-border bg-surface overflow-hidden">
        {loading ? (
          <div className="p-12 flex justify-center text-text-secondary">
            <Loader2 className="h-8 w-8 animate-spin" />
          </div>
        ) : pullRequests.length === 0 ? (
          <div className="p-12 text-center text-text-secondary">
            <GitPullRequest className="h-8 w-8 mx-auto mb-4 text-text-muted" />
            <h3 className="text-lg font-medium text-text-primary">No pull requests yet.</h3>
            <p className="mt-2">Create a validated and approved patch to start the delivery workflow.</p>
          </div>
        ) : (
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>PR</TableHead>
                <TableHead>Incident</TableHead>
                <TableHead>Branch</TableHead>
                <TableHead>Validation</TableHead>
                <TableHead>Regression</TableHead>
                <TableHead>CI</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Created</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {pullRequests.map((pr) => {
                const inc = incidents[pr.incident_id];
                const dep = deployments[pr.id];
                const g = dep?.gate_result;

                return (
                  <TableRow 
                    key={pr.id} 
                    className="cursor-pointer hover:bg-surface-hover"
                    onClick={() => navigate(`/pull-requests/${pr.id}`)}
                  >
                    <TableCell className="font-mono text-xs text-text-secondary">
                      {pr.id.substring(0,8)}
                    </TableCell>
                    <TableCell>
                      {inc ? (
                        <>
                          <div className="font-medium text-text-primary">{inc.incident_key}</div>
                          <div className="text-xs text-text-secondary truncate max-w-[200px]">{inc.title}</div>
                        </>
                      ) : 'Unknown'}
                    </TableCell>
                    <TableCell className="font-mono text-xs text-text-secondary">
                      {pr.branch_name || 'N/A'}
                    </TableCell>
                    <TableCell>{getSubStatus(g?.validation_passed)}</TableCell>
                    <TableCell>{getSubStatus(g?.regression_passed)}</TableCell>
                    <TableCell>{getSubStatus(g?.ci_passed)}</TableCell>
                    <TableCell>{getStatusBadge(pr.status)}</TableCell>
                    <TableCell className="text-sm text-text-secondary">
                      {new Date(pr.created_at).toLocaleString()}
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
