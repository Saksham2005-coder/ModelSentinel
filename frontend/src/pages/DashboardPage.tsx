import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { MetricCard } from '@/components/ui/MetricCard';
import { ChartCard } from '@/components/ui/ChartCard';
import { Button } from '@/components/ui/Button';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/Table';
import { PageHeader } from '@/components/ui/Layout';
import { StatusBadge } from '@/components/ui/StatusBadge';
import { 
  Box, ChevronDown, Loader2, Activity, ShieldAlert,
  Server, GitBranch, Zap
} from 'lucide-react';
import { ModelsApi, Model } from '@/services/api/models';
import { IncidentApi, Incident } from '@/services/api/incidents';
import { DeploymentApi, Deployment } from '@/services/api/deployments';
import { analyticsApi, OverviewMetrics, IncidentAnalytics } from '@/services/api/analytics';
import { engineeringIntelligenceApi, ReliabilityTrend } from '@/services/api/engineering_intelligence';
import {
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  Legend,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid
} from 'recharts';

const severityColors: Record<string, string> = {
  'critical': 'var(--color-status-danger, #ef4444)',
  'high': 'var(--color-status-warning, #f59e0b)',
  'medium': 'var(--color-status-warning-muted, #fcd34d)',
  'low': 'var(--color-status-info, #3b82f6)',
  'resolved': 'var(--color-status-success, #10b981)',
  'other': 'var(--color-text-muted, #71717a)',
};

