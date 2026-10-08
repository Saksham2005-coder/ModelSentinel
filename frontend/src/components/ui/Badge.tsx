import React from 'react';
import { cn } from '@/lib/utils';

interface BadgeProps extends React.HTMLAttributes<HTMLSpanElement> {
  variant?: 'default' | 'success' | 'warning' | 'danger' | 'info';
  children: React.ReactNode;
}

export function Badge({ variant = 'default', className, children, ...props }: BadgeProps) {
  const variantStyles = {
    default: 'bg-surface/50 text-text-primary border-border/50 shadow-soft',
    success: 'bg-status-success/10 text-status-success border-status-success/30 shadow-[0_0_10px_rgba(16,185,129,0.2)]',
    warning: 'bg-status-warning/10 text-status-warning border-status-warning/30 shadow-[0_0_10px_rgba(245,158,11,0.2)]',
    danger: 'bg-status-danger/10 text-status-danger border-status-danger/30 shadow-[0_0_10px_rgba(239,68,68,0.2)]',
    info: 'bg-status-info/10 text-status-info border-status-info/30 shadow-[0_0_10px_rgba(59,130,246,0.2)]',
  };

  return (
    <span
      className={cn(
        'inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium border backdrop-blur-sm',
        variantStyles[variant],
        className
      )}
      {...props}
    >
      {children}
    </span>
  );
}
