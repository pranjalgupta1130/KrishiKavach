import React, { useState, useEffect } from 'react';
import { Sliders, Wind, CloudRain, RefreshCw, Loader2, ArrowRight, AlertTriangle, CheckCircle2, ShieldAlert, Sparkles, Info, WifiOff } from 'lucide-react';
import { useLanguage } from '../contexts/LanguageContext';
import { useSimulateDecision } from '../hooks/useDecision';
import { SimulationResponse } from '../types/api';

interface WhatIfControlsProps {
  plotId: string;
}

export const WhatIfControls: React.FC<WhatIfControlsProps> = ({ plotId }) => {
  const { language, t } = useLanguage();
  const simulateMutation = useSimulateDecision();

  // Network state
  const [isOnline, setIsOnline] = useState(navigator.onLine);

  useEffect(() => {
    const handleOnline = () => setIsOnline(true);
    const handleOffline = () => setIsOnline(false);

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);

  // Slider state - Initialized to Tukaram benchmark demo baseline
  const [windSpeed, setWindSpeed] = useState<number>(18.5);
  const [rain36h, setRain36h] = useState<number>(28.0);

  // Simulation result state
  const [simResult, setSimResult] = useState<SimulationResponse | null>(null);
  const [simError, setSimError] = useState<string | null>(null);

  // Trigger Backend Simulation
  const handleCheckNewAdvice = () => {
    if (!isOnline) {
      setSimError(t.whatIfOfflineNotice);
      return;
    }

    setSimError(null);
    simulateMutation.mutate(
      {
        plot_id: plotId,
        overrides: {
          wind_speed_kmh: windSpeed,
          rain_next_36h_mm: rain36h,
        },
      },
      {
        onSuccess: (data) => {
          setSimResult(data);
        },
        onError: (err) => {
          setSimError(err.message || t.simErrorTitle);
        },
      }
    );
  };

  // Reset to Baseline Demo Weather
  const handleReset = () => {
    setWindSpeed(18.5);
    setRain36h(28.0);
    setSimResult(null);
    setSimError(null);
  };

  // Resolve Vernacular Strings for Simulated Decision
  const getSimulatedAction = (res: SimulationResponse) => {
    const card = res.simulated_decision;
    const trans = card.translations?.[language];
    return trans?.primary_action || card.primary_action;
  };

  const getSimulatedProhibition = (res: SimulationResponse) => {
    const card = res.simulated_decision;
    const trans = card.translations?.[language];
    return trans?.critical_prohibition || card.critical_prohibition;
  };

  const getOriginalAction = (res: SimulationResponse) => {
    const card = res.original_decision;
    const trans = card.translations?.[language];
    return trans?.primary_action || card.primary_action;
  };

  const getOriginalProhibition = (res: SimulationResponse) => {
    const card = res.original_decision;
    const trans = card.translations?.[language];
    return trans?.critical_prohibition || card.critical_prohibition;
  };

  return (
    <div className="farmer-card bg-white space-y-5 border border-slate-200 shadow-sm">
      {/* Header */}
      <div className="flex items-center justify-between gap-2 pb-3 border-b border-slate-200">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-lg bg-emerald-100 text-emerald-800 flex items-center justify-center font-bold">
            <Sliders className="w-4 h-4 text-emerald-700" />
          </div>
          <div>
            <h3 className="text-lg font-bold text-slate-900 leading-tight">
              {t.whatIfTitle}
            </h3>
            <p className="text-xs text-slate-600 font-medium">
              {t.whatIfSubtitle}
            </p>
          </div>
        </div>

        <button
          type="button"
          onClick={handleReset}
          className="inline-flex items-center gap-1 px-2.5 py-1.5 rounded-lg bg-slate-100 hover:bg-slate-200 text-slate-800 text-xs font-bold transition-colors cursor-pointer border border-slate-300 min-h-[36px]"
        >
          <RefreshCw className="w-3.5 h-3.5 text-slate-600" />
          <span>{t.resetWeatherButton}</span>
        </button>
      </div>

      {/* Interactive Controls / Sliders */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        {/* Wind Speed Control */}
        <div className="p-3.5 rounded-xl bg-slate-50 border border-slate-200 space-y-2">
          <div className="flex items-center justify-between">
            <label className="text-xs font-bold text-slate-900 flex items-center gap-1.5">
              <Wind className="w-4 h-4 text-emerald-700" />
              {t.windSpeedLabel}
            </label>
            <span className="text-sm font-extrabold text-emerald-800 bg-emerald-100 px-2 py-0.5 rounded-md border border-emerald-200">
              {windSpeed.toFixed(1)} km/h
            </span>
          </div>
          <input
            type="range"
            min="0"
            max="40"
            step="0.5"
            value={windSpeed}
            onChange={(e) => setWindSpeed(parseFloat(e.target.value))}
            className="w-full h-2 bg-slate-200 rounded-lg appearance-none cursor-pointer accent-emerald-700"
            aria-label={t.windSpeedLabel}
          />
          <div className="flex justify-between text-[10px] font-semibold text-slate-500">
            <span>0 km/h (Calm)</span>
            <span>15 km/h (Limit)</span>
            <span>40 km/h (Strong)</span>
          </div>
        </div>

        {/* Rain Expected 36h Control */}
        <div className="p-3.5 rounded-xl bg-slate-50 border border-slate-200 space-y-2">
          <div className="flex items-center justify-between">
            <label className="text-xs font-bold text-slate-900 flex items-center gap-1.5">
              <CloudRain className="w-4 h-4 text-blue-700" />
              {t.rain36hLabel}
            </label>
            <span className="text-sm font-extrabold text-blue-900 bg-blue-100 px-2 py-0.5 rounded-md border border-blue-200">
              {rain36h.toFixed(1)} mm
            </span>
          </div>
          <input
            type="range"
            min="0"
            max="60"
            step="1"
            value={rain36h}
            onChange={(e) => setRain36h(parseFloat(e.target.value))}
            className="w-full h-2 bg-slate-200 rounded-lg appearance-none cursor-pointer accent-blue-600"
            aria-label={t.rain36hLabel}
          />
          <div className="flex justify-between text-[10px] font-semibold text-slate-500">
            <span>0 mm (Dry)</span>
            <span>25 mm (Threshold)</span>
            <span>60 mm (Heavy)</span>
          </div>
        </div>
      </div>

      {/* Action Button: Trigger Backend Simulation */}
      <div className="pt-1">
        <button
          type="button"
          onClick={handleCheckNewAdvice}
          disabled={simulateMutation.isPending || !isOnline}
          className="w-full py-3 px-4 rounded-xl bg-emerald-700 hover:bg-emerald-800 disabled:bg-slate-400 text-white font-bold text-sm shadow-md transition-colors cursor-pointer flex items-center justify-center gap-2 min-h-[48px]"
        >
          {simulateMutation.isPending ? (
            <>
              <Loader2 className="w-4.5 h-4.5 animate-spin text-white" />
              <span>{t.checkingAdviceButton}</span>
            </>
          ) : !isOnline ? (
            <>
              <WifiOff className="w-4.5 h-4.5 text-white" />
              <span>{t.whatIfOfflineNotice}</span>
            </>
          ) : (
            <>
              <Sparkles className="w-4.5 h-4.5 text-white" />
              <span>{t.seeNewAdviceButton}</span>
            </>
          )}
        </button>
      </div>

      {/* Simulation Error State */}
      {simError && (
        <div className="p-3 rounded-lg bg-amber-50 border border-amber-300 flex items-center gap-2 text-xs font-semibold text-amber-950">
          <ShieldAlert className="w-4 h-4 text-amber-700 shrink-0" />
          <span>{simError}</span>
        </div>
      )}

      {/* Simulation Result Output */}
      {simResult && (
        <div className="space-y-4 pt-2 border-t border-slate-200">
          {/* Flip Status Banner */}
          <div
            className={`p-3.5 rounded-xl border flex items-start gap-2.5 ${
              simResult.is_flipped
                ? 'bg-emerald-50 border-emerald-300 text-emerald-950'
                : 'bg-slate-50 border-slate-300 text-slate-900'
            }`}
          >
            {simResult.is_flipped ? (
              <CheckCircle2 className="w-5 h-5 text-emerald-700 shrink-0 mt-0.5" />
            ) : (
              <Info className="w-5 h-5 text-slate-600 shrink-0 mt-0.5" />
            )}
            <div className="space-y-0.5">
              <p className="text-sm font-extrabold">
                {simResult.is_flipped ? t.recommendationFlippedTitle : t.recommendationSameTitle}
              </p>
              <p className="text-xs font-medium opacity-90 leading-relaxed">
                {simResult.flip_reason}
              </p>
            </div>
          </div>

          {/* Before & After Comparison Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {/* Original Decision */}
            <div className="p-3.5 rounded-xl bg-slate-50 border border-slate-200 space-y-2">
              <div className="flex items-center justify-between text-xs font-bold text-slate-700 border-b border-slate-200 pb-1.5">
                <span>{t.currentAdviceHeader}</span>
                <span className="text-[10px] bg-slate-200 text-slate-800 px-1.5 py-0.5 rounded">Baseline</span>
              </div>
              <div className="space-y-1">
                <p className="text-xs font-bold text-emerald-900 flex items-center gap-1">
                  🌱 Action:
                </p>
                <p className="text-xs font-semibold text-slate-900">
                  {getOriginalAction(simResult)}
                </p>
              </div>
              <div className="space-y-1 pt-1">
                <p className="text-xs font-bold text-amber-900 flex items-center gap-1">
                  ⚠️ Prohibition:
                </p>
                <p className="text-xs font-bold text-amber-950">
                  {getOriginalProhibition(simResult)}
                </p>
              </div>
            </div>

            {/* Simulated New Decision */}
            <div className="p-3.5 rounded-xl bg-emerald-50/70 border-2 border-emerald-300 space-y-2 shadow-xs">
              <div className="flex items-center justify-between text-xs font-bold text-emerald-900 border-b border-emerald-200 pb-1.5">
                <span className="flex items-center gap-1">
                  <ArrowRight className="w-3.5 h-3.5 text-emerald-700" />
                  {t.newAdviceHeader}
                </span>
                <span className="text-[10px] bg-emerald-700 text-white font-bold px-1.5 py-0.5 rounded">Simulated</span>
              </div>
              <div className="space-y-1">
                <p className="text-xs font-bold text-emerald-950 flex items-center gap-1">
                  🌱 New Action:
                </p>
                <p className="text-xs sm:text-sm font-extrabold text-slate-900">
                  {getSimulatedAction(simResult)}
                </p>
              </div>
              <div className="space-y-1 pt-1">
                <p className="text-xs font-bold text-amber-950 flex items-center gap-1">
                  ⚠️ New Prohibition:
                </p>
                <p className="text-xs sm:text-sm font-bold text-amber-950">
                  {getSimulatedProhibition(simResult)}
                </p>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
