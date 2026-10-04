import { fetchApi } from './client';

export interface MetricResult {
  id: string;
  monitoring_run_id: string;
  metric_name: string;
  metric_value: number;
  status: string;
  created_at: string;
}

export interface DataQualityResult {
  id: string;
  monitoring_run_id: string;
  metric_name: string;
  value: number;
  status: string;
  created_at: string;
}

export interface FeatureDriftResult {
  id: string;
  monitoring_run_id: string;
  feature_name: string;
  feature_type: string;
  drift_method: string;
  drift_score: number;
  status: string;
  created_at: string;
}

export interface PredictionDriftResult {
  id: string;
  monitoring_run_id: string;
  prediction_metric: string;
  value: number;
  status: string;
  created_at: string;
}

export interface SegmentResult {
  id: string;
  monitoring_run_id: string;
  segment_name: string;
  sample_count: number;
  primary_metric: string;
  baseline_metric_value: number | null;
  current_metric_value: number;
  change: number | null;
  status: string;
}

export interface MonitoringRun {
  id: string;
  model_id: string;
  model_version_id: string;
  status: string;
  health_summary: string | null;
  started_at: string;
  completed_at: string;
  created_at: string;
}

export const MonitoringApi = {
  getRuns: (modelId: string) => 
    fetchApi<MonitoringRun[]>(`/models/${modelId}/monitoring/runs`),
    
  runMonitoring: (modelId: string, versionId: string) => 
    fetchApi<MonitoringRun>(`/models/${modelId}/monitoring/runs`, {
        method: 'POST',
        body: JSON.stringify({
            model_version_id: versionId,
            run_type: 'batch'
        })
    }),
    
  getMetrics: (modelId: string, runId?: string) => 
    fetchApi<MetricResult[]>(`/models/${modelId}/monitoring/metrics${runId ? `?run_id=${runId}` : ''}`),
    
  getDataQuality: (modelId: string, runId?: string) => 
    fetchApi<DataQualityResult[]>(`/models/${modelId}/monitoring/data-quality${runId ? `?run_id=${runId}` : ''}`),
    
  getFeatureDrift: (modelId: string, runId?: string) => 
    fetchApi<FeatureDriftResult[]>(`/models/${modelId}/monitoring/drift${runId ? `?run_id=${runId}` : ''}`),
    
  getPredictionDrift: (modelId: string, runId?: string) => 
    fetchApi<PredictionDriftResult[]>(`/models/${modelId}/monitoring/predictions${runId ? `?run_id=${runId}` : ''}`),
    
  getSegments: (modelId: string, runId?: string) => 
    fetchApi<SegmentResult[]>(`/models/${modelId}/monitoring/segments${runId ? `?run_id=${runId}` : ''}`)
};
