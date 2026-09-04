import React, { useState, useEffect } from 'react';
import { Sprout, AlertTriangle, Info, Loader2, RefreshCw, Calendar, Database, ShieldAlert, ArrowUpRight, WifiOff, Clock } from 'lucide-react';
import { useLanguage } from '../contexts/LanguageContext';
import { useDailyDecision } from '../hooks/useDecision';
import { VoicePlayer } from './VoicePlayer';
import { ExplainabilityDrawer } from './ExplainabilityDrawer';
import { offlineStorage } from '../utils/offlineStorage';
import { DecisionCard } from '../types/api';

interface DailyDecisionCardProps {
  plotId: string;
}

export const DailyDecisionCard: React.FC<DailyDecisionCardProps> = ({ plotId }) => {
  const { language, t } = useLanguage();
  const { data: liveDecision, isLoading, isError, error, refetch, isFetching } = useDailyDecision(plotId);
  const [isDrawerOpen, setIsDrawerOpen] = useState(false);
  const [isOfflineMode, setIsOfflineMode] = useState(!navigator.onLine);
  const [cachedDecision, setCachedDecision] = useState<DecisionCard | null>(() => offlineStorage.getDecision());

  // Listen to network status
  useEffect(() => {
    const handleOnline = () => setIsOfflineMode(false);
    const handleOffline = () => setIsOfflineMode(true);

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);

  // Save live decision to persistent offline storage when query succeeds
  useEffect(() => {
    if (liveDecision) {
      offlineStorage.saveDecision(liveDecision);
      setCachedDecision(liveDecision);
    }
  }, [liveDecision]);

  // Determine active decision object (Live or Cached Fallback)
  const activeDecision = liveDecision || (isError || isOfflineMode ? cachedDecision : null);
  const isUsingCache = !liveDecision && !!cachedDecision;
  const lastUpdatedTime = offlineStorage.getLastUpdated();

  // 1. Loading State (Only if no cached decision exists)
  if (isLoading && !activeDecision) {
    return (
      <div className="farmer-card border-l-4 border-l-emerald-600 bg-white p-6 space-y-4 animate-pulse">
        <div className="flex items-center justify-between">
          <div className="h-6 bg-slate-200 rounded w-40"></div>
          <div className="h-6 bg-slate-200 rounded w-20"></div>
        </div>
        <div className="p-4 bg-emerald-50/60 rounded-lg space-y-2">
          <div className="h-4 bg-emerald-200 rounded w-28"></div>
          <div className="h-6 bg-emerald-300/60 rounded w-full"></div>
        </div>
        <div className="p-4 bg-amber-50/60 rounded-lg space-y-2">
          <div className="h-4 bg-amber-200 rounded w-28"></div>
          <div className="h-6 bg-amber-300/60 rounded w-full"></div>
        </div>
        <div className="flex items-center justify-center gap-2 pt-2 text-slate-700 font-semibold text-xs sm:text-sm">
          <Loader2 className="w-4 h-4 animate-spin text-emerald-700" />
          <span>{t.loadingDecision}</span>
        </div>
      </div>
    );
  }

  // 2. Error State (When offline or API failed AND no cached decision exists)
  if ((isError || !activeDecision) && !cachedDecision) {
    return (
      <div className="farmer-card border-l-4 border-l-amber-500 bg-amber-50/50 p-5 space-y-3">
        <div className="flex items-start gap-3">
          <ShieldAlert className="w-6 h-6 text-amber-700 shrink-0 mt-0.5" />
          <div className="space-y-1">
            <h3 className="text-base font-bold text-slate-900">
              {t.errorDecisionTitle}
            </h3>
            <p className="text-xs sm:text-sm text-slate-700 font-medium leading-relaxed">
              {error?.message || t.errorDecisionDesc}
            </p>
          </div>
        </div>
        <div className="pt-2 flex justify-end">
          <button
            type="button"
            onClick={() => refetch()}
            disabled={isFetching}
            className="inline-flex items-center gap-1.5 px-4 py-2 rounded-lg bg-emerald-700 hover:bg-emerald-800 text-white font-bold text-xs shadow-xs transition-colors cursor-pointer min-h-[38px]"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${isFetching ? 'animate-spin' : ''}`} />
            <span>{t.retry}</span>
          </button>
        </div>
      </div>
    );
  }

  // 3. Resolve Vernacular Text (Backend translations are authoritative)
  const langTranslations = activeDecision?.translations?.[language];
  const primaryActionText = langTranslations?.primary_action || activeDecision?.primary_action || '';
  const criticalProhibitionText = langTranslations?.critical_prohibition || activeDecision?.critical_prohibition || '';
  const scientificRationaleText = langTranslations?.scientific_rationale || activeDecision?.scientific_rationale || '';

  return (
    <>
      <div className="farmer-card border-l-4 border-l-emerald-600 bg-white space-y-4 shadow-sm">
        {/* Offline Banner Indicator if using cached decision */}
        {isUsingCache && (
          <div className="p-2.5 rounded-lg bg-amber-50 border border-amber-300 flex items-center justify-between gap-2 text-xs font-bold text-amber-950">
            <div className="flex items-center gap-2">
              <WifiOff className="w-4 h-4 text-amber-700 shrink-0" />
              <span>{t.offlineBannerTitle} — {t.offlineBannerDesc}</span>
            </div>
            {lastUpdatedTime && (
              <span className="text-[11px] font-semibold text-amber-800 flex items-center gap-1 shrink-0">
                <Clock className="w-3 h-3" />
                {new Date(lastUpdatedTime).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
              </span>
            )}
          </div>
        )}

        {/* Header: Title, Date, Confidence & Voice Player */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 border-b border-slate-200">
          <div>
            <div className="flex items-center gap-2">
              <Sprout className="w-5 h-5 text-emerald-700 shrink-0" />
              <h3 className="text-lg font-bold text-slate-900 leading-tight">
                {t.todaysAdvice}
              </h3>
            </div>
            <p className="text-xs font-semibold text-slate-600 flex items-center gap-1.5 mt-0.5">
              <Calendar className="w-3.5 h-3.5 text-slate-500" />
              <span>{activeDecision?.date}</span>
              <span className="text-slate-300">•</span>
              <Database className="w-3.5 h-3.5 text-slate-500" />
              <span className="text-emerald-800 font-bold">{activeDecision?.confidence_indicator}</span>
            </p>
          </div>

          {/* Integrated One-Tap Voice Player (Works Offline with Cached Text) */}
          {activeDecision && <VoicePlayer decision={activeDecision} />}
        </div>

        {/* 1. Primary Action Section */}
        <div className="p-4 rounded-xl bg-emerald-50/90 border border-emerald-200/90 space-y-1.5 shadow-xs">
          <div className="flex items-center gap-1.5 text-xs font-bold text-emerald-900 uppercase tracking-wider">
            <Sprout className="w-4 h-4 text-emerald-700" />
            <span>{t.todaysAdvice}</span>
          </div>
          <p className="text-base sm:text-lg font-extrabold text-slate-900 leading-snug">
            {primaryActionText}
          </p>
        </div>

        {/* 2. Critical Prohibition Section (Red/Amber Alert) */}
        <div className="p-4 rounded-xl bg-amber-50/95 border-2 border-amber-400 space-y-1.5 shadow-xs">
          <div className="flex items-center gap-1.5 text-xs font-extrabold text-amber-950 uppercase tracking-wider">
            <AlertTriangle className="w-4.5 h-4.5 text-amber-700 stroke-[2.5]" />
            <span>{t.doNotDoThis}</span>
          </div>
          <p className="text-base sm:text-lg font-black text-amber-950 leading-snug tracking-wide">
            {criticalProhibitionText}
          </p>
        </div>

        {/* 3. Why This Advice? Section & Explainability Trigger */}
        <div className="p-3.5 rounded-xl bg-slate-50 border border-slate-200 space-y-2 text-slate-800">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-1.5 text-xs font-bold text-slate-900">
              <Info className="w-4 h-4 text-slate-700 shrink-0" />
              <span>{t.whyThisAdvice}</span>
            </div>

            <button
              type="button"
              onClick={() => setIsDrawerOpen(true)}
              className="inline-flex items-center gap-1 px-2.5 py-1 rounded-lg bg-emerald-100 hover:bg-emerald-200 text-emerald-900 text-xs font-bold transition-colors cursor-pointer border border-emerald-300 min-h-[32px]"
            >
              <span>{t.whyThisAdvice}</span>
              <ArrowUpRight className="w-3.5 h-3.5 text-emerald-800" />
            </button>
          </div>

          <p className="text-xs sm:text-sm font-medium text-slate-800 leading-relaxed pl-5">
            {scientificRationaleText}
          </p>
        </div>
      </div>

      {/* Real Explainability Drawer */}
      {activeDecision && (
        <ExplainabilityDrawer
          decisionId={activeDecision.explainability_id || activeDecision.decision_id}
          isOpen={isDrawerOpen}
          onClose={() => setIsDrawerOpen(false)}
        />
      )}
    </>
  );
};
