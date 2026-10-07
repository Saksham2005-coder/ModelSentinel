import { fetchApi } from './client';

export interface Telemetry {
  id: string;
  model_id: string;
  model_version_id: string;
  source: string;
  window_start: string;
  window_end: string;
  sample_count?: number;
  status: string;
  validation_errors?: string[];
  monitoring_run_id?: string;
  incident_id?: string;
  received_at: string;
  created_at: string;
  updated_at: string;
}

export const TelemetryApi = {
  getTelemetryList: (limit: number = 50) => {
    return fetchApi<Telemetry[]>(`/telemetry/?limit=${limit}`);
  },
  
  getTelemetryDetail: (id: string) => {
    return fetchApi<Telemetry>(`/telemetry/${id}`);
  },
  
  uploadTelemetry: (data: FormData) => {
    return fetchApi<Telemetry>('/telemetry/', {
      method: 'POST',
      body: data,
    });
  }
};
