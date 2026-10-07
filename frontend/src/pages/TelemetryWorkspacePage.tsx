import { useState, useEffect, useCallback } from 'react';
import { Link } from 'react-router-dom';
import { Button } from '@/components/ui/Button';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/Table';
import { Badge } from '@/components/ui/Badge';
import { RefreshCw, Loader2, AlertCircle, UploadCloud, Activity, CheckCircle, XCircle } from 'lucide-react';
import { TelemetryApi, Telemetry } from '@/services/api/telemetry';
import { IngestTelemetryModal } from '@/features/telemetry/components/IngestTelemetryModal';

export function TelemetryWorkspacePage() {
  const [telemetry, setTelemetry] = useState<Telemetry[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);

  const fetchTelemetry = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await TelemetryApi.getTelemetryList();
      setTelemetry(data);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to fetch telemetry data');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchTelemetry();
  }, [fetchTelemetry]);

  const handleRefresh = () => {
    fetchTelemetry();
  };

  const getStatusBadge = (status: string) => {
    switch(status) {
      case 'PROCESSED':
      case 'VALID':
        return <Badge variant="success">PROCESSED</Badge>;
      case 'VALIDATING':
      case 'RECEIVED':
        return <Badge variant="warning">PROCESSING</Badge>;
      case 'INVALID':
      case 'FAILED':
        return <Badge variant="danger">FAILED</Badge>;
      default:
        return <Badge variant="default">{status}</Badge>;
    }
  };

  // Compute summary stats
  const processed = telemetry.filter(t => t.status === 'PROCESSED').length;
  const failed = telemetry.filter(t => t.status === 'FAILED' || t.status === 'INVALID').length;
  const total = telemetry.length;

  return (
    <div className="flex flex-col gap-8">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-text-primary">Production Telemetry</h1>
          <p className="text-text-secondary mt-1">Monitor incoming model behavior and detect reliability degradation.</p>
        </div>
        <div className="flex items-center gap-4">
          <Button variant="outline" onClick={handleRefresh}>
            {loading ? <Loader2 className="h-4 w-4 animate-spin mr-2" /> : <RefreshCw className="h-4 w-4 mr-2" />}
            Refresh
          </Button>
          <Button variant="primary" className="gap-2" onClick={() => setIsModalOpen(true)}>
            <UploadCloud className="h-4 w-4" />
            Process Telemetry
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-surface border border-border rounded-xl p-6 flex flex-col gap-2">
          <div className="flex items-center justify-between text-text-secondary">
            <h3 className="font-medium">Total Windows</h3>
            <Activity className="h-5 w-5 text-brand" />
          </div>
          <div className="text-3xl font-bold text-text-primary">{total}</div>
        </div>
        <div className="bg-surface border border-border rounded-xl p-6 flex flex-col gap-2">
          <div className="flex items-center justify-between text-text-secondary">
            <h3 className="font-medium">Successfully Processed</h3>
            <CheckCircle className="h-5 w-5 text-status-success" />
          </div>
          <div className="text-3xl font-bold text-text-primary">{processed}</div>
        </div>
        <div className="bg-surface border border-border rounded-xl p-6 flex flex-col gap-2">
          <div className="flex items-center justify-between text-text-secondary">
            <h3 className="font-medium">Validation / Processing Failed</h3>
            <XCircle className="h-5 w-5 text-status-danger" />
          </div>
          <div className="text-3xl font-bold text-text-primary">{failed}</div>
        </div>
      </div>

      {error ? (
        <div className="p-4 bg-status-danger/10 border border-status-danger/20 rounded-xl flex items-center gap-3 text-status-danger">
          <AlertCircle className="h-5 w-5" />
          <p>{error}</p>
        </div>
      ) : null}

      <div className="rounded-xl border border-border bg-surface overflow-hidden">
        {loading && telemetry.length === 0 ? (
          <div className="flex flex-col items-center justify-center p-12 text-text-secondary">
            <Loader2 className="h-8 w-8 animate-spin text-brand mb-4" />
            <p>Loading telemetry...</p>
          </div>
        ) : telemetry.length === 0 ? (
          <div className="flex flex-col items-center justify-center p-12 text-text-secondary text-center">
            <div className="h-12 w-12 rounded-full bg-surface-hover flex items-center justify-center mb-4">
              <UploadCloud className="h-6 w-6 text-text-muted" />
            </div>
            <h3 className="text-lg font-medium text-text-primary">No telemetry windows found</h3>
            <p className="max-w-sm mt-1">Upload your first telemetry window to begin deterministic monitoring and incident detection.</p>
            <Button variant="primary" className="mt-4 gap-2" onClick={() => setIsModalOpen(true)}>
              <UploadCloud className="h-4 w-4" />
              Process Telemetry
            </Button>
          </div>
        ) : (
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Time Window</TableHead>
                <TableHead>Model / Source</TableHead>
                <TableHead>Samples</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Incident</TableHead>
                <TableHead>Received</TableHead>
                <TableHead className="text-right">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {telemetry.map((t) => (
                <TableRow key={t.id}>
                  <TableCell className="font-medium text-text-primary">
                    {new Date(t.window_start).toLocaleDateString()} {new Date(t.window_start).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})} - {new Date(t.window_end).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}
                  </TableCell>
                  <TableCell>
                    <div className="flex flex-col">
                      <span className="text-text-primary">{t.model_id}</span>
                      <span className="text-xs text-text-muted">{t.source}</span>
                    </div>
                  </TableCell>
                  <TableCell className="text-text-secondary">
                    {t.sample_count?.toLocaleString() || '-'}
                  </TableCell>
                  <TableCell>
                    {getStatusBadge(t.status)}
                  </TableCell>
                  <TableCell>
                    {t.incident_id ? (
                      <Link to={`/incidents/${t.incident_id}`} className="text-status-danger hover:underline font-medium flex items-center gap-1">
                        <AlertCircle className="h-3 w-3" /> Yes
                      </Link>
                    ) : (
                      <span className="text-text-muted">None</span>
                    )}
                  </TableCell>
                  <TableCell className="text-text-secondary">
                    {new Date(t.created_at).toLocaleDateString()}
                  </TableCell>
                  <TableCell className="text-right">
                    <Button variant="outline" size="sm" asChild>
                      <Link to={`/telemetry/${t.id}`}>View Details</Link>
                    </Button>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        )}
      </div>
      
      {isModalOpen && (
        <IngestTelemetryModal 
          open={isModalOpen} 
          onOpenChange={setIsModalOpen} 
          onSuccess={fetchTelemetry}
        />
      )}
    </div>
  );
}
