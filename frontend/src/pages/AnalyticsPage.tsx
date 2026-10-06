import React, { useEffect, useState } from 'react';
import { analyticsApi, OverviewMetrics, IncidentAnalytics, ModelReliability, RootCauseTrend, DeploymentHealth, FixEffectiveness } from '../services/api/analytics';
import { Link } from 'react-router-dom';
import { Activity, BarChart2, Shield, GitMerge } from 'lucide-react';

export const AnalyticsPage: React.FC = () => {
  const [loading, setLoading] = useState(true);
  const [days, setDays] = useState<number | undefined>(30);
  
  const [overview, setOverview] = useState<OverviewMetrics | null>(null);
  const [incidents, setIncidents] = useState<IncidentAnalytics | null>(null);
  const [models, setModels] = useState<ModelReliability[]>([]);
  const [rootCauses, setRootCauses] = useState<RootCauseTrend[]>([]);
  const [deployments, setDeployments] = useState<DeploymentHealth | null>(null);
  useEffect(() => {
    if (incidents) console.debug('Incidents:', incidents);
    if (deployments) console.debug('Deployments:', deployments);
  }, [incidents, deployments]);
  const [fixEffectiveness, setFixEffectiveness] = useState<FixEffectiveness | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      try {
        const [ovData, incData, modData, rcData, depData, fixData] = await Promise.all([
          analyticsApi.getOverview(days),
          analyticsApi.getIncidents(days),
          analyticsApi.getModels(days),
          analyticsApi.getRootCauses(days),
          analyticsApi.getDeployments(days),
          analyticsApi.getFixEffectiveness(days)
        ]);
        setOverview(ovData);
        setIncidents(incData);
        setModels(modData);
        setRootCauses(rcData);
        setDeployments(depData);
        setFixEffectiveness(fixData);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [days]);

  return (
    <div className="min-h-screen bg-neutral-900 text-neutral-100 p-8 pt-24 font-sans selection:bg-indigo-500/30">
      <div className="max-w-7xl mx-auto space-y-8">
        
        {/* Header & Filters */}
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
          <div>
            <h1 className="text-3xl font-bold tracking-tight text-white flex items-center gap-3">
              <BarChart2 className="w-8 h-8 text-indigo-400" />
              ML Reliability Analytics
            </h1>
            <p className="text-neutral-400 mt-1">Engineering intelligence and deterministic reliability metrics.</p>
          </div>
          <div className="flex bg-neutral-800/80 p-1 rounded-lg border border-neutral-700/50">
            {[7, 30, 90, undefined].map((d) => (
              <button
                key={d || 'all'}
                onClick={() => setDays(d)}
                className={`px-4 py-1.5 rounded-md text-sm font-medium transition-all ${days === d ? 'bg-indigo-500/20 text-indigo-300' : 'text-neutral-400 hover:text-white hover:bg-neutral-700/50'}`}
              >
                {d ? `${d} Days` : 'All Time'}
              </button>
            ))}
          </div>
        </div>

        {loading ? (
          <div className="flex items-center justify-center h-64 text-neutral-400 animate-pulse">
            Calculating deterministically...
          </div>
        ) : (
          <div className="space-y-8">
            
            {/* Overview */}
            {overview && (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                <div className="bg-neutral-800/50 border border-neutral-700/50 rounded-xl p-6 shadow-xl relative overflow-hidden group">
                  <div className="absolute inset-0 bg-gradient-to-br from-indigo-500/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity"></div>
                  <h3 className="text-sm font-medium text-neutral-400 mb-2">Reliability Score</h3>
                  <div className="flex items-end gap-2">
                    <span className={`text-4xl font-bold tracking-tight ${overview.reliability_score > 80 ? 'text-emerald-400' : overview.reliability_score > 50 ? 'text-yellow-400' : 'text-red-400'}`}>
                      {overview.reliability_score}
                    </span>
                    <span className="text-neutral-500 mb-1">/ 100</span>
                  </div>
                </div>

                <div className="bg-neutral-800/50 border border-neutral-700/50 rounded-xl p-6 shadow-xl relative overflow-hidden group">
                  <div className="absolute inset-0 bg-gradient-to-br from-emerald-500/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity"></div>
                  <h3 className="text-sm font-medium text-neutral-400 mb-2">Regression Coverage</h3>
                  <div className="text-4xl font-bold tracking-tight text-white">
                    {overview.regression_coverage.toFixed(1)}%
                  </div>
                </div>

                <div className="bg-neutral-800/50 border border-neutral-700/50 rounded-xl p-6 shadow-xl relative overflow-hidden group">
                  <div className="absolute inset-0 bg-gradient-to-br from-yellow-500/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity"></div>
                  <h3 className="text-sm font-medium text-neutral-400 mb-2">Mean Time to Resolve (MTTR)</h3>
                  <div className="text-4xl font-bold tracking-tight text-white">
                    {overview.mttr_minutes !== null ? `${overview.mttr_minutes.toFixed(1)}m` : 'Insufficient Data'}
                  </div>
                </div>

                <div className="bg-neutral-800/50 border border-neutral-700/50 rounded-xl p-6 shadow-xl relative overflow-hidden group">
                  <div className="absolute inset-0 bg-gradient-to-br from-red-500/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity"></div>
                  <h3 className="text-sm font-medium text-neutral-400 mb-2">Post-Deploy Degradation</h3>
                  <div className="text-4xl font-bold tracking-tight text-white">
                    {overview.deployment_degradation_rate.toFixed(1)}%
                  </div>
                </div>
              </div>
            )}

            {/* Models Table */}
            <div className="bg-neutral-800/50 border border-neutral-700/50 rounded-xl shadow-xl overflow-hidden">
              <div className="p-6 border-b border-neutral-700/50">
                <h2 className="text-xl font-bold text-white flex items-center gap-2">
                  <Activity className="w-5 h-5 text-emerald-400" />
                  Model Reliability
                </h2>
              </div>
              <div className="overflow-x-auto">
                <table className="w-full text-sm text-left">
                  <thead className="text-xs text-neutral-400 uppercase bg-neutral-900/50">
                    <tr>
                      <th className="px-6 py-4 font-medium">Model</th>
                      <th className="px-6 py-4 font-medium text-center">Score</th>
                      <th className="px-6 py-4 font-medium text-center">Incidents (Critical)</th>
                      <th className="px-6 py-4 font-medium text-center">Validation Success</th>
                      <th className="px-6 py-4 font-medium text-center">Regression Coverage</th>
                      <th className="px-6 py-4 font-medium text-center">Degradation Rate</th>
                      <th className="px-6 py-4 font-medium text-center">MTTR</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-neutral-800">
                    {models.map((model) => (
                      <tr key={model.model_id} className="hover:bg-neutral-800/30 transition-colors">
                        <td className="px-6 py-4 font-medium text-white">
                          <Link to={`/analytics/models/${model.model_id}`} className="text-indigo-400 hover:text-indigo-300">
                            {model.model_name}
                          </Link>
                        </td>
                        <td className="px-6 py-4 text-center">
                          <span className={`px-2 py-1 rounded text-xs font-medium ${model.reliability_score > 80 ? 'bg-emerald-500/10 text-emerald-400' : 'bg-yellow-500/10 text-yellow-400'}`}>
                            {model.reliability_score}
                          </span>
                        </td>
                        <td className="px-6 py-4 text-center text-neutral-300">
                          {model.incidents} <span className="text-red-400">({model.critical_incidents})</span>
                        </td>
                        <td className="px-6 py-4 text-center text-neutral-300">
                          {model.validation_success !== null ? `${model.validation_success.toFixed(1)}%` : '-'}
                        </td>
                        <td className="px-6 py-4 text-center text-neutral-300">
                          {model.regression_coverage.toFixed(1)}%
                        </td>
                        <td className="px-6 py-4 text-center text-neutral-300">
                          {model.degradation_rate.toFixed(1)}%
                        </td>
                        <td className="px-6 py-4 text-center text-neutral-300">
                          {model.mttr_minutes !== null ? `${model.mttr_minutes.toFixed(1)}m` : '-'}
                        </td>
                      </tr>
                    ))}
                    {models.length === 0 && (
                      <tr>
                        <td colSpan={7} className="px-6 py-8 text-center text-neutral-500">
                          No model analytics data available for this period.
                        </td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
              {/* Root Causes */}
              <div className="bg-neutral-800/50 border border-neutral-700/50 rounded-xl shadow-xl overflow-hidden">
                <div className="p-6 border-b border-neutral-700/50">
                  <h2 className="text-xl font-bold text-white flex items-center gap-2">
                    <Shield className="w-5 h-5 text-rose-400" />
                    Recurring Root Causes
                  </h2>
                </div>
                <div className="p-6">
                  {rootCauses.length > 0 ? (
                    <div className="space-y-4">
                      {rootCauses.map(rc => (
                        <div key={rc.root_cause} className="bg-neutral-900/50 border border-neutral-800 rounded-lg p-4 flex items-center justify-between">
                          <div>
                            <h3 className="font-medium text-neutral-200 capitalize">{rc.root_cause.replace(/_/g, ' ')}</h3>
                            <p className="text-xs text-neutral-400 mt-1">
                              {rc.frequency} incidents across {rc.affected_models} models
                            </p>
                          </div>
                          <div className="text-right">
                            <div className={`text-sm font-bold ${rc.successful_fix_rate < 80 ? 'text-rose-400' : 'text-emerald-400'}`}>
                              {rc.successful_fix_rate.toFixed(1)}% Fix Rate
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="text-center text-neutral-500 py-8">No recurring root causes identified.</div>
                  )}
                </div>
              </div>

              {/* Fix Effectiveness */}
              <div className="bg-neutral-800/50 border border-neutral-700/50 rounded-xl shadow-xl overflow-hidden">
                <div className="p-6 border-b border-neutral-700/50">
                  <h2 className="text-xl font-bold text-white flex items-center gap-2">
                    <GitMerge className="w-5 h-5 text-indigo-400" />
                    Closed-Loop Effectiveness
                  </h2>
                </div>
                <div className="p-6">
                  {fixEffectiveness ? (
                    <div className="space-y-6">
                      <div>
                        <div className="flex justify-between text-sm mb-1">
                          <span className="text-neutral-400">Patch Validation Success</span>
                          <span className="font-medium text-white">{fixEffectiveness.patch_validation_success_rate.toFixed(1)}%</span>
                        </div>
                        <div className="w-full bg-neutral-900 rounded-full h-2">
                          <div className="bg-indigo-500 h-2 rounded-full" style={{ width: `${fixEffectiveness.patch_validation_success_rate}%` }}></div>
                        </div>
                      </div>

                      <div>
                        <div className="flex justify-between text-sm mb-1">
                          <span className="text-neutral-400">Deployment Health Success</span>
                          <span className="font-medium text-white">{fixEffectiveness.deployment_health_success_rate.toFixed(1)}%</span>
                        </div>
                        <div className="w-full bg-neutral-900 rounded-full h-2">
                          <div className="bg-emerald-500 h-2 rounded-full" style={{ width: `${fixEffectiveness.deployment_health_success_rate}%` }}></div>
                        </div>
                      </div>

                      <div>
                        <div className="flex justify-between text-sm mb-1">
                          <span className="text-neutral-400">Full-Loop Completion (Detected → Verified)</span>
                          <span className="font-medium text-white">{fixEffectiveness.full_loop_completion_rate.toFixed(1)}%</span>
                        </div>
                        <div className="w-full bg-neutral-900 rounded-full h-2">
                          <div className="bg-purple-500 h-2 rounded-full" style={{ width: `${fixEffectiveness.full_loop_completion_rate}%` }}></div>
                        </div>
                      </div>
                      
                      <div className="pt-4 border-t border-neutral-800 flex justify-between text-xs text-neutral-500">
                        <span>{fixEffectiveness.funnel.detected} Detected</span>
                        <span>→</span>
                        <span>{fixEffectiveness.funnel.validated} Validated</span>
                        <span>→</span>
                        <span>{fixEffectiveness.funnel.deployed} Deployed</span>
                        <span>→</span>
                        <span className="text-emerald-400">{fixEffectiveness.funnel.verified_healthy} Healthy</span>
                      </div>
                    </div>
                  ) : (
                     <div className="text-center text-neutral-500 py-8">Insufficient data.</div>
                  )}
                </div>
              </div>
            </div>

          </div>
        )}
      </div>
    </div>
  );
};
