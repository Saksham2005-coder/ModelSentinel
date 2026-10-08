import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import { ArrowLeft, CheckCircle2 } from 'lucide-react';
import { fetchApi } from '@/services/api/client';

export interface PolicyRule {
  type: string;
  operator: string;
  required?: string | number | boolean;
  actual?: string | number | boolean;
  value?: string | number | boolean;
}

export interface ReliabilityPolicy {
  id: string;
  name: string;
  description: string;
  scope: string;
  environment?: string;
  priority: number;
  enabled: boolean;
  rules: PolicyRule[];
}

export interface PolicyEvaluation {
  id: string;
  target_type: string;
  target_id: string;
  evaluated_at: string;
  result: string;
}

export interface PolicyDetailData {
  policy: ReliabilityPolicy;
  recent_evaluations: PolicyEvaluation[];
}

export function PolicyDetailPage() {
  const { id } = useParams();
  const [data, setData] = useState<PolicyDetailData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchPolicy = async () => {
      try {
        const res = await fetchApi<PolicyDetailData>(`/policies/${id}`);
        setData(res);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchPolicy();
  }, [id]);

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
          <h1 className="text-2xl font-semibold tracking-tight tracking-tight">{policy.name}</h1>
          <div className="flex gap-2 mt-2">
            <Badge variant={policy.enabled ? 'default' : 'default'}>
              {policy.enabled ? 'Enabled' : 'Disabled'}
            </Badge>
            <Badge variant="default">Scope: {policy.scope}</Badge>
            {policy.environment && <Badge variant="default">Env: {policy.environment}</Badge>}
            <Badge variant="default">Priority: {policy.priority}</Badge>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Policy Rules</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {policy.rules && policy.rules.map((rule: PolicyRule, i: number) => (
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
              recent_evaluations.map((evalItem: PolicyEvaluation) => (
                <div key={evalItem.id} className="p-3 border rounded-lg flex items-center justify-between">
                  <div>
                    <div className="font-medium">{evalItem.target_type} : {evalItem.target_id.slice(0, 8)}</div>
                    <div className="text-xs text-muted-foreground mt-1">
                      {new Date(evalItem.evaluated_at).toLocaleString()}
                    </div>
                  </div>
                  <Badge variant={
                    evalItem.result === 'ALLOW' ? 'success' : 
                    evalItem.result === 'BLOCK' ? 'danger' : 'warning'
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
