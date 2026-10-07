import { fetchApi } from './client';

export interface ReliabilityEvent {
  id: string;
  model_id: string;
  model_version_id?: string;
  event_type: string;
  source_type: string;
  source_id: string;
  title: string;
  severity?: string;
  status?: string;
  summary?: string;
  metadata_json: Record<string, unknown>;
  occurred_at: string;
  created_at: string;
}

export interface ReliabilityEdge {
  id: string;
  from_id: string;
  to_id: string;
  type: string;
}

export interface CausalGraph {
  nodes: ReliabilityEvent[];
  edges: ReliabilityEdge[];
}

export const ReliabilityApi = {
  getTimeline: (modelId: string, params?: { limit?: number; start_time?: string; end_time?: string }) => {
    let url = `/models/${modelId}/reliability/timeline`;
    if (params) {
      const searchParams = new URLSearchParams();
      if (params.limit) searchParams.append('limit', params.limit.toString());
      if (params.start_time) searchParams.append('start_time', params.start_time);
      if (params.end_time) searchParams.append('end_time', params.end_time);
      url += `?${searchParams.toString()}`;
    }
    return fetchApi<ReliabilityEvent[]>(url);
  },

  getIncidentGraph: (modelId: string, incidentEventId: string) => {
    return fetchApi<CausalGraph>(`/models/${modelId}/reliability/graph/${incidentEventId}`);
  },

  getIncidentGraphByIncidentId: (modelId: string, incidentId: string) => {
    return fetchApi<CausalGraph>(`/models/${modelId}/reliability/incidents/${incidentId}/graph`);
  }
};
