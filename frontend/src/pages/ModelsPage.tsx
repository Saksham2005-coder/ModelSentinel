import { useState, useEffect, useCallback } from 'react';
import { Link } from 'react-router-dom';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/Table';
import { Badge } from '@/components/ui/Badge';
import { PageHeader, EmptyState } from '@/components/ui/Layout';
import { StatusBadge } from '@/components/ui/StatusBadge';
import { Plus, Search, Filter, Box, Loader2, AlertCircle } from 'lucide-react';
import { ModelsApi, Model } from '@/services/api/models';
import { AddModelModal } from '@/features/models/components/AddModelModal';

export function ModelsPage() {
  const [models, setModels] = useState<Model[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [search, setSearch] = useState('');
  const [isAddModalOpen, setIsAddModalOpen] = useState(false);

  const fetchModels = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await ModelsApi.getModels({ search });
      setModels(data.items);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to fetch models');
    } finally {
      setLoading(false);
    }
  }, [search]);

  useEffect(() => {
    fetchModels();
  }, [fetchModels]);

  const handleRefresh = () => {
    fetchModels();
  };

  const handleSearch = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSearch(e.target.value);
  };

  return (
    <div className="flex flex-col gap-8">
      <PageHeader 
        title="Models" 
        description="Manage and monitor all your ML models."
      >
        <Button variant="outline" onClick={handleRefresh}>
          {loading ? <Loader2 className="h-4 w-4 animate-spin mr-2" /> : null}
          Refresh
        </Button>
        <Button variant="primary" className="gap-2" onClick={() => setIsAddModalOpen(true)}>
          <Plus className="h-4 w-4" />
          Add Model
        </Button>
      </PageHeader>

      <div className="flex flex-col md:flex-row items-center gap-4">
        <div className="relative flex-1">
          <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-text-muted" />
          <Input 
            placeholder="Search models..." 
            className="pl-9 w-full md:max-w-sm"
            value={search}
            onChange={handleSearch}
          />
        </div>
        <Button variant="outline" className="gap-2">
          <Filter className="h-4 w-4" />
          Filters
        </Button>
      </div>

      {error ? (
        <div className="p-4 bg-status-danger/10 border border-status-danger/20 rounded-xl flex items-center gap-3 text-status-danger">
          <AlertCircle className="h-5 w-5" />
          <p>{error}</p>
        </div>
      ) : null}

      <div className="rounded-xl border border-border bg-surface overflow-hidden">
        {loading && models.length === 0 ? (
          <div className="flex flex-col items-center justify-center p-12 text-text-secondary">
            <Loader2 className="h-8 w-8 animate-spin text-brand mb-4" />
            <p>Loading models...</p>
          </div>
        ) : models.length === 0 ? (
          <EmptyState
            title="No models found"
            description="You haven't added any models yet. Add your first model to start monitoring."
            icon={<Box className="h-8 w-8" />}
            action={
              <Button variant="primary" className="gap-2" onClick={() => setIsAddModalOpen(true)}>
                <Plus className="h-4 w-4" />
                Add Model
              </Button>
            }
          />
        ) : (
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Model Name</TableHead>
                <TableHead>Framework</TableHead>
                <TableHead>Task Type</TableHead>
                <TableHead>Environment</TableHead>
                <TableHead>Status</TableHead>
                <TableHead className="text-right">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {models.map((model) => (
                <TableRow key={model.id}>
                  <TableCell className="font-medium text-text-primary">
                    <div className="flex items-center gap-3">
                      <div className="bg-surface-hover p-2 rounded-lg border border-border-strong">
                        <Box className="h-4 w-4 text-brand" />
                      </div>
                      <div>
                        <div>{model.name}</div>
                        <div className="text-xs text-text-muted font-normal">{model.slug}</div>
                      </div>
                    </div>
                  </TableCell>
                  <TableCell className="text-text-secondary capitalize">{model.framework}</TableCell>
                  <TableCell className="text-text-secondary capitalize">{model.task_type.replace('_', ' ')}</TableCell>
                  <TableCell>
                    <Badge variant="default" className="capitalize">{model.environment}</Badge>
                  </TableCell>
                  <TableCell>
                    <StatusBadge status={model.status} />
                  </TableCell>
                  <TableCell className="text-right">
                    <div className="flex justify-end gap-2">
                      <Button variant="outline" size="sm" asChild>
                        <Link to={`/models/${model.id}/intelligence`}>Intelligence</Link>
                      </Button>
                      <Button variant="outline" size="sm" asChild>
                        <Link to={`/models/${model.id}/monitoring`}>Monitoring</Link>
                      </Button>
                      <Button variant="outline" size="sm" asChild>
                        <Link to={`/models/${model.id}/reliability`}>Timeline</Link>
                      </Button>
                      <Button variant="outline" size="sm" asChild>
                        <Link to={`/analytics/models/${model.id}`}>Analytics</Link>
                      </Button>
                    </div>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        )}
      </div>

      <AddModelModal 
        open={isAddModalOpen} 
        onOpenChange={setIsAddModalOpen} 
        onSuccess={fetchModels} 
      />
    </div>
  );
}
