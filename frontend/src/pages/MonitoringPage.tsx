import { useEffect, useState, useCallback } from 'react';
import { useParams } from 'react-router-dom';
import { ModelsApi, ModelDetailResponse } from '@/services/api/models';
import { 
  MonitoringApi, 
  MonitoringRun, 
  MetricResult, 
  FeatureDriftResult, 
  DataQualityResult,
  PredictionDriftResult,
  SegmentResult
} from '@/services/api/monitoring';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { RunMonitoringModal } from '@/features/monitoring/components/RunMonitoringModal';
import { Play } from 'lucide-react';

import { DEMO_MODELS } from '@/services/api/demoData';

export function MonitoringPage() {
  const { modelId } = useParams<{ modelId: string }>();
  const [model, setModel] = useState<ModelDetailResponse | null>(null);
  const [runs, setRuns] = useState<MonitoringRun[]>([]);
  const [metrics, setMetrics] = useState<MetricResult[]>([]);
  const [featureDrift, setFeatureDrift] = useState<FeatureDriftResult[]>([]);
  const [dataQuality, setDataQuality] = useState<DataQualityResult[]>([]);
  const [predictionDrift, setPredictionDrift] = useState<PredictionDriftResult[]>([]);
  const [segments, setSegments] = useState<SegmentResult[]>([]);
  const [loading, setLoading] = useState(true);
  const [isModalOpen, setIsModalOpen] = useState(false);

  const fetchData = useCallback(async () => {
    if (!modelId) return;
    setLoading(true);
    try {
      const [modelRes, runsRes, metricsRes, driftRes, dqRes, pdRes, segRes] = await Promise.all([
        ModelsApi.getModel(modelId).catch(() => null),
        MonitoringApi.getRuns(modelId).catch(() => []),
        MonitoringApi.getMetrics(modelId).catch(() => []),
        MonitoringApi.getFeatureDrift(modelId).catch(() => []),
        MonitoringApi.getDataQuality(modelId).catch(() => []),
        MonitoringApi.getPredictionDrift(modelId).catch(() => []),
        MonitoringApi.getSegments(modelId).catch(() => [])
      ]);

      const matchedDemo = DEMO_MODELS.items.find(m => m.id === modelId || m.slug === modelId) || DEMO_MODELS.items[0];
      const effectiveModel: ModelDetailResponse = (modelRes as ModelDetailResponse) || {
        ...matchedDemo,
        versions: [
          { id: 'v-21', model_id: matchedDemo.id, version: 'v2.1', is_active: true, created_at: new Date().toISOString() },
          { id: 'v-20', model_id: matchedDemo.id, version: 'v2.0', is_active: false, created_at: new Date(Date.now() - 864000000).toISOString() }
        ]
      };
      setModel(effectiveModel);

      const defaultRunId = (runsRes && runsRes.length > 0) ? runsRes[0].id : 'mon-run-latest';
      const effectiveRuns: MonitoringRun[] = (runsRes && runsRes.length > 0) ? runsRes : [
        {
          id: defaultRunId,
          model_id: effectiveModel.id,
          model_version_id: 'v2.1',
          status: 'COMPLETED',
          health_summary: effectiveModel.status === 'UNHEALTHY' ? 'critical' : effectiveModel.status === 'AT_RISK' ? 'warning' : 'healthy',
          started_at: new Date(Date.now() - 3600000).toISOString(),
          completed_at: new Date(Date.now() - 3300000).toISOString(),
          created_at: new Date(Date.now() - 3600000).toISOString()
        }
      ];
      setRuns(effectiveRuns);

      const effectiveMetrics: MetricResult[] = (metricsRes && metricsRes.length > 0) ? metricsRes : [
        {
          id: 'm-1',
          monitoring_run_id: defaultRunId,
          metric_name: 'f1_score',
          metric_value: effectiveModel.status === 'UNHEALTHY' ? 0.72 : 0.89,
          status: effectiveModel.status === 'UNHEALTHY' ? 'degraded' : 'healthy',
          created_at: new Date().toISOString()
        },
        {
          id: 'm-2',
          monitoring_run_id: defaultRunId,
          metric_name: 'accuracy',
          metric_value: 0.88,
          status: 'healthy',
          created_at: new Date().toISOString()
        }
      ];
      setMetrics(effectiveMetrics);

      const effectiveFeatureDrift: FeatureDriftResult[] = (driftRes && driftRes.length > 0) ? driftRes : [
        {
          id: 'fd-1',
          monitoring_run_id: defaultRunId,
          feature_name: 'text_length',
          feature_type: 'numerical',
          drift_method: 'ks_test',
          drift_score: 0.12,
          status: 'healthy',
          created_at: new Date().toISOString()
        },
        {
          id: 'fd-2',
          monitoring_run_id: defaultRunId,
          feature_name: 'emoji_count',
          feature_type: 'numerical',
          drift_method: 'ks_test',
          drift_score: 0.44,
          status: 'drift_detected',
          created_at: new Date().toISOString()
        },
        {
          id: 'fd-3',
          monitoring_run_id: defaultRunId,
          feature_name: 'capital_run_length',
          feature_type: 'numerical',
          drift_method: 'psi',
          drift_score: 0.08,
          status: 'healthy',
          created_at: new Date().toISOString()
        }
      ];
      setFeatureDrift(effectiveFeatureDrift);

      const effectiveDataQuality: DataQualityResult[] = (dqRes && dqRes.length > 0) ? dqRes : [
        {
          id: 'dq-1',
          monitoring_run_id: defaultRunId,
          metric_name: 'missing_value_percentage',
          value: 0.05,
          status: 'healthy',
          created_at: new Date().toISOString()
        }
      ];
      setDataQuality(effectiveDataQuality);

      const effectivePredictionDrift: PredictionDriftResult[] = (pdRes && pdRes.length > 0) ? pdRes : [
        {
          id: 'pd-1',
          monitoring_run_id: defaultRunId,
          prediction_metric: 'class_drift_psi',
          value: 0.18,
          status: 'warning',
          created_at: new Date().toISOString()
        }
      ];
      setPredictionDrift(effectivePredictionDrift);

      const effectiveSegments: SegmentResult[] = (segRes && segRes.length > 0) ? segRes : [
        {
          id: 'seg-1',
          monitoring_run_id: defaultRunId,
          segment_name: 'url_heavy',
          sample_count: 12400,
          primary_metric: 'f1_score',
          baseline_metric_value: 0.89,
          current_metric_value: 0.68,
          change: -0.21,
          status: 'degraded'
        },
        {
          id: 'seg-2',
          monitoring_run_id: defaultRunId,
          segment_name: 'normal',
          sample_count: 37600,
          primary_metric: 'f1_score',
          baseline_metric_value: 0.91,
          current_metric_value: 0.89,
          change: -0.02,
          status: 'healthy'
        }
      ];
      setSegments(effectiveSegments);
    } catch {
      // Never crash the view
    } finally {
      setLoading(false);
    }
  }, [modelId]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  if (loading && !model) return <div className="p-8">Loading monitoring data...</div>;
  if (!model) return <div className="p-8">Loading model telemetry...</div>;

  const activeVersion = model.versions.find(v => v.is_active) || model.versions[0];
  const latestRun = runs.length > 0 ? runs[0] : null;
  const latestMetrics = metrics.filter(m => latestRun && m.monitoring_run_id === latestRun.id);
  const f1Metric = latestMetrics.find(m => m.metric_name === 'f1_score');
  
  return (
    <div className="p-8 space-y-8">
      <div className="flex justify-between items-start">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight tracking-tight mb-2">Monitoring: {model.name}</h1>
          <div className="flex gap-2">
            <Badge variant="default">Version: {activeVersion?.version || 'N/A'}</Badge>
            <Badge variant="default">{model.environment}</Badge>
            <Badge variant={latestRun?.health_summary === 'critical' ? 'danger' : latestRun?.health_summary === 'warning' ? 'warning' : 'success'}>
              {latestRun ? latestRun.health_summary : 'No runs yet'}
            </Badge>
          </div>
        </div>
        <Button onClick={() => setIsModalOpen(true)}>
          <Play className="w-4 h-4 mr-2" />
          Run Monitoring
        </Button>
      </div>

      {!latestRun ? (
        <div className="p-12 text-center border rounded-lg bg-surface-50 text-text-secondary">
          No monitoring runs found for this model. Click "Run Monitoring" to establish a baseline.
        </div>
      ) : (
        <>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="p-4 border rounded-lg bg-surface-50">
              <div className="text-sm text-text-secondary mb-1">Model Performance (F1)</div>
              <div className="text-2xl font-semibold tracking-tight">{f1Metric ? (f1Metric.metric_value * 100).toFixed(1) + '%' : 'N/A'}</div>
              <div className={`text-sm ${f1Metric?.status === 'healthy' ? 'text-green-500' : 'text-brand'}`}>
                {f1Metric?.status || 'Unknown'}
              </div>
            </div>
            <div className="p-4 border rounded-lg bg-surface-50">
              <div className="text-sm text-text-secondary mb-1">Data Quality (Missing)</div>
              {(() => {
                const dq = dataQuality.find(d => d.monitoring_run_id === latestRun.id && d.metric_name === 'missing_value_percentage');
                return (
                  <>
                    <div className="text-2xl font-semibold tracking-tight">{dq ? dq.value.toFixed(2) + '%' : '0%'}</div>
                    <div className={`text-sm ${dq?.status === 'healthy' ? 'text-green-500' : 'text-brand'}`}>{dq?.status || 'Healthy'}</div>
                  </>
                );
              })()}
            </div>
            <div className="p-4 border rounded-lg bg-surface-50">
              <div className="text-sm text-text-secondary mb-1">Prediction Drift</div>
              {(() => {
                const pd = predictionDrift.find(d => d.monitoring_run_id === latestRun.id && d.prediction_metric === 'class_drift_psi');
                return (
                  <>
                    <div className="text-2xl font-semibold tracking-tight">{pd ? pd.value.toFixed(3) : 'N/A'}</div>
                    <div className={`text-sm ${pd?.status === 'healthy' ? 'text-green-500' : 'text-brand'}`}>{pd?.status || 'Unknown'}</div>
                  </>
                );
              })()}
            </div>
            <div className="p-4 border rounded-lg bg-surface-50">
              <div className="text-sm text-text-secondary mb-1">Last Run</div>
              <div className="text-lg font-medium">{new Date(latestRun.completed_at).toLocaleString()}</div>
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            <div className="space-y-4">
              <h2 className="text-xl font-semibold">Feature Drift</h2>
              <div className="border rounded-lg overflow-hidden">
                <table className="w-full text-sm text-left">
                  <thead className="bg-surface-100 text-text-secondary">
                    <tr>
                      <th className="px-4 py-3 font-medium">Feature</th>
                      <th className="px-4 py-3 font-medium">Method</th>
                      <th className="px-4 py-3 font-medium">Score</th>
                      <th className="px-4 py-3 font-medium">Status</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-border">
                    {featureDrift.filter(d => d.monitoring_run_id === latestRun.id).map(drift => (
                      <tr key={drift.id} className="bg-surface-50">
                        <td className="px-4 py-3 font-medium">{drift.feature_name}</td>
                        <td className="px-4 py-3">{drift.drift_method}</td>
                        <td className="px-4 py-3">{drift.drift_score.toFixed(3)}</td>
                        <td className="px-4 py-3">
                          <Badge variant={drift.status === 'critical' ? 'danger' : drift.status === 'warning' ? 'warning' : 'success'}>
                            {drift.status}
                          </Badge>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>

            <div className="space-y-4">
              <h2 className="text-xl font-semibold">Segment Analysis</h2>
              <div className="border rounded-lg overflow-hidden">
                <table className="w-full text-sm text-left">
                  <thead className="bg-surface-100 text-text-secondary">
                    <tr>
                      <th className="px-4 py-3 font-medium">Segment</th>
                      <th className="px-4 py-3 font-medium">Samples</th>
                      <th className="px-4 py-3 font-medium">Change (F1)</th>
                      <th className="px-4 py-3 font-medium">Status</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-border">
                    {segments.filter(s => s.monitoring_run_id === latestRun.id).map(seg => (
                      <tr key={seg.id} className="bg-surface-50">
                        <td className="px-4 py-3 font-medium">{seg.segment_name}</td>
                        <td className="px-4 py-3">{seg.sample_count}</td>
                        <td className="px-4 py-3">{seg.change ? seg.change.toFixed(1) + '%' : 'N/A'}</td>
                        <td className="px-4 py-3">
                          <Badge variant={seg.status === 'critical' ? 'danger' : seg.status === 'warning' ? 'warning' : 'success'}>
                            {seg.status}
                          </Badge>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
          
          <div className="space-y-4">
            <h2 className="text-xl font-semibold">Monitoring Run History</h2>
            <div className="border rounded-lg overflow-hidden">
              <table className="w-full text-sm text-left">
                <thead className="bg-surface-100 text-text-secondary">
                  <tr>
                    <th className="px-4 py-3 font-medium">Run ID</th>
                    <th className="px-4 py-3 font-medium">Started</th>
                    <th className="px-4 py-3 font-medium">Status</th>
                    <th className="px-4 py-3 font-medium">Health Summary</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-border">
                  {runs.map(run => (
                    <tr key={run.id} className="bg-surface-50">
                      <td className="px-4 py-3 font-medium font-mono text-xs">{run.id}</td>
                      <td className="px-4 py-3">{new Date(run.started_at).toLocaleString()}</td>
                      <td className="px-4 py-3 capitalize">{run.status}</td>
                      <td className="px-4 py-3">
                        <Badge variant={run.health_summary === 'critical' ? 'danger' : run.health_summary === 'warning' ? 'warning' : 'success'}>
                          {run.health_summary}
                        </Badge>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </>
      )}

      {isModalOpen && activeVersion && (
        <RunMonitoringModal
          open={isModalOpen}
          onClose={() => setIsModalOpen(false)}
          modelId={model.id}
          versionId={activeVersion.id}
          onSuccess={fetchData}
        />
      )}
    </div>
  );
}
