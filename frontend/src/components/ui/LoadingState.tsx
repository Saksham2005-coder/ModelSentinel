import { Loader2 } from 'lucide-react';

interface LoadingStateProps {
  text?: string;
  className?: string;
}

export function LoadingState({ text = 'Loading...', className = '' }: LoadingStateProps) {
  return (
    <div className={`flex flex-col items-center justify-center p-8 space-y-4 text-text-muted ${className}`}>
      <Loader2 className="w-8 h-8 animate-spin text-brand" />
      <span className="text-sm font-medium">{text}</span>
    </div>
  );
}

export function LoadingInline({ text, className = '' }: LoadingStateProps) {
  return (
    <div className={`flex items-center gap-2 text-text-muted ${className}`}>
      <Loader2 className="w-4 h-4 animate-spin text-brand" />
      {text && <span className="text-sm">{text}</span>}
    </div>
  );
}
