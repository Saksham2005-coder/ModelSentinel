import { NavLink } from 'react-router-dom';
import { 
  LayoutDashboard, 
  Box, 
  AlertCircle, 
  Search, 
  TestTube2, 
  CheckSquare, 
  Rocket, 
  GitBranch, 
  GitPullRequest,
  BrainCircuit, 
  Settings,
  BarChart2,
  ShieldAlert,
  ShieldCheck,
  Activity,
  GitCommit
} from 'lucide-react';
import { cn } from '@/lib/utils';

const navigation = [
  { name: 'Dashboard', href: '/dashboard', icon: LayoutDashboard },
  { name: 'Analytics', href: '/analytics', icon: BarChart2 },
  { name: 'Change Risk', href: '/change-risk', icon: ShieldAlert },
  { name: 'Change Intelligence', href: '/change-intelligence', icon: Activity },
  { name: 'Policies', href: '/policies', icon: ShieldCheck },
  { name: 'Workflows', href: '/workflows', icon: GitCommit },
  { name: 'Models', href: '/models', icon: Box },
  { name: 'Telemetry', href: '/telemetry', icon: Activity },
  { name: 'Incidents', href: '/incidents', icon: AlertCircle },
  { name: 'Investigations', href: '/investigations', icon: Search },
  { name: 'Experiments', href: '/experiments', icon: TestTube2 },
  { name: 'Regression Tests', href: '/regression-tests', icon: CheckSquare },
  { name: 'Deployments', href: '/deployments', icon: Rocket },
  { name: 'Pull Requests', href: '/pull-requests', icon: GitPullRequest },
  { name: 'Repository', href: '/repository', icon: GitBranch },
  { name: 'Incident Memory', href: '/incident-memory', icon: BrainCircuit },
  { name: 'Integrations', href: '/integrations', icon: Search },
  { name: 'SLOs', href: '/slo', icon: Activity },
  { name: 'Alerts', href: '/alerts', icon: AlertCircle },
];

export function Sidebar() {
  return (
    <div className="flex flex-col w-64 border-r border-border bg-background-primary h-full">
      <div className="p-6">
        <div className="flex items-center gap-2 text-brand font-bold text-xl">
          <BrainCircuit className="h-6 w-6" />
          <span className="text-text-primary">ModelSentinel</span>
        </div>
      </div>
      
      <div className="flex-1 px-3 space-y-1 overflow-y-auto">
        {navigation.map((item) => (
          <NavLink
            key={item.name}
            to={item.href}
            className={({ isActive }) =>
              cn(
                'group flex items-center px-3 py-2 text-sm font-medium rounded-md transition-colors',
                isActive
                  ? 'bg-brand-soft text-brand'
                  : 'text-text-secondary hover:bg-surface-hover hover:text-text-primary'
              )
            }
          >
            {({ isActive }) => (
              <>
                <item.icon
                  className={cn(
                    'mr-3 h-5 w-5 flex-shrink-0 transition-colors',
                    isActive ? 'text-brand' : 'text-text-muted group-hover:text-text-primary'
                  )}
                  aria-hidden="true"
                />
                {item.name}
              </>
            )}
          </NavLink>
        ))}
      </div>

      <div className="mt-auto p-4">
        <div className="pt-4 border-t border-border">
          <NavLink
            to="/settings"
            className={({ isActive }) =>
              cn(
                'group flex items-center px-3 py-2 text-sm font-medium rounded-md transition-colors',
                isActive
                  ? 'bg-brand-soft text-brand'
                  : 'text-text-secondary hover:bg-surface-hover hover:text-text-primary'
              )
            }
          >
            {({ isActive }) => (
              <>
                <Settings
                  className={cn(
                    'mr-3 h-5 w-5 flex-shrink-0 transition-colors',
                    isActive ? 'text-brand' : 'text-text-muted group-hover:text-text-primary'
                  )}
                  aria-hidden="true"
                />
                Settings
              </>
            )}
          </NavLink>
        </div>
      </div>
    </div>
  );
}
