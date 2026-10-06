import { fetchApi } from './client';

export interface Factor {
  factor: string;
  contribution: number;
}

export interface BlastRadius {
  files: string[];
  models: string[];
  features: string[];
  regression_tests: string[];
  historical_incidents: string[];
}

export interface ChangeRiskAssessment {
  id: string;
  patch_proposal_id: string;
  risk_score: number;
  risk_level: string; // LOW, MODERATE, HIGH, CRITICAL
  factors: Factor[];
  blast_radius: BlastRadius;
  recommended_regressions: string[];
  created_at: string;
}

export const changeRiskService = {
  getRecentAssessments: async (): Promise<ChangeRiskAssessment[]> => {
    return await fetchApi<ChangeRiskAssessment[]>('/change-risk');
  },

  getAssessmentForPatch: async (patchId: string): Promise<ChangeRiskAssessment> => {
    return await fetchApi<ChangeRiskAssessment>(`/change-risk/${patchId}`);
  },
};
