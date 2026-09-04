import React, { useState } from 'react';
import { AppLayout } from './layouts/AppLayout';
import { PlotProfileCard } from './components/PlotProfileCard';
import { OnboardingForm } from './components/OnboardingForm';
import { DailyDecisionCard } from './components/DailyDecisionCard';
import { WhatIfControls } from './components/WhatIfControls';
import { TrendChartsSection } from './components/TrendChartsSection';
import { usePlotProfile } from './hooks/usePlot';
import { useDailyDecision } from './hooks/useDecision';
import { PlotProfile } from './types/api';
import { useLanguage } from './contexts/LanguageContext';
import { CheckCircle2, Sparkles } from 'lucide-react';

const STORAGE_PLOT_KEY = 'krishikavach_active_plot_id';

export const App: React.FC = () => {
  const { t } = useLanguage();
  
  // Default active plot ID (uses localStorage or Tukaram benchmark plot)
  const [activePlotId, setActivePlotId] = useState<string>(() => {
    try {
      return localStorage.getItem(STORAGE_PLOT_KEY) || 'tukaram_beed_01';
    } catch {
      return 'tukaram_beed_01';
    }
  });

  const [showOnboarding, setShowOnboarding] = useState<boolean>(false);
  const [successBanner, setSuccessBanner] = useState<string | null>(null);

  // Fetch real plot profile from backend
  const { data: plot, isLoading, isError } = usePlotProfile(activePlotId);
  const { data: decision } = useDailyDecision(activePlotId);

  const handlePlotCreated = (savedPlot: PlotProfile) => {
    try {
      localStorage.setItem(STORAGE_PLOT_KEY, savedPlot.plot_id);
    } catch {
      // Ignore
    }
    setActivePlotId(savedPlot.plot_id);
    setShowOnboarding(false);
    setSuccessBanner(t.farmSavedSuccess);
    setTimeout(() => setSuccessBanner(null), 5000);
  };

  return (
    <AppLayout>
      {/* Success Notification Banner */}
      {successBanner && (
        <div className="p-3.5 rounded-xl bg-emerald-50 border border-emerald-300 flex items-center justify-between gap-2 text-xs sm:text-sm font-bold text-emerald-900 shadow-xs animate-fade-in">
          <div className="flex items-center gap-2">
            <CheckCircle2 className="w-5 h-5 text-emerald-700 shrink-0" />
            <span>{successBanner}</span>
          </div>
          <Sparkles className="w-4 h-4 text-emerald-600" />
        </div>
      )}

      {/* Main Content Area */}
      {showOnboarding ? (
        <OnboardingForm
          onSuccess={handlePlotCreated}
          onCancel={plot ? () => setShowOnboarding(false) : undefined}
        />
      ) : (
        <>
          {/* 1. Farmer/Field Summary Card */}
          <PlotProfileCard
            plot={plot}
            isLoading={isLoading}
            isError={isError}
            onEditClick={() => setShowOnboarding(true)}
          />

          {/* 2. Real Daily Decision Card with Integrated Voice Player & Explainability Drawer */}
          <DailyDecisionCard plotId={activePlotId} />

          {/* 3. Real Interactive What-If Simulation Controls */}
          <WhatIfControls plotId={activePlotId} />

          {/* 4. Real Recharts Trend Visualizations Section */}
          <TrendChartsSection decisionId={decision?.explainability_id || decision?.decision_id || null} />
        </>
      )}
    </AppLayout>
  );
};

export default App;
