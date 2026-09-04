import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  MapPin,
  Calendar,
  Layers,
  Sparkles,
  Camera,
  CloudSun,
  Sliders,
  History as HistoryIcon,
  ChevronRight,
  Droplets,
  Wind,
  Bug,
  TrendingUp
} from 'lucide-react';
import { useFieldContext } from '../contexts/FieldContext';
import { useDailyDecision, useExplainability } from '../hooks/useDecision';
import { useLanguage } from '../contexts/LanguageContext';
import { DailyDecisionCard } from '../components/DailyDecisionCard';
import { WhatIfControls } from '../components/WhatIfControls';
import { ExplainabilityDrawer } from '../components/ExplainabilityDrawer';

export const DashboardPage: React.FC = () => {
  const { activePlotId, activePlot, isLoadingPlot } = useFieldContext();
  const { data: decision } = useDailyDecision(activePlotId);
  const { data: explainability } = useExplainability(decision?.explainability_id || null);
  const { t } = useLanguage();
  const navigate = useNavigate();

  const [showWhatIf, setShowWhatIf] = useState(false);
  const [showExplainability, setShowExplainability] = useState(false);

  return (
    <div className="space-y-4 sm:space-y-6 animate-fade-in">
      {/* 1. Selected Field Banner */}
      <div className="bg-gradient-to-r from-emerald-900 via-emerald-800 to-teal-900 text-white rounded-2xl p-4 sm:p-5 shadow-sm relative overflow-hidden">
        <div className="absolute right-0 top-0 translate-x-4 -translate-y-4 opacity-10 pointer-events-none">
          <Sparkles className="w-48 h-48 text-white" />
        </div>

        <div className="relative z-10 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div className="space-y-1">
            <div className="flex items-center gap-2 text-emerald-200 text-xs font-bold uppercase tracking-wider">
              <MapPin className="w-3.5 h-3.5" />
              <span>{activePlot?.location.district || 'Selected Location'}</span>
              <span>•</span>
              <span>{activePlot?.crop_type === 'bt_cotton' ? 'Bt Cotton' : activePlot?.crop_type === 'soybean' ? 'Soybean' : activePlot?.crop_type || 'Crop'}</span>
            </div>
            <h2 className="text-xl sm:text-2xl font-black tracking-tight text-white">
              {activePlot ? `${activePlot.farmer_name}'s Field` : "Farmer's Field"}
            </h2>
            <p className="text-xs text-emerald-100/90 font-medium">
              {t.subHeading}
            </p>
          </div>

          {activePlot && (
            <div className="flex flex-wrap items-center gap-2 text-xs bg-white/10 backdrop-blur-md rounded-xl p-2.5 border border-white/15 shrink-0">
              <div className="flex items-center gap-1.5 px-2 py-1 rounded-lg bg-emerald-950/40">
                <Calendar className="w-3.5 h-3.5 text-emerald-300" />
                <span className="font-bold">{activePlot.sowing_date}</span>
              </div>
              <div className="flex items-center gap-1.5 px-2 py-1 rounded-lg bg-emerald-950/40">
                <Layers className="w-3.5 h-3.5 text-emerald-300" />
                <span className="font-bold">{activePlot.plot_area_ha} Ha</span>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* 2. Primary Decision Card */}
      <DailyDecisionCard plotId={activePlotId} />

      {/* 3. Concise Metrics Strip */}
      {explainability && (
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-2.5 sm:gap-3">
          <div className="p-3 bg-white border border-slate-200 rounded-xl shadow-2xs space-y-1">
            <div className="flex items-center gap-1.5 text-slate-500 text-[11px] font-bold">
              <Droplets className="w-3.5 h-3.5 text-blue-600" />
              <span>Soil Depletion</span>
            </div>
            <p className="text-base font-black text-slate-900">
              {explainability.soil_metrics?.depletion_mm?.toFixed(1) || '0.0'} mm
            </p>
            <p className="text-[10px] text-slate-500 font-semibold truncate">
              RAW Limit: {explainability.soil_metrics?.raw_mm?.toFixed(1) || '78.0'} mm
            </p>
          </div>

          <div className="p-3 bg-white border border-slate-200 rounded-xl shadow-2xs space-y-1">
            <div className="flex items-center gap-1.5 text-slate-500 text-[11px] font-bold">
              <Wind className="w-3.5 h-3.5 text-cyan-600" />
              <span>Wind Speed</span>
            </div>
            <p className="text-base font-black text-slate-900">
              {explainability.spray_window_metrics?.wind_speed_kmh?.toFixed(1) || '0.0'} km/h
            </p>
            <p className="text-[10px] text-slate-500 font-semibold truncate">
              Safe Limit: 15.0 km/h
            </p>
          </div>

          <div className="p-3 bg-white border border-slate-200 rounded-xl shadow-2xs space-y-1">
            <div className="flex items-center gap-1.5 text-slate-500 text-[11px] font-bold">
              <CloudSun className="w-3.5 h-3.5 text-amber-600" />
              <span>36h Rain</span>
            </div>
            <p className="text-base font-black text-slate-900">
              {explainability.spray_window_metrics?.rain_next_36h_mm?.toFixed(1) || '0.0'} mm
            </p>
            <p className="text-[10px] text-slate-500 font-semibold truncate">
              Irrig Block: 25.0 mm
            </p>
          </div>

          <div className="p-3 bg-white border border-slate-200 rounded-xl shadow-2xs space-y-1">
            <div className="flex items-center gap-1.5 text-slate-500 text-[11px] font-bold">
              <Bug className="w-3.5 h-3.5 text-rose-600" />
              <span>Pest GDD</span>
            </div>
            <p className="text-base font-black text-slate-900">
              {explainability.pest_metrics?.accumulated_gdd?.toFixed(0) || '0'} GDD
            </p>
            <p className="text-[10px] text-slate-500 font-semibold truncate">
              Threshold: {explainability.pest_metrics?.gdd_threshold?.toFixed(0) || '450'} GDD
            </p>
          </div>
        </div>
      )}

      {/* 4. Quick Action Grid */}
      <div className="space-y-2">
        <h3 className="text-xs font-bold text-slate-500 uppercase tracking-wider">
          {t.quickActionsTitle || 'Quick Actions'}
        </h3>
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-2.5">
          <button
            onClick={() => navigate('/scan')}
            className="p-3 bg-emerald-50 hover:bg-emerald-100 border border-emerald-200 rounded-xl flex items-center gap-2.5 text-left transition-colors group"
          >
            <div className="w-9 h-9 rounded-lg bg-emerald-700 text-white flex items-center justify-center shrink-0 shadow-2xs">
              <Camera className="w-5 h-5" />
            </div>
            <div>
              <p className="text-xs font-black text-emerald-950 group-hover:text-emerald-900">
                {t.navScan || 'Scan Crop'}
              </p>
              <p className="text-[10px] font-semibold text-emerald-700">Image Check</p>
            </div>
          </button>

          <button
            onClick={() => navigate('/weather')}
            className="p-3 bg-cyan-50 hover:bg-cyan-100 border border-cyan-200 rounded-xl flex items-center gap-2.5 text-left transition-colors group"
          >
            <div className="w-9 h-9 rounded-lg bg-cyan-700 text-white flex items-center justify-center shrink-0 shadow-2xs">
              <CloudSun className="w-5 h-5" />
            </div>
            <div>
              <p className="text-xs font-black text-cyan-950 group-hover:text-cyan-900">
                {t.navWeather || 'Weather'}
              </p>
              <p className="text-[10px] font-semibold text-cyan-700">Forecast Data</p>
            </div>
          </button>

          <button
            onClick={() => setShowWhatIf(!showWhatIf)}
            className="p-3 bg-amber-50 hover:bg-amber-100 border border-amber-200 rounded-xl flex items-center gap-2.5 text-left transition-colors group"
          >
            <div className="w-9 h-9 rounded-lg bg-amber-600 text-white flex items-center justify-center shrink-0 shadow-2xs">
              <Sliders className="w-5 h-5" />
            </div>
            <div>
              <p className="text-xs font-black text-amber-950 group-hover:text-amber-900">
                {t.whatIf || 'What If?'}
              </p>
              <p className="text-[10px] font-semibold text-amber-700">Simulate</p>
            </div>
          </button>

          <button
            onClick={() => navigate('/history')}
            className="p-3 bg-purple-50 hover:bg-purple-100 border border-purple-200 rounded-xl flex items-center gap-2.5 text-left transition-colors group"
          >
            <div className="w-9 h-9 rounded-lg bg-purple-700 text-white flex items-center justify-center shrink-0 shadow-2xs">
              <HistoryIcon className="w-5 h-5" />
            </div>
            <div>
              <p className="text-xs font-black text-purple-950 group-hover:text-purple-900">
                {t.navHistory || 'History'}
              </p>
              <p className="text-[10px] font-semibold text-purple-700">Past Decisions</p>
            </div>
          </button>
        </div>
      </div>

      {/* 5. Embedded What-If Simulation Controls (Togglable / Active) */}
      {showWhatIf && (
        <div className="animate-fade-in border-2 border-amber-300 rounded-2xl p-1 bg-amber-50/50">
          <WhatIfControls plotId={activePlotId} />
        </div>
      )}

      {/* Explainability Drawer */}
      {decision?.explainability_id && (
        <ExplainabilityDrawer
          decisionId={decision.explainability_id}
          isOpen={showExplainability}
          onClose={() => setShowExplainability(false)}
        />
      )}
    </div>
  );
};
