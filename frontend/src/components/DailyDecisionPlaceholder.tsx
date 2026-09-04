import React from 'react';
import { Sprout, AlertTriangle, Volume2, Info } from 'lucide-react';
import { useLanguage } from '../contexts/LanguageContext';

export const DailyDecisionPlaceholder: React.FC = () => {
  const { t } = useLanguage();

  return (
    <div className="farmer-card border-l-4 border-l-emerald-600 space-y-4">
      {/* Header with Title and Audio Button */}
      <div className="flex items-center justify-between gap-2 pb-2 border-b border-slate-200">
        <div className="flex items-center gap-2">
          <Sprout className="w-5 h-5 text-emerald-700" />
          <h3 className="text-lg font-bold text-slate-900">
            {t.todaysAdvice}
          </h3>
        </div>
        <button
          type="button"
          className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-emerald-100 hover:bg-emerald-200 text-emerald-900 text-xs font-bold transition-colors cursor-pointer border border-emerald-300 min-h-[40px]"
          aria-label="Listen to advice audio"
        >
          <Volume2 className="w-4 h-4 text-emerald-800" />
          <span>Audio</span>
        </button>
      </div>

      {/* Primary Action Card Placeholder */}
      <div className="p-3.5 sm:p-4 rounded-lg bg-emerald-50/80 border border-emerald-200 space-y-1">
        <div className="flex items-center gap-1.5 text-xs font-bold text-emerald-900 uppercase tracking-wider">
          <Sprout className="w-4 h-4 text-emerald-700" />
          <span>{t.todaysAdvice}</span>
        </div>
        <p className="text-base sm:text-lg font-bold text-slate-900 leading-snug">
          Clear field drainage trenches immediately and deploy biological pheromone traps
        </p>
      </div>

      {/* Critical Prohibition Card Placeholder */}
      <div className="p-3.5 sm:p-4 rounded-lg bg-amber-50/90 border border-amber-300 space-y-1">
        <div className="flex items-center gap-1.5 text-xs font-bold text-amber-900 uppercase tracking-wider">
          <AlertTriangle className="w-4 h-4 text-amber-700" />
          <span>{t.doNotDoThis}</span>
        </div>
        <p className="text-base sm:text-lg font-bold text-amber-950 leading-snug">
          DO NOT IRRIGATE OR APPLY CHEMICAL SPRAYS TODAY
        </p>
      </div>

      {/* Scientific Rationale / Why Wording */}
      <div className="p-3 rounded-lg bg-slate-50 border border-slate-200 flex gap-2.5 text-slate-800">
        <Info className="w-5 h-5 text-slate-600 shrink-0 mt-0.5" />
        <div className="text-xs sm:text-sm font-medium leading-relaxed">
          <p className="font-bold text-slate-900 mb-0.5">{t.whyThisAdvice}</p>
          Soil depletion has reached 48.0mm (RAW limit: 45.0mm), but heavy rain (28.0mm) is expected within 36 hours. Wind speed is 18.5 km/h (safe limit: 15.0 km/h).
        </div>
      </div>
    </div>
  );
};
