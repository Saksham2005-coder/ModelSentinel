import { fetchApi } from './client';

export interface EngineeringOverview {
  reliability_score: number;
  total_incidents: number;
  models_at_risk: number;
  active_slo_pressure: number;
}

export interface ReliabilityTrend {
  timestamp: string;
  incidents: number;
  reliability_score: number;
}

export interface ReliabilityTrendsResponse {
  trends: ReliabilityTrend[];
  direction: string;
  data_sufficiency: string;
}

export interface ModelComparison {
  model_id: string;
  model_name: string;
  reliability_score: number;
  incidents: number;
  critical_incidents: number;
  mttr_minutes: number | null;
  deployment_health: number;
  slo_breaches: number;
  status: string;
  trend: string;
}

export interface EngineeringEffectiveness {
  patch_validation_success_rate: number;
  deployment_health_success_rate: number;
}

export interface RootCauseIntelligence {
  root_cause: string;
  frequency: number;
  successful_fix_rate: number;
  severity: string;
}

export interface Hotspot {
  component: string;
  hotspot_score: number;
  category: string;
  incident_pressure: number;
}

export interface SloIntelligence {
  total_objectives: number;
  slo_compliance_rate: number;
  average_remaining_budget: number;
  active_alerts: number;
}

export interface ReliabilityDriver {
  driver: string;
  evidence_count: number;
  affected_models: number;
  confidence: string;
}

export const engineeringIntelligenceApi = {
  getOverview: (days?: number, modelId?: string) => {
    const params = new URLSearchParams();
    if (days) params.append('time_range_days', days.toString());
    if (modelId) params.append('model_id', modelId);
    return fetchApi<EngineeringOverview>(`/analytics/engineering-overview?${params.toString()}`);
  },
  
  getTrends: (days?: number, modelId?: string) => {
    const params = new URLSearchParams();
    if (days) params.append('time_range_days', days.toString());
    if (modelId) params.append('model_id', modelId);
    return fetchApi<ReliabilityTrendsResponse>(`/analytics/reliability-trends?${params.toString()}`);
  },

  getModelsComparison: (days?: number) => {
    const params = new URLSearchParams();
    if (days) params.append('time_range_days', days.toString());
    return fetchApi<ModelComparison[]>(`/analytics/models/comparison?${params.toString()}`);
  },

  getEffectiveness: (days?: number, modelId?: string) => {
    const params = new URLSearchParams();
    if (days) params.append('time_range_days', days.toString());
    if (modelId) params.append('model_id', modelId);
    return fetchApi<EngineeringEffectiveness>(`/analytics/engineering-effectiveness?${params.toString()}`);
  },

  getRootCauses: (days?: number, modelId?: string) => {
    const params = new URLSearchParams();
    if (days) params.append('time_range_days', days.toString());
    if (modelId) params.append('model_id', modelId);
    return fetchApi<RootCauseIntelligence[]>(`/analytics/root-causes/intelligence?${params.toString()}`);
  },

  getHotspots: (days?: number) => {
    const params = new URLSearchParams();
    if (days) params.append('time_range_days', days.toString());
    return fetchApi<Hotspot[]>(`/analytics/hotspots?${params.toString()}`);
  },

  getSloIntelligence: (days?: number, modelId?: string) => {
    const params = new URLSearchParams();
    if (days) params.append('time_range_days', days.toString());
    if (modelId) params.append('model_id', modelId);
    return fetchApi<SloIntelligence>(`/analytics/slo-intelligence?${params.toString()}`);
  },

  getDrivers: (days?: number, modelId?: string) => {
    const params = new URLSearchParams();
    if (days) params.append('time_range_days', days.toString());
    if (modelId) params.append('model_id', modelId);
    return fetchApi<ReliabilityDriver[]>(`/analytics/reliability-drivers?${params.toString()}`);
  }
};
