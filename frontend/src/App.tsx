import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { AppLayout } from '@/layouts/AppLayout';
import { LandingPage } from '@/pages/LandingPage';
import { DashboardPage } from '@/pages/DashboardPage';
import { ModelsPage } from '@/pages/ModelsPage';
import { PlaceholderPage } from '@/pages/PlaceholderPage';

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
          <Route path="/incidents" element={<PlaceholderPage title="Incidents" />} />
          <Route path="/investigations" element={<PlaceholderPage title="Investigations" />} />
          <Route path="/experiments" element={<PlaceholderPage title="Experiments" />} />
          <Route path="/regression-tests" element={<PlaceholderPage title="Regression Tests" />} />
          <Route path="/deployments" element={<PlaceholderPage title="Deployments" />} />
          <Route path="/repository" element={<PlaceholderPage title="Repository" />} />
          <Route path="/incident-memory" element={<PlaceholderPage title="Incident Memory" />} />
          <Route path="/settings" element={<PlaceholderPage title="Settings" />} />
          
          {/* Incident-specific sub-routes as placeholders */}
          <Route path="/incidents/:incidentId" element={<PlaceholderPage title="Incident Details" />} />
          <Route path="/incidents/:incidentId/investigation" element={<PlaceholderPage title="Investigation" />} />
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
