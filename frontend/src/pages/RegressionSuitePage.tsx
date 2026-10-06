/* eslint-disable @typescript-eslint/no-explicit-any */
/* eslint-disable @typescript-eslint/no-unused-vars */
import { useState, useEffect } from 'react';
import { Card, CardContent } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { Loader2, ShieldCheck, PlayCircle, Clock } from 'lucide-react';
import { Link } from 'react-router-dom';
import { Button } from '@/components/ui/Button';

export function RegressionSuitePage() {
  const [cases, setCases] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch('http://localhost:8000/api/v1/regression-tests')
      .then(res => res.json())
      .then(data => {
        setCases(data);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, []);

  return (
    <div className="p-8 space-y-8 animate-in fade-in duration-500">
      <div className="flex justify-between items-start">
        <div>
          <h1 className="text-4xl font-bold tracking-tight mb-2 flex items-center">
            <ShieldCheck className="w-8 h-8 mr-3 text-emerald-500" />
            Regression Tests
          </h1>
          <p className="text-muted-foreground text-lg">
            Automated test suite generated from learned incident memories.
          </p>
        </div>
        <Button className="bg-emerald-600 hover:bg-emerald-700 text-white">
          <PlayCircle className="w-4 h-4 mr-2" />
          Run Suite
        </Button>
      </div>

      {loading ? (
        <div className="flex justify-center p-12">
          <Loader2 className="w-8 h-8 animate-spin text-emerald-500" />
        </div>
      ) : cases.length === 0 ? (
        <Card className="border-dashed">
          <CardContent className="flex flex-col items-center justify-center py-20 text-center">
            <ShieldCheck className="w-12 h-12 text-muted-foreground/50 mb-4" />
            <h3 className="text-xl font-semibold mb-2">No regression tests yet</h3>
            <p className="text-muted-foreground max-w-sm">
              Turn a validated incident into a regression case to prevent future regressions.
            </p>
          </CardContent>
        </Card>
      ) : (
        <div className="bg-card border border-border rounded-lg overflow-hidden">
          <table className="w-full text-sm text-left">
            <thead className="bg-muted/50 text-muted-foreground border-b border-border">
              <tr>
                <th className="px-4 py-3 font-medium">Test</th>
                <th className="px-4 py-3 font-medium">Source Incident</th>
                <th className="px-4 py-3 font-medium">Severity</th>
                <th className="px-4 py-3 font-medium">Last Result</th>
                <th className="px-4 py-3 font-medium">Last Run</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {cases.map((c) => (
                <tr key={c.id} className="hover:bg-muted/20 transition-colors group">
                  <td className="px-4 py-3">
                    <Link to={`/regression-tests/${c.id}`} className="font-medium text-emerald-500 hover:underline">
                      {c.name}
                    </Link>
                  </td>
                  <td className="px-4 py-3 text-muted-foreground text-xs font-mono">{c.source_incident_id.substring(0,8)}</td>
                  <td className="px-4 py-3">
                    <Badge variant={c.severity === 'critical' ? 'danger' : 'warning'} className={c.severity === 'critical' ? 'border-red-500/50 text-red-500' : ''}>
                      {c.severity}
                    </Badge>
                  </td>
                  <td className="px-4 py-3">
                    {c.last_run ? (
                      <Badge variant={
                        c.last_run === 'PASS' ? 'success' :
                        c.last_run === 'FAIL' ? 'danger' : 'warning'
                      } className={
                        c.last_run === 'PASS' ? 'border-emerald-500/50 text-emerald-500 bg-emerald-500/10' :
                        c.last_run === 'FAIL' ? 'border-red-500/50 text-red-500 bg-red-500/10' :
                        'border-amber-500/50 text-amber-500 bg-amber-500/10'
                      }>
                        {c.last_run}
                      </Badge>
                    ) : (
                      <span className="text-muted-foreground">Not Run</span>
                    )}
                  </td>
                  <td className="px-4 py-3 text-muted-foreground flex items-center">
                    <Clock className="w-3 h-3 mr-1.5" />
                    {c.last_run_time ? new Date(c.last_run_time).toLocaleString() : '-'}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
