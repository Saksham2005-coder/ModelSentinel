import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Card, CardHeader, CardTitle, CardContent, CardDescription } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { Loader2, Code2, AlertTriangle, CheckCircle2, XCircle, RefreshCw } from 'lucide-react';
import { PatchesApi, PatchProposal } from '@/services/api/patches';
import { InvestigationsApi } from '@/services/api/investigations';
import { changeRiskService, ChangeRiskAssessment } from '@/services/api/changeRisk';

export const PatchWorkspacePage: React.FC = () => {
  const { incidentId } = useParams<{ incidentId: string }>();
  const navigate = useNavigate();

  const [loading, setLoading] = useState(true);
  const [investigationId, setInvestigationId] = useState<string | null>(null);
  const [patches, setPatches] = useState<PatchProposal[]>([]);
  const [activePatch, setActivePatch] = useState<PatchProposal | null>(null);
  const [riskAssessment, setRiskAssessment] = useState<ChangeRiskAssessment | null>(null);
  
  const [generating, setGenerating] = useState(false);
  const [feedback, setFeedback] = useState('');
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchData();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [incidentId]);

  const fetchData = async () => {
    try {
      setLoading(true);
      setError(null);
      // Get investigation for this incident
      const investigations = await InvestigationsApi.getInvestigations(incidentId!);
      if (investigations.length > 0) {
        const inv = investigations[0];
        setInvestigationId(inv.id);
        
        // Get patches
        const pList = await PatchesApi.list(inv.id);
        setPatches(pList);
        if (pList.length > 0) {
          setActivePatch(pList[0]);
        }
      }
    } catch (err: unknown) {
      setError('Failed to load investigation or patches.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (activePatch) {
      changeRiskService.getAssessmentForPatch(activePatch.id)
        .then(data => setRiskAssessment(data))
        .catch(err => console.error("Failed to load risk assessment", err));
    } else {
      setRiskAssessment(null);
    }
  }, [activePatch]);

  const handleProposeFix = async () => {
    if (!investigationId) return;
    
    try {
      setGenerating(true);
      setError(null);
      
      const plan = await PatchesApi.plan(investigationId);
      await PatchesApi.generate(investigationId, plan, activePatch?.id, feedback);
      
      setFeedback('');
      fetchData();
    } catch (err: unknown) {
      const e = err as { response?: { data?: { detail?: string } }, message: string };
      setError(e.response?.data?.detail || e.message || 'Error generating patch');
    } finally {
      setGenerating(false);
    }
  };

  const handleReview = async (decision: 'approve' | 'reject' | 'request_changes') => {
    if (!activePatch) return;
    try {
      setLoading(true);
      setError(null);
      await PatchesApi.review(activePatch.id, decision, feedback);
      setFeedback('');
      fetchData();
    } catch (err: unknown) {
      const e = err as Error;
      setError(e.message || 'Error reviewing patch');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen bg-slate-950">
        <Loader2 className="w-8 h-8 animate-spin text-slate-400" />
      </div>
    );
  }

  if (!investigationId) {
    return (
      <div className="p-8 max-w-4xl mx-auto text-center">
        <AlertTriangle className="w-12 h-12 text-yellow-500 mx-auto mb-4" />
        <h2 className="text-xl font-bold text-slate-100">No Investigation Found</h2>
        <p className="text-slate-400 mt-2">A completed investigation is required before proposing a fix.</p>
        <Button className="mt-4" onClick={() => navigate(`/incidents/${incidentId}/investigation`)}>
          Go to Investigation
        </Button>
      </div>
    );
  }

  return (
    <div className="p-8 max-w-6xl mx-auto space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-slate-100">Fix Workspace</h1>
          <p className="text-slate-400">Review and orchestrate automated repository patches.</p>
        </div>
        <Button onClick={handleProposeFix} disabled={generating} className="bg-emerald-600 hover:bg-emerald-700">
          {generating ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : <Code2 className="w-4 h-4 mr-2" />}
          {patches.length > 0 ? 'Regenerate Patch' : 'Propose Fix'}
        </Button>
      </div>

      {error && (
        <div className="bg-rose-500/10 border border-rose-500/20 text-rose-400 px-4 py-3 rounded">
          {error}
        </div>
      )}

      {!activePatch ? (
        <Card className="bg-slate-900 border-slate-800">
          <CardContent className="py-12 text-center text-slate-400">
            <Code2 className="w-12 h-12 mx-auto mb-4 opacity-50" />
            <p>No patches proposed yet. Click "Propose Fix" to let the AI agent analyze the investigation and generate a code patch.</p>
          </CardContent>
        </Card>
      ) : (
        <div className="grid grid-cols-3 gap-6">
          <div className="col-span-2 space-y-6">
            <Card className="bg-slate-900 border-slate-800">
              <CardHeader>
                <div className="flex justify-between items-center">
                  <CardTitle className="text-slate-100">Patch Proposal</CardTitle>
                  <div className="flex items-center gap-4">
                    {activePatch.status === 'approved' && (
                      <Button
                        size="sm"
                        onClick={() => navigate(`/incidents/${incidentId}/validation`)}
                        className="bg-emerald-600 hover:bg-emerald-700 text-white"
                      >
                        <CheckCircle2 className="w-4 h-4 mr-2" />
                        Validate Patch
                      </Button>
                    )}
                    <Badge variant={
                      activePatch.status === 'approved' ? 'success' :
                      activePatch.status === 'rejected' ? 'danger' : 'default'
                    }>
                      {activePatch.status.toUpperCase()}
                    </Badge>
                  </div>
                </div>
                <CardDescription>Version {activePatch.version}</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <h3 className="font-semibold text-slate-300">Summary</h3>
                  <p className="text-sm text-slate-400">{activePatch.summary}</p>
                </div>
                <div>
                  <h3 className="font-semibold text-slate-300">Rationale</h3>
                  <p className="text-sm text-slate-400">{activePatch.rationale}</p>
                </div>
                <div>
                  <h3 className="font-semibold text-slate-300">Risk Assessment</h3>
                  <div className="mt-2 flex items-center gap-2">
                    <Badge variant={activePatch.risk_summary?.level === 'Low' ? 'default' : 'danger'}>
                      {activePatch.risk_summary?.level} Risk
                    </Badge>
                    <span className="text-sm text-slate-400">
                      {activePatch.risk_summary?.stats?.files_changed || 0} files changed
                    </span>
                  </div>
                  {activePatch.risk_summary?.reasons && activePatch.risk_summary.reasons.length > 0 && (
                    <ul className="list-disc list-inside mt-2 text-sm text-slate-400">
                      {activePatch.risk_summary.reasons.map((r, i) => <li key={i}>{r}</li>)}
                    </ul>
                  )}
                </div>

                {riskAssessment && (
                  <div className="pt-4 border-t border-slate-800">
                    <h3 className="font-semibold text-slate-300 mb-4">CHANGE RISK</h3>
                    <div className="flex items-center gap-4 mb-4">
                      <div className="text-2xl font-bold text-slate-100">{riskAssessment.risk_score}</div>
                      <Badge variant={
                        riskAssessment.risk_level === 'CRITICAL' ? 'danger' :
                        riskAssessment.risk_level === 'HIGH' ? 'danger' :
                        riskAssessment.risk_level === 'MODERATE' ? 'warning' : 'success'
                      }>
                        {riskAssessment.risk_level} RISK
                      </Badge>
                    </div>
                    
                    <div className="grid grid-cols-2 gap-4 text-sm">
                      <div>
                        <span className="text-slate-400 block mb-1">Blast Radius</span>
                        <ul className="text-slate-300 space-y-1">
                          <li>{riskAssessment.blast_radius.files.length} files</li>
                          <li>{riskAssessment.blast_radius.models.length} models</li>
                          <li>{riskAssessment.blast_radius.regression_tests.length} regression tests</li>
                          <li>{riskAssessment.blast_radius.historical_incidents.length} historical incidents</li>
                        </ul>
                      </div>
                      <div>
                        <span className="text-slate-400 block mb-1">Primary Risk Factors</span>
                        <ul className="text-slate-300 space-y-1">
                          {riskAssessment.factors.map((f, i) => (
                            <li key={i} className="truncate" title={f.factor}>• {f.factor} (+{f.contribution})</li>
                          ))}
                        </ul>
                      </div>
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>

            <div className="space-y-4">
              <h3 className="text-lg font-semibold text-slate-100">File Changes</h3>
              {activePatch.file_changes.map((change) => (
                <Card key={change.id} className="bg-slate-900 border-slate-800 overflow-hidden">
                  <CardHeader className="bg-slate-950 py-3 border-b border-slate-800">
                    <div className="flex items-center justify-between">
                      <span className="font-mono text-sm text-emerald-400">{change.file_path}</span>
                      <div className="text-xs space-x-2">
                        <span className="text-emerald-500">+{change.additions}</span>
                        <span className="text-rose-500">-{change.deletions}</span>
                      </div>
                    </div>
                  </CardHeader>
                  <CardContent className="p-0">
                    <pre className="p-4 text-sm font-mono text-slate-300 overflow-x-auto whitespace-pre-wrap">
                      {change.diff_text}
                    </pre>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>

          <div className="space-y-6">
            <Card className="bg-slate-900 border-slate-800">
              <CardHeader>
                <CardTitle className="text-slate-100">Review</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <textarea
                  placeholder="Leave feedback or request changes..."
                  className="w-full bg-slate-950 border border-slate-800 rounded-md p-3 text-sm text-slate-300 focus:outline-none focus:ring-1 focus:ring-emerald-500"
                  rows={4}
                  value={feedback}
                  onChange={(e) => setFeedback(e.target.value)}
                />
                
                {activePatch.status === 'review' && (
                  <div className="grid grid-cols-2 gap-2">
                    <Button 
                      variant="outline" 
                      className="border-emerald-500 text-emerald-500 hover:bg-emerald-950"
                      onClick={() => handleReview('approve')}
                    >
                      <CheckCircle2 className="w-4 h-4 mr-2" />
                      Approve
                    </Button>
                    <Button 
                      variant="outline" 
                      className="border-rose-500 text-rose-500 hover:bg-rose-950"
                      onClick={() => handleReview('reject')}
                    >
                      <XCircle className="w-4 h-4 mr-2" />
                      Reject
                    </Button>
                    <Button 
                      variant="outline" 
                      className="col-span-2 border-yellow-500 text-yellow-500 hover:bg-yellow-950"
                      onClick={() => handleReview('request_changes')}
                    >
                      <RefreshCw className="w-4 h-4 mr-2" />
                      Request Changes
                    </Button>
                  </div>
                )}
              </CardContent>
            </Card>
            
            {activePatch.reviews.length > 0 && (
              <Card className="bg-slate-900 border-slate-800">
                <CardHeader>
                  <CardTitle className="text-slate-100">Review History</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {activePatch.reviews.map(rev => (
                      <div key={rev.id} className="border-l-2 border-slate-700 pl-4 py-1">
                        <div className="flex items-center gap-2 mb-1">
                          <span className="font-semibold text-sm text-slate-300 capitalize">{rev.reviewer_type}</span>
                          <Badge variant="info" className="text-[10px] uppercase">
                            {rev.decision}
                          </Badge>
                        </div>
                        {rev.comment && (
                          <p className="text-sm text-slate-400">{rev.comment}</p>
                        )}
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            )}
          </div>
        </div>
      )}
    </div>
  );
};
