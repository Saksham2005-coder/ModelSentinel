import { Link } from 'react-router-dom';
import { AlertCircle } from 'lucide-react';

export function NotFoundPage() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-background-primary px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8 text-center">
        <div className="flex flex-col items-center">
          <AlertCircle className="h-16 w-16 text-brand mb-4" />
          <h2 className="text-3xl font-bold text-text-primary">Page Not Found</h2>
          <p className="mt-2 text-text-secondary">
            The page you're looking for doesn't exist or has been moved.
          </p>
        </div>
        <div className="flex justify-center space-x-4">
          <Link
            to="/dashboard"
            className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-black bg-brand hover:bg-brand-hover focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-black focus:ring-brand transition-colors"
          >
            Return to Dashboard
          </Link>
          <button
            onClick={() => window.history.back()}
            className="inline-flex items-center px-4 py-2 border border-border text-sm font-medium rounded-md shadow-sm text-text-primary bg-background-secondary hover:bg-surface-hover focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-black focus:ring-brand transition-colors"
          >
            Go Back
          </button>
        </div>
      </div>
    </div>
  );
}
