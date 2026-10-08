import { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { Table, TableHeader, TableBody, TableRow, TableHead, TableCell } from '@/components/ui/Table';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
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
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-white mb-2">Service Level Objectives</h1>
          <p className="text-zinc-400">Manage and monitor your reliability objectives and error budgets.</p>
        </div>
        <Button className="bg-amber-600 hover:bg-amber-700 text-white">
          <Plus className="mr-2 h-4 w-4" />
          Create SLO
        </Button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card className="bg-[#111111] border-zinc-800">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div className="space-y-1">
                <p className="text-sm font-medium text-zinc-400">Total SLOs</p>
                <p className="text-3xl font-bold text-white">{objectives.length}</p>
              </div>
              <div className="p-3 bg-zinc-800/50 rounded-lg">
                <ShieldAlert className="h-6 w-6 text-amber-500" />
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      <Card className="bg-[#111111] border-zinc-800">
        <CardHeader>
          <CardTitle className="text-lg font-medium text-white flex items-center">
            <Activity className="mr-2 h-5 w-5 text-amber-500" />
            Reliability Objectives
          </CardTitle>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow className="border-zinc-800">
                <TableHead className="text-zinc-400">Name</TableHead>
                <TableHead className="text-zinc-400">Type</TableHead>
                <TableHead className="text-zinc-400">Target</TableHead>
                <TableHead className="text-zinc-400">Window</TableHead>
                <TableHead className="text-zinc-400">Status</TableHead>
                <TableHead className="text-zinc-400 text-right">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {loading ? (
                <TableRow>
                  <TableCell colSpan={6} className="text-center text-zinc-500 py-8">
                    Loading objectives...
                  </TableCell>
                </TableRow>
              ) : objectives.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={6} className="text-center text-zinc-500 py-8">
                    No SLOs defined. Create one to get started.
                  </TableCell>
                </TableRow>
              ) : (
                objectives.map((obj) => (
                  <TableRow key={obj.id} className="border-zinc-800">
                    <TableCell className="font-medium text-zinc-200">{obj.name}</TableCell>
                    <TableCell className="text-zinc-400">{obj.objective_type}</TableCell>
                    <TableCell className="text-zinc-300">
                      {obj.comparison_operator} {obj.target_value}
                    </TableCell>
                    <TableCell className="text-zinc-400">{obj.evaluation_window}</TableCell>
                    <TableCell>
                      <Badge variant={obj.enabled ? "success" : "default"}>
                        {obj.enabled ? "Active" : "Inactive"}
                      </Badge>
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
