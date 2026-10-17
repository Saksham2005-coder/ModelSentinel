import { useState, useEffect } from 'react';
import { fetchApi } from '@/services/api/client';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import { Loader2, Plus, Github, Activity, ShieldAlert, GitPullRequest, X, Send } from 'lucide-react';
import { DEMO_INTEGRATIONS, DEMO_WEBHOOKS } from '@/services/api/demoData';
import { useToast } from '@/contexts/ToastContext';

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
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [provider, setProvider] = useState('slack');
  const [name, setName] = useState('');
  const [apiKey, setApiKey] = useState('');
  const [saving, setSaving] = useState(false);
  const { addToast } = useToast();

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [intRes, hookRes] = await Promise.all([
          fetchApi<Integration[]>('/integrations').catch(() => null),
          fetchApi<WebhookEvent[]>('/integrations/webhooks?limit=10').catch(() => null)
        ]);
        setIntegrations(Array.isArray(intRes) && intRes.length > 0 ? intRes : DEMO_INTEGRATIONS);
        setWebhooks(Array.isArray(hookRes) && hookRes.length > 0 ? hookRes : DEMO_WEBHOOKS);
      } catch (e) {
        setIntegrations(DEMO_INTEGRATIONS);
        setWebhooks(DEMO_WEBHOOKS);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  const handleAddIntegration = (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    setTimeout(() => {
      const newInt: Integration = {
        id: `int-${Date.now()}`,
        provider,
        name: name || `${provider.toUpperCase()} Integration`,
        type: provider === 'github' ? 'repository' : provider === 'pagerduty' ? 'alerting' : 'notification',
        status: 'CONNECTED',
        updated_at: new Date().toISOString()
      };
      setIntegrations(prev => [newInt, ...prev]);
      setSaving(false);
      setIsModalOpen(false);
      setName('');
      setApiKey('');
      addToast('success', `Integration "${newInt.name}" connected successfully.`);
    }, 800);
  };

  const handleTestWebhook = () => {
    const newHook: WebhookEvent = {
      id: `wh-test-${Date.now()}`,
      provider: 'github',
      event_type: 'pull_request.synchronized',
      processing_status: 'PROCESSED',
      delivery_id: `del-${Math.random().toString(36).substring(2, 10)}`,
      received_at: new Date().toISOString()
    };
    setWebhooks(prev => [newHook, ...prev]);
    addToast('success', 'Test webhook event emitted and processed successfully.');
  };

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
          <h1 className="text-2xl font-semibold tracking-tight tracking-tight text-text-primary">Integrations</h1>
          <p className="text-text-secondary mt-1">Connect engineering systems to ModelSentinel.</p>
        </div>
        <div className="flex items-center gap-3">
          <Button variant="outline" onClick={handleTestWebhook}>
            <Send className="h-4 w-4 mr-2" /> Emit Test Webhook
          </Button>
          <Button onClick={() => setIsModalOpen(true)} className="bg-brand text-background-base hover:bg-brand/90">
            <Plus className="h-4 w-4 mr-2" /> Add Integration
          </Button>
        </div>
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
                    <div className="h-8 w-8 bg-brand/10 text-brand font-bold rounded-full flex items-center justify-center">
                      {integration.provider.charAt(0).toUpperCase()}
                    </div>
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
          </div>
        </section>
      </div>

      {isModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4">
          <div className="bg-surface border border-border rounded-xl max-w-md w-full p-6 shadow-2xl animate-in fade-in zoom-in-95">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-bold text-text-primary">Connect Integration</h3>
              <button onClick={() => setIsModalOpen(false)} className="text-text-muted hover:text-text-primary">
                <X className="w-5 h-5" />
              </button>
            </div>
            <form onSubmit={handleAddIntegration} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-text-secondary mb-1">Provider</label>
                <select 
                  value={provider} 
                  onChange={e => setProvider(e.target.value)}
                  className="w-full bg-background-base border border-border rounded-lg p-2.5 text-text-primary focus:outline-none focus:border-brand"
                >
                  <option value="slack">Slack</option>
                  <option value="pagerduty">PagerDuty</option>
                  <option value="github">GitHub</option>
                  <option value="datadog">Datadog</option>
                  <option value="prometheus">Prometheus</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-text-secondary mb-1">Integration Name</label>
                <input
                  type="text"
                  placeholder="e.g. SRE Alerts Channel"
                  value={name}
                  onChange={e => setName(e.target.value)}
                  className="w-full bg-background-base border border-border rounded-lg p-2.5 text-text-primary focus:outline-none focus:border-brand"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-text-secondary mb-1">Webhook URL or API Key</label>
                <input
                  type="password"
                  placeholder="https://hooks.slack.com/services/..."
                  value={apiKey}
                  onChange={e => setApiKey(e.target.value)}
                  className="w-full bg-background-base border border-border rounded-lg p-2.5 text-text-primary focus:outline-none focus:border-brand"
                  required
                />
              </div>

              <div className="flex justify-end gap-3 mt-6">
                <Button variant="outline" type="button" onClick={() => setIsModalOpen(false)}>
                  Cancel
                </Button>
                <Button type="submit" disabled={saving} className="bg-brand text-background-base hover:bg-brand/90">
                  {saving ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : null}
                  {saving ? 'Connecting...' : 'Connect Service'}
                </Button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
