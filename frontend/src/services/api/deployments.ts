/* eslint-disable @typescript-eslint/no-explicit-any */
import { fetchApi } from './client';

export interface DeploymentGateResult {
  patch_approved: boolean;
  validation_passed: boolean;
  regression_passed: boolean;
  security_passed: boolean;
  ci_passed: boolean;
  human_approved: boolean;
}

export interface DeploymentVerification {
  id: string;
  status: string;
  summary?: string;
  failure_reason?: string;
  started_at: string;
  completed_at?: string;
  observations?: any;
  baseline?: any;
}

export interface Deployment {
  id: string;
  pull_request_id: string;
  incident_id: string;
  commit_sha?: string;
  status: string;
  gate_result: DeploymentGateResult;
  block_reason?: string;
  policy_result?: any;
  approved_by?: string;
  deployed_at?: string;
  environment?: string;
  deployment_source?: string;
  created_at: string;
  updated_at?: string;
  verifications?: DeploymentVerification[];
}

export const DeploymentApi = {
  getDeployments: () => 
    fetchApi<Deployment[]>('/deployments'),
    
  getDeployment: (id: string) => 
    fetchApi<Deployment>(`/deployments/${id}`),
    
  evaluateGate: (prId: string) => 
    fetchApi<Deployment>(`/deployments/${prId}/evaluate`, { method: 'POST' }),
    
  recordDeployment: (id: string, environment: string, source: string) =>
    fetchApi<{status: string, deployed_at: string}>(`/deployments/${id}/record`, { 
      method: 'POST',
      body: JSON.stringify({ environment, deployment_source: source })
    }),
    
  startVerification: (id: string) =>
    fetchApi<{status: string, verification_id: string}>(`/deployments/${id}/verify/start`, { method: 'POST' }),
    
  evaluateHealth: (id: string) =>
    fetchApi<{status: string, summary: string, failure_reason: string, observations: any}>(`/deployments/${id}/verify/evaluate`, { method: 'POST' }),
};
