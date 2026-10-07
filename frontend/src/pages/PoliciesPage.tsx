import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import { ShieldCheck, ShieldAlert, Plus, Activity } from 'lucide-react';
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

export function PoliciesPage() {
  const [policies, setPolicies] = useState<ReliabilityPolicy[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchPolicies();
  }, []);

  const fetchPolicies = async () => {
    try {
      const data = await fetchApi<ReliabilityPolicy[]>('/policies');
      setPolicies(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="p-8">Loading policies...</div>;
  }

  return (
    <div className="p-8 space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Reliability Policies</h1>
          <p className="text-muted-foreground mt-2">
            Manage engineering guardrails and deterministic enforcement rules.
          </p>
        </div>
        <Button>
          <Plus className="mr-2 h-4 w-4" />
          Create Policy
        </Button>
      </div>

      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Active Policies</CardTitle>
            <ShieldCheck className="h-4 w-4 text-emerald-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{policies.filter(p => p.enabled).length}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Blocked Evaluations</CardTitle>
            <ShieldAlert className="h-4 w-4 text-destructive" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">--</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Review Required</CardTitle>
            <Activity className="h-4 w-4 text-amber-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">--</div>
          </CardContent>
        </Card>
      </div>

      <div className="grid gap-6">
        {policies.length === 0 ? (
          <Card>
            <CardContent className="flex flex-col items-center justify-center h-48 text-muted-foreground">
              <p>No policies defined.</p>
            </CardContent>
          </Card>
        ) : (
          policies.map(policy => (
            <Card key={policy.id} className="hover:border-primary/50 transition-colors">
              <CardHeader className="flex flex-row items-center justify-between">
                <div>
                  <CardTitle>
                    <Link to={`/policies/${policy.id}`} className="hover:underline">
                      {policy.name}
                    </Link>
                  </CardTitle>
                  <div className="flex gap-2 mt-2">
                    <Badge variant={policy.enabled ? 'default' : 'default'}>
                      {policy.enabled ? 'Enabled' : 'Disabled'}
                    </Badge>
                    <Badge variant="default">{policy.scope}</Badge>
                    {policy.environment && <Badge variant="default">{policy.environment}</Badge>}
                  </div>
                </div>
                <Button variant="outline" asChild>
                  <Link to={`/policies/${policy.id}`}>View Details</Link>
                </Button>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-muted-foreground">{policy.description}</p>
                <div className="mt-4 flex gap-4 text-sm text-muted-foreground">
                  <span>Priority: {policy.priority}</span>
                  <span>Rules: {policy.rules?.length || 0}</span>
                </div>
              </CardContent>
            </Card>
          ))
        )}
      </div>
    </div>
  );
}
