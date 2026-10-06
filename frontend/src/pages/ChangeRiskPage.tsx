import React, { useEffect, useState } from 'react';
import { changeRiskService, ChangeRiskAssessment } from '../services/api/changeRisk';

export const ChangeRiskPage: React.FC = () => {
  const [assessments, setAssessments] = useState<ChangeRiskAssessment[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchAssessments = async () => {
      try {
        const data = await changeRiskService.getRecentAssessments();
        setAssessments(data);
      } catch (error) {
        console.error('Failed to fetch risk assessments', error);
      } finally {
        setLoading(false);
      }
    };
    fetchAssessments();
  }, []);

  const getRiskColor = (level: string) => {
    switch (level) {
      case 'CRITICAL': return 'bg-red-500 text-white';
      case 'HIGH': return 'bg-orange-500 text-white';
      case 'MODERATE': return 'bg-yellow-500 text-black';
      case 'LOW': return 'bg-green-500 text-white';
      default: return 'bg-gray-500 text-white';
    }
  };

  if (loading) {
    return (
      <div className="p-8 text-white">
        <h1 className="text-2xl font-bold mb-6">Change Risk Intelligence</h1>
        <div className="text-gray-400">Loading risk assessments...</div>
      </div>
    );
  }

  if (assessments.length === 0) {
    return (
      <div className="p-8 text-white">
        <h1 className="text-2xl font-bold mb-6">Change Risk Intelligence</h1>
        <div className="bg-gray-800 p-8 rounded-lg text-center text-gray-400">
          No change risk assessments found.
        </div>
      </div>
    );
  }

  return (
    <div className="p-8 text-white">
      <h1 className="text-2xl font-bold mb-6 text-amber-500">Change Risk Intelligence</h1>
      <p className="text-gray-400 mb-8">
        Review deterministic risk scores and blast radius calculations for recent patch proposals.
      </p>

      <div className="space-y-6">
        {assessments.map((a) => (
          <div key={a.id} className="bg-gray-800 border border-gray-700 rounded-lg p-6">
            <div className="flex items-start justify-between mb-4">
              <div>
                <h3 className="text-lg font-medium">Patch {a.patch_proposal_id.substring(0, 8)}</h3>
                <div className="text-sm text-gray-400 mt-1">Evaluated on {new Date(a.created_at).toLocaleString()}</div>
              </div>
              <div className="flex items-center space-x-4">
                <div className="text-2xl font-bold">{a.risk_score}/100</div>
                <div className={`px-3 py-1 rounded-full text-xs font-bold ${getRiskColor(a.risk_level)}`}>
                  {a.risk_level}
                </div>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <h4 className="text-sm font-semibold text-gray-300 mb-2 uppercase tracking-wider">Risk Factors</h4>
                <ul className="space-y-2">
                  {a.factors.map((f, i) => (
                    <li key={i} className="flex justify-between items-center text-sm bg-gray-900 p-2 rounded">
                      <span className="text-gray-300">{f.factor}</span>
                      <span className="text-amber-500 font-mono">+{f.contribution}</span>
                    </li>
                  ))}
                </ul>
              </div>

              <div>
                <h4 className="text-sm font-semibold text-gray-300 mb-2 uppercase tracking-wider">Blast Radius</h4>
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div className="bg-gray-900 p-3 rounded">
                    <div className="text-gray-400">Files</div>
                    <div className="text-xl font-medium">{a.blast_radius.files.length}</div>
                  </div>
                  <div className="bg-gray-900 p-3 rounded">
                    <div className="text-gray-400">Models</div>
                    <div className="text-xl font-medium">{a.blast_radius.models.length}</div>
                  </div>
                  <div className="bg-gray-900 p-3 rounded">
                    <div className="text-gray-400">Features</div>
                    <div className="text-xl font-medium">{a.blast_radius.features.length}</div>
                  </div>
                  <div className="bg-gray-900 p-3 rounded">
                    <div className="text-gray-400">Historical Incidents</div>
                    <div className="text-xl font-medium">{a.blast_radius.historical_incidents.length}</div>
                  </div>
                </div>
                
                {a.recommended_regressions.length > 0 && (
                  <div className="mt-4">
                    <h5 className="text-xs font-semibold text-gray-400 mb-1">Recommended Regressions</h5>
                    <div className="flex flex-wrap gap-2">
                      {a.recommended_regressions.map(r => (
                        <span key={r} className="text-xs bg-amber-500/20 text-amber-300 px-2 py-1 rounded">
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
