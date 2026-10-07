import { fetchApi } from './client';

export interface OverviewMetrics {
  reliability_score: number;
  score_contributors: Record<string, number>;
  total_incidents: number;
  open_incidents: number;
  resolved_incidents: number;
  critical_incidents: number;
  mttd_minutes: number | null;
  mttr_minutes: number | null;
  deployment_degradation_rate: number;
  regression_coverage: number;
}

export interface IncidentAnalytics {
  total_incidents: number;
  critical_incidents: number;
  warning_incidents: number;
  resolved_incidents: number;
  recurring_incidents: number;
  severity_distribution: { name: string; value: number }[];
  status_distribution: { name: string; value: number }[];
  category_distribution: { name: string; value: number }[];
}

export interface ModelReliability {
  model_id: string;
  model_name: string;
  incidents: number;
  critical_incidents: number;
  validation_success: number | null;
  regression_coverage: number;
  degradation_rate: number;
  mttr_minutes: number | null;
  reliability_score: number;
}

export interface RootCauseTrend {
  root_cause: string;
  frequency: number;
  affected_models: number;
  successful_fix_rate: number;
  severity: string;
}

export interface DeploymentHealth {
  total_deployments: number;
  healthy: number;
  degraded: number;
  failed: number;
  verification_pending: number;
  post_deployment_degradation_rate: number;
}

export interface FixEffectiveness {
  patch_validation_success_rate: number;
  deployment_health_success_rate: number;
  full_loop_completion_rate: number;
  funnel: {
    detected: number;
    investigated: number;
    validated: number;
    learned: number;
    deployed: number;
    verified_healthy: number;
  };
}

export interface PolicyMetrics {
  total_evaluations: number;
  allowed: number;
  blocked: number;
  review_required: number;
  target_distribution: { name: string; value: number }[];
}

export const analyticsApi = {
  getOverview: (days?: number, modelId?: string) => {
    const params = new URLSearchParams();
    if (days) params.append('time_range_days', days.toString());
    if (modelId) params.append('model_id', modelId);
    return fetchApi<OverviewMetrics>(`/analytics/overview?${params.toString()}`);
  },
  
  getIncidents: (days?: number) => {
    const params = new URLSearchParams();
    if (days) params.append('time_range_days', days.toString());
    return fetchApi<IncidentAnalytics>(`/analytics/incidents?${params.toString()}`);
  },

  getModels: (days?: number) => {
    const params = new URLSearchParams();
    if (days) params.append('time_range_days', days.toString());
    return fetchApi<ModelReliability[]>(`/analytics/models?${params.toString()}`);
  },

  getModelDetail: (modelId: string, days?: number) => {
    const params = new URLSearchParams();
    if (days) params.append('time_range_days', days.toString());
    return fetchApi<OverviewMetrics>(`/analytics/models/${modelId}?${params.toString()}`);
  },

  getRootCauses: (days?: number) => {
    const params = new URLSearchParams();
    if (days) params.append('time_range_days', days.toString());
    return fetchApi<RootCauseTrend[]>(`/analytics/root-causes?${params.toString()}`);
  },

  getDeployments: (days?: number) => {
    const params = new URLSearchParams();
    if (days) params.append('time_range_days', days.toString());
    return fetchApi<DeploymentHealth>(`/analytics/deployments?${params.toString()}`);
  },

  getFixEffectiveness: (days?: number) => {
    const params = new URLSearchParams();
    if (days) params.append('time_range_days', days.toString());
    return fetchApi<FixEffectiveness>(`/analytics/fix-effectiveness?${params.toString()}`);
  },

  getPolicyMetrics: (days?: number) => {
    const params = new URLSearchParams();
    if (days) params.append('time_range_days', days.toString());
    return fetchApi<PolicyMetrics>(`/analytics/policies?${params.toString()}`);
  }
};
