import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Loader2, ArrowLeft, PlayCircle, CheckCircle2, XCircle } from 'lucide-react';

export function RegressionTestPage() {
  const { id } = useParams();
  const [test, setTest] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [running, setRunning] = useState(false);

  const loadTest = () => {
    fetch(`http://localhost:8000/api/v1/regression-tests/${id}`)
      .then(res => res.json())
      .then(data => {
        setTest(data);
        setLoading(false);
      });
  };

  useEffect(() => {
    loadTest();
  }, [id]);

  const runTest = () => {
    setRunning(true);
    fetch(`http://localhost:8000/api/v1/regression-tests/${id}/run`, { method: 'POST' })
      .then(() => {
        // Poll for completion (simulation)
        setTimeout(() => {
          loadTest();
          setRunning(false);
        }, 2000);
      });
  };

  if (loading) return <div className="p-12 flex justify-center"><Loader2 className="w-8 h-8 animate-spin" /></div>;
  if (!test) return <div className="p-12 text-center">Test not found</div>;

  return (
    <div className="p-8 space-y-8 animate-in fade-in duration-500">
      <div>
        <Button variant="ghost" size="sm" asChild className="mb-4 -ml-3 text-muted-foreground">
          <Link to="/regression-tests"><ArrowLeft className="w-4 h-4 mr-2" />Back to Suite</Link>
        </Button>
        <div className="flex justify-between items-start">
          <div>
            <h1 className="text-3xl font-bold tracking-tight mb-2">{test.name}</h1>
            <div className="flex space-x-3 text-sm text-muted-foreground">
              <span>Source Incident: <Link to={`/incidents/${test.source_incident_id}`} className="text-emerald-500 hover:underline">{test.source_incident_id.substring(0,8)}</Link></span>
              <span>•</span>
              <span>Segments: {test.affected_segments?.join(', ') || 'Global'}</span>
            </div>
          </div>
          <Button onClick={runTest} disabled={running} className="bg-emerald-600 hover:bg-emerald-700 text-white">
            {running ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : <PlayCircle className="w-4 h-4 mr-2" />}
            {running ? 'Running...' : 'Run Regression Test'}
          </Button>
        </div>
      </div>

      <div className="grid md:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Failure Signature</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm">{test.failure_signature}</p>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Expected Behavior</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm">{test.expected_behavior}</p>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Run History</CardTitle>
        </CardHeader>
        <CardContent>
          {test.runs?.length === 0 ? (
            <div className="text-center py-8 text-muted-foreground text-sm">
              No runs recorded yet.
            </div>
          ) : (
            <div className="space-y-4">
              {test.runs?.map((run: any) => (
                <div key={run.id} className="border border-border rounded-md p-4 flex flex-col space-y-3">
                  <div className="flex justify-between items-center">
                    <div className="flex items-center space-x-3">
                      {run.status === 'PASS' ? (
                        <CheckCircle2 className="w-5 h-5 text-emerald-500" />
                      ) : run.status === 'FAIL' ? (
                        <XCircle className="w-5 h-5 text-red-500" />
                      ) : (
                        <Loader2 className="w-5 h-5 text-amber-500 animate-spin" />
                      )}
                      <span className="font-medium text-sm">{new Date(run.started_at).toLocaleString()}</span>
                    </div>
                    <Badge variant="outline" className={
                      run.status === 'PASS' ? 'border-emerald-500/50 text-emerald-500' :
                      run.status === 'FAIL' ? 'border-red-500/50 text-red-500' : 'border-amber-500/50 text-amber-500'
                    }>
                      {run.status}
                    </Badge>
                  </div>
                  
                  {run.results?.length > 0 && (
                    <div className="pl-8 pt-2 grid grid-cols-2 gap-4 text-sm">
                      {run.results.map((res: any, idx: number) => (
                        <div key={idx} className="flex flex-col">
                          <span className="text-muted-foreground">{res.segment || 'Global'} - {res.metric}</span>
                          <span className={res.status === 'PASS' ? 'text-emerald-500' : 'text-red-500'}>
                            Actual: {res.actual?.toFixed(4)} (Expected {'>='} {res.expected?.toFixed(4)})
                          </span>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
