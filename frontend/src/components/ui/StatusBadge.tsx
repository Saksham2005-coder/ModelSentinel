
import { Badge } from './Badge';

export type StatusType = 
  | 'HEALTHY' | 'WARNING' | 'CRITICAL' | 'AT_RISK' | 'BREACHED' | 'NO_DATA'
  | 'PENDING' | 'RUNNING' | 'WAITING' | 'COMPLETED' | 'FAILED' | 'CANCELLED'
  | 'APPROVED' | 'REJECTED' | 'VALIDATED' | 'STALE' | 'INFO';

interface StatusBadgeProps {
  status: StatusType | string;
  className?: string;
}

export function StatusBadge({ status, className = '' }: StatusBadgeProps) {
  const normalizedStatus = status.toUpperCase().replace(' ', '_');
  
  let variant: 'success' | 'warning' | 'danger' | 'info' | 'default' = 'default';
  
  switch (normalizedStatus) {
    case 'HEALTHY':
    case 'COMPLETED':
    case 'APPROVED':
    case 'VALIDATED':
      variant = 'success';
      break;
    case 'WARNING':
    case 'AT_RISK':
    case 'PENDING':
    case 'WAITING':
    case 'STALE':
    case 'HIGH':
      variant = 'warning';
      break;
    case 'CRITICAL':
    case 'BREACHED':
    case 'FAILED':
    case 'REJECTED':
    case 'CANCELLED':
      variant = 'danger';
      break;
    case 'RUNNING':
    case 'INFO':
    case 'MEDIUM':
    case 'LOW':
      variant = 'info';
      break;
    case 'NO_DATA':
    default:
      variant = 'default';
      break;
  }
  
  return (
    <Badge variant={variant} className={className}>
      {status.replace('_', ' ')}
    </Badge>
  );
}
