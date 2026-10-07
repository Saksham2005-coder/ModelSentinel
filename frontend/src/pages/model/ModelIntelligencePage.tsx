import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { IntelligenceApi, ModelIntelligence } from '@/services/api/intelligence';
import { ModelsApi, Model } from '@/services/api/models';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { Loader2, ArrowLeft, BrainCircuit, Activity, ShieldCheck, TrendingDown, TrendingUp, Minus } from 'lucide-react';

export function ModelIntelligencePage() {
  const { modelId } = useParams<{ modelId: string }>();
  const [model, setModel] = useState<Model | null>(null);
  const [intelligence, setIntelligence] = useState<ModelIntelligence | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      if (!modelId) return;
      try {
        setLoading(true);
        const [modelData, intelData] = await Promise.all([
          ModelsApi.getModel(modelId),
          IntelligenceApi.getModelIntelligence(modelId)
        ]);
        setModel(modelData);
        setIntelligence(intelData);
      } catch (err) {
        console.error('Failed to fetch intelligence', err);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [modelId]);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="w-8 h-8 animate-spin text-primary-500" />
      </div>
    );
  }

  if (!model || !intelligence) {
    return (
      <div className="text-center py-12">
        <p className="text-text-secondary">Failed to load model intelligence.</p>
      </div>
    );
  }

  const getHealthColor = (status: string) => {
    switch (status) {
      case 'HEALTHY': return 'text-success-500';
      case 'STABLE': return 'text-blue-500';
      case 'DEGRADED': return 'text-warning-500';
      case 'CRITICAL': return 'text-error-500';
      default: return 'text-text-secondary';
    }
  };

  const getHealthBadge = (status: string) => {
    switch (status) {
      case 'HEALTHY': return <Badge variant="success">Healthy</Badge>;
      case 'STABLE': return <Badge variant="info">Stable</Badge>;
      case 'DEGRADED': return <Badge variant="warning">Degraded</Badge>;
      case 'CRITICAL': return <Badge variant="danger">Critical</Badge>;
      default: return <Badge variant="default">Unknown</Badge>;
    }
  };

  const getTrendIcon = (trend: string) => {
    if (trend === 'increasing') return <TrendingUp className="w-4 h-4 text-error-500" />;
    if (trend === 'decreasing') return <TrendingDown className="w-4 h-4 text-success-500" />;
    return <Minus className="w-4 h-4 text-text-muted" />;
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Link to={`/models/${modelId}`}>
            <Button variant="ghost" size="sm">
              <ArrowLeft className="w-4 h-4 mr-2" />
              Back to Model
            </Button>
          </Link>
          <div>
            <h1 className="text-2xl font-semibold text-text-primary flex items-center gap-2">
              <BrainCircuit className="w-6 h-6 text-primary-500" />
              Model Intelligence
            </h1>
            <p className="text-sm text-text-secondary">
              Health, version analytics, and behavioral insights for {model.name}
            </p>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-1 space-y-6">
          <div className="bg-surface rounded-xl border border-border-subtle p-6 flex flex-col items-center justify-center text-center">
            <h3 className="text-sm font-medium text-text-secondary mb-4 uppercase tracking-wider">Overall Health Score</h3>
            <div className={`text-7xl font-bold mb-4 ${getHealthColor(intelligence.health.status)}`}>
              {intelligence.health.score}
            </div>
            {getHealthBadge(intelligence.health.status)}
          </div>

          <div className="bg-surface rounded-xl border border-border-subtle p-6 space-y-4">
            <h3 className="font-medium text-text-primary">Health Breakdown</h3>
            <div className="space-y-3">
              <div className="flex justify-between items-center text-sm">
                <span className="text-text-secondary">Performance</span>
                <span className="font-medium">{intelligence.health.breakdown.performance} / 35</span>
              </div>
              <div className="w-full bg-surface-hover rounded-full h-2">
                <div className="bg-success-500 h-2 rounded-full" style={{ width: `${(intelligence.health.breakdown.performance / 35) * 100}%` }}></div>
              </div>

              <div className="flex justify-between items-center text-sm">
                <span className="text-text-secondary">Data Quality</span>
                <span className="font-medium">{intelligence.health.breakdown.data_quality} / 20</span>
              </div>
              <div className="w-full bg-surface-hover rounded-full h-2">
                <div className="bg-blue-500 h-2 rounded-full" style={{ width: `${(intelligence.health.breakdown.data_quality / 20) * 100}%` }}></div>
              </div>

              <div className="flex justify-between items-center text-sm">
                <span className="text-text-secondary">Feature Drift</span>
                <span className="font-medium">{intelligence.health.breakdown.feature_drift} / 20</span>
              </div>
              <div className="w-full bg-surface-hover rounded-full h-2">
                <div className="bg-warning-500 h-2 rounded-full" style={{ width: `${(intelligence.health.breakdown.feature_drift / 20) * 100}%` }}></div>
              </div>

              <div className="flex justify-between items-center text-sm">
                <span className="text-text-secondary">Prediction Stability</span>
                <span className="font-medium">{intelligence.health.breakdown.prediction_stability} / 10</span>
              </div>
              <div className="w-full bg-surface-hover rounded-full h-2">
                <div className="bg-purple-500 h-2 rounded-full" style={{ width: `${(intelligence.health.breakdown.prediction_stability / 10) * 100}%` }}></div>
              </div>

              <div className="flex justify-between items-center text-sm">
                <span className="text-text-secondary">Incident State</span>
                <span className="font-medium">{intelligence.health.breakdown.incident_state} / 15</span>
              </div>
              <div className="w-full bg-surface-hover rounded-full h-2">
                <div className="bg-error-500 h-2 rounded-full" style={{ width: `${(intelligence.health.breakdown.incident_state / 15) * 100}%` }}></div>
              </div>
            </div>
          </div>
        </div>

        <div className="lg:col-span-2 space-y-6">
          <div className="bg-surface rounded-xl border border-border-subtle overflow-hidden">
            <div className="p-4 border-b border-border-subtle bg-surface-hover">
              <h3 className="font-medium text-text-primary flex items-center gap-2">
                <Activity className="w-4 h-4" /> Feature Health Insights
              </h3>
            </div>
            <div className="p-0 overflow-x-auto">
              <table className="w-full text-sm text-left">
                <thead className="text-xs text-text-secondary uppercase bg-surface-hover">
                  <tr>
                    <th className="px-6 py-3">Feature</th>
                    <th className="px-6 py-3">Type</th>
                    <th className="px-6 py-3">Drift Score</th>
                    <th className="px-6 py-3">Trend</th>
                    <th className="px-6 py-3">Incidents</th>
                    <th className="px-6 py-3">Status</th>
                  </tr>
                </thead>
                <tbody>
                  {intelligence.features.map((feat) => (
                    <tr key={feat.feature_name} className="border-b border-border-subtle">
                      <td className="px-6 py-4 font-medium text-text-primary">{feat.feature_name}</td>
                      <td className="px-6 py-4 text-text-secondary">{feat.feature_type}</td>
                      <td className="px-6 py-4 font-mono">{feat.drift_score.toFixed(3)}</td>
                      <td className="px-6 py-4">
                        <div className="flex items-center gap-1">
                          {getTrendIcon(feat.trend)}
                          <span className="capitalize text-xs">{feat.trend}</span>
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        {feat.incident_count > 0 ? (
                          <span className="text-error-500 font-medium">{feat.incident_count}</span>
                        ) : (
                          <span className="text-text-muted">0</span>
                        )}
                      </td>
                      <td className="px-6 py-4">
                        <Badge variant={feat.status === 'healthy' ? 'success' : feat.status === 'warning' ? 'warning' : 'danger'}>
                          {feat.status}
                        </Badge>
                      </td>
                    </tr>
                  ))}
                  {intelligence.features.length === 0 && (
                    <tr>
                      <td colSpan={6} className="px-6 py-8 text-center text-text-secondary">
                        No feature health data available.
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>

          <div className="bg-surface rounded-xl border border-border-subtle overflow-hidden">
            <div className="p-4 border-b border-border-subtle bg-surface-hover">
              <h3 className="font-medium text-text-primary flex items-center gap-2">
                <ShieldCheck className="w-4 h-4" /> Segment Health Insights
              </h3>
            </div>
            <div className="p-0 overflow-x-auto">
              <table className="w-full text-sm text-left">
                <thead className="text-xs text-text-secondary uppercase bg-surface-hover">
                  <tr>
                    <th className="px-6 py-3">Segment</th>
                    <th className="px-6 py-3">Metric</th>
                    <th className="px-6 py-3">Baseline</th>
                    <th className="px-6 py-3">Current</th>
                    <th className="px-6 py-3">Change</th>
                    <th className="px-6 py-3">Status</th>
                  </tr>
                </thead>
                <tbody>
                  {intelligence.segments.map((seg) => (
                    <tr key={seg.segment_name} className="border-b border-border-subtle">
                      <td className="px-6 py-4 font-medium text-text-primary">{seg.segment_name}</td>
                      <td className="px-6 py-4 text-text-secondary">{seg.primary_metric}</td>
                      <td className="px-6 py-4 font-mono">{seg.baseline_metric_value?.toFixed(3) || '-'}</td>
                      <td className="px-6 py-4 font-mono">{seg.current_metric_value.toFixed(3)}</td>
                      <td className="px-6 py-4 font-mono text-error-500">
                        {seg.change < 0 ? (
                          <span className="flex items-center gap-1">
                            <TrendingDown className="w-3 h-3" /> {(seg.change * 100).toFixed(1)}%
                          </span>
                        ) : (
                          <span className="text-success-500">{(seg.change * 100).toFixed(1)}%</span>
                        )}
                      </td>
                      <td className="px-6 py-4">
                        <Badge variant={seg.status === 'healthy' ? 'success' : seg.status === 'warning' ? 'warning' : 'danger'}>
                          {seg.status}
                        </Badge>
                      </td>
                    </tr>
                  ))}
                  {intelligence.segments.length === 0 && (
                    <tr>
                      <td colSpan={6} className="px-6 py-8 text-center text-text-secondary">
                        No segment health data available.
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
