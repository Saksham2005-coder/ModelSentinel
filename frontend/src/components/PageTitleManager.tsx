import { useEffect } from 'react';
import { useLocation } from 'react-router-dom';

const routeTitles: Record<string, string> = {
  '/': 'ModelSentinel',
  '/login': 'ModelSentinel — Sign In',
  '/register': 'ModelSentinel — Create Account',
  '/forgot-password': 'ModelSentinel — Forgot Password',
  '/dashboard': 'ModelSentinel — Dashboard',
  '/models': 'ModelSentinel — Models',
  '/incidents': 'ModelSentinel — Incidents',
  '/investigations': 'ModelSentinel — Investigations',
  '/incident-memory': 'ModelSentinel — Incident Memory',
  '/regression-tests': 'ModelSentinel — Regression',
  '/engineering-intelligence': 'ModelSentinel — Engineering Intelligence',
  '/deployments': 'ModelSentinel — Deployments',
  '/pull-requests': 'ModelSentinel — Pull Requests',
  '/repository': 'ModelSentinel — Repositories',
  '/change-risk': 'ModelSentinel — Change Risk',
  '/change-intelligence': 'ModelSentinel — Change Intelligence',
  '/telemetry': 'ModelSentinel — Telemetry',
  '/slo': 'ModelSentinel — SLOs',
  '/alerts': 'ModelSentinel — Alerts',
  '/policies': 'ModelSentinel — Policies',
  '/audit': 'ModelSentinel — Audit',
  '/workflows': 'ModelSentinel — Workflows',
  '/integrations': 'ModelSentinel — Integrations',
};

export function PageTitleManager() {
  const location = useLocation();

  useEffect(() => {
    const path = location.pathname;
    
    // Exact matches
    if (routeTitles[path]) {
      document.title = routeTitles[path];
      return;
    }

    // Dynamic routes
    if (path.startsWith('/models/') && path.includes('/monitoring')) {
      document.title = 'ModelSentinel — Monitoring';
    } else if (path.startsWith('/models/') && path.includes('/intelligence')) {
      document.title = 'ModelSentinel — Model Intelligence';
    } else if (path.startsWith('/incidents/')) {
      document.title = 'ModelSentinel — Incident Details';
    } else if (path.startsWith('/regression-tests/')) {
      document.title = 'ModelSentinel — Regression Details';
    } else if (path.startsWith('/deployment-gates/')) {
      document.title = 'ModelSentinel — Deployment Details';
    } else if (path.startsWith('/pull-requests/')) {
      document.title = 'ModelSentinel — Pull Request Details';
    } else if (path.startsWith('/telemetry/')) {
      document.title = 'ModelSentinel — Telemetry Details';
    } else if (path.startsWith('/policies/')) {
      document.title = 'ModelSentinel — Policy Details';
    } else if (path.startsWith('/analytics/models/')) {
      document.title = 'ModelSentinel — Model Analytics';
    } else if (path.startsWith('/models/') && path.includes('/reliability')) {
      document.title = 'ModelSentinel — Reliability Timeline';
    } else if (path.startsWith('/models/')) {
      document.title = 'ModelSentinel — Model Details';
    } else {
      document.title = 'ModelSentinel';
    }
  }, [location]);

  return null;
}
