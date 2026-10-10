import { useState, useEffect } from 'react';
import { useParams, Link, useSearchParams } from 'react-router-dom';
import { IntelligenceApi, VersionComparisonResult } from '@/services/api/intelligence';
import { ModelsApi, Model, ModelVersion } from '@/services/api/models';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { Loader2, ArrowLeft, GitCompare, AlertTriangle, CheckCircle2 } from 'lucide-react';

export function VersionComparisonPage() {
  const { modelId } = useParams<{ modelId: string }>();
  const [searchParams] = useSearchParams();
  const v1Param = searchParams.get('v1');
  const v2Param = searchParams.get('v2');

  const [model, setModel] = useState<Model | null>(null);
  const [versions, setVersions] = useState<ModelVersion[]>([]);
  const [v1, setV1] = useState<string>(v1Param || '');
  const [v2, setV2] = useState<string>(v2Param || '');
  
  const [comparison, setComparison] = useState<VersionComparisonResult | null>(null);
  const [loading, setLoading] = useState(true);
  const [comparing, setComparing] = useState(false);

  useEffect(() => {
    const fetchBaseData = async () => {
      if (!modelId) return;
      try {
        setLoading(true);
        const [modelData, versionsData] = await Promise.all([
          ModelsApi.getModel(modelId),
          ModelsApi.getVersions(modelId)
        ]);
        setModel(modelData);
        setVersions(versionsData);
        
        if (versionsData.length >= 2 && !v1Param && !v2Param) {
          setV1(versionsData[1].id);
          setV2(versionsData[0].id);
        }
      } catch (err) {
        console.error('Failed to fetch data', err);
      } finally {
        setLoading(false);
      }
    };
    fetchBaseData();
  }, [modelId, v1Param, v2Param]);

  const handleCompare = async () => {
    if (!modelId || !v1 || !v2) return;
    try {
      setComparing(true);
      const data = await IntelligenceApi.getVersionComparison(modelId, v1, v2);
      setComparison(data);
    } catch (err) {
      console.error('Failed to compare versions', err);
    } finally {
      setComparing(false);
    }
  };

  useEffect(() => {
    const runCompare = async () => {
      if (!modelId || !v1 || !v2) return;
      try {
        setComparing(true);
        const data = await IntelligenceApi.getVersionComparison(modelId, v1, v2);
        setComparison(data);
      } catch (err) {
        console.error('Failed to compare versions', err);
      } finally {
        setComparing(false);
      }
    };
    if (v1 && v2 && modelId) {
      runCompare();
    }
  }, [v1, v2, modelId]);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="w-8 h-8 animate-spin text-primary-500" />
      </div>
    );
  }

  if (!model) {
    return (
      <div className="text-center py-12">
        <p className="text-text-secondary">Model not found.</p>
      </div>
    );
  }

  const v1Name = versions.find(v => v.id === v1)?.version || 'Version A';
  const v2Name = versions.find(v => v.id === v2)?.version || 'Version B';

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Button variant="ghost" size="sm" asChild>
            <Link to={`/models/${modelId}`}>
              <ArrowLeft className="w-4 h-4 mr-2" />
              Back to Model
            </Link>
          </Button>
          <div>
            <h1 className="text-2xl font-semibold text-text-primary flex items-center gap-2">
              <GitCompare className="w-6 h-6 text-primary-500" />
              Version Comparison
            </h1>
            <p className="text-sm text-text-secondary">
              Compare performance, drift, and reliability between two versions of {model.name}
            </p>
          </div>
        </div>
      </div>

      <div className="bg-surface rounded-xl border border-border-subtle p-6 flex flex-col md:flex-row gap-4 items-end">
        <div className="flex-1 space-y-2">
          <label className="text-sm font-medium text-text-secondary">Baseline Version (A)</label>
          <select 
            className="w-full bg-surface-hover border border-border-subtle rounded-md px-3 py-2 text-text-primary focus:outline-none focus:border-primary-500"
            value={v1}
            onChange={(e) => setV1(e.target.value)}
          >
            <option value="" disabled>Select Version</option>
            {versions.map(v => (
              <option key={v.id} value={v.id}>{v.version}</option>
            ))}
          </select>
        </div>
        
        <div className="hidden md:flex pb-2 items-center justify-center px-4">
          <GitCompare className="w-5 h-5 text-text-muted" />
        </div>

        <div className="flex-1 space-y-2">
          <label className="text-sm font-medium text-text-secondary">Comparison Version (B)</label>
          <select 
            className="w-full bg-surface-hover border border-border-subtle rounded-md px-3 py-2 text-text-primary focus:outline-none focus:border-primary-500"
            value={v2}
            onChange={(e) => setV2(e.target.value)}
          >
            <option value="" disabled>Select Version</option>
            {versions.map(v => (
              <option key={v.id} value={v.id}>{v.version}</option>
            ))}
          </select>
        </div>

        <Button onClick={handleCompare} disabled={comparing || !v1 || !v2 || v1 === v2}>
          {comparing ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : null}
          Compare
        </Button>
      </div>

      {comparison && (
        <div className="bg-surface rounded-xl border border-border-subtle overflow-hidden">
          <div className="p-4 border-b border-border-subtle bg-surface-hover flex justify-between items-center">
            <h3 className="font-medium text-text-primary">Comparison Results</h3>
            <div className="flex gap-2">
              <Badge variant="default" className="bg-surface text-text-secondary">Baseline: {v1Name}</Badge>
              <Badge variant="info">Target: {v2Name}</Badge>
            </div>
          </div>
          <div className="p-0 overflow-x-auto">
            <table className="w-full text-sm text-left">
              <thead className="text-xs text-text-secondary uppercase bg-surface-hover">
                <tr>
                  <th className="px-6 py-3">Metric</th>
                  <th className="px-6 py-3">Type</th>
                  <th className="px-6 py-3">{v1Name} (A)</th>
                  <th className="px-6 py-3">{v2Name} (B)</th>
                  <th className="px-6 py-3">Difference</th>
                  <th className="px-6 py-3 text-right">Status</th>
                </tr>
              </thead>
              <tbody>
                {comparison.comparisons.map((c, i) => (
                  <tr key={i} className="border-b border-border-subtle hover:bg-surface-hover/50 transition-colors">
                    <td className="px-6 py-4 font-medium text-text-primary capitalize">{c.metric.replace(/_/g, ' ')}</td>
                    <td className="px-6 py-4 text-text-secondary capitalize">{c.type}</td>
                    <td className="px-6 py-4 font-mono">
                      {typeof c.version_a === 'number' ? c.version_a.toFixed(4) : (c.version_a || 'N/A')}
                    </td>
                    <td className="px-6 py-4 font-mono">
                      {typeof c.version_b === 'number' ? c.version_b.toFixed(4) : (c.version_b || 'N/A')}
                    </td>
                    <td className="px-6 py-4 font-mono">
                      {typeof c.difference === 'number' ? (
                        <span className={c.difference > 0 ? (c.is_regression ? 'text-error-500' : 'text-success-500') : (c.difference < 0 ? (c.is_regression ? 'text-error-500' : 'text-success-500') : 'text-text-muted')}>
                          {c.difference > 0 ? '+' : ''}{c.difference.toFixed(4)}
                        </span>
                      ) : '-'}
                    </td>
                    <td className="px-6 py-4 text-right">
                      {c.is_regression ? (
                        <Badge variant="danger" className="inline-flex items-center gap-1">
                          <AlertTriangle className="w-3 h-3" /> Regression
                        </Badge>
                      ) : (
                        <Badge variant="success" className="inline-flex items-center gap-1">
                          <CheckCircle2 className="w-3 h-3" /> OK
                        </Badge>
                      )}
                    </td>
                  </tr>
                ))}
                {comparison.comparisons.length === 0 && (
                  <tr>
                    <td colSpan={6} className="px-6 py-8 text-center text-text-secondary">
                      No comparable metrics found between these versions.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
