import React, { useEffect, useState } from 'react';
import { 
  engineeringIntelligenceApi, 
  EngineeringOverview, 
  ReliabilityTrendsResponse,
  ModelComparison,
  EngineeringEffectiveness,
  RootCauseIntelligence,
  Hotspot,
  SloIntelligence,
  ReliabilityDriver
} from '../services/api/engineering_intelligence';
import { Brain, Activity, ShieldAlert, Target, GitCommit, AlertTriangle, TrendingUp, AlertOctagon } from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, ResponsiveContainer } from 'recharts';

export const EngineeringIntelligencePage: React.FC = () => {
  const [loading, setLoading] = useState(true);
  const [days, setDays] = useState<number | undefined>(30);
  
  const [overview, setOverview] = useState<EngineeringOverview | null>(null);
  const [trends, setTrends] = useState<ReliabilityTrendsResponse | null>(null);
  const [models, setModels] = useState<ModelComparison[]>([]);
  const [effectiveness, setEffectiveness] = useState<EngineeringEffectiveness | null>(null);
  const [rootCauses, setRootCauses] = useState<RootCauseIntelligence[]>([]);
  const [hotspots, setHotspots] = useState<Hotspot[]>([]);
  const [slo, setSlo] = useState<SloIntelligence | null>(null);
  const [drivers, setDrivers] = useState<ReliabilityDriver[]>([]);

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      try {
        const [ovData, trData, modData, effData, rcData, hotData, sloData, drData] = await Promise.all([
          engineeringIntelligenceApi.getOverview(days),
          engineeringIntelligenceApi.getTrends(days),
          engineeringIntelligenceApi.getModelsComparison(days),
          engineeringIntelligenceApi.getEffectiveness(days),
          engineeringIntelligenceApi.getRootCauses(days),
          engineeringIntelligenceApi.getHotspots(days),
          engineeringIntelligenceApi.getSloIntelligence(days),
          engineeringIntelligenceApi.getDrivers(days)
        ]);
        setOverview(ovData);
        setTrends(trData);
        setModels(modData);
        setEffectiveness(effData);
        setRootCauses(rcData);
        setHotspots(hotData);
        setSlo(sloData);
        setDrivers(drData);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [days]);

  return (
    <div className="min-h-screen bg-background-base text-text-primary p-8 pt-24 font-sans selection:bg-brand/30">
      <div className="max-w-7xl mx-auto space-y-8">
        
        {/* Header & Filters */}
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
          <div>
            <h1 className="text-2xl font-semibold tracking-tight tracking-tight text-text-primary flex items-center gap-3">
              <Brain className="w-8 h-8 text-brand" />
              Engineering Intelligence
            </h1>
            <p className="text-text-secondary mt-1">Advanced reliability analytics & engineering hotspots.</p>
          </div>
          <div className="flex bg-background-secondary/80 p-1 rounded-lg border border-border-strong/50">
            {[7, 30, 90, undefined].map((d) => (
              <button
                key={d || 'all'}
                onClick={() => setDays(d)}
                className={`px-4 py-1.5 rounded-md text-sm font-medium transition-all ${days === d ? 'bg-brand/20 text-brand-hover' : 'text-text-secondary hover:text-text-primary hover:bg-background-elevated/50'}`}
              >
                {d ? `${d} Days` : 'All Time'}
              </button>
            ))}
          </div>
        </div>

        {loading ? (
          <div className="flex items-center justify-center h-64 text-text-secondary animate-pulse">
            Analyzing engineering intelligence...
          </div>
        ) : (
          <div className="space-y-8">
            
            {/* Overview */}
            {overview && (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                <div className="bg-background-secondary/50 border border-border-strong/50 rounded-xl p-6 shadow-xl relative overflow-hidden group">
                  <div className="absolute inset-0 bg-gradient-to-br from-amber-500/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity"></div>
                  <h3 className="text-sm font-medium text-text-secondary mb-2 flex items-center gap-2">
                    <Activity className="w-4 h-4 text-brand-hover" />
                    Overall Reliability
                  </h3>
                  <div className="flex items-end gap-2">
                    <span className={`text-4xl font-bold tracking-tight ${overview.reliability_score > 80 ? 'text-status-success' : overview.reliability_score > 50 ? 'text-brand-hover' : 'text-red-400'}`}>
                      {overview.reliability_score}
                    </span>
                    <span className="text-text-muted mb-1">/ 100</span>
                  </div>
                </div>

                <div className="bg-background-secondary/50 border border-border-strong/50 rounded-xl p-6 shadow-xl relative overflow-hidden group">
                  <div className="absolute inset-0 bg-gradient-to-br from-amber-500/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity"></div>
                  <h3 className="text-sm font-medium text-text-secondary mb-2 flex items-center gap-2">
                    <AlertOctagon className="w-4 h-4 text-brand-hover" />
                    Models At Risk
                  </h3>
                  <div className="flex items-end gap-2">
                    <span className="text-2xl font-semibold tracking-tight tracking-tight text-text-primary">{overview.models_at_risk}</span>
                  </div>
                </div>

                <div className="bg-background-secondary/50 border border-border-strong/50 rounded-xl p-6 shadow-xl relative overflow-hidden group">
                  <div className="absolute inset-0 bg-gradient-to-br from-amber-500/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity"></div>
                  <h3 className="text-sm font-medium text-text-secondary mb-2 flex items-center gap-2">
                    <ShieldAlert className="w-4 h-4 text-brand-hover" />
                    Total Incidents
                  </h3>
                  <div className="flex items-end gap-2">
                    <span className="text-2xl font-semibold tracking-tight tracking-tight text-text-primary">{overview.total_incidents}</span>
                  </div>
                </div>
                
                <div className="bg-background-secondary/50 border border-border-strong/50 rounded-xl p-6 shadow-xl relative overflow-hidden group">
                  <div className="absolute inset-0 bg-gradient-to-br from-amber-500/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity"></div>
                  <h3 className="text-sm font-medium text-text-secondary mb-2 flex items-center gap-2">
                    <Target className="w-4 h-4 text-brand-hover" />
                    Active SLO Pressure
                  </h3>
                  <div className="flex items-end gap-2">
                    <span className="text-2xl font-semibold tracking-tight tracking-tight text-text-primary">{overview.active_slo_pressure}</span>
                  </div>
                </div>
              </div>
            )}

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                {/* Trends Chart */}
                <div className="bg-background-secondary/50 border border-border-strong/50 rounded-xl p-6 shadow-xl">
                  <h2 className="text-lg font-medium text-text-primary mb-6 flex items-center gap-2">
                    <TrendingUp className="w-5 h-5 text-brand-hover" />
                    Reliability Trends ({trends?.direction || 'N/A'})
                  </h2>
                  <div className="h-64">
                    {trends && trends.trends.length > 0 ? (
                      <ResponsiveContainer width="100%" height="100%">
                        <LineChart data={trends.trends}>
                          <CartesianGrid strokeDasharray="3 3" stroke="#404040" />
                          <XAxis 
                            dataKey="timestamp" 
                            stroke="#737373" 
                            tickFormatter={(val) => new Date(val).toLocaleDateString()}
                          />
                          <YAxis yAxisId="left" stroke="#f59e0b" domain={[0, 100]} />
                          <YAxis yAxisId="right" orientation="right" stroke="#ef4444" />
                          <RechartsTooltip 
                            contentStyle={{ backgroundColor: '#262626', border: '1px solid #404040', borderRadius: '0.5rem' }}
                            itemStyle={{ color: '#e5e5e5' }}
                          />
                          <Line yAxisId="left" type="monotone" dataKey="reliability_score" stroke="#f59e0b" strokeWidth={2} name="Score" dot={false} />
                          <Line yAxisId="right" type="stepAfter" dataKey="incidents" stroke="#ef4444" strokeWidth={2} name="Incidents" dot={false} />
                        </LineChart>
                      </ResponsiveContainer>
                    ) : (
                      <div className="h-full flex items-center justify-center text-text-muted">
                        Insufficient data
                      </div>
                    )}
                  </div>
                </div>

                {/* Hotspots */}
                <div className="bg-background-secondary/50 border border-border-strong/50 rounded-xl p-6 shadow-xl">
                  <h2 className="text-lg font-medium text-text-primary mb-6 flex items-center gap-2">
                    <AlertTriangle className="w-5 h-5 text-brand-hover" />
                    Engineering Hotspots
                  </h2>
                  <div className="space-y-4">
                    {hotspots.length > 0 ? (
                      hotspots.map((h, i) => (
                        <div key={i} className="flex items-center justify-between p-3 rounded-lg bg-background-base/50 border border-border">
                          <div>
                            <div className="font-medium text-text-primary">{h.component}</div>
                            <div className="text-xs text-text-secondary mt-1">{h.category}</div>
                          </div>
                          <div className="text-right">
                            <div className="font-bold text-brand-hover">{h.hotspot_score.toFixed(1)}</div>
                            <div className="text-xs text-text-muted">Score</div>
                          </div>
                        </div>
                      ))
                    ) : (
                      <div className="text-center text-text-muted py-8">No hotspots found</div>
                    )}
                  </div>
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                {/* Engineering Effectiveness */}
                <div className="bg-background-secondary/50 border border-border-strong/50 rounded-xl p-6 shadow-xl">
                  <h2 className="text-lg font-medium text-text-primary mb-6 flex items-center gap-2">
                    <GitCommit className="w-5 h-5 text-brand-hover" />
                    Fix Effectiveness
                  </h2>
                  {effectiveness ? (
                    <div className="space-y-6">
                      <div>
                        <div className="flex justify-between text-sm mb-2">
                          <span className="text-text-primary">Validation Success Rate</span>
                          <span className="font-bold text-text-primary">{effectiveness.patch_validation_success_rate.toFixed(1)}%</span>
                        </div>
                        <div className="w-full bg-background-base rounded-full h-2">
                          <div className="bg-emerald-500 h-2 rounded-full" style={{ width: `${effectiveness.patch_validation_success_rate}%` }}></div>
                        </div>
                      </div>
                      <div>
                        <div className="flex justify-between text-sm mb-2">
                          <span className="text-text-primary">Deployment Health Rate</span>
                          <span className="font-bold text-text-primary">{effectiveness.deployment_health_success_rate.toFixed(1)}%</span>
                        </div>
                        <div className="w-full bg-background-base rounded-full h-2">
                          <div className="bg-indigo-500 h-2 rounded-full" style={{ width: `${effectiveness.deployment_health_success_rate}%` }}></div>
                        </div>
                      </div>
                    </div>
                  ) : (
                    <div className="text-center text-text-muted py-8">Insufficient data</div>
                  )}
                </div>

                {/* SLO Intelligence */}
                <div className="bg-background-secondary/50 border border-border-strong/50 rounded-xl p-6 shadow-xl">
                  <h2 className="text-lg font-medium text-text-primary mb-6 flex items-center gap-2">
                    <Target className="w-5 h-5 text-brand-hover" />
                    SLO Intelligence
                  </h2>
                  {slo ? (
                    <div className="grid grid-cols-2 gap-4">
                      <div className="p-4 rounded-lg bg-background-base/50 border border-border">
                        <div className="text-sm text-text-secondary mb-1">Total Objectives</div>
                        <div className="text-2xl font-semibold tracking-tight text-text-primary">{slo.total_objectives}</div>
                      </div>
                      <div className="p-4 rounded-lg bg-background-base/50 border border-border">
                        <div className="text-sm text-text-secondary mb-1">Compliance Rate</div>
                        <div className="text-2xl font-semibold tracking-tight text-text-primary">{slo.slo_compliance_rate.toFixed(1)}%</div>
                      </div>
                      <div className="p-4 rounded-lg bg-background-base/50 border border-border">
                        <div className="text-sm text-text-secondary mb-1">Avg Remaining Budget</div>
                        <div className="text-2xl font-semibold tracking-tight text-text-primary">{slo.average_remaining_budget.toFixed(1)}%</div>
                      </div>
                      <div className="p-4 rounded-lg bg-background-base/50 border border-border">
                        <div className="text-sm text-text-secondary mb-1">Active Alerts</div>
                        <div className="text-2xl font-semibold tracking-tight text-brand-hover">{slo.active_alerts}</div>
                      </div>
                    </div>
                  ) : (
                    <div className="text-center text-text-muted py-8">Insufficient data</div>
                  )}
                </div>
            </div>

            {/* Model Comparison Table */}
            <div className="bg-background-secondary/50 border border-border-strong/50 rounded-xl p-6 shadow-xl overflow-hidden">
              <h2 className="text-lg font-medium text-text-primary mb-6">Cross-Model Reliability Comparison</h2>
              <div className="overflow-x-auto">
                <table className="w-full text-left text-sm text-text-primary">
                  <thead className="text-xs text-text-secondary uppercase bg-background-base/50 border-b border-border-strong/50">
                    <tr>
                      <th className="px-4 py-3 font-medium">Model</th>
                      <th className="px-4 py-3 font-medium">Reliability Score</th>
                      <th className="px-4 py-3 font-medium">Status</th>
                      <th className="px-4 py-3 font-medium">Incidents</th>
                      <th className="px-4 py-3 font-medium">SLO Breaches</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-neutral-800">
                    {models.map((m) => (
                      <tr key={m.model_id} className="hover:bg-background-secondary/50 transition-colors">
                        <td className="px-4 py-4 font-medium text-text-primary">{m.model_name}</td>
                        <td className="px-4 py-4">
                            <span className={`font-bold ${m.reliability_score >= 80 ? 'text-status-success' : m.reliability_score >= 50 ? 'text-brand-hover' : 'text-red-400'}`}>
                                {m.reliability_score}
                            </span>
                        </td>
                        <td className="px-4 py-4">
                            <span className={`px-2 py-1 rounded-full text-xs font-medium border ${
                                m.status === 'HEALTHY' ? 'bg-status-success-soft text-status-success border-status-success/20' :
                                m.status === 'STABLE' ? 'bg-brand-soft text-brand border-brand/20' :
                                m.status === 'AT_RISK' ? 'bg-brand/10 text-brand-hover border-brand/20' :
                                'bg-red-500/10 text-red-400 border-red-500/20'
                            }`}>
                                {m.status}
                            </span>
                        </td>
                        <td className="px-4 py-4">{m.incidents}</td>
                        <td className="px-4 py-4">{m.slo_breaches}</td>
                      </tr>
                    ))}
                    {models.length === 0 && (
                      <tr>
                        <td colSpan={5} className="px-4 py-8 text-center text-text-muted">
                          No models found
                        </td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                {/* Root Causes */}
                <div className="bg-background-secondary/50 border border-border-strong/50 rounded-xl p-6 shadow-xl">
                  <h2 className="text-lg font-medium text-text-primary mb-6 flex items-center gap-2">
                    <AlertTriangle className="w-5 h-5 text-brand-hover" />
                    Root Cause Intelligence
                  </h2>
                  <div className="space-y-4">
                    {rootCauses.length > 0 ? (
                      rootCauses.map((rc, i) => (
                        <div key={i} className="flex items-center justify-between p-3 rounded-lg bg-background-base/50 border border-border">
                          <div>
                            <div className="font-medium text-text-primary">{rc.root_cause}</div>
                            <div className="text-xs text-text-secondary mt-1">Severity: {rc.severity}</div>
                          </div>
                          <div className="text-right">
                            <div className="font-bold text-brand-hover">{rc.frequency}</div>
                            <div className="text-xs text-text-muted">Frequency</div>
                          </div>
                        </div>
                      ))
                    ) : (
                      <div className="text-center text-text-muted py-8">No root causes found</div>
                    )}
                  </div>
                </div>

                {/* Reliability Drivers */}
                <div className="bg-background-secondary/50 border border-border-strong/50 rounded-xl p-6 shadow-xl">
                  <h2 className="text-lg font-medium text-text-primary mb-6 flex items-center gap-2">
                    <Activity className="w-5 h-5 text-brand-hover" />
                    Reliability Drivers
                  </h2>
                  <div className="space-y-4">
                    {drivers.length > 0 ? (
                      drivers.map((d, i) => (
                        <div key={i} className="flex items-center justify-between p-3 rounded-lg bg-background-base/50 border border-border">
                          <div>
                            <div className="font-medium text-text-primary">{d.driver}</div>
                            <div className="text-xs text-text-secondary mt-1">Confidence: {d.confidence}</div>
                          </div>
                          <div className="text-right">
                            <div className="font-bold text-brand-hover">{d.evidence_count}</div>
                            <div className="text-xs text-text-muted">Evidence</div>
                          </div>
                        </div>
                      ))
                    ) : (
                      <div className="text-center text-text-muted py-8">No drivers found</div>
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
