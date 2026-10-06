import { fetchApi } from './client';

export interface DeploymentGateResult {
  patch_approved: boolean;
  validation_passed: boolean;
  regression_passed: boolean;
  security_passed: boolean;
  ci_passed: boolean;
  human_approved: boolean;
}

export interface Deployment {
  id: string;
  pull_request_id: string;
  incident_id: string;
  commit_sha?: string;
  status: string;
  gate_result: DeploymentGateResult;
  block_reason?: string;
  approved_by?: string;
  created_at: string;
  updated_at?: string;
}

export const DeploymentApi = {
  getDeployments: () => 
    fetchApi<Deployment[]>('/deployments'),
    
  evaluateGate: (prId: string) => 
    fetchApi<Deployment>(`/deployments/${prId}/evaluate`, { method: 'POST' }),
};
