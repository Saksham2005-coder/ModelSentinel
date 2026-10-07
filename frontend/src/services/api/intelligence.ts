import { fetchApi } from './client';

export interface ModelHealth {
  score: number;
  status: 'HEALTHY' | 'STABLE' | 'DEGRADED' | 'CRITICAL';
  breakdown: {
    performance: number;
    data_quality: number;
    feature_drift: number;
    prediction_stability: number;
    incident_state: number;
  };
}

export interface ModelHealthHistory {
  timestamp: string;
  score: number;
  status: 'HEALTHY' | 'STABLE' | 'DEGRADED' | 'CRITICAL';
  incidents_created: number;
  deployments: number;
}

export interface FeatureHealth {
  feature_name: string;
  feature_type: string;
  drift_score: number;
  status: string;
  trend: 'stable' | 'increasing' | 'decreasing';
  incident_count: number;
}

export interface SegmentHealth {
  segment_name: string;
  primary_metric: string;
  baseline_metric_value: number | null;
  current_metric_value: number;
  change: number;
  status: string;
}

export interface VersionComparison {
  metric: string;
  type: string;
  version_a: number | string | null;
  version_b: number | string | null;
  difference: number | null;
  is_regression: boolean;
}

export interface VersionComparisonResult {
  version_a_id: string;
  version_b_id: string;
  comparisons: VersionComparison[];
}

export interface ModelIntelligence {
  health: ModelHealth;
  history: ModelHealthHistory[];
  features: FeatureHealth[];
  segments: SegmentHealth[];
}

export class IntelligenceApi {
  static async getModelIntelligence(modelId: string, days: number = 30): Promise<ModelIntelligence> {
    return fetchApi(`/models/${modelId}/intelligence?days=${days}`);
  }

  static async getVersionComparison(modelId: string, v1: string, v2: string): Promise<VersionComparisonResult> {
    return fetchApi(`/models/${modelId}/versions/compare?v1=${v1}&v2=${v2}`);
  }
}

