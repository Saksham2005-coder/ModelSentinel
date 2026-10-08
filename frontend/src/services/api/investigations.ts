import { fetchApi } from './client';

export interface InvestigationEvent {
  id: string;
  investigation_id: string;
  event_type: string;
  title: string;
  message: string;
  tool_name?: string;
  status: string;
  metadata_json?: Record<string, unknown>;
  created_at: string;
}

export interface InvestigationEvidence {
  id: string;
  investigation_id: string;
  hypothesis_id?: string;
  evidence_type: string;
  source_type: string;
  source_id?: string;
  title: string;
  value_json?: Record<string, unknown>;
  relationship_type: string;
  explanation: string;
  created_at: string;
}

export interface InvestigationHypothesis {
  id: string;
  investigation_id: string;
  title: string;
  description: string;
  status: string;
  rank?: number;
  evidence_strength: string;
  created_at: string;
  updated_at: string;
  evidence_items: InvestigationEvidence[];
}

export interface Investigation {
  id: string;
  incident_id: string;
  status: string;
  summary?: string;
  current_step?: string;
  primary_hypothesis_id?: string;
  started_at?: string;
  completed_at?: string;
  created_at: string;
  updated_at: string;
}

export interface InvestigationDetail extends Investigation {
  events: InvestigationEvent[];
  hypotheses: InvestigationHypothesis[];
  evidence: InvestigationEvidence[];
}

export const InvestigationsApi = {
  createInvestigation: (incidentId: string) => 
    fetchApi<Investigation>(`/incidents/${incidentId}/investigations`, { method: 'POST' }),
  
  getInvestigations: (incidentId: string) => 
    fetchApi<Investigation[]>(`/incidents/${incidentId}/investigations`),
    
  getAllInvestigations: () =>
    fetchApi<Investigation[]>(`/investigations`),
    
  getInvestigation: (investigationId: string) => 
    fetchApi<InvestigationDetail>(`/investigations/${investigationId}`),
    
  startInvestigation: (investigationId: string) => 
    fetchApi<{message: string}>(`/investigations/${investigationId}/start`, { method: 'POST' }),
    
  cancelInvestigation: (investigationId: string) => 
    fetchApi<{message: string}>(`/investigations/${investigationId}/cancel`, { method: 'POST' }),
};
