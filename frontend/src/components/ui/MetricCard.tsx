import { Card, CardContent } from './Card';
import { cn } from '@/lib/utils';
import { LucideIcon } from 'lucide-react';

interface MetricCardProps {
  title: string;
  value: string | number;
  icon?: LucideIcon;
  trend?: {
    value: number;
    isPositive: boolean;
  };
  className?: string;
}

export function MetricCard({ title, value, icon: Icon, trend, className }: MetricCardProps) {
  return (
    <Card className={cn('p-1', className)}>
      <CardContent className="p-4 flex flex-col gap-2">
        <div className="flex justify-between items-center text-text-secondary">
          <span className="text-sm font-medium">{title}</span>
          {Icon && <Icon className="h-4 w-4" />}
        </div>
        <div className="flex items-baseline gap-2">
          <span className="text-2xl font-bold text-text-primary">{value}</span>
          {trend && (
            <span
              className={cn(
                'text-xs font-medium',
                trend.isPositive ? 'text-status-success' : 'text-status-danger'
              )}
            >
              {trend.isPositive ? '+' : '-'}{Math.abs(trend.value)}%
            </span>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
