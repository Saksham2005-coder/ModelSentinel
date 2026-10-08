import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { AppLayout } from '@/layouts/AppLayout';
import { LandingPage } from '@/pages/LandingPage';
import { DashboardPage } from '@/pages/DashboardPage';
import { ModelsPage } from '@/pages/ModelsPage';
import { MonitoringPage } from '@/pages/MonitoringPage';
import { IncidentsPage } from '@/pages/IncidentsPage';
import { IncidentDetailPage } from '@/pages/IncidentDetailPage';
import { PlaceholderPage } from '@/pages/PlaceholderPage';

import { InvestigationPage } from '@/pages/InvestigationPage';
import { RepositoryPage } from '@/pages/RepositoryPage';
import { PatchWorkspacePage } from '@/pages/PatchWorkspacePage';
import { ValidationWorkspacePage } from '@/pages/ValidationWorkspacePage';
import { IncidentMemoryPage } from '@/pages/IncidentMemoryPage';
import { RegressionSuitePage } from '@/pages/RegressionSuitePage';
import { RegressionTestPage } from '@/pages/RegressionTestPage';
import { PullRequestsPage } from '@/pages/PullRequestsPage';
import { PullRequestDetailPage } from '@/pages/PullRequestDetailPage';
import { DeploymentGatesPage } from '@/pages/DeploymentGatesPage';
import { DeploymentGateDetailPage } from '@/pages/DeploymentGateDetailPage';
import { AnalyticsPage } from '@/pages/AnalyticsPage';
import { ModelAnalyticsDetailPage } from '@/pages/ModelAnalyticsDetailPage';
import { ChangeRiskPage } from '@/pages/ChangeRiskPage';
import { PoliciesPage } from '@/pages/PoliciesPage';
import { PolicyDetailPage } from '@/pages/PolicyDetailPage';
import { TelemetryWorkspacePage } from '@/pages/TelemetryWorkspacePage';
import { TelemetryDetailPage } from '@/pages/TelemetryDetailPage';
import ReliabilityTimelinePage from '@/pages/model/ReliabilityTimelinePage';
import { ModelIntelligencePage } from '@/pages/model/ModelIntelligencePage';
import { VersionComparisonPage } from '@/pages/model/VersionComparisonPage';
import { ChangeIntelligencePage } from '@/pages/ChangeIntelligencePage';
import Workflows from '@/pages/Workflows';
import WorkflowDetail from '@/pages/WorkflowDetail';
import { IntegrationsPage } from '@/pages/IntegrationsPage';

import { AuthProvider } from '@/AuthContext';
import { LoginPage } from '@/pages/LoginPage';
import { RegisterPage } from '@/pages/RegisterPage';
import { ForgotPasswordPage } from '@/pages/ForgotPasswordPage';
import { AuditPage } from '@/pages/AuditPage';
import { ProtectedRoute } from '@/components/ProtectedRoute';

function App() {
  return (
    <AuthProvider>
      <Router>
        <Routes>
          <Route path="/" element={<LandingPage />} />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />
          <Route path="/forgot-password" element={<ForgotPasswordPage />} />
          
          <Route element={<ProtectedRoute />}>
            <Route element={<AppLayout />}>
              <Route path="/dashboard" element={<DashboardPage />} />
              <Route path="/models" element={<ModelsPage />} />
              <Route path="/models/:modelId/monitoring" element={<MonitoringPage />} />
              <Route path="/models/:modelId/intelligence" element={<ModelIntelligencePage />} />
              <Route path="/models/:modelId/compare" element={<VersionComparisonPage />} />
              <Route path="/models/:id/reliability" element={<ReliabilityTimelinePage />} />
              <Route path="/incidents" element={<IncidentsPage />} />
              <Route path="/incidents/:incidentId" element={<IncidentDetailPage />} />
              <Route path="/investigations" element={<PlaceholderPage title="Investigations" />} />
              <Route path="/experiments" element={<PlaceholderPage title="Experiments" />} />
              <Route path="/regression-tests" element={<RegressionSuitePage />} />
              <Route path="/regression-tests/:id" element={<RegressionTestPage />} />
              <Route path="/deployments" element={<DeploymentGatesPage />} />
              <Route path="/deployment-gates/:id" element={<DeploymentGateDetailPage />} />
              <Route path="/pull-requests" element={<PullRequestsPage />} />
              <Route path="/pull-requests/:id" element={<PullRequestDetailPage />} />
              <Route path="/repository" element={<RepositoryPage />} />
              <Route path="/incident-memory" element={<IncidentMemoryPage />} />
              <Route path="/workflows" element={<Workflows />} />
              <Route path="/workflows/:id" element={<WorkflowDetail />} />
              <Route path="/integrations" element={<IntegrationsPage />} />
              <Route path="/audit" element={<AuditPage />} />
              <Route path="/settings" element={<PlaceholderPage title="Settings" />} />
              
              <Route path="/analytics" element={<AnalyticsPage />} />
              <Route path="/analytics/models/:modelId" element={<ModelAnalyticsDetailPage />} />
              <Route path="/change-risk" element={<ChangeRiskPage />} />
              <Route path="/change-intelligence" element={<ChangeIntelligencePage />} />
              <Route path="/policies" element={<PoliciesPage />} />
              <Route path="/policies/:id" element={<PolicyDetailPage />} />
              <Route path="/telemetry" element={<TelemetryWorkspacePage />} />
              <Route path="/telemetry/:id" element={<TelemetryDetailPage />} />
              
              {/* Incident-specific sub-routes as placeholders */}
              <Route path="/incidents/:incidentId/investigation" element={<InvestigationPage />} />
              <Route path="/incidents/:incidentId/root-cause" element={<PlaceholderPage title="Root Cause" />} />
              <Route path="/incidents/:incidentId/timeline" element={<PlaceholderPage title="Timeline" />} />
              <Route path="/incidents/:incidentId/fix" element={<PatchWorkspacePage />} />
              <Route path="/incidents/:incidentId/validation" element={<ValidationWorkspacePage />} />
            </Route>
          </Route>
        </Routes>
      </Router>
    </AuthProvider>
  );
}

export default App;
