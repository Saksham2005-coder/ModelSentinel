import { useState } from 'react';
import { Dialog, DialogHeader, DialogTitle } from '@/components/ui/Dialog';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { MonitoringApi } from '@/services/api/monitoring';

interface Props {
  open: boolean;
  onClose: () => void;
  modelId: string;
  versionId: string;
  onSuccess: () => void;
}

export function RunMonitoringModal({ open, onClose, modelId, versionId, onSuccess }: Props) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleRun = async () => {
    setLoading(true);
    setError(null);
    try {
      await MonitoringApi.runMonitoring(modelId, versionId);
      onSuccess();
      onClose();
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to run monitoring');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={(open) => !open && onClose()}>
        <DialogHeader>
          <DialogTitle>Run Monitoring</DialogTitle>
        </DialogHeader>
        
        <div className="space-y-4 py-4">
          <p className="text-sm text-text-secondary">
            Execute a deterministic monitoring job comparing the baseline dataset to the current dataset window. 
            This will calculate performance metrics, feature drift, prediction drift, and data quality.
          </p>
          
          <div className="space-y-2">
            <label className="text-sm font-medium">Model Version</label>
            <Input value={versionId} disabled />
          </div>

          {error && <div className="text-red-500 text-sm">{error}</div>}

          <div className="flex justify-end gap-3 mt-6">
            <Button variant="outline" onClick={onClose} disabled={loading}>
              Cancel
            </Button>
            <Button onClick={handleRun} disabled={loading}>
              {loading ? 'Running...' : 'Run Monitoring'}
            </Button>
          </div>
        </div>
    </Dialog>
  );
}
