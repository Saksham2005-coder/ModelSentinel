import { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { Table, TableHeader, TableBody, TableRow, TableHead, TableCell } from '@/components/ui/Table';
import { Button } from '@/components/ui/Button';
import { PageHeader, EmptyState } from '@/components/ui/Layout';
import { StatusBadge } from '@/components/ui/StatusBadge';
import { fetchApi } from '@/services/api/client';
import { ShieldAlert, Activity, Plus } from 'lucide-react';

interface Objective {
  id: string;
  name: string;
  objective_type: string;
  comparison_operator: string;
  target_value: number;
  evaluation_window: string;
  enabled: boolean;
}

export function SLOPage() {
  const [objectives, setObjectives] = useState<Objective[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchSLOs = async () => {
      try {
        const response = await fetchApi<Objective[]>('/slo/objectives');
        setObjectives(response || []);
      } catch (err) {
        console.error('Failed to fetch SLOs', err);
      } finally {
        setLoading(false);
      }
    };
    fetchSLOs();
  }, []);

  const handleEvaluate = async (id: string) => {
    try {
      await fetchApi(`/slo/objectives/${id}/evaluate`, { method: 'POST' });
      alert("Evaluation triggered successfully!");
    } catch (err) {
      console.error(err);
      alert("Failed to evaluate SLO.");
    }
  }

  return (
    <div className="space-y-6">
      <PageHeader
        title="Service Level Objectives"
        description="Manage and monitor your reliability objectives and error budgets."
      >
        <Button variant="primary" disabled title="SLO creation is configured via the CLI">
          <Plus className="mr-2 h-4 w-4" />
          Create SLO
        </Button>
      </PageHeader>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div className="space-y-1">
                <p className="text-sm font-medium text-text-muted">Total SLOs</p>
                <p className="text-2xl font-semibold tracking-tight text-text-primary">{objectives.length}</p>
              </div>
              <div className="p-3 bg-surface-hover rounded-lg">
                <ShieldAlert className="h-6 w-6 text-brand" />
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="text-lg font-medium text-text-primary flex items-center">
            <Activity className="mr-2 h-5 w-5 text-brand" />
            Reliability Objectives
          </CardTitle>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Name</TableHead>
                <TableHead>Type</TableHead>
                <TableHead>Target</TableHead>
                <TableHead>Window</TableHead>
                <TableHead>Status</TableHead>
                <TableHead className="text-right">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {loading ? (
                <TableRow>
                  <TableCell colSpan={6} className="text-center text-text-secondary py-8">
                    Loading objectives...
                  </TableCell>
                </TableRow>
              ) : objectives.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={6}>
                    <EmptyState
                      title="No SLOs defined"
                      description="Create an SLO to start monitoring."
                      icon={<ShieldAlert className="h-8 w-8" />}
                    />
                  </TableCell>
                </TableRow>
              ) : (
                objectives.map((obj) => (
                  <TableRow key={obj.id}>
                    <TableCell className="font-medium text-text-primary">{obj.name}</TableCell>
                    <TableCell className="text-text-secondary">{obj.objective_type}</TableCell>
                    <TableCell className="text-text-primary">
                      {obj.comparison_operator} {obj.target_value}
                    </TableCell>
                    <TableCell className="text-text-secondary">{obj.evaluation_window}</TableCell>
                    <TableCell>
                      <StatusBadge status={obj.enabled ? "ACTIVE" : "DISABLED"} />
                    </TableCell>
                    <TableCell className="text-right">
                      <Button variant="outline" size="sm" onClick={() => handleEvaluate(obj.id)}>
                        Evaluate
                      </Button>
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  );
}
