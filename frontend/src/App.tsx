import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { FieldProvider } from './contexts/FieldContext';
import { AppLayout } from './layouts/AppLayout';
import { DashboardPage } from './pages/DashboardPage';
import { FieldsPage } from './pages/FieldsPage';
import { WeatherPage } from './pages/WeatherPage';
import { CropHealthPage } from './pages/CropHealthPage';
import { MarketPage } from './pages/MarketPage';
import { HistoryPage } from './pages/HistoryPage';
import { ScanCropPage } from './pages/ScanCropPage';
import { SettingsPage } from './pages/SettingsPage';

export const App: React.FC = () => {
  return (
    <BrowserRouter>
      <FieldProvider>
        <AppLayout>
          <Routes>
            <Route path="/" element={<Navigate to="/dashboard" replace />} />
            <Route path="/dashboard" element={<DashboardPage />} />
            <Route path="/fields" element={<FieldsPage />} />
            <Route path="/weather" element={<WeatherPage />} />
            <Route path="/crop-health" element={<CropHealthPage />} />
            <Route path="/market" element={<MarketPage />} />
            <Route path="/history" element={<HistoryPage />} />
            <Route path="/scan" element={<ScanCropPage />} />
            <Route path="/settings" element={<SettingsPage />} />
            <Route path="*" element={<Navigate to="/dashboard" replace />} />
          </Routes>
        </AppLayout>
      </FieldProvider>
    </BrowserRouter>
  );
};

export default App;
