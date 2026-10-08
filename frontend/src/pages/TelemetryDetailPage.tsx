import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { ChevronLeft, Loader2, AlertCircle, Calendar, Hash, FileCheck, CheckCircle2, XCircle } from 'lucide-react';
import { TelemetryApi, Telemetry } from '@/services/api/telemetry';

export function TelemetryDetailPage() {
  const { id } = useParams<{ id: string }>();
  const [telemetry, setTelemetry] = useState<Telemetry | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (id) {
      TelemetryApi.getTelemetryDetail(id)
        .then(setTelemetry)
        .catch((err) => setError(err.message || 'Failed to fetch telemetry details'))
        .finally(() => setLoading(false));
    }
  }, [id]);

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center p-12 text-text-secondary">
        <Loader2 className="h-8 w-8 animate-spin text-brand mb-4" />
        <p>Loading telemetry details...</p>
      </div>
    );
  }

  if (error || !telemetry) {
    return (
      <div className="p-4 bg-status-danger/10 border border-status-danger/20 rounded-xl flex items-center gap-3 text-status-danger">
        <AlertCircle className="h-5 w-5" />
        <p>{error || 'Telemetry not found'}</p>
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-8 max-w-4xl mx-auto w-full">
      <div className="flex items-center gap-4 text-text-muted text-sm">
        <Link to="/telemetry" className="hover:text-text-primary transition-colors">
          Telemetry
        </Link>
        <span>/</span>
        <span className="text-text-primary truncate">{telemetry.id}</span>
      </div>

      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight tracking-tight text-text-primary flex items-center gap-3">
            Telemetry Window
            {telemetry.status === 'PROCESSED' || telemetry.status === 'VALID' ? (
              <Badge variant="success">PROCESSED</Badge>
            ) : telemetry.status === 'FAILED' || telemetry.status === 'INVALID' ? (
              <Badge variant="danger">FAILED</Badge>
            ) : (
              <Badge variant="warning">{telemetry.status}</Badge>
            )}
          </h1>
          <p className="text-text-secondary mt-1">Source: {telemetry.source}</p>
        </div>
        <div className="flex items-center gap-3">
          <Button variant="outline" asChild>
            <Link to="/telemetry">
              <ChevronLeft className="h-4 w-4 mr-2" />
              Back
            </Link>
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-surface border border-border rounded-xl p-6 flex flex-col gap-1">
          <div className="text-text-secondary text-sm flex items-center gap-2">
            <Calendar className="h-4 w-4" /> Window Start
          </div>
          <div className="text-lg font-medium text-text-primary">
            {new Date(telemetry.window_start).toLocaleString()}
          </div>
        </div>
        <div className="bg-surface border border-border rounded-xl p-6 flex flex-col gap-1">
          <div className="text-text-secondary text-sm flex items-center gap-2">
            <Calendar className="h-4 w-4" /> Window End
          </div>
          <div className="text-lg font-medium text-text-primary">
            {new Date(telemetry.window_end).toLocaleString()}
          </div>
        </div>
        <div className="bg-surface border border-border rounded-xl p-6 flex flex-col gap-1">
          <div className="text-text-secondary text-sm flex items-center gap-2">
            <Hash className="h-4 w-4" /> Samples
          </div>
          <div className="text-lg font-medium text-text-primary">
            {telemetry.sample_count?.toLocaleString() || 'N/A'}
          </div>
        </div>
      </div>

      <div className="bg-surface border border-border rounded-xl overflow-hidden">
        <div className="px-6 py-4 border-b border-border bg-surface-hover">
          <h2 className="text-lg font-semibold text-text-primary">Processing Summary</h2>
        </div>
        <div className="p-6 flex flex-col gap-6">
          
          <div className="flex items-start gap-4">
            <div className="mt-1">
              <CheckCircle2 className="h-6 w-6 text-status-success" />
            </div>
            <div>
              <h3 className="text-base font-medium text-text-primary">Validation</h3>
              {telemetry.validation_errors?.length ? (
                <div className="mt-2 flex flex-col gap-1 text-sm text-status-danger">
                  {telemetry.validation_errors.map((err, i) => <span key={i}>• {err}</span>)}
                </div>
              ) : (
                <p className="text-sm text-text-secondary mt-1">Schema and content validated successfully.</p>
              )}
            </div>
          </div>

          {telemetry.monitoring_run_id && (
            <div className="flex items-start gap-4">
              <div className="mt-1">
                <FileCheck className="h-6 w-6 text-brand" />
              </div>
              <div className="flex-1">
                <h3 className="text-base font-medium text-text-primary">Deterministic Monitoring Run</h3>
                <p className="text-sm text-text-secondary mt-1">
                  Monitoring engine evaluated metric threshold, feature drift, and data quality.
                </p>
                <div className="mt-3">
                  <Button variant="outline" size="sm" asChild>
                    <Link to={`/models/${telemetry.model_id}/monitoring?run=${telemetry.monitoring_run_id}`}>
                      View Monitoring Run
                    </Link>
                  </Button>
                </div>
              </div>
            </div>
          )}

          {telemetry.incident_id && (
            <div className="flex items-start gap-4">
              <div className="mt-1">
                <XCircle className="h-6 w-6 text-status-danger" />
              </div>
              <div className="flex-1">
                <h3 className="text-base font-medium text-status-danger">Incident Detected</h3>
                <p className="text-sm text-text-secondary mt-1">
                  Degradation crossed incident thresholds. Incident automatically created.
                </p>
                <div className="mt-3">
                  <Button variant="outline" size="sm" className="border-status-danger text-status-danger hover:bg-status-danger/10" asChild>
                    <Link to={`/incidents/${telemetry.incident_id}`}>
                      View Incident
                    </Link>
                  </Button>
                </div>
              </div>
            </div>
          )}

          {!telemetry.incident_id && telemetry.monitoring_run_id && (
            <div className="flex items-start gap-4">
              <div className="mt-1">
                <CheckCircle2 className="h-6 w-6 text-status-success" />
              </div>
              <div className="flex-1">
                <h3 className="text-base font-medium text-status-success">Healthy Run</h3>
                <p className="text-sm text-text-secondary mt-1">
                  No incident thresholds were crossed.
                </p>
              </div>
            </div>
          )}

        </div>
      </div>
    </div>
  );
}
