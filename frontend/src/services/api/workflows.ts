import { fetchApi } from './client';

export interface WorkflowApproval {
  id: string;
  status: 'PENDING' | 'APPROVED' | 'REJECTED';
  requested_at: string;
  approved_by?: string;
  approved_at?: string;
  approval_role?: string;
  approval_comment?: string;
  rejected_by?: string;
  rejected_at?: string;
  rejection_comment?: string;
}

export interface WorkflowStepRun {
  id: string;
  workflow_run_id: string;
  name: string;
  step_type: string;
  order: number;
  is_automatic: boolean;
  requires_approval: boolean;
  status: 'PENDING' | 'RUNNING' | 'SUCCESS' | 'FAILED' | 'SKIPPED' | 'WAITING' | 'BLOCKED';
  attempt_count: number;
  max_attempts: number;
  started_at: string | null;
  completed_at: string | null;
  error_message: string | null;
  approval?: WorkflowApproval | null;
}

export interface WorkflowRun {
  id: string;
  name: string;
  workflow_type: string;
  description: string | null;
  status: 'PENDING' | 'RUNNING' | 'WAITING_APPROVAL' | 'PAUSED' | 'COMPLETED' | 'FAILED' | 'CANCELLED';
  entity_type: string | null;
  entity_id: string | null;
  started_at: string | null;
  completed_at: string | null;
  created_at: string;
  steps: WorkflowStepRun[];
}

export const workflowsApi = {
  listWorkflows: async (): Promise<WorkflowRun[]> => {
    return fetchApi('/workflows/');
  },

  getWorkflow: async (id: string): Promise<WorkflowRun> => {
    return fetchApi(`/workflows/${id}`);
  },

  startWorkflow: async (id: string): Promise<WorkflowRun> => {
    return fetchApi(`/workflows/${id}/start`, { method: 'POST' });
  },

  resumeWorkflow: async (id: string): Promise<WorkflowRun> => {
    return fetchApi(`/workflows/${id}/resume`, { method: 'POST' });
  },

  cancelWorkflow: async (id: string): Promise<WorkflowRun> => {
    return fetchApi(`/workflows/${id}/cancel`, { method: 'POST' });
  },

  approveWorkflow: async (id: string, comments: string = ''): Promise<WorkflowRun> => {
    return fetchApi(`/workflows/${id}/approve`, {
      method: 'POST',
      body: JSON.stringify({ comments })
    });
  },

  rejectWorkflow: async (id: string, comments: string = ''): Promise<WorkflowRun> => {
    return fetchApi(`/workflows/${id}/reject`, {
      method: 'POST',
      body: JSON.stringify({ comments })
    });
  },
  
  createWorkflow: async (name: string, workflowType: string, entityType: string, entityId: string): Promise<WorkflowRun> => {
    return fetchApi(`/workflows/?name=${encodeURIComponent(name)}&workflow_type=${workflowType}&entity_type=${entityType}&entity_id=${entityId}`, { method: 'POST' });
  }
};
