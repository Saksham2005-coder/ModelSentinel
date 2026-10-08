import { NavLink } from 'react-router-dom';
import { 
  LayoutDashboard, 
  Box, 
  AlertCircle, 
  Search, 
  CheckSquare, 
  Rocket, 
  GitBranch, 
  GitPullRequest,
  BrainCircuit, 
  BarChart2,
  ShieldAlert,
  ShieldCheck,
  Activity,
  GitCommit,
  Brain
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { useEffect } from 'react';

const navigationGroups = [
  {
    name: 'Overview',
    items: [
      { name: 'Dashboard', href: '/dashboard', icon: LayoutDashboard },
      { name: 'Analytics', href: '/analytics', icon: BarChart2 },
    ]
  },
  {
    name: 'Models',
    items: [
      { name: 'Models', href: '/models', icon: Box },
    ]
  },
  {
    name: 'Reliability',
    items: [
      { name: 'Incidents', href: '/incidents', icon: AlertCircle },
      { name: 'Investigations', href: '/investigations', icon: Search },
      { name: 'Telemetry', href: '/telemetry', icon: Activity },
      { name: 'SLOs', href: '/slo', icon: Activity },
      { name: 'Alerts', href: '/alerts', icon: AlertCircle },
    ]
  },
  {
    name: 'Engineering',
    items: [
      { name: 'Repositories', href: '/repository', icon: GitBranch },
      { name: 'Change Risk', href: '/change-risk', icon: ShieldAlert },
      { name: 'Change Intelligence', href: '/change-intelligence', icon: Activity },
      { name: 'Pull Requests', href: '/pull-requests', icon: GitPullRequest },
      { name: 'Deployments', href: '/deployments', icon: Rocket },
    ]
  },
  {
    name: 'Intelligence',
    items: [
      { name: 'Engineering Intelligence', href: '/engineering-intelligence', icon: Brain },
      { name: 'Incident Memory', href: '/incident-memory', icon: BrainCircuit },
      { name: 'Regression', href: '/regression-tests', icon: CheckSquare },
    ]
  },
  {
    name: 'Automation',
    items: [
      { name: 'Workflows', href: '/workflows', icon: GitCommit },
      { name: 'Integrations', href: '/integrations', icon: Search },
    ]
  },
  {
    name: 'Governance',
    items: [
      { name: 'Policies', href: '/policies', icon: ShieldCheck },
      { name: 'Audit', href: '/audit', icon: ShieldCheck },
    ]
  }
];

export function Sidebar({ mobileOpen = false, onClose }: { mobileOpen?: boolean; onClose?: () => void }) {
  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && mobileOpen && onClose) {
        onClose();
      }
    };
    document.addEventListener('keydown', handleEscape);
    return () => document.removeEventListener('keydown', handleEscape);
  }, [mobileOpen, onClose]);

  useEffect(() => {
    if (mobileOpen) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = '';
    }
    return () => {
      document.body.style.overflow = '';
    };
  }, [mobileOpen]);

  return (
    <>
      {/* Mobile Backdrop */}
      {mobileOpen && (
        <div 
          className="fixed inset-0 bg-black/60 backdrop-blur-sm z-40 md:hidden" 
          onClick={onClose}
          aria-hidden="true"
        />
      )}
      
      {/* Sidebar Container */}
      <div 
        className={cn(
          "flex flex-col w-64 border-r border-border bg-background-primary/95 md:bg-background-primary/50 backdrop-blur-md h-full z-50 fixed md:relative transition-transform duration-300 ease-in-out",
          mobileOpen ? "translate-x-0" : "-translate-x-full md:translate-x-0"
        )}
      >
      <div className="p-6 pb-2">
        <NavLink to="/dashboard" onClick={onClose} className="flex items-center gap-2 text-brand font-bold text-xl hover:opacity-90 transition-opacity">
          <BrainCircuit className="h-6 w-6" />
          <span className="text-text-primary tracking-tight">ModelSentinel</span>
        </NavLink>
      </div>
      
      <div className="flex-1 px-3 space-y-6 overflow-y-auto py-4">
        {navigationGroups.map((group) => (
          <div key={group.name} className="space-y-1">
            <h3 className="px-3 text-xs font-semibold text-text-muted uppercase tracking-wider mb-2">
              {group.name}
            </h3>
            {group.items.map((item) => (
              <NavLink
                key={item.name}
                to={item.href}
                onClick={onClose}
                className={({ isActive }) =>
                  cn(
                    'group flex items-center px-3 py-2 text-sm font-medium rounded-md transition-all duration-300 relative',
                    isActive
                      ? 'bg-brand/10 text-brand shadow-[inset_2px_0_0_0_#f59e0b]'
                      : 'text-text-secondary hover:bg-surface-hover hover:text-text-primary'
                  )
                }
              >
                {({ isActive }) => (
                  <>
                    <item.icon
                      className={cn(
                        'mr-3 h-4 w-4 flex-shrink-0 transition-colors',
                        isActive ? 'text-brand' : 'text-text-muted group-hover:text-brand-soft'
                      )}
                      aria-hidden="true"
                    />
                    {item.name}
                  </>
                )}
              </NavLink>
            ))}
          </div>
        ))}
      </div>


    </div>
    </>
  );
}
