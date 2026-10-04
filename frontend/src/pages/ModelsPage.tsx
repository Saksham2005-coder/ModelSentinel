import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/Table';
import { Badge } from '@/components/ui/Badge';
import { Plus, Search, Filter, Box, Loader2, AlertCircle } from 'lucide-react';
import { ModelsApi, Model } from '@/services/api/models';
import { AddModelModal } from '@/features/models/components/AddModelModal';

export function ModelsPage() {
  const [models, setModels] = useState<Model[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [search, setSearch] = useState('');
  const [isAddModalOpen, setIsAddModalOpen] = useState(false);

  const fetchModels = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await ModelsApi.getModels({ search });
      setModels(data.items);
    } catch (err: any) {
      setError(err.message || 'Failed to fetch models');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchModels();
  }, [search]);

  const handleRefresh = () => {
    fetchModels();
  };

  const handleSearch = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSearch(e.target.value);
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
          <Button variant="primary" className="gap-2" onClick={() => setIsAddModalOpen(true)}>
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
          <div className="flex flex-col items-center justify-center p-12 text-text-secondary text-center">
            <div className="h-12 w-12 rounded-full bg-surface-hover flex items-center justify-center mb-4">
              <Box className="h-6 w-6 text-text-muted" />
            </div>
            <h3 className="text-lg font-medium text-text-primary">No models found</h3>
            <p className="max-w-sm mt-1">You haven't added any models yet. Add your first model to start monitoring.</p>
            <Button variant="primary" className="mt-4 gap-2" onClick={() => setIsAddModalOpen(true)}>
              <Plus className="h-4 w-4" />
              Add Model
            </Button>
          </div>
        ) : (
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Model Name</TableHead>
                <TableHead>Framework</TableHead>
                <TableHead>Task Type</TableHead>
                <TableHead>Environment</TableHead>
                <TableHead>Status</TableHead>
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
                    <Badge 
                      variant={
                        model.status === 'active' ? 'success' : 
                        model.status === 'warning' || model.status === 'degraded' ? 'warning' : 'default'
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

      <AddModelModal 
        open={isAddModalOpen} 
        onOpenChange={setIsAddModalOpen} 
        onSuccess={fetchModels} 
      />
    </div>
  );
}
