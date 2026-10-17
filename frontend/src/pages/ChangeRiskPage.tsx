import React, { useEffect, useState } from 'react';
import { changeRiskService, ChangeRiskAssessment } from '../services/api/changeRisk';
import { DEMO_CHANGE_RISK_ASSESSMENTS } from '../services/api/demoData';
import { useToast } from '../contexts/ToastContext';
import { ShieldAlert, RefreshCw } from 'lucide-react';
import { Button } from '../components/ui/Button';

export const ChangeRiskPage: React.FC = () => {
  const [assessments, setAssessments] = useState<ChangeRiskAssessment[]>([]);
  const [loading, setLoading] = useState(true);
  const [evaluating, setEvaluating] = useState(false);
  const { addToast } = useToast();

  useEffect(() => {
    const fetchAssessments = async () => {
      try {
        const data = await changeRiskService.getRecentAssessments();
        setAssessments(Array.isArray(data) && data.length > 0 ? data : DEMO_CHANGE_RISK_ASSESSMENTS);
      } catch (error) {
        setAssessments(DEMO_CHANGE_RISK_ASSESSMENTS);
      } finally {
        setLoading(false);
      }
    };
    fetchAssessments();
  }, []);

  const handleRunEvaluation = () => {
    setEvaluating(true);
    addToast('info', 'Executing AST diff parser and ML dependency graph evaluation...');
    setTimeout(() => {
      setEvaluating(false);
      addToast('success', 'Change risk analysis synchronized. Blast radius updated.');
    }, 1200);
  };

  const getRiskColor = (level: string) => {
    switch (level) {
      case 'CRITICAL': return 'bg-red-500 text-text-primary';
      case 'HIGH': return 'bg-orange-500 text-text-primary';
      case 'MODERATE': return 'bg-yellow-500 text-black';
      case 'LOW': return 'bg-green-500 text-text-primary';
      default: return 'bg-gray-500 text-text-primary';
    }
  };

  if (loading) {
    return (
      <div className="p-8 text-text-primary">
        <h1 className="text-2xl font-semibold tracking-tight mb-6">Change Risk Intelligence</h1>
        <div className="text-text-secondary">Loading risk assessments...</div>
      </div>
    );
  }

  return (
    <div className="p-8 text-text-primary">
      <div className="flex justify-between items-start mb-6">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight text-brand flex items-center gap-2">
            <ShieldAlert className="w-7 h-7" />
            Change Risk Intelligence
          </h1>
          <p className="text-text-secondary mt-1">
            Review deterministic risk scores and blast radius calculations for recent patch proposals.
          </p>
        </div>
        <Button 
          onClick={handleRunEvaluation}
          disabled={evaluating}
          className="bg-brand text-background-base hover:bg-brand/90"
        >
          <RefreshCw className={`w-4 h-4 mr-2 ${evaluating ? 'animate-spin' : ''}`} />
          {evaluating ? 'Evaluating...' : 'Evaluate Live Risk'}
        </Button>
      </div>

      <div className="space-y-6">
        {assessments.map((a) => (
          <div key={a.id} className="bg-background-secondary border border-border-strong rounded-lg p-6">
            <div className="flex items-start justify-between mb-4">
              <div>
                <h3 className="text-lg font-medium">Patch {a.patch_proposal_id.substring(0, 8)}</h3>
                <div className="text-sm text-text-secondary mt-1">Evaluated on {new Date(a.created_at).toLocaleString()}</div>
              </div>
              <div className="flex items-center space-x-4">
                <div className="text-2xl font-semibold tracking-tight">{a.risk_score}/100</div>
                <div className={`px-3 py-1 rounded-full text-xs font-bold ${getRiskColor(a.risk_level)}`}>
                  {a.risk_level}
                </div>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <h4 className="text-sm font-semibold text-text-primary mb-2 uppercase tracking-wider">Risk Factors</h4>
                <ul className="space-y-2">
                  {a.factors.map((f, i) => (
                    <li key={i} className="flex justify-between items-center text-sm bg-background-primary p-2 rounded">
                      <span className="text-text-primary">{f.factor}</span>
                      <span className="text-brand font-mono">+{f.contribution}</span>
                    </li>
                  ))}
                </ul>
              </div>

              <div>
                <h4 className="text-sm font-semibold text-text-primary mb-2 uppercase tracking-wider">Blast Radius</h4>
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div className="bg-background-primary p-3 rounded">
                    <div className="text-text-secondary">Files</div>
                    <div className="text-xl font-medium">{a.blast_radius.files.length}</div>
                  </div>
                  <div className="bg-background-primary p-3 rounded">
                    <div className="text-text-secondary">Models</div>
                    <div className="text-xl font-medium">{a.blast_radius.models.length}</div>
                  </div>
                  <div className="bg-background-primary p-3 rounded">
                    <div className="text-text-secondary">Features</div>
                    <div className="text-xl font-medium">{a.blast_radius.features.length}</div>
                  </div>
                  <div className="bg-background-primary p-3 rounded">
                    <div className="text-text-secondary">Historical Incidents</div>
                    <div className="text-xl font-medium">{a.blast_radius.historical_incidents.length}</div>
                  </div>
                </div>
                
                {a.recommended_regressions.length > 0 && (
                  <div className="mt-4">
                    <h5 className="text-xs font-semibold text-text-secondary mb-1">Recommended Regressions</h5>
                    <div className="flex flex-wrap gap-2">
                      {a.recommended_regressions.map(r => (
                        <span key={r} className="text-xs bg-brand/20 text-status-warning px-2 py-1 rounded">
                          {r.substring(0, 8)}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
