import React from 'react';
import { Sliders, CloudRain, Wind, HelpCircle } from 'lucide-react';
import { useLanguage } from '../contexts/LanguageContext';

export const WhatIfPlaceholder: React.FC = () => {
  const { t } = useLanguage();

  return (
    <div className="farmer-card space-y-4">
      <div className="flex items-center gap-2 pb-2 border-b border-slate-200">
        <Sliders className="w-5 h-5 text-emerald-700" />
        <h3 className="text-lg font-bold text-slate-900">
          {t.whatIf}
        </h3>
      </div>

      <p className="text-xs sm:text-sm text-slate-700 font-medium">
        {t.whatIfDesc}
      </p>

      {/* Simulated Controls Preview */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
        <div className="p-3 rounded-lg bg-slate-50 border border-slate-200 space-y-1.5">
          <div className="flex items-center justify-between text-xs font-semibold text-slate-700">
            <span className="flex items-center gap-1.5">
              <Wind className="w-4 h-4 text-emerald-700" />
              Wind Speed
            </span>
            <span className="font-bold text-slate-900">18.5 km/h</span>
          </div>
          <div className="h-2 w-full bg-slate-200 rounded-full overflow-hidden">
            <div className="h-full bg-emerald-600 rounded-full" style={{ width: '60%' }}></div>
          </div>
        </div>

        <div className="p-3 rounded-lg bg-slate-50 border border-slate-200 space-y-1.5">
          <div className="flex items-center justify-between text-xs font-semibold text-slate-700">
            <span className="flex items-center gap-1.5">
              <CloudRain className="w-4 h-4 text-blue-600" />
              Rain Next 36h
            </span>
            <span className="font-bold text-slate-900">28.0 mm</span>
          </div>
          <div className="h-2 w-full bg-slate-200 rounded-full overflow-hidden">
            <div className="h-full bg-blue-600 rounded-full" style={{ width: '75%' }}></div>
          </div>
        </div>
      </div>

      <div className="p-2.5 rounded-lg bg-blue-50/60 border border-blue-200 flex items-center gap-2 text-xs text-blue-900 font-medium">
        <HelpCircle className="w-4 h-4 text-blue-700 shrink-0" />
        <span>What-If simulation will connect directly to backend conflict arbitration engine in Phase 2.</span>
      </div>
    </div>
  );
};
