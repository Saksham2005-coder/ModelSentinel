import React, { useState, useEffect, useCallback } from 'react';
import { useParams, Link } from 'react-router-dom';
import { CheckCircle2, Circle, AlertCircle, XCircle, ChevronRight, Check, X } from 'lucide-react';
import { workflowsApi, WorkflowRun } from '../services/api/workflows';

const WorkflowDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [workflow, setWorkflow] = useState<WorkflowRun | null>(null);
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState(false);

  const fetchWorkflow = useCallback(async () => {
    if (!id) return;
    try {
      const data = await workflowsApi.getWorkflow(id);
      setWorkflow(data);
    } catch (error) {
      console.error(error);
    } finally {
      setLoading(false);
    }
  }, [id]);

  useEffect(() => {
    fetchWorkflow();
  }, [fetchWorkflow]);

  const handleApprove = async () => {
    if (!id) return;
    setActionLoading(true);
    try {
      const data = await workflowsApi.approveWorkflow(id, "Approved via UI");
      setWorkflow(data);
    } catch (error) {
      console.error(error);
    } finally {
      setActionLoading(false);
    }
  };

  const handleReject = async () => {
    if (!id) return;
    setActionLoading(true);
    try {
      const data = await workflowsApi.rejectWorkflow(id, "Rejected via UI");
      setWorkflow(data);
    } catch (error) {
      console.error(error);
    } finally {
      setActionLoading(false);
    }
  };

  if (loading || !workflow) {
    return <div className="p-8 text-text-secondary">Loading workflow...</div>;
  }

  return (
    <div className="p-8 max-w-4xl mx-auto">
      <div className="mb-8">
        <div className="flex items-center space-x-2 text-sm text-text-secondary mb-4">
          <Link to="/workflows" className="hover:text-text-primary transition-colors">Workflows</Link>
          <ChevronRight className="w-4 h-4" />
          <span className="text-text-primary">{workflow.id}</span>
        </div>
        
        <div className="flex justify-between items-start">
          <div>
            <h1 className="text-2xl font-semibold tracking-tight text-text-primary mb-2">{workflow.name}</h1>
            <p className="text-text-secondary">
              Type: {workflow.workflow_type} | Entity: {workflow.entity_type} {workflow.entity_id}
            </p>
          </div>
          <div className="flex items-center space-x-3 bg-background-primary px-4 py-2 rounded-lg border border-border">
            <span className="text-text-secondary text-sm font-medium">Status</span>
            <span className={`px-2 py-1 rounded text-xs font-bold ${
              workflow.status === 'COMPLETED' ? 'bg-status-success-soft text-status-success' :
              workflow.status === 'FAILED' ? 'bg-red-500/10 text-red-400' :
              workflow.status === 'WAITING_APPROVAL' ? 'bg-brand/10 text-brand-hover' :
              'bg-blue-500/10 text-blue-400'
            }`}>
              {workflow.status}
            </span>
          </div>
        </div>
      </div>

      <div className="bg-background-primary border border-border rounded-xl p-6">
        <h2 className="text-lg font-medium text-text-primary mb-6">Workflow Progress</h2>
        
        <div className="space-y-6">
          {workflow.steps.map((step, idx) => (
            <div key={step.id} className="relative flex items-start">
              {idx !== workflow.steps.length - 1 && (
                <div className="absolute left-3 top-8 bottom-0 w-px bg-background-secondary -ml-px h-full"></div>
              )}
              
              <div className="relative z-10 flex-shrink-0 w-6 h-6 flex items-center justify-center bg-background-primary rounded-full">
                {step.status === 'SUCCESS' ? (
                  <CheckCircle2 className="w-6 h-6 text-status-success" />
                ) : step.status === 'FAILED' ? (
                  <XCircle className="w-6 h-6 text-red-500" />
                ) : step.status === 'WAITING' ? (
                  <AlertCircle className="w-6 h-6 text-brand" />
                ) : step.status === 'RUNNING' ? (
                  <div className="w-5 h-5 rounded-full border-2 border-blue-500 border-t-transparent animate-spin" />
                ) : (
                  <Circle className="w-6 h-6 text-slate-700" />
                )}
              </div>
              
              <div className="ml-4 flex-1">
                <div className="flex items-center justify-between">
                  <h3 className={`font-medium ${step.status === 'PENDING' ? 'text-text-muted' : 'text-text-primary'}`}>
                    {step.name}
                  </h3>
                  {step.started_at && (
                    <span className="text-xs text-text-muted">
                      {new Date(step.started_at).toLocaleTimeString()}
                    </span>
                  )}
                </div>
                
                {step.error_message && (
                  <div className="mt-2 text-sm text-red-400 bg-red-900/10 border border-red-900/20 rounded p-2">
                    {step.error_message}
                  </div>
                )}

                {step.status === 'WAITING' && step.requires_approval && (
                  <div className="mt-4 p-4 bg-background-secondary rounded-lg border border-border-strong">
                    <p className="text-sm text-text-primary mb-4">
                      Human approval is required to proceed with <strong>{step.name}</strong>.
                    </p>
                    <div className="flex space-x-3">
                      <button
                        onClick={handleApprove}
                        disabled={actionLoading}
                        className="flex items-center space-x-2 px-4 py-2 bg-status-success hover:bg-status-success/90 text-background-base rounded-lg transition-colors text-sm font-medium disabled:opacity-50"
                      >
                        <Check className="w-4 h-4" />
                        <span>Approve & Continue</span>
                      </button>
                      <button
                        onClick={handleReject}
                        disabled={actionLoading}
                        className="flex items-center space-x-2 px-4 py-2 bg-background-elevated hover:bg-slate-600 text-text-primary rounded-lg transition-colors text-sm font-medium disabled:opacity-50"
                      >
                        <X className="w-4 h-4" />
                        <span>Reject</span>
                      </button>
                    </div>
                  </div>
                )}
                
                {step.approval && step.approval.status === 'APPROVED' && (
                  <div className="mt-2 text-sm text-status-success">
                    Approved by: {step.approval.approved_by || 'Unknown'} 
                    {step.approval.approval_role ? ` (${step.approval.approval_role})` : ''}
                  </div>
                )}
                
                {step.approval && step.approval.status === 'REJECTED' && (
                  <div className="mt-2 text-sm text-red-400">
                    Rejected by: {step.approval.rejected_by || 'Unknown'}
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default WorkflowDetail;
