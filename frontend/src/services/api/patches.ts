import { fetchApi } from './client';

export interface PatchFileChange {
  id: string;
  file_path: string;
  change_type: string;
  target_symbol?: string;
  start_line?: number;
  end_line?: number;
  rationale: string;
  additions: number;
  deletions: number;
  diff_text: string;
}

export interface PatchReview {
  id: string;
  reviewer_type: string;
  decision: string;
  comment?: string;
  created_at: string;
}

export interface PatchProposal {
  id: string;
  investigation_id: string;
  incident_id: string;
  repository_id: string;
  version: number;
  status: string;
  summary: string;
  rationale: string;
  expected_behavior: string;
  risk_summary?: {
    level: string;
    reasons: string[];
    stats: Record<string, number>;
  };
  file_changes: PatchFileChange[];
  reviews: PatchReview[];
  created_at: string;
}

export interface PatchPlan {
  problem_statement: string;
  evidence_summary: string;
  intended_behavior: string;
  affected_files: { file_path: string; relevance?: string }[];
  test_changes: string[];
  risks: string[];
  assumptions: string[];
}

export const PatchesApi = {
  plan: (investigationId: string) => 
    fetchApi<PatchPlan>(`/investigations/${investigationId}/patches/plan`, { method: 'POST' }),
  
  generate: (investigationId: string, plan: PatchPlan, parentPatchId?: string, feedback?: string) => {
    let url = `/investigations/${investigationId}/patches`;
    const params = new URLSearchParams();
    if (parentPatchId) params.append('parent_patch_id', parentPatchId);
    if (feedback) params.append('feedback', feedback);
    const qs = params.toString();
    if (qs) url += `?${qs}`;
    
    return fetchApi<PatchProposal>(url, {
      method: 'POST',
      body: JSON.stringify(plan)
    });
  },
  
  list: (investigationId: string) => 
    fetchApi<PatchProposal[]>(`/investigations/${investigationId}/patches`),
  
  get: (patchId: string) => 
    fetchApi<PatchProposal>(`/patches/${patchId}`),
  
  review: (patchId: string, decision: 'approve' | 'reject' | 'request_changes', comment?: string) => 
    fetchApi<PatchProposal>(`/patches/${patchId}/review`, {
      method: 'POST',
      body: JSON.stringify({ decision, comment, reviewer_type: 'human' })
    })
};
