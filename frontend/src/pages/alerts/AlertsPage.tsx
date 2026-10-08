import { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { Table, TableHeader, TableBody, TableRow, TableHead, TableCell } from '@/components/ui/Table';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import { fetchApi } from '@/services/api/client';
import { AlertTriangle, Bell } from 'lucide-react';

interface Alert {
  id: string;
  summary: string;
  severity: string;
  status: string;
  triggered_at: string;
}

export function AlertsPage() {
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchAlerts = async () => {
      try {
        const response = await fetchApi<Alert[]>('/alerts');
        setAlerts(response || []);
      } catch (err) {
        console.error('Failed to fetch alerts', err);
      } finally {
        setLoading(false);
      }
    };
    fetchAlerts();
  }, []);

  const handleAcknowledge = async (id: string) => {
    try {
      await fetchApi(`/alerts/${id}/acknowledge`, { method: 'POST' });
      // Refresh list
      const response = await fetchApi<Alert[]>('/alerts');
      setAlerts(response || []);
    } catch (err) {
      console.error(err);
      alert("Failed to acknowledge alert.");
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight tracking-tight text-text-primary mb-2">Active Alerts</h1>
          <p className="text-zinc-400">Monitor and respond to reliability alerts and SLO breaches.</p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card className="bg-[#111111] border-zinc-800">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div className="space-y-1">
                <p className="text-sm font-medium text-zinc-400">Total Alerts</p>
                <p className="text-2xl font-semibold tracking-tight text-text-primary">{alerts.length}</p>
              </div>
              <div className="p-3 bg-amber-900/20 rounded-lg">
                <Bell className="h-6 w-6 text-brand" />
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      <Card className="bg-[#111111] border-zinc-800">
        <CardHeader>
          <CardTitle className="text-lg font-medium text-text-primary flex items-center">
            <AlertTriangle className="mr-2 h-5 w-5 text-brand" />
            Alert History
          </CardTitle>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow className="border-zinc-800">
                <TableHead className="text-zinc-400">Summary</TableHead>
                <TableHead className="text-zinc-400">Severity</TableHead>
                <TableHead className="text-zinc-400">Status</TableHead>
                <TableHead className="text-zinc-400">Triggered At</TableHead>
                <TableHead className="text-zinc-400 text-right">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {loading ? (
                <TableRow>
                  <TableCell colSpan={5} className="text-center text-zinc-500 py-8">
                    Loading alerts...
                  </TableCell>
                </TableRow>
              ) : alerts.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={5} className="text-center text-zinc-500 py-8">
                    No active alerts. All systems normal.
                  </TableCell>
                </TableRow>
              ) : (
                alerts.map((alert) => (
                  <TableRow key={alert.id} className="border-zinc-800">
                    <TableCell className="font-medium text-zinc-200">{alert.summary}</TableCell>
                    <TableCell>
                      <Badge variant={alert.severity === 'critical' ? 'danger' : alert.severity === 'high' ? 'warning' : 'default'}>
                        {alert.severity}
                      </Badge>
                    </TableCell>
                    <TableCell>
                      <Badge variant={alert.status === 'OPEN' ? 'danger' : 'success'}>
                        {alert.status}
                      </Badge>
                    </TableCell>
                    <TableCell className="text-zinc-400">
                      {new Date(alert.triggered_at).toLocaleString()}
                    </TableCell>
                    <TableCell className="text-right">
                      {alert.status === 'OPEN' && (
                        <Button variant="outline" size="sm" onClick={() => handleAcknowledge(alert.id)}>
                          Acknowledge
                        </Button>
                      )}
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
