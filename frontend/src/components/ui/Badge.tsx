import React from 'react';
import { cn } from '@/lib/utils';

interface BadgeProps extends React.HTMLAttributes<HTMLSpanElement> {
  variant?: 'default' | 'success' | 'warning' | 'danger' | 'info';
  children: React.ReactNode;
}

export function Badge({ variant = 'default', className, children, ...props }: BadgeProps) {
  const variantStyles = {
    default: 'bg-surface-hover text-text-primary border-border',
    success: 'bg-status-success-soft text-status-success border-status-success-soft',
    warning: 'bg-status-warning-soft text-status-warning border-status-warning-soft',
    danger: 'bg-status-danger-soft text-status-danger border-status-danger-soft',
    info: 'bg-status-info-soft text-status-info border-status-info-soft',
  };

  return (
    <span
      className={cn(
        'inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium border',
        variantStyles[variant],
        className
      )}
      {...props}
    >
      {children}
    </span>
  );
}
