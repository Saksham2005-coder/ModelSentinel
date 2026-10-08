import { useState, useEffect } from 'react';
import { fetchApi } from '@/services/api/client';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import { Loader2, Plus, Github, Activity, ShieldAlert, GitPullRequest } from 'lucide-react';

interface Integration {
  id: string;
  provider: string;
  name: string;
  type: string;
  status: string;
  updated_at: string;
}

interface WebhookEvent {
  id: string;
  provider: string;
  event_type: string;
  processing_status: string;
  delivery_id: string;
  received_at: string;
  error_summary?: string;
}

export function IntegrationsPage() {
  const [integrations, setIntegrations] = useState<Integration[]>([]);
  const [webhooks, setWebhooks] = useState<WebhookEvent[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [intRes, hookRes] = await Promise.all([
          fetchApi<Integration[]>('/integrations'),
          fetchApi<WebhookEvent[]>('/integrations/webhooks?limit=10')
        ]);
        setIntegrations(intRes);
        setWebhooks(hookRes);
      } catch (e) {
        console.error('Failed to load integrations', e);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full">
        <Loader2 className="h-8 w-8 animate-spin text-text-secondary" />
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-8 pb-12">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-text-primary">Integrations</h1>
          <p className="text-text-secondary mt-1">Connect engineering systems to ModelSentinel.</p>
        </div>
        <Button>
          <Plus className="h-4 w-4 mr-2" /> Add Integration
        </Button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <section className="bg-surface border border-border rounded-xl p-6">
          <h2 className="text-lg font-bold text-text-primary mb-4 flex items-center gap-2">
            <Activity className="h-5 w-5 text-brand" /> Active Integrations
          </h2>
          <div className="space-y-4">
            {integrations.map(integration => (
              <div key={integration.id} className="flex items-center justify-between p-4 border border-border rounded-lg bg-background-base">
                <div className="flex items-center gap-4">
                  {integration.provider === 'github' ? (
                    <Github className="h-8 w-8 text-text-secondary" />
                  ) : (
                    <div className="h-8 w-8 bg-border rounded-full flex items-center justify-center text-text-muted">?</div>
                  )}
                  <div>
                    <h3 className="font-semibold text-text-primary">{integration.name}</h3>
                    <p className="text-sm text-text-secondary">{integration.type}</p>
                  </div>
                </div>
                <div className="flex flex-col items-end gap-2">
                  <Badge variant={integration.status === 'CONNECTED' ? 'success' : 'warning'}>
                    {integration.status}
                  </Badge>
                  {integration.updated_at && (
                    <span className="text-xs text-text-muted">
                      Updated {new Date(integration.updated_at).toLocaleString()}
                    </span>
                  )}
                </div>
              </div>
            ))}
            {integrations.length === 0 && (
              <p className="text-sm text-text-muted text-center py-4">No active integrations found.</p>
            )}
          </div>
        </section>

        <section className="bg-surface border border-border rounded-xl p-6">
          <h2 className="text-lg font-bold text-text-primary mb-4 flex items-center gap-2">
            <GitPullRequest className="h-5 w-5 text-brand" /> Recent Webhook Events
          </h2>
          <div className="space-y-3">
            {webhooks.map(hook => (
              <div key={hook.id} className="p-3 border border-border rounded bg-background-base text-sm">
                <div className="flex items-center justify-between mb-2">
                  <span className="font-medium flex items-center gap-2">
                    <span className="capitalize">{hook.provider}</span>: {hook.event_type}
                  </span>
                  <Badge variant={
                    hook.processing_status === 'PROCESSED' ? 'success' :
                    hook.processing_status === 'PENDING' ? 'info' : 'danger'
                  }>
                    {hook.processing_status}
                  </Badge>
                </div>
                <div className="flex items-center justify-between text-xs text-text-muted">
                  <span className="font-mono">{hook.delivery_id.substring(0,12)}</span>
                  <span>{new Date(hook.received_at).toLocaleString()}</span>
                </div>
                {hook.error_summary && (
                  <div className="mt-2 text-xs text-status-danger bg-status-danger/10 p-2 rounded flex items-start gap-1">
                    <ShieldAlert className="h-3 w-3 mt-0.5 shrink-0" />
                    <span className="break-all">{hook.error_summary}</span>
                  </div>
                )}
              </div>
            ))}
            {webhooks.length === 0 && (
              <p className="text-sm text-text-muted text-center py-4">No webhook events received.</p>
            )}
          </div>
        </section>
      </div>
    </div>
  );
}
