import { useEffect, useState } from 'react';
import { fetchApi } from '@/services/api/client';

interface AuditEvent {
  id: string;
  timestamp: string;
  action: string;
  user_id: string;
  user_role: string;
  resource_type: string;
  resource_id: string;
}

export function AuditPage() {
  const [events, setEvents] = useState<AuditEvent[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    fetchApi<AuditEvent[]>('/audit')
      .then(setEvents)
      .catch(console.error)
      .finally(() => setIsLoading(false));
  }, []);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight text-text-primary text-text-primary">Audit Log</h1>
        <p className="mt-1 text-sm text-text-muted dark:text-text-secondary">Review system-wide actions and approvals.</p>
      </div>
      
      {isLoading ? (
        <div>Loading...</div>
      ) : (
        <div className="bg-white dark:bg-background-secondary rounded-lg border border-slate-200 dark:border-border-strong overflow-hidden">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-slate-50 dark:bg-background-elevated/50">
                <th className="px-6 py-4 text-xs font-semibold text-text-muted dark:text-text-secondary uppercase">Time</th>
                <th className="px-6 py-4 text-xs font-semibold text-text-muted dark:text-text-secondary uppercase">Action</th>
                <th className="px-6 py-4 text-xs font-semibold text-text-muted dark:text-text-secondary uppercase">User</th>
                <th className="px-6 py-4 text-xs font-semibold text-text-muted dark:text-text-secondary uppercase">Role</th>
                <th className="px-6 py-4 text-xs font-semibold text-text-muted dark:text-text-secondary uppercase">Resource</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-200 dark:divide-border-strong">
              {events.map((event) => (
                <tr key={event.id} className="hover:bg-slate-50 dark:hover:bg-background-elevated/50">
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-text-disabled dark:text-text-primary">
                    {new Date(event.timestamp).toLocaleString()}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-text-primary text-text-primary">
                    {event.action}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-text-disabled dark:text-text-primary">
                    {event.user_id}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-text-disabled dark:text-text-primary">
                    {event.user_role}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-text-disabled dark:text-text-primary">
                    {event.resource_type}: {event.resource_id}
                  </td>
                </tr>
              ))}
              {events.length === 0 && (
                <tr>
                  <td colSpan={5} className="px-6 py-8 text-center text-sm text-text-muted dark:text-text-secondary">
                    No audit events found.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
