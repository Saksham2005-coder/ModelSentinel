import { useState } from 'react';
import { Dialog, DialogHeader, DialogTitle, DialogDescription, DialogFooter, DialogClose } from '@/components/ui/Dialog';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { ModelsApi, ModelCreate } from '@/services/api/models';
import { Loader2 } from 'lucide-react';

interface AddModelModalProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onSuccess: () => void;
}

export function AddModelModal({ open, onOpenChange, onSuccess }: AddModelModalProps) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [formData, setFormData] = useState<ModelCreate>({
    name: '',
    slug: '',
    description: '',
    framework: 'scikit-learn',
    task_type: 'classification',
    primary_metric: 'f1_score',
    environment: 'development',
    status: 'draft'
  });

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value,
      // Auto-generate slug from name if user types in name
      ...(name === 'name' && !prev.slug.trim() ? { slug: value.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/(^-|-$)+/g, '') } : {})
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      setLoading(true);
      setError(null);
      await ModelsApi.createModel(formData);
      onSuccess();
      onOpenChange(false);
      // Reset form
      setFormData({
        name: '',
        slug: '',
        description: '',
        framework: 'scikit-learn',
        task_type: 'classification',
        primary_metric: 'f1_score',
        environment: 'development',
        status: 'draft'
      });
    } catch (err: any) {
      setError(err.message || 'Failed to create model');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogHeader>
        <DialogTitle>Add New Model</DialogTitle>
        <DialogDescription>
          Register a new machine learning model to track its performance and lifecycle.
        </DialogDescription>
        <DialogClose onClick={() => onOpenChange(false)} />
      </DialogHeader>

      <form onSubmit={handleSubmit} className="space-y-4 mt-4">
        {error && (
          <div className="p-3 text-sm text-status-danger bg-status-danger/10 border border-status-danger/20 rounded-lg">
            {error}
          </div>
        )}
        
        <div className="grid grid-cols-2 gap-4">
          <div className="space-y-1.5">
            <label htmlFor="name" className="text-sm font-medium text-text-primary">Model Name *</label>
            <Input 
              id="name" 
              name="name" 
              required 
              value={formData.name} 
              onChange={handleChange} 
              placeholder="e.g. Customer Churn V2" 
            />
          </div>
          <div className="space-y-1.5">
            <label htmlFor="slug" className="text-sm font-medium text-text-primary">Slug ID *</label>
            <Input 
              id="slug" 
              name="slug" 
              required 
              value={formData.slug} 
              onChange={handleChange} 
              placeholder="customer-churn-v2" 
            />
          </div>
        </div>

        <div className="space-y-1.5">
          <label htmlFor="description" className="text-sm font-medium text-text-primary">Description</label>
          <textarea
            id="description"
            name="description"
            rows={2}
            className="flex w-full rounded-md border border-input bg-surface-hover px-3 py-2 text-sm ring-offset-background placeholder:text-text-muted focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 text-text-primary"
            value={formData.description}
            onChange={handleChange}
            placeholder="What does this model do?"
          />
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div className="space-y-1.5">
            <label htmlFor="framework" className="text-sm font-medium text-text-primary">Framework *</label>
            <select
              id="framework"
              name="framework"
              required
              className="flex h-10 w-full rounded-md border border-input bg-surface-hover px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 text-text-primary"
              value={formData.framework}
              onChange={handleChange}
            >
              <option value="scikit-learn">Scikit-Learn</option>
              <option value="pytorch">PyTorch</option>
              <option value="tensorflow">TensorFlow</option>
              <option value="xgboost">XGBoost</option>
              <option value="lightgbm">LightGBM</option>
              <option value="custom">Custom</option>
            </select>
          </div>
          <div className="space-y-1.5">
            <label htmlFor="task_type" className="text-sm font-medium text-text-primary">Task Type *</label>
            <select
              id="task_type"
              name="task_type"
              required
              className="flex h-10 w-full rounded-md border border-input bg-surface-hover px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 text-text-primary"
              value={formData.task_type}
              onChange={handleChange}
            >
              <option value="classification">Classification</option>
              <option value="regression">Regression</option>
              <option value="clustering">Clustering</option>
              <option value="anomaly_detection">Anomaly Detection</option>
              <option value="forecasting">Forecasting</option>
              <option value="nlp">NLP / Text</option>
              <option value="cv">Computer Vision</option>
            </select>
          </div>
        </div>
        
        <div className="grid grid-cols-2 gap-4">
          <div className="space-y-1.5">
            <label htmlFor="primary_metric" className="text-sm font-medium text-text-primary">Primary Metric *</label>
            <Input 
              id="primary_metric" 
              name="primary_metric" 
              required 
              value={formData.primary_metric} 
              onChange={handleChange} 
              placeholder="e.g. f1_score, mse" 
            />
          </div>
          <div className="space-y-1.5">
            <label htmlFor="environment" className="text-sm font-medium text-text-primary">Environment *</label>
            <select
              id="environment"
              name="environment"
              required
              className="flex h-10 w-full rounded-md border border-input bg-surface-hover px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 text-text-primary"
              value={formData.environment}
              onChange={handleChange}
            >
              <option value="development">Development</option>
              <option value="staging">Staging</option>
              <option value="production">Production</option>
            </select>
          </div>
        </div>

        <DialogFooter>
          <Button type="button" variant="outline" onClick={() => onOpenChange(false)}>
            Cancel
          </Button>
          <Button type="submit" variant="primary" disabled={loading}>
            {loading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
            Create Model
          </Button>
        </DialogFooter>
      </form>
    </Dialog>
  );
}
