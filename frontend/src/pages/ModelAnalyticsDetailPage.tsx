import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { analyticsApi, OverviewMetrics } from '../services/api/analytics';
import { ArrowLeft, Activity, ShieldAlert, GitCommit, Crosshair, Clock } from 'lucide-react';

export const ModelAnalyticsDetailPage: React.FC = () => {
  const { modelId } = useParams<{ modelId: string }>();
  const [loading, setLoading] = useState(true);
  const [overview, setOverview] = useState<OverviewMetrics | null>(null);

  useEffect(() => {
    if (modelId) {
      analyticsApi.getModelDetail(modelId)
        .then(setOverview)
        .catch(console.error)
        .finally(() => setLoading(false));
    }
  }, [modelId]);

  if (loading) {
    return (
      <div className="min-h-screen bg-neutral-900 p-8 pt-24 flex items-center justify-center text-neutral-400 animate-pulse">
        Loading model analytics...
      </div>
    );
  }

  if (!overview) {
    return (
      <div className="min-h-screen bg-neutral-900 p-8 pt-24 text-center text-red-400">
        Failed to load model analytics.
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-neutral-900 text-neutral-100 p-8 pt-24 font-sans">
      <div className="max-w-5xl mx-auto space-y-8">
        
        {/* Header */}
        <div>
          <Link to="/analytics" className="inline-flex items-center text-sm font-medium text-neutral-400 hover:text-text-primary mb-4 transition-colors">
            <ArrowLeft className="w-4 h-4 mr-2" /> Back to Analytics
          </Link>
          <div className="flex justify-between items-start">
            <div>
              <h1 className="text-2xl font-semibold tracking-tight tracking-tight text-text-primary flex items-center gap-3">
                <Activity className="w-8 h-8 text-indigo-400" />
                Model Reliability Overview
              </h1>
              <p className="text-neutral-400 mt-1">Deterministic performance breakdown for the selected model.</p>
            </div>
            <Link to={`/models/${modelId}/reliability`} className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-text-primary rounded-lg transition-colors flex items-center gap-2 font-medium">
              <Clock className="w-4 h-4" />
              View Reliability Timeline
            </Link>
          </div>
        </div>

        {/* Score Breakdown */}
        <div className="bg-neutral-800/50 border border-neutral-700/50 rounded-xl p-8 shadow-xl">
          <div className="flex flex-col md:flex-row items-center gap-12">
            <div className="text-center shrink-0">
              <div className={`text-7xl font-black ${overview.reliability_score > 80 ? 'text-emerald-400' : overview.reliability_score > 50 ? 'text-yellow-400' : 'text-red-400'}`}>
                {overview.reliability_score}
              </div>
              <div className="text-sm font-medium text-neutral-500 uppercase tracking-widest mt-2">Reliability Score</div>
            </div>
            
            <div className="flex-1 w-full grid grid-cols-1 sm:grid-cols-2 gap-4">
              {Object.entries(overview.score_contributors).map(([factor, value]) => (
                <div key={factor} className="bg-neutral-900/50 rounded-lg p-4 border border-neutral-800 flex justify-between items-center">
                  <span className="text-sm font-medium text-neutral-300">{factor}</span>
                  <span className={`text-sm font-bold ${value > 0 ? 'text-emerald-400' : value < 0 ? 'text-red-400' : 'text-neutral-500'}`}>
                    {value > 0 ? '+' : ''}{value}
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Metrics Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-6">
          <div className="bg-neutral-800/50 border border-neutral-700/50 rounded-xl p-5 shadow-xl">
            <div className="flex items-center gap-2 mb-2 text-neutral-400">
              <ShieldAlert className="w-4 h-4" />
              <span className="text-xs font-bold uppercase tracking-wider">Incidents</span>
            </div>
            <div className="text-3xl font-semibold text-text-primary">
              {overview.total_incidents}
            </div>
            <div className="text-xs text-red-400 mt-1">{overview.critical_incidents} Critical</div>
          </div>

          <div className="bg-neutral-800/50 border border-neutral-700/50 rounded-xl p-5 shadow-xl">
            <div className="flex items-center gap-2 mb-2 text-neutral-400">
              <Clock className="w-4 h-4" />
              <span className="text-xs font-bold uppercase tracking-wider">MTTR</span>
            </div>
            <div className="text-3xl font-semibold text-text-primary">
              {overview.mttr_minutes !== null ? `${overview.mttr_minutes.toFixed(1)}m` : 'N/A'}
            </div>
            <div className="text-xs text-neutral-500 mt-1">Mean Time to Resolve</div>
          </div>

          <div className="bg-neutral-800/50 border border-neutral-700/50 rounded-xl p-5 shadow-xl">
            <div className="flex items-center gap-2 mb-2 text-neutral-400">
              <Crosshair className="w-4 h-4" />
              <span className="text-xs font-bold uppercase tracking-wider">Coverage</span>
            </div>
            <div className="text-3xl font-semibold text-text-primary">
              {overview.regression_coverage.toFixed(1)}%
            </div>
            <div className="text-xs text-neutral-500 mt-1">Regression Defense</div>
          </div>

          <div className="bg-neutral-800/50 border border-neutral-700/50 rounded-xl p-5 shadow-xl">
            <div className="flex items-center gap-2 mb-2 text-neutral-400">
              <GitCommit className="w-4 h-4" />
              <span className="text-xs font-bold uppercase tracking-wider">Degradation</span>
            </div>
            <div className="text-3xl font-semibold text-text-primary">
              {overview.deployment_degradation_rate.toFixed(1)}%
            </div>
            <div className="text-xs text-neutral-500 mt-1">Post-Deploy Failure</div>
          </div>
        </div>

      </div>
    </div>
  );
};
