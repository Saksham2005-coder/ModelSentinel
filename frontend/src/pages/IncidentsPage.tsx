import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { IncidentApi, Incident } from '@/services/api/incidents';
import { ModelsApi, Model } from '@/services/api/models';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { Input } from '@/components/ui/Input';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/Table';
import { Loader2, Search, Filter, AlertTriangle } from 'lucide-react';

export function IncidentsPage() {
  const navigate = useNavigate();
  const [incidents, setIncidents] = useState<Incident[]>([]);
  const [models, setModels] = useState<Record<string, Model>>({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  const [activeTab, setActiveTab] = useState('All');
  
  const fetchIncidents = async () => {
    setLoading(true);
    try {
      let statusFilter;
      if (activeTab === 'Active') statusFilter = 'detected';
      else if (activeTab === 'Investigating') statusFilter = 'investigating';
      else if (activeTab === 'Fix Generated') statusFilter = 'fix_generated';
      else if (activeTab === 'Resolved') statusFilter = 'resolved';
      
      const [incs, mods] = await Promise.all([
        IncidentApi.getIncidents({ status: statusFilter }),
        ModelsApi.getModels({})
      ]);
      setIncidents(incs);
      
      const modelMap: Record<string, Model> = {};
      mods.items.forEach(m => { modelMap[m.id] = m; });
      setModels(modelMap);
    } catch (err: any) {
      setError(err.message || 'Failed to fetch incidents');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchIncidents();
  }, [activeTab]);

  const tabs = ['All', 'Active', 'Investigating', 'Fix Generated', 'Resolved'];

  const getSeverityBadge = (severity: string) => {
    switch (severity.toLowerCase()) {
      case 'critical': return <Badge variant="danger">Critical</Badge>;
      case 'high': return <Badge variant="warning">High</Badge>;
      case 'medium': return <Badge variant="warning">Medium</Badge>;
      default: return <Badge variant="info">Low</Badge>;
    }
  };

  const getStatusBadge = (status: string) => {
    const s = status.toLowerCase();
    if (s === 'resolved' || s === 'suppressed') return <Badge variant="success">{status}</Badge>;
    if (s === 'investigating' || s === 'fix_generated' || s === 'validation') return <Badge variant="info">{status}</Badge>;
    return <Badge variant="default">{status}</Badge>;
  };

  return (
    <div className="flex flex-col gap-8">
      <div>
        <h1 className="text-3xl font-bold tracking-tight text-text-primary">Incidents</h1>
        <p className="text-text-secondary mt-1">View, investigate, and resolve issues across your ML systems.</p>
      </div>

      <div className="flex flex-col md:flex-row items-center gap-4 justify-between border-b border-border pb-4">
        <div className="flex gap-4">
          {tabs.map(t => (
            <button
              key={t}
              className={`pb-2 text-sm font-medium transition-colors border-b-2 ${
                activeTab === t ? 'border-brand text-brand' : 'border-transparent text-text-secondary hover:text-text-primary'
              }`}
              onClick={() => setActiveTab(t)}
            >
              {t}
            </button>
          ))}
        </div>
        
        <div className="flex items-center gap-4 w-full md:w-auto">
          <div className="relative flex-1 md:w-64">
            <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-text-muted" />
            <Input placeholder="Search incidents..." className="pl-9 w-full" />
          </div>
          <Button variant="outline" className="gap-2">
            <Filter className="h-4 w-4" />
            Filters
          </Button>
        </div>
      </div>

      {error && <div className="text-status-danger p-4 bg-status-danger/10 rounded-lg">{error}</div>}

      <div className="rounded-xl border border-border bg-surface overflow-hidden">
        {loading ? (
          <div className="p-12 flex justify-center text-text-secondary">
            <Loader2 className="h-8 w-8 animate-spin" />
          </div>
        ) : incidents.length === 0 ? (
          <div className="p-12 text-center text-text-secondary">
            <AlertTriangle className="h-8 w-8 mx-auto mb-4 text-text-muted" />
            <h3 className="text-lg font-medium text-text-primary">No incidents found</h3>
            <p>No incidents match the current criteria.</p>
          </div>
        ) : (
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>ID</TableHead>
                <TableHead>Model</TableHead>
                <TableHead>Issue</TableHead>
                <TableHead>Severity</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Detected At</TableHead>
                <TableHead>Last Seen</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {incidents.map((inc) => (
                <TableRow 
                  key={inc.id} 
                  className="cursor-pointer hover:bg-surface-hover"
                  onClick={() => navigate(`/incidents/${inc.id}`)}
                >
                  <TableCell className="font-mono text-xs text-text-secondary">
                    {inc.id.substring(0,8)}
                  </TableCell>
                  <TableCell className="font-medium">
                    {models[inc.model_id]?.name || 'Unknown Model'}
                  </TableCell>
                  <TableCell>
                    <div className="font-medium text-text-primary">{inc.title}</div>
                    <div className="text-xs text-text-secondary capitalize">{inc.category.replace('_', ' ')}</div>
                  </TableCell>
                  <TableCell>{getSeverityBadge(inc.severity)}</TableCell>
                  <TableCell>{getStatusBadge(inc.status)}</TableCell>
                  <TableCell className="text-sm text-text-secondary">
                    {new Date(inc.detected_at).toLocaleString()}
                  </TableCell>
                  <TableCell className="text-sm text-text-secondary">
                    {new Date(inc.last_seen_at).toLocaleString()}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        )}
      </div>
    </div>
  );
}
