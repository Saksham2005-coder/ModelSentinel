import { useState } from 'react';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/Table';
import { Badge } from '@/components/ui/Badge';
import { Plus, Search, Filter, Box, Loader2 } from 'lucide-react';
import { modelsDemo } from '@/features/models/demoData';

export function ModelsPage() {
  const [loading, setLoading] = useState(false);

  // Demonstrate simple loading state toggle for UX requirements
  const handleRefresh = () => {
    setLoading(true);
    setTimeout(() => setLoading(false), 800);
  };

  return (
    <div className="flex flex-col gap-8">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-text-primary">Models</h1>
          <p className="text-text-secondary mt-1">Manage and monitor all your ML models.</p>
        </div>
        <div className="flex items-center gap-4">
          <Button variant="outline" onClick={handleRefresh}>
            {loading ? <Loader2 className="h-4 w-4 animate-spin mr-2" /> : null}
            Refresh
          </Button>
          <Button variant="primary" className="gap-2">
            <Plus className="h-4 w-4" />
            Add Model
          </Button>
        </div>
      </div>

      <div className="flex flex-col md:flex-row items-center gap-4">
        <div className="relative flex-1">
          <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-text-muted" />
          <Input 
            placeholder="Search models..." 
            className="pl-9 w-full md:max-w-sm"
          />
        </div>
        <Button variant="outline" className="gap-2">
          <Filter className="h-4 w-4" />
          Filters
        </Button>
      </div>

      <div className="rounded-xl border border-border bg-surface overflow-hidden">
        {loading ? (
          <div className="flex flex-col items-center justify-center p-12 text-text-secondary">
            <Loader2 className="h-8 w-8 animate-spin text-brand mb-4" />
            <p>Loading models...</p>
          </div>
        ) : modelsDemo.length === 0 ? (
          <div className="flex flex-col items-center justify-center p-12 text-text-secondary text-center">
            <div className="h-12 w-12 rounded-full bg-surface-hover flex items-center justify-center mb-4">
              <Box className="h-6 w-6 text-text-muted" />
            </div>
            <h3 className="text-lg font-medium text-text-primary">No models found</h3>
            <p className="max-w-sm mt-1">You haven't added any models yet. Add your first model to start monitoring.</p>
            <Button variant="primary" className="mt-4 gap-2">
              <Plus className="h-4 w-4" />
              Add Model
            </Button>
          </div>
        ) : (
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Model</TableHead>
                <TableHead>Type</TableHead>
                <TableHead>Health (F1/Acc)</TableHead>
                <TableHead>Latency</TableHead>
                <TableHead>Status</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {modelsDemo.map((model) => (
                <TableRow key={model.id}>
                  <TableCell className="font-medium text-text-primary">
                    <div className="flex items-center gap-3">
                      <div className="bg-surface-hover p-2 rounded-lg border border-border-strong">
                        <Box className="h-4 w-4 text-brand" />
                      </div>
                      {model.name}
                    </div>
                  </TableCell>
                  <TableCell className="text-text-secondary">{model.type}</TableCell>
                  <TableCell>
                    <div className="flex items-center gap-2">
                      <span className="font-medium text-text-primary">{model.health}%</span>
                      <span className={model.trend.isPositive ? 'text-status-success text-xs' : 'text-status-danger text-xs'}>
                        {model.trend.isPositive ? '+' : '-'}{model.trend.value}%
                      </span>
                    </div>
                  </TableCell>
                  <TableCell className="text-text-secondary">{model.latency}</TableCell>
                  <TableCell>
                    <Badge 
                      variant={
                        model.status === 'healthy' ? 'success' : 
                        model.status === 'warning' ? 'warning' : 'danger'
                      }
                    >
                      {model.status.toUpperCase()}
                    </Badge>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        )}
      </div>
    </div>
  );
}