export function DashboardPage() {
  const navigate = useNavigate();
  const [incidents, setIncidents] = useState<Incident[]>([]);
  const [models, setModels] = useState<Model[]>([]);
  const [deployments, setDeployments] = useState<Deployment[]>([]);
  const [reliability, setReliability] = useState<OverviewMetrics | null>(null);
  const [incidentAnalytics, setIncidentAnalytics] = useState<IncidentAnalytics | null>(null);
  const [trends, setTrends] = useState<ReliabilityTrend[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      try {
        const [incRes, modRes, depRes, relRes, incAnaRes, trendsRes] = await Promise.all([
          IncidentApi.getIncidents({ limit: 5 }).catch(() => ({ items: [], total: 0 })),
          ModelsApi.getModels({}).catch(() => ({ items: [], total: 0 })),
          DeploymentApi.getDeployments().catch(() => []),
          analyticsApi.getOverview(7).catch(() => null),
          analyticsApi.getIncidents(7).catch(() => null),
          engineeringIntelligenceApi.getTrends(7).catch(() => ({ trends: [] }))
        ]);
        
        // IncidentApi.getIncidents returns an array in some mocks, or { items: [] } in others. Handle both:
        setIncidents(Array.isArray(incRes) ? incRes : incRes.items || []);
        setModels(modRes.items || []);
        setDeployments(Array.isArray(depRes) ? depRes : []);
        setReliability(relRes);
        setIncidentAnalytics(incAnaRes);
        setTrends(trendsRes?.trends || []);
      } catch (e) {
        console.error('Failed to load dashboard data:', e);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  if (loading) {
    return (
      <div className="flex flex-col gap-8 h-full">
        <PageHeader title="ModelSentinel" description="Reliability Overview" />
        <div className="flex items-center justify-center flex-1 h-64">
          <Loader2 className="h-8 w-8 animate-spin text-brand" />
        </div>
      </div>
    );
  }

  const activeIncidents = incidents.filter(i => !['resolved', 'suppressed'].includes(i.status));
  const modelsWithIssues = models.filter(m => m.status !== 'HEALTHY' && m.status !== 'STABLE');

  return (
    <div className="flex flex-col gap-8 pb-10">
      <PageHeader 
        title="ModelSentinel" 
        description="Monitor model health, production incidents, engineering changes, and recovery activity across your ML systems."
      >
        <Button variant="outline" className="gap-2" onClick={() => alert('Time range selection coming soon!')}>
          Last 7 days
          <ChevronDown className="h-4 w-4" />
        </Button>
      </PageHeader>

      {/* Hero Insight Panel */}
      <div className="rounded-2xl border border-border bg-surface-hover p-5 flex items-center gap-5 shadow-soft">
        <div className="p-3 bg-brand-soft rounded-xl">
          <Zap className="h-6 w-6 text-brand" />
        </div>
        <div>
          <h3 className="text-base font-semibold text-text-primary">Reliability Signal</h3>
          <p className="text-sm text-text-secondary mt-1 leading-relaxed">
            {modelsWithIssues.length > 0 
              ? `${modelsWithIssues.length} model${modelsWithIssues.length > 1 ? 's' : ''} currently requires attention.` 
              : 'All tracked models and deployments currently healthy.'}
            {activeIncidents.length > 0 && ` ${activeIncidents.length} active reliability alert${activeIncidents.length > 1 ? 's' : ''}.`}
          </p>
        </div>
      </div>

      {/* Metric Strip */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <MetricCard
          title="Reliability Score"
          value={reliability?.reliability_score !== undefined ? `${reliability.reliability_score}%` : 'N/A'}
          icon={Activity}
        />
        <MetricCard
          title="Total Models"
          value={models.length}
          icon={Box}
        />
        <MetricCard
          title="Active Incidents"
          value={activeIncidents.length}
          icon={ShieldAlert}
        />
        <MetricCard
          title="Deployments"
          value={deployments.length}
          icon={Server}
        />
      </div>

      {/* Main Analytics Row */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <ChartCard title="Model Reliability Trend" className="lg:col-span-2">
          <div className="h-[300px] w-full">
            {trends && trends.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={trends} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                  <defs>
                    <linearGradient id="colorScore" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="var(--color-brand, #f59e0b)" stopOpacity={0.3}/>
                      <stop offset="95%" stopColor="var(--color-brand, #f59e0b)" stopOpacity={0}/>
                    </linearGradient>
                    <linearGradient id="colorIncidents" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="var(--color-status-danger, #ef4444)" stopOpacity={0.3}/>
                      <stop offset="95%" stopColor="var(--color-status-danger, #ef4444)" stopOpacity={0}/>
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="var(--color-border)" opacity={0.5} />
                  <XAxis 
                    dataKey="timestamp" 
                    tickFormatter={(val) => {
                      try { return new Date(val).toLocaleDateString(undefined, { month: 'short', day: 'numeric' }); } 
                      catch { return val; }
                    }}
                    stroke="var(--color-text-muted)"
                    fontSize={12}
                    tickMargin={10}
                  />
                  <YAxis 
                    yAxisId="left"
                    stroke="var(--color-text-muted)" 
                    fontSize={12}
                    tickFormatter={(val) => `${val}%`}
                  />
                  <YAxis 
                    yAxisId="right" 
                    orientation="right" 
                    stroke="var(--color-text-muted)" 
                    fontSize={12}
                  />
                  <Tooltip 
                    contentStyle={{ backgroundColor: 'var(--color-surface)', borderColor: 'var(--color-border)', borderRadius: '8px' }}
                    itemStyle={{ color: 'var(--color-text-primary)' }}
                    labelStyle={{ color: 'var(--color-text-secondary)', marginBottom: '4px' }}
                    // eslint-disable-next-line @typescript-eslint/no-explicit-any
                    labelFormatter={(val: any) => {
                      try { return new Date(val).toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' }); } 
                      catch { return String(val); }
                    }}
                  />
                  <Legend verticalAlign="top" height={36} wrapperStyle={{ fontSize: '12px', color: 'var(--color-text-secondary)' }}/>
                  <Area 
                    yAxisId="left"
                    type="monotone" 
                    dataKey="reliability_score" 
                    name="Reliability Score"
                    stroke="var(--color-brand, #f59e0b)" 
                    strokeWidth={2}
                    fillOpacity={1} 
                    fill="url(#colorScore)" 
                  />
                  <Area 
                    yAxisId="right"
                    type="monotone" 
                    dataKey="incidents" 
                    name="Incident Pressure"
                    stroke="var(--color-status-danger, #ef4444)" 
                    strokeWidth={2}
                    fillOpacity={1} 
                    fill="url(#colorIncidents)" 
                  />
                </AreaChart>
              </ResponsiveContainer>
            ) : (
              <div className="flex items-center justify-center h-full text-text-secondary text-sm">
                Insufficient data for this trend
              </div>
            )}
          </div>
        </ChartCard>

        <ChartCard title="Incident Distribution" className="lg:col-span-1">
          <div className="h-[300px] w-full">
            {incidentAnalytics?.severity_distribution?.length ? (
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={incidentAnalytics.severity_distribution}
                    cx="50%"
                    cy="50%"
                    innerRadius={70}
                    outerRadius={90}
                    paddingAngle={3}
                    dataKey="value"
                    stroke="none"
                  >
                    {incidentAnalytics.severity_distribution.map((entry: { name: string; value: number }, index: number) => (
                      <Cell key={`cell-${index}`} fill={severityColors[entry.name.toLowerCase()] || severityColors['other']} />
                    ))}
                  </Pie>
                  <Tooltip 
                    contentStyle={{ backgroundColor: 'var(--color-surface)', borderColor: 'var(--color-border)', borderRadius: '8px', border: '1px solid var(--color-border)' }}
                    itemStyle={{ color: 'var(--color-text-primary)' }}
                    // eslint-disable-next-line @typescript-eslint/no-explicit-any
                    formatter={(value: any, name: any) => {
                      const strName = String(name || '');
                      return [value, strName.charAt(0).toUpperCase() + strName.slice(1)];
                    }}
                  />
                  <Legend 
                    verticalAlign="bottom" 
                    height={36} 
                    iconType="circle"
                    formatter={(value) => <span className="capitalize">{value}</span>}
                    wrapperStyle={{ fontSize: '12px', color: 'var(--color-text-secondary)' }}
                  />
                </PieChart>
              </ResponsiveContainer>
            ) : (
              <div className="flex items-center justify-center h-full text-text-secondary text-sm">
                No incident data available
              </div>
            )}
          </div>
        </ChartCard>
      </div>

      {/* Model Health Row */}
      <div className="flex flex-col gap-4 mt-2">
        <h2 className="text-lg font-semibold tracking-tight text-text-primary">Model Health</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {models.length === 0 ? (
            <div className="col-span-full py-8 text-center text-text-secondary border border-dashed border-border rounded-xl">
              No models currently tracked
            </div>
          ) : (
            models.map(model => (
              <div 
                key={model.id} 
                className="p-4 rounded-xl border border-border bg-surface hover:border-brand/50 transition-colors cursor-pointer group"
                onClick={() => navigate(`/models/${model.id}/intelligence`)}
              >
                <div className="flex items-start justify-between mb-3">
                  <h3 className="font-medium text-sm text-text-primary group-hover:text-brand transition-colors line-clamp-1">{model.name}</h3>
                  <StatusBadge status={model.status} />
                </div>
                <div className="flex items-center justify-between mt-4">
                  <span className="text-xs text-text-muted">{model.framework}</span>
                  <span className="text-xs font-mono text-text-secondary">
                    {model.primary_metric}
                  </span>
                </div>
              </div>
            ))
          )}
        </div>
      </div>

      {/* Bottom Section: Incidents & Deployments */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mt-2">
        {/* Recent Incidents */}
        <div className="flex flex-col gap-4">
          <h2 className="text-xl font-semibold tracking-tight text-text-primary">Recent Incidents</h2>
          <div className="rounded-xl border border-border bg-surface overflow-x-auto">
            <Table className="min-w-[600px]">
              <TableHeader>
                <TableRow>
                  <TableHead>Incident</TableHead>
                  <TableHead>Severity</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead className="text-right">Detected</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {incidents.length === 0 && (
                  <TableRow>
                    <TableCell colSpan={4} className="text-center py-8 text-text-secondary text-sm">No recent incidents</TableCell>
                  </TableRow>
                )}
                {incidents.map((incident) => {
                  const model = models.find(m => m.id === incident.model_id);
                  return (
                    <TableRow 
                      key={incident.id} 
                      className="cursor-pointer hover:bg-surface-hover"
                      onClick={() => navigate(`/incidents/${incident.id}`)}
                    >
                      <TableCell>
                        <div className="flex flex-col">
                          <span className="font-medium text-sm text-text-primary">{model?.name || 'Unknown Model'}</span>
                          <span className="text-xs text-text-muted font-mono">{incident.id.substring(0,8)}</span>
                        </div>
                      </TableCell>
                      <TableCell>
                        <StatusBadge status={incident.severity} />
                      </TableCell>
                      <TableCell>
                        <StatusBadge status={incident.status} />
                      </TableCell>
                      <TableCell className="text-right text-xs text-text-muted">
                        {(() => {
                          try { 
                            const d = new Date(incident.detected_at);
                            return `${d.toLocaleDateString(undefined, {month:'short', day:'numeric'})}, ${d.toLocaleTimeString(undefined, {hour:'2-digit', minute:'2-digit', hour12: false})}`;
                          }
                          catch { return incident.detected_at; }
                        })()}
                      </TableCell>
                    </TableRow>
                  );
                })}
              </TableBody>
            </Table>
          </div>
        </div>

        {/* Recent Deployments */}
        <div className="flex flex-col gap-4">
          <h2 className="text-xl font-semibold tracking-tight text-text-primary">Engineering Activity</h2>
          <div className="rounded-xl border border-border bg-surface overflow-x-auto">
            <Table className="min-w-[500px]">
              <TableHeader>
                <TableRow>
                  <TableHead>Event</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead className="text-right">Time</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {deployments.length === 0 && (
                  <TableRow>
                    <TableCell colSpan={3} className="text-center py-8 text-text-secondary text-sm">No recent activity</TableCell>
                  </TableRow>
                )}
                {deployments.slice(0, 5).map((deployment) => (
                  <TableRow 
                    key={deployment.id}
                    className="cursor-pointer hover:bg-surface-hover"
                    onClick={() => navigate(`/deployment-gates/${deployment.id}`)}
                  >
                    <TableCell>
                      <div className="flex flex-col">
                        <span className="font-medium text-sm text-text-primary flex items-center gap-1.5">
                          <GitBranch className="h-3.5 w-3.5 text-text-muted" />
                          Deployment {deployment.id.substring(0,8)}
                        </span>
                        <span className="text-xs text-text-muted">PR: {deployment.pull_request_id ? deployment.pull_request_id.substring(0,8) : 'N/A'}</span>
                      </div>
                    </TableCell>
                    <TableCell>
                      <StatusBadge status={deployment.status} />
                    </TableCell>
                    <TableCell className="text-right text-xs text-text-muted">
                      {(() => {
                        try { 
                          const d = new Date(deployment.created_at || deployment.deployed_at || Date.now());
                          return `${d.toLocaleDateString(undefined, {month:'short', day:'numeric'})}, ${d.toLocaleTimeString(undefined, {hour:'2-digit', minute:'2-digit', hour12: false})}`;
                        }
                        catch { return 'Recent'; }
                      })()}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
        </div>
      </div>
    </div>
  );
}
