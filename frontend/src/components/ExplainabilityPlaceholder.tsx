import React from 'react';
import { FileText, Droplets, Bug, Wind, ArrowUpRight } from 'lucide-react';
import { useLanguage } from '../contexts/LanguageContext';

export const ExplainabilityPlaceholder: React.FC = () => {
  const { t } = useLanguage();

  return (
    <div className="farmer-card space-y-4">
      <div className="flex items-center gap-2 pb-2 border-b border-slate-200">
        <FileText className="w-5 h-5 text-emerald-700" />
        <h3 className="text-lg font-bold text-slate-900">
          {t.whyThisAdvice}
        </h3>
      </div>

      <p className="text-xs sm:text-sm text-slate-700 font-medium">
        {t.whyDesc}
      </p>

      {/* Metric Breakdown Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
        {/* Soil Moisture Depletion Metric */}
        <div className="p-3 rounded-lg bg-emerald-50/50 border border-emerald-200 space-y-1">
          <div className="flex items-center justify-between text-xs font-semibold text-emerald-900">
            <span className="flex items-center gap-1">
              <Droplets className="w-3.5 h-3.5 text-emerald-700" />
              Soil Depletion
            </span>
            <span className="px-1.5 py-0.5 rounded bg-emerald-200 text-emerald-900 font-bold text-[10px]">Stress</span>
          </div>
          <p className="text-base font-bold text-slate-900">48.0 mm</p>
          <p className="text-[11px] font-medium text-slate-600">RAW Limit: 45.0 mm</p>
        </div>

        {/* Pest GDD Metric */}
        <div className="p-3 rounded-lg bg-amber-50/50 border border-amber-200 space-y-1">
          <div className="flex items-center justify-between text-xs font-semibold text-amber-900">
            <span className="flex items-center gap-1">
              <Bug className="w-3.5 h-3.5 text-amber-700" />
              Pink Bollworm
            </span>
            <span className="px-1.5 py-0.5 rounded bg-amber-200 text-amber-900 font-bold text-[10px]">Risk</span>
          </div>
          <p className="text-base font-bold text-slate-900">462 GDD</p>
          <p className="text-[11px] font-medium text-slate-600">Threshold: 450 GDD</p>
        </div>

        {/* Spray Wind Limit Metric */}
        <div className="p-3 rounded-lg bg-slate-50 border border-slate-200 space-y-1">
          <div className="flex items-center justify-between text-xs font-semibold text-slate-900">
            <span className="flex items-center gap-1">
              <Wind className="w-3.5 h-3.5 text-slate-700" />
              Wind Speed
            </span>
            <span className="px-1.5 py-0.5 rounded bg-red-100 text-red-800 font-bold text-[10px]">Unsafe</span>
          </div>
          <p className="text-base font-bold text-slate-900">18.5 km/h</p>
          <p className="text-[11px] font-medium text-slate-600">Safe Limit: 15.0 km/h</p>
        </div>
      </div>

      <div className="flex justify-end pt-1">
        <span className="inline-flex items-center gap-1 text-xs font-bold text-emerald-800 hover:text-emerald-950 cursor-pointer">
          Detailed Arbitration Traces <ArrowUpRight className="w-3.5 h-3.5" />
        </span>
      </div>
    </div>
  );
};
