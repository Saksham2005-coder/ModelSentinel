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

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/login" element={<PlaceholderPage title="Login" />} />
        <Route path="/signup" element={<PlaceholderPage title="Sign Up" />} />
        
        <Route element={<AppLayout />}>
          <Route path="/dashboard" element={<DashboardPage />} />
          <Route path="/models" element={<ModelsPage />} />
          <Route path="/models/:modelId/monitoring" element={<MonitoringPage />} />
          <Route path="/incidents" element={<IncidentsPage />} />
          <Route path="/incidents/:incidentId" element={<IncidentDetailPage />} />
          <Route path="/investigations" element={<PlaceholderPage title="Investigations" />} />
          <Route path="/experiments" element={<PlaceholderPage title="Experiments" />} />
          <Route path="/regression-tests" element={<PlaceholderPage title="Regression Tests" />} />
          <Route path="/deployments" element={<PlaceholderPage title="Deployments" />} />
          <Route path="/repository" element={<RepositoryPage />} />
          <Route path="/incident-memory" element={<PlaceholderPage title="Incident Memory" />} />
          <Route path="/settings" element={<PlaceholderPage title="Settings" />} />
          
          {/* Incident-specific sub-routes as placeholders */}
          <Route path="/incidents/:incidentId/investigation" element={<InvestigationPage />} />
          <Route path="/incidents/:incidentId/root-cause" element={<PlaceholderPage title="Root Cause" />} />
          <Route path="/incidents/:incidentId/timeline" element={<PlaceholderPage title="Timeline" />} />
          <Route path="/incidents/:incidentId/fix" element={<PlaceholderPage title="Proposed Fix" />} />
          <Route path="/incidents/:incidentId/validation" element={<PlaceholderPage title="Validation" />} />
        </Route>
      </Routes>
    </Router>
  );
}

export default App;
