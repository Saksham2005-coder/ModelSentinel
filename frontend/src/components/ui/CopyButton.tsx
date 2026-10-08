import { useState } from 'react';
import { Check, Copy } from 'lucide-react';
import { Button } from './Button';

interface CopyButtonProps {
  value: string;
  className?: string;
  label?: string;
}

export function CopyButton({ value, className, label = 'Copy' }: CopyButtonProps) {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(value);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error('Failed to copy text: ', err);
    }
  };

  return (
    <Button
      variant="ghost"
      size="sm"
      className={`h-8 w-8 p-0 text-text-muted hover:text-text-primary ${className || ''}`}
      onClick={handleCopy}
      aria-label={copied ? 'Copied' : label}
      title={label}
    >
      {copied ? <Check className="h-4 w-4 text-status-success" /> : <Copy className="h-4 w-4" />}
    </Button>
  );
}
