import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { X, Loader2, UploadCloud } from 'lucide-react';
import { ModelsApi, Model } from '@/services/api/models';
import { TelemetryApi } from '@/services/api/telemetry';

interface IngestTelemetryModalProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onSuccess: () => void;
}

export function IngestTelemetryModal({ open, onOpenChange, onSuccess }: IngestTelemetryModalProps) {
  const [models, setModels] = useState<Model[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [modelId, setModelId] = useState('');
  const [source, setSource] = useState('production-api');
  const [windowStart, setWindowStart] = useState('');
  const [windowEnd, setWindowEnd] = useState('');
  const [file, setFile] = useState<File | null>(null);

  useEffect(() => {
    if (open) {
      ModelsApi.getModels({ limit: 100 }).then((res) => {
        setModels(res.items);
        if (res.items.length > 0) {
          setModelId(res.items[0].id);
        }
      });
      // default times
      const now = new Date();
      const oneHourAgo = new Date(now.getTime() - 60 * 60 * 1000);
      setWindowEnd(now.toISOString().slice(0, 16));
      setWindowStart(oneHourAgo.toISOString().slice(0, 16));
    } else {
      setFile(null);
      setError(null);
      setLoading(false);
    }
  }, [open]);

  if (!open) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file) {
      setError("Please select a CSV file.");
      return;
    }

    try {
      setLoading(true);
      setError(null);
      const formData = new FormData();
      formData.append('model_id', modelId);
      
      // In a real app we'd fetch versions. For demo, modelsentinel handles it or we pass a hardcoded/fetched version
      // The backend creates models, let's fetch versions or pass a dummy that backend ignores if it finds active
      // Actually backend needs real version_id. We'll fetch it!
      const modelDetail = await ModelsApi.getModel(modelId);
      if (!modelDetail.versions || modelDetail.versions.length === 0) {
        throw new Error("Model has no versions");
      }
      const actualVersionId = modelDetail.versions[0].id; // just use first version
      
      formData.append('model_version_id', actualVersionId);
      formData.append('source', source);
      formData.append('window_start', new Date(windowStart).toISOString());
      formData.append('window_end', new Date(windowEnd).toISOString());
      formData.append('file', file);

      await TelemetryApi.uploadTelemetry(formData);
      onSuccess();
      onOpenChange(false);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to process telemetry');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-background/80 backdrop-blur-sm p-4">
      <div className="bg-surface border border-border w-full max-w-lg rounded-2xl shadow-xl flex flex-col max-h-[90vh]">
        <div className="flex items-center justify-between p-6 border-b border-border">
          <h2 className="text-xl font-bold text-text-primary flex items-center gap-2">
            <UploadCloud className="h-5 w-5 text-brand" />
            Process Telemetry
          </h2>
          <button 
            onClick={() => onOpenChange(false)}
            className="text-text-muted hover:text-text-primary transition-colors"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        <div className="p-6 overflow-y-auto">
          {error && (
            <div className="mb-6 p-4 bg-status-danger/10 border border-status-danger/20 rounded-xl text-status-danger text-sm">
              {error}
            </div>
          )}

          <form id="telemetry-form" onSubmit={handleSubmit} className="flex flex-col gap-5">
            
            <div className="flex flex-col gap-2">
              <label className="text-sm font-medium text-text-primary">Target Model</label>
              <select 
                value={modelId}
                onChange={(e) => setModelId(e.target.value)}
                className="w-full bg-surface border border-border-strong rounded-lg px-3 py-2 text-text-primary focus:outline-none focus:border-brand"
                required
              >
                {models.map(m => (
                  <option key={m.id} value={m.id}>{m.name}</option>
                ))}
              </select>
            </div>

            <div className="flex flex-col gap-2">
              <label className="text-sm font-medium text-text-primary">Source</label>
              <Input 
                value={source} 
                onChange={e => setSource(e.target.value)} 
                placeholder="e.g., production-api"
                required
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="flex flex-col gap-2">
                <label className="text-sm font-medium text-text-primary">Window Start</label>
                <Input 
                  type="datetime-local" 
                  value={windowStart} 
                  onChange={e => setWindowStart(e.target.value)} 
                  required
                />
              </div>
              <div className="flex flex-col gap-2">
                <label className="text-sm font-medium text-text-primary">Window End</label>
                <Input 
                  type="datetime-local" 
                  value={windowEnd} 
                  onChange={e => setWindowEnd(e.target.value)} 
                  required
                />
              </div>
            </div>

            <div className="flex flex-col gap-2">
              <label className="text-sm font-medium text-text-primary">Telemetry File (CSV)</label>
              <div className="border-2 border-dashed border-border-strong rounded-xl p-6 flex flex-col items-center justify-center text-center">
                <Input 
                  type="file" 
                  accept=".csv"
                  onChange={(e) => setFile(e.target.files?.[0] || null)}
                  className="w-full"
                  required
                />
                <p className="text-xs text-text-muted mt-2">
                  Must include feature columns and 'prediction' column.
                </p>
              </div>
            </div>
          </form>
        </div>

        <div className="p-6 border-t border-border flex justify-end gap-3 bg-surface-hover/50 rounded-b-2xl">
          <Button variant="outline" onClick={() => onOpenChange(false)} type="button">
            Cancel
          </Button>
          <Button variant="primary" type="submit" form="telemetry-form" disabled={loading}>
            {loading ? <Loader2 className="h-4 w-4 animate-spin mr-2" /> : null}
            Process Window
          </Button>
        </div>
      </div>
    </div>
  );
}
