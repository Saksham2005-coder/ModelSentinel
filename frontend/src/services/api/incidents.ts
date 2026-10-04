import { fetchApi } from './client';

export interface IncidentSignal {
  id: string;
  source_type: string;
  source_id?: string;
  signal_name: string;
  observed_value?: number;
  threshold?: number;
  comparison?: string;
  status: string;
  explanation?: string;
  created_at: string;
}

export interface IncidentEvent {
  id: string;
  event_type: string;
  message: string;
  metadata_json?: Record<string, unknown>;
  created_at: string;
}

export interface IncidentEvidence {
  id: string;
  monitoring_run_id: string;
  snapshot: Record<string, unknown>;
  created_at: string;
}

export interface Incident {
  id: string;
  incident_key: string;
  model_id: string;
  model_version_id: string;
  title: string;
  summary?: string;
  severity: string;
  status: string;
  category: string;
  detected_at: string;
  last_seen_at: string;
  acknowledged_at?: string;
  resolved_at?: string;
  created_at: string;
  updated_at: string;
}

export interface IncidentDetail extends Incident {
  signals: IncidentSignal[];
  events: IncidentEvent[];
  evidence?: IncidentEvidence;
}

export const IncidentApi = {
  getIncidents: (params?: { 
    model_id?: string; 
    severity?: string; 
    status?: string; 
    category?: string; 
    skip?: number; 
    limit?: number 
  }) => {
    const query = new URLSearchParams();
    if (params) {
      Object.entries(params).forEach(([k, v]) => {
        if (v !== undefined) query.append(k, String(v));
      });
    }
    const qStr = query.toString();
    return fetchApi<Incident[]>(`/incidents${qStr ? `?${qStr}` : ''}`);
  },
  
  getIncident: (id: string) => 
    fetchApi<IncidentDetail>(`/incidents/${id}`),
    
  acknowledge: (id: string) => 
    fetchApi<Incident>(`/incidents/${id}/acknowledge`, { method: 'POST' }),
    
  startInvestigation: (id: string) => 
    fetchApi<Incident>(`/incidents/${id}/start-investigation`, { method: 'POST' }),
    
  resolve: (id: string, resolution_note?: string) => 
    fetchApi<Incident>(`/incidents/${id}/resolve`, {
      method: 'POST',
      body: JSON.stringify({ resolution_note })
    }),
    
  suppress: (id: string) => 
    fetchApi<Incident>(`/incidents/${id}/suppress`, { method: 'POST' }),
    
  detectFromRun: (modelId: string, runId: string) => 
    fetchApi<{ message: string, incident_id?: string }>(`/models/${modelId}/monitoring/runs/${runId}/detect-incidents`, { method: 'POST' })
};
