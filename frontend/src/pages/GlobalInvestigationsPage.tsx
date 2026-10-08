import { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { InvestigationsApi, Investigation } from '@/services/api/investigations';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/Table';
import { PageHeader, EmptyState } from '@/components/ui/Layout';
import { StatusBadge } from '@/components/ui/StatusBadge';
import { Loader2, Activity, Clock } from 'lucide-react';

export function GlobalInvestigationsPage() {
  const navigate = useNavigate();
  const [investigations, setInvestigations] = useState<Investigation[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchInvestigations = useCallback(async () => {
    setLoading(true);
    try {
      const data = await InvestigationsApi.getAllInvestigations();
      setInvestigations(data || []);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to fetch investigations');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchInvestigations();
  }, [fetchInvestigations]);

  return (
    <div className="flex flex-col gap-8">
      <PageHeader 
        title="Investigations" 
        description="Monitor and manage all AI-driven incident investigations."
      />

      {error && <div className="text-status-danger p-4 bg-status-danger/10 rounded-lg border border-status-danger/20">{error}</div>}

      <div className="rounded-xl border border-border bg-surface overflow-hidden">
        {loading ? (
          <div className="p-12 flex justify-center text-text-secondary">
            <Loader2 className="h-8 w-8 animate-spin text-brand" />
          </div>
        ) : investigations.length === 0 ? (
          <EmptyState
            title="No Investigations Found"
            description="Investigations are automatically triggered for new incidents or can be started manually."
            icon={<Activity className="h-8 w-8" />}
          />
        ) : (
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>ID</TableHead>
                <TableHead>Incident ID</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Current Step</TableHead>
                <TableHead>Created At</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {investigations.map((inv) => (
                <TableRow 
                  key={inv.id} 
                  className="cursor-pointer hover:bg-surface-hover"
                  onClick={() => navigate(`/incidents/${inv.incident_id}/investigation`)}
                >
                  <TableCell className="font-mono text-xs text-text-secondary">
                    {inv.id.substring(0,8)}
                  </TableCell>
                  <TableCell className="font-mono text-xs text-brand hover:underline">
                    {inv.incident_id.substring(0,8)}
                  </TableCell>
                  <TableCell>
                    <StatusBadge status={inv.status.toUpperCase()} />
                  </TableCell>
                  <TableCell className="text-sm text-text-secondary">
                    {inv.current_step || 'N/A'}
                  </TableCell>
                  <TableCell className="text-sm text-text-secondary flex items-center gap-2">
                    <Clock className="w-3 h-3" />
                    {new Date(inv.created_at).toLocaleString()}
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
