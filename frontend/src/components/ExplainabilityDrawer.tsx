import React, { useEffect } from 'react';
import { X, Droplets, Bug, Wind, CloudRain, TrendingUp, CheckCircle, ShieldAlert, FileText, Loader2, RefreshCw } from 'lucide-react';
import { useLanguage } from '../contexts/LanguageContext';
import { useExplainability } from '../hooks/useDecision';

interface ExplainabilityDrawerProps {
  decisionId: string | null;
  isOpen: boolean;
  onClose: () => void;
}

export const ExplainabilityDrawer: React.FC<ExplainabilityDrawerProps> = ({
  decisionId,
  isOpen,
  onClose,
}) => {
  const { t } = useLanguage();
  const { data: details, isLoading, isError, error, refetch } = useExplainability(isOpen ? decisionId : null);

  // Close on Escape key
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && isOpen) {
        onClose();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto bg-slate-900/60 backdrop-blur-xs flex justify-end transition-opacity">
      {/* Backdrop click to close */}
      <div className="fixed inset-0" onClick={onClose} aria-hidden="true" />

      {/* Drawer Container */}
      <div className="relative w-full max-w-2xl bg-white min-h-screen shadow-2xl flex flex-col z-10 border-l border-slate-200">
        {/* Header */}
        <div className="sticky top-0 z-20 bg-white border-b border-slate-200 px-5 py-4 flex items-center justify-between shadow-xs">
          <div className="flex items-center gap-2.5">
            <div className="w-9 h-9 rounded-lg bg-emerald-100 text-emerald-800 flex items-center justify-center font-bold">
              <FileText className="w-5 h-5 text-emerald-700" />
            </div>
            <div>
              <h2 className="text-lg font-bold text-slate-900 leading-tight">
                {t.explainabilityTitle}
              </h2>
              <p className="text-xs text-slate-600 font-medium">
                {t.explainabilitySubtitle}
              </p>
            </div>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="p-2 rounded-lg text-slate-500 hover:text-slate-900 hover:bg-slate-100 transition-colors cursor-pointer min-h-[40px] min-w-[40px] flex items-center justify-center"
            aria-label={t.closeDrawer}
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Drawer Body Content */}
        <div className="flex-1 p-5 space-y-6 overflow-y-auto">
          {/* Loading State */}
          {isLoading && (
            <div className="py-12 flex flex-col items-center justify-center space-y-3 text-slate-700 font-semibold">
              <Loader2 className="w-8 h-8 animate-spin text-emerald-700" />
              <p className="text-sm">{t.loadingExplainability}</p>
            </div>
          )}

          {/* Error State */}
          {isError && (
            <div className="p-4 rounded-xl bg-amber-50 border border-amber-300 space-y-3">
              <div className="flex items-start gap-2.5 text-amber-900">
                <ShieldAlert className="w-5 h-5 text-amber-700 shrink-0 mt-0.5" />
                <p className="text-sm font-bold">{error?.message || t.errorExplainability}</p>
              </div>
              <button
                type="button"
                onClick={() => refetch()}
                className="px-3.5 py-1.5 rounded-lg bg-emerald-700 text-white font-bold text-xs shadow-xs hover:bg-emerald-800 transition-colors cursor-pointer flex items-center gap-1.5"
              >
                <RefreshCw className="w-3.5 h-3.5" />
                <span>{t.retry}</span>
              </button>
            </div>
          )}

          {/* Render Actual Backend Explainability Data */}
          {details && (
            <>
              {/* Context Summary Badge */}
              <div className="p-3.5 rounded-xl bg-slate-50 border border-slate-200 flex flex-wrap items-center justify-between gap-2 text-xs font-semibold text-slate-700">
                <span>Plot: <strong className="text-slate-900">{details.plot_id}</strong></span>
                <span>Date: <strong className="text-slate-900">{details.date}</strong></span>
                <span>Source: <strong className="text-emerald-800 font-bold">{details.confidence_indicator}</strong></span>
              </div>

              {/* 1. Soil Moisture Metrics */}
              <div className="farmer-card bg-white space-y-3 border-slate-200">
                <div className="flex items-center justify-between border-b border-slate-100 pb-2">
                  <h3 className="text-sm font-bold text-slate-900 flex items-center gap-2">
                    <Droplets className="w-4 h-4 text-emerald-700" />
                    {t.soilSectionTitle}
                  </h3>
                  <span className={`px-2 py-0.5 rounded-md text-[11px] font-bold ${
                    details.soil_metrics.is_moisture_stressed ? 'bg-amber-100 text-amber-900 border border-amber-300' : 'bg-emerald-100 text-emerald-900 border border-emerald-300'
                  }`}>
                    {details.soil_metrics.is_moisture_stressed ? 'Moisture Stress' : 'Moisture Adequate'}
                  </span>
                </div>

                <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
                  <div className="p-2.5 bg-slate-50 rounded-lg border border-slate-200">
                    <p className="text-[10px] font-bold text-slate-500 uppercase">Current Depletion</p>
                    <p className="text-base font-extrabold text-slate-900">{details.soil_metrics.depletion_mm} mm</p>
                    <p className="text-[10px] text-slate-600">Root-zone water loss</p>
                  </div>
                  <div className="p-2.5 bg-slate-50 rounded-lg border border-slate-200">
                    <p className="text-[10px] font-bold text-slate-500 uppercase">RAW Threshold</p>
                    <p className="text-base font-extrabold text-slate-900">{details.soil_metrics.raw_mm} mm</p>
                    <p className="text-[10px] text-slate-600">Readily available limit</p>
                  </div>
                  <div className="p-2.5 bg-slate-50 rounded-lg border border-slate-200 col-span-2 sm:col-span-1">
                    <p className="text-[10px] font-bold text-slate-500 uppercase">TAW Capacity</p>
                    <p className="text-base font-extrabold text-slate-900">{details.soil_metrics.taw_mm} mm</p>
                    <p className="text-[10px] text-slate-600">Total available water</p>
                  </div>
                </div>
              </div>

              {/* 2. Rain & Spray Window Metrics */}
              <div className="farmer-card bg-white space-y-3 border-slate-200">
                <div className="flex items-center justify-between border-b border-slate-100 pb-2">
                  <h3 className="text-sm font-bold text-slate-900 flex items-center gap-2">
                    <CloudRain className="w-4 h-4 text-blue-700" />
                    {t.waterSectionTitle}
                  </h3>
                  <span className="text-xs font-bold text-blue-900 bg-blue-50 px-2 py-0.5 rounded border border-blue-200">
                    {details.spray_window_metrics.rain_next_36h_mm} mm in 36h
                  </span>
                </div>

                <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
                  <div className="p-2.5 bg-slate-50 rounded-lg border border-slate-200">
                    <p className="text-[10px] font-bold text-slate-500 uppercase">Rain Next 36h</p>
                    <p className="text-base font-extrabold text-blue-900">{details.spray_window_metrics.rain_next_36h_mm} mm</p>
                    <p className="text-[10px] text-slate-600">Limit: {details.spray_window_metrics.rain_irrigation_suppress_threshold_mm} mm</p>
                  </div>
                  <div className="p-2.5 bg-slate-50 rounded-lg border border-slate-200">
                    <p className="text-[10px] font-bold text-slate-500 uppercase">Rain Next 12h</p>
                    <p className="text-base font-extrabold text-slate-900">{details.spray_window_metrics.rain_next_12h_mm} mm</p>
                    <p className="text-[10px] text-slate-600">Foliar wash-off risk</p>
                  </div>
                  <div className="p-2.5 bg-slate-50 rounded-lg border border-slate-200 col-span-2 sm:col-span-1">
                    <p className="text-[10px] font-bold text-slate-500 uppercase">Rain Prob 6h</p>
                    <p className="text-base font-extrabold text-slate-900">{details.spray_window_metrics.rain_prob_next_6h}%</p>
                    <p className="text-[10px] text-slate-600">Spray block: {details.spray_window_metrics.rain_prob_spray_block_threshold}%</p>
                  </div>
                </div>
              </div>

              {/* 3. Wind & Pest Metrics Grid */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                {/* Wind Metrics */}
                <div className="farmer-card bg-white space-y-2 border-slate-200">
                  <div className="flex items-center justify-between border-b border-slate-100 pb-1.5">
                    <h3 className="text-xs font-bold text-slate-900 flex items-center gap-1.5">
                      <Wind className="w-4 h-4 text-emerald-700" />
                      {t.windSectionTitle}
                    </h3>
                    <span className={`px-1.5 py-0.5 rounded text-[10px] font-bold ${
                      details.spray_window_metrics.wind_speed_kmh > details.spray_window_metrics.wind_safe_limit_kmh
                        ? 'bg-red-100 text-red-800'
                        : 'bg-emerald-100 text-emerald-800'
                    }`}>
                      {details.spray_window_metrics.wind_speed_kmh > details.spray_window_metrics.wind_safe_limit_kmh ? 'Drift Risk' : 'Safe Window'}
                    </span>
                  </div>
                  <p className="text-base font-extrabold text-slate-900">{details.spray_window_metrics.wind_speed_kmh} km/h</p>
                  <p className="text-[11px] font-medium text-slate-600">Safe spraying limit: {details.spray_window_metrics.wind_safe_limit_kmh} km/h</p>
                </div>

                {/* Pest Metrics */}
                <div className="farmer-card bg-white space-y-2 border-slate-200">
                  <div className="flex items-center justify-between border-b border-slate-100 pb-1.5">
                    <h3 className="text-xs font-bold text-slate-900 flex items-center gap-1.5">
                      <Bug className="w-4 h-4 text-amber-700" />
                      {t.pestSectionTitle}
                    </h3>
                    <span className={`px-1.5 py-0.5 rounded text-[10px] font-bold ${
                      details.pest_metrics.risk_triggered ? 'bg-amber-100 text-amber-900' : 'bg-emerald-100 text-emerald-800'
                    }`}>
                      {details.pest_metrics.risk_triggered ? 'Risk Triggered' : 'Nominal'}
                    </span>
                  </div>
                  <p className="text-base font-extrabold text-slate-900">{details.pest_metrics.accumulated_gdd} GDD</p>
                  <p className="text-[11px] font-medium text-slate-600">Emergence threshold: {details.pest_metrics.gdd_threshold} GDD</p>
                </div>
              </div>

              {/* 4. Market Momentum Metrics */}
              {details.market_metrics && (
                <div className="farmer-card bg-white space-y-3 border-slate-200">
                  <div className="flex items-center justify-between border-b border-slate-100 pb-2">
                    <h3 className="text-sm font-bold text-slate-900 flex items-center gap-2">
                      <TrendingUp className="w-4 h-4 text-emerald-700" />
                      {t.marketSectionTitle}
                    </h3>
                    <span className="text-xs font-bold text-emerald-900 bg-emerald-100 px-2 py-0.5 rounded border border-emerald-200">
                      +{details.market_metrics.price_momentum_percent}% Momentum
                    </span>
                  </div>
                  <div className="grid grid-cols-2 gap-3">
                    <div className="p-2.5 bg-slate-50 rounded-lg border border-slate-200">
                      <p className="text-[10px] font-bold text-slate-500 uppercase">Daily Modal Price</p>
                      <p className="text-base font-extrabold text-slate-900">₹{details.market_metrics.modal_price_inr} / q</p>
                    </div>
                    <div className="p-2.5 bg-slate-50 rounded-lg border border-slate-200">
                      <p className="text-[10px] font-bold text-slate-500 uppercase">7-Day Moving Average</p>
                      <p className="text-base font-extrabold text-slate-900">₹{details.market_metrics.sma_7_inr} / q</p>
                    </div>
                  </div>
                </div>
              )}

              {/* 5. Rule Traces Log */}
              <div className="farmer-card bg-white space-y-3 border-slate-200">
                <div className="border-b border-slate-100 pb-2">
                  <h3 className="text-sm font-bold text-slate-900 flex items-center gap-2">
                    <FileText className="w-4 h-4 text-emerald-700" />
                    {t.ruleTracesTitle}
                  </h3>
                </div>

                <div className="space-y-2.5">
                  {details.rule_traces.map((trace) => (
                    <div
                      key={trace.rule_id}
                      className={`p-3 rounded-xl border space-y-1 ${
                        trace.triggered
                          ? 'bg-emerald-50/60 border-emerald-200'
                          : 'bg-slate-50 border-slate-200'
                      }`}
                    >
                      <div className="flex items-center justify-between text-xs">
                        <span className="font-bold text-slate-900 flex items-center gap-1.5">
                          {trace.triggered ? (
                            <CheckCircle className="w-4 h-4 text-emerald-600 shrink-0" />
                          ) : (
                            <span className="w-2 h-2 rounded-full bg-slate-400 shrink-0 ml-1 mr-1" />
                          )}
                          {trace.rule_name}
                        </span>
                        <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                          trace.triggered ? 'bg-emerald-200 text-emerald-950' : 'bg-slate-200 text-slate-700'
                        }`}>
                          {trace.triggered ? t.ruleTriggered : t.ruleNotTriggered}
                        </span>
                      </div>
                      <p className="text-[11px] font-mono text-slate-700 pl-5">
                        <strong className="text-slate-900 font-sans">Condition:</strong> {trace.condition_evaluated}
                      </p>
                      <p className="text-xs font-semibold text-slate-900 pl-5">
                        <strong className="text-slate-900 font-bold">Effect:</strong> {trace.effect}
                      </p>
                    </div>
                  ))}
                </div>
              </div>
            </>
          )}
        </div>

        {/* Footer */}
        <div className="sticky bottom-0 bg-white border-t border-slate-200 p-4">
          <button
            type="button"
            onClick={onClose}
            className="w-full py-2.5 px-4 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-900 font-bold text-sm transition-colors cursor-pointer border border-slate-300 min-h-[44px]"
          >
            {t.closeDrawer}
          </button>
        </div>
      </div>
    </div>
  );
};
