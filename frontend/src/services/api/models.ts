import { fetchApi } from './client';

export interface Model {
  id: string;
  name: string;
  slug: string;
  description?: string;
  framework: string;
  task_type: string;
  problem_type?: string;
  primary_metric: string;
  owner?: string;
  status: string;
  environment: string;
  repository_id?: string;
  created_at: string;
  updated_at: string;
}

export interface ModelVersion {
  id: string;
  model_id: string;
  version: string;
  description?: string;
  artifact_uri?: string;
  git_commit?: string;
  framework_version?: string;
  python_version?: string;
  is_active: boolean;
  created_at: string;
}

export interface Metric {
  id: string;
  model_version_id: string;
  metric_name: string;
  metric_value: number;
  dataset_name?: string;
  evaluation_type?: string;
  recorded_at: string;
}

export interface ModelListResponse {
  items: Model[];
  total: number;
  page: number;
  limit: number;
}

export interface ModelDetailResponse extends Model {
  versions: ModelVersion[];
}

export interface ModelCreate {
  name: string;
  slug: string;
  description?: string;
  framework: string;
  task_type: string;
  problem_type?: string;
  primary_metric: string;
  owner?: string;
  status?: string;
  environment?: string;
  repository_id?: string;
}

export interface ModelVersionCreate {
  version: string;
  description?: string;
  artifact_uri?: string;
  git_commit?: string;
  framework_version?: string;
  python_version?: string;
  is_active?: boolean;
}

export const ModelsApi = {
  getModels: (params?: Record<string, string | number | boolean>) => {
    const searchParams = new URLSearchParams();
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (value) searchParams.append(key, value.toString());
      });
    }
    const qs = searchParams.toString();
    return fetchApi<ModelListResponse>(`/models${qs ? `?${qs}` : ''}`);
  },

  getModel: (id: string) => 
    fetchApi<ModelDetailResponse>(`/models/${id}`),

  createModel: (data: ModelCreate) => 
    fetchApi<Model>('/models', {
      method: 'POST',
      body: JSON.stringify(data)
    }),

  updateModel: (id: string, data: Partial<ModelCreate>) => 
    fetchApi<Model>(`/models/${id}`, {
      method: 'PATCH',
      body: JSON.stringify(data)
    }),

  deleteModel: (id: string) => 
    fetchApi<void>(`/models/${id}`, { method: 'DELETE' }),

  getVersions: (modelId: string) =>
    fetchApi<ModelVersion[]>(`/models/${modelId}/versions`),

  createVersion: (modelId: string, data: ModelVersionCreate) =>
    fetchApi<ModelVersion>(`/models/${modelId}/versions`, {
      method: 'POST',
      body: JSON.stringify(data)
    }),

  activateVersion: (modelId: string, versionId: string) =>
    fetchApi<ModelVersion>(`/models/${modelId}/versions/${versionId}/activate`, {
      method: 'POST'
    }),

  getMetrics: (modelId: string) =>
    fetchApi<Metric[]>(`/models/${modelId}/metrics`)
};
