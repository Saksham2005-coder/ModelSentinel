import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { ArrowLeft, CheckCircle2, AlertCircle, Info } from 'lucide-react';
import { api } from '@/lib/api';
import { formatDistanceToNow } from 'date-fns';

export function PolicyDetailPage() {
  const { id } = useParams();
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchPolicy();
  }, [id]);

  const fetchPolicy = async () => {
    try {
      const res = await api.get(`/policies/${id}`);
      setData(res.data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="p-8">Loading policy details...</div>;
  }

  if (!data || !data.policy) {
    return <div className="p-8 text-destructive">Policy not found.</div>;
  }

  const { policy, recent_evaluations } = data;

  return (
    <div className="p-8 space-y-6">
      <div className="flex items-center gap-4 mb-4">
        <Button variant="ghost" size="icon" asChild>
          <Link to="/policies"><ArrowLeft className="h-5 w-5" /></Link>
        </Button>
        <div>
          <h1 className="text-3xl font-bold tracking-tight">{policy.name}</h1>
          <div className="flex gap-2 mt-2">
            <Badge variant={policy.enabled ? 'default' : 'secondary'}>
              {policy.enabled ? 'Enabled' : 'Disabled'}
            </Badge>
            <Badge variant="outline">Scope: {policy.scope}</Badge>
            {policy.environment && <Badge variant="outline">Env: {policy.environment}</Badge>}
            <Badge variant="outline">Priority: {policy.priority}</Badge>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Policy Rules</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {policy.rules && policy.rules.map((rule: any, i: number) => (
              <div key={i} className="flex items-start gap-3 p-3 bg-muted/50 rounded-lg">
                <CheckCircle2 className="h-5 w-5 text-emerald-500 mt-0.5" />
                <div>
                  <div className="font-medium">{rule.type}</div>
                  <div className="text-sm text-muted-foreground flex gap-2 mt-1">
                    <span className="font-mono bg-background px-1 rounded border">OP: {rule.operator}</span>
                    <span className="font-mono bg-background px-1 rounded border">VAL: {String(rule.value)}</span>
                  </div>
                </div>
              </div>
            ))}
            {(!policy.rules || policy.rules.length === 0) && (
              <div className="text-muted-foreground">No rules defined.</div>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Recent Evaluations</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {recent_evaluations && recent_evaluations.length > 0 ? (
              recent_evaluations.map((evalItem: any) => (
                <div key={evalItem.id} className="p-3 border rounded-lg flex items-center justify-between">
                  <div>
                    <div className="font-medium">{evalItem.target_type} : {evalItem.target_id.slice(0, 8)}</div>
                    <div className="text-xs text-muted-foreground mt-1">
                      {formatDistanceToNow(new Date(evalItem.evaluated_at), { addSuffix: true })}
                    </div>
                  </div>
                  <Badge variant={
                    evalItem.result === 'ALLOW' ? 'default' : 
                    evalItem.result === 'BLOCK' ? 'destructive' : 'secondary'
                  }>
                    {evalItem.result}
                  </Badge>
                </div>
              ))
            ) : (
              <div className="text-muted-foreground">No recent evaluations.</div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
