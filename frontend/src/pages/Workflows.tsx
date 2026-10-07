import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Activity, Clock, CheckCircle, XCircle, AlertCircle } from 'lucide-react';
import { workflowsApi, WorkflowRun } from '../services/api/workflows';

const Workflows: React.FC = () => {
  const [workflows, setWorkflows] = useState<WorkflowRun[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchWorkflows = async () => {
      try {
        const data = await workflowsApi.listWorkflows();
        setWorkflows(data);
      } catch (error) {
        console.error("Failed to fetch workflows", error);
      } finally {
        setLoading(false);
      }
    };
    fetchWorkflows();
  }, []);

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'COMPLETED': return <CheckCircle className="w-5 h-5 text-emerald-400" />;
      case 'FAILED': return <XCircle className="w-5 h-5 text-red-400" />;
      case 'RUNNING': return <Activity className="w-5 h-5 text-blue-400" />;
      case 'WAITING_APPROVAL': return <AlertCircle className="w-5 h-5 text-amber-400" />;
      default: return <Clock className="w-5 h-5 text-slate-400" />;
    }
  };

  if (loading) {
    return <div className="p-8 text-slate-400">Loading workflows...</div>;
  }

  return (
    <div className="p-8">
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-2xl font-bold text-white mb-2">Workflow Orchestration</h1>
          <p className="text-slate-400">Manage and observe automated reliability workflows.</p>
        </div>
      </div>

      <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden">
        <table className="w-full text-left text-sm">
          <thead className="bg-slate-800/50 text-slate-400">
            <tr>
              <th className="px-6 py-4 font-medium">Status</th>
              <th className="px-6 py-4 font-medium">Workflow</th>
              <th className="px-6 py-4 font-medium">Target</th>
              <th className="px-6 py-4 font-medium">Started At</th>
              <th className="px-6 py-4 font-medium text-right">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800 text-slate-300">
            {workflows.length === 0 ? (
              <tr>
                <td colSpan={5} className="px-6 py-8 text-center text-slate-500">
                  No workflows found
                </td>
              </tr>
            ) : (
              workflows.map(wf => (
                <tr key={wf.id} className="hover:bg-slate-800/50 transition-colors">
                  <td className="px-6 py-4">
                    <div className="flex items-center space-x-2">
                      {getStatusIcon(wf.status)}
                      <span className="capitalize">{wf.status.replace('_', ' ')}</span>
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    <div className="font-medium text-slate-200">{wf.name}</div>
                    <div className="text-xs text-slate-500 mt-1">{wf.id}</div>
                  </td>
                  <td className="px-6 py-4">
                    <span className="px-2 py-1 rounded bg-slate-800 text-slate-300 text-xs">
                      {wf.entity_type}: {wf.entity_id}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-slate-400">
                    {wf.started_at ? new Date(wf.started_at).toLocaleString() : 'Not started'}
                  </td>
                  <td className="px-6 py-4 text-right">
                    <Link
                      to={`/workflows/${wf.id}`}
                      className="px-4 py-2 bg-blue-500/10 text-blue-400 hover:bg-blue-500/20 rounded-lg transition-colors inline-flex items-center"
                    >
                      View Details
                    </Link>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default Workflows;
