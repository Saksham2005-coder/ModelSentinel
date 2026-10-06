import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { MetricCard } from '@/components/ui/MetricCard';
import { ChartCard } from '@/components/ui/ChartCard';
import { Button } from '@/components/ui/Button';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/Table';
import { Badge } from '@/components/ui/Badge';
import { Box, AlertCircle, GitPullRequest, ChevronDown, Loader2 } from 'lucide-react';
import { ModelsApi, Model } from '@/services/api/models';
import { IncidentApi, Incident } from '@/services/api/incidents';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  Legend
} from 'recharts';

const performanceData = [
  { time: '00:00', production: 98, validation: 97 },
  { time: '04:00', production: 97, validation: 96 },
  { time: '08:00', production: 92, validation: 97 }, // Incident
  { time: '12:00', production: 85, validation: 96 },
  { time: '16:00', production: 96, validation: 96 }, // Recovered
  { time: '20:00', production: 98, validation: 97 },
];

const incidentTypeData = [
  { name: 'Data Drift', value: 45, color: 'var(--color-chart-drift, #f59e0b)' },
  { name: 'Concept Drift', value: 25, color: 'var(--color-chart-incident, #ef4444)' },
  { name: 'Latency', value: 20, color: 'var(--color-chart-baseline, #3b82f6)' },
  { name: 'Other', value: 10, color: 'var(--color-text-muted, #71717a)' },
];

export function DashboardPage() {
  const navigate = useNavigate();
  const [incidents, setIncidents] = useState<Incident[]>([]);
  const [models, setModels] = useState<Model[]>([]);
  const [memories, setMemories] = useState<any[]>([]);
  const [regressionCases, setRegressionCases] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      try {
        const [incRes, modRes, memRes, regRes] = await Promise.all([
          IncidentApi.getIncidents({ limit: 5 }),
          ModelsApi.getModels({}),
          fetch('http://localhost:8000/api/v1/memories').then(r => r.json()),
          fetch('http://localhost:8000/api/v1/regression-tests').then(r => r.json())
        ]);
        setIncidents(incRes);
        setModels(modRes.items);
        setMemories(memRes || []);
        setRegressionCases(regRes || []);
      } catch (e) {
        console.error(e);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  const activeIncidents = incidents.filter(i => !['resolved', 'suppressed'].includes(i.status));
  
  if (loading) return <div className="p-12 flex justify-center"><Loader2 className="h-8 w-8 animate-spin text-text-secondary" /></div>;
  return (
    <div className="flex flex-col gap-8">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-text-primary">Good morning, Engineer</h1>
          <p className="text-text-secondary mt-1">Here's the current status of your ML systems.</p>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="outline" className="gap-2">
            Last 7 days
            <ChevronDown className="h-4 w-4" />
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <MetricCard
          title="Total Models"
          value={models.length}
          icon={Box}
        />
        <MetricCard
          title="Active Incidents"
          value={activeIncidents.length}
          icon={AlertCircle}
        />
        <MetricCard
          title="Incident Memories"
          value={memories.length}
          icon={Box}
        />
        <MetricCard
          title="Regression Tests"
          value={regressionCases.length}
          icon={Box}
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <ChartCard title="Model Performance Trends" description="Aggregated accuracy across production models" className="lg:col-span-2">
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={performanceData} margin={{ top: 5, right: 20, bottom: 5, left: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border-strong)" vertical={false} />
              <XAxis dataKey="time" stroke="var(--color-text-muted)" fontSize={12} tickLine={false} axisLine={false} />
              <YAxis stroke="var(--color-text-muted)" fontSize={12} tickLine={false} axisLine={false} domain={['auto', 100]} />
              <Tooltip 
                contentStyle={{ backgroundColor: 'var(--color-surface)', borderColor: 'var(--color-border)', borderRadius: '8px' }}
                itemStyle={{ color: 'var(--color-text-primary)' }}
              />
              <Line type="monotone" dataKey="production" name="Production" stroke="var(--color-chart-production)" strokeWidth={2} dot={false} activeDot={{ r: 8 }} />
              <Line type="monotone" dataKey="validation" name="Validation" stroke="var(--color-chart-validation)" strokeWidth={2} dot={false} strokeDasharray="5 5" />
            </LineChart>
          </ResponsiveContainer>
        </ChartCard>

        <ChartCard title="Incidents by Type" className="lg:col-span-1">
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={incidentTypeData}
                cx="50%"
                cy="50%"
                innerRadius={60}
                outerRadius={80}
                paddingAngle={2}
                dataKey="value"
              >
                {incidentTypeData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip 
                contentStyle={{ backgroundColor: 'var(--color-surface)', borderColor: 'var(--color-border)', borderRadius: '8px' }}
                itemStyle={{ color: 'var(--color-text-primary)' }}
              />
              <Legend verticalAlign="bottom" height={36} wrapperStyle={{ fontSize: '12px', color: 'var(--color-text-secondary)' }}/>
            </PieChart>
          </ResponsiveContainer>
        </ChartCard>
      </div>

      <div className="flex flex-col gap-4">
        <h2 className="text-xl font-bold tracking-tight text-text-primary">Recent Incidents</h2>
        <div className="rounded-xl border border-border bg-surface overflow-hidden">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>ID</TableHead>
                <TableHead>Model</TableHead>
                <TableHead>Severity</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Detected At</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {incidents.length === 0 && (
                <TableRow>
                  <TableCell colSpan={5} className="text-center py-8 text-text-secondary">No recent incidents</TableCell>
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
                    <TableCell className="font-mono text-xs text-text-secondary">{incident.id.substring(0,8)}</TableCell>
                    <TableCell className="font-medium text-text-primary">{model?.name || 'Unknown Model'}</TableCell>
                    <TableCell>
                      <Badge variant={incident.severity === 'critical' ? 'danger' : incident.severity === 'high' ? 'warning' : 'default'}>
                        {incident.severity.toUpperCase()}
                      </Badge>
                    </TableCell>
                    <TableCell>
                      <Badge variant="info">
                        {incident.status.toUpperCase()}
                      </Badge>
                    </TableCell>
                    <TableCell className="text-text-muted">{new Date(incident.detected_at).toLocaleString()}</TableCell>
                  </TableRow>
                );
              })}
            </TableBody>
          </Table>
        </div>
      </div>
    </div>
  );
}
