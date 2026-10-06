import { fetchApi } from './client';

export interface PullRequest {
  id: string;
  incident_id: string;
  patch_proposal_id: string;
  validation_run_id: string;
  repository_id: string;
  repository_snapshot_id: string;
  
  branch_name: string;
  commit_sha?: string;
  external_pr_id?: string;
  external_pr_url?: string;
  
  status: string;
  created_at: string;
  updated_at: string;
}

export const PullRequestApi = {
  getPullRequests: () => 
    fetchApi<PullRequest[]>('/pull-requests'),
    
  getPullRequest: (id: string) => 
    fetchApi<PullRequest>(`/pull-requests/${id}`),
    
  createPullRequest: (incidentId: string, patchId: string, validationRunId: string) =>
    fetchApi<PullRequest>(`/pull-requests?incident_id=${incidentId}&patch_id=${patchId}&validation_run_id=${validationRunId}`, { method: 'POST' }),
};
