import React from 'react';
import {
  Bug,
  AlertTriangle,
  CheckCircle2,
  ShieldCheck,
  Search,
  Loader2,
  AlertCircle,
  Calendar,
  Layers
} from 'lucide-react';
import { useFieldContext } from '../contexts/FieldContext';
import { useCropHealth } from '../hooks/useDecision';
import { useLanguage } from '../contexts/LanguageContext';

export const CropHealthPage: React.FC = () => {
  const { activePlotId, activePlot } = useFieldContext();
  const { data: health, isLoading, isError, error } = useCropHealth(activePlotId);
  const { t } = useLanguage();

  const accumulatedGdd = health?.accumulated_gdd ?? 0;
  const gddThreshold = health?.threshold_gdd ?? 450;
  const isRiskTriggered = health?.pest_risk_high ?? false;
  const pestPercent = Math.min(100, Math.round((accumulatedGdd / (gddThreshold || 1)) * 100));

  return (
    <div className="space-y-4 sm:space-y-6 animate-fade-in">
      {/* Page Title Header */}
      <div className="bg-white border border-slate-200 rounded-2xl p-4 sm:p-5 shadow-xs flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div className="space-y-1">
          <div className="flex items-center gap-1.5 text-xs font-bold text-rose-700 uppercase tracking-wider">
            <Bug className="w-4 h-4" />
            <span>{t.navCropHealth || 'Crop Health & Pest Phenology'}</span>
          </div>
          <h2 className="text-xl sm:text-2xl font-black text-slate-900">
            {activePlot ? `${activePlot.farmer_name}'s ${health?.crop || (activePlot.crop_type === 'bt_cotton' ? 'Bt Cotton' : activePlot.crop_type)} Health` : 'Crop Phenology & Pest Status'}
          </h2>
          <p className="text-xs text-slate-600 font-medium">
            Thermal degree-day emergence tracking and biological pest lifecycle risk.
          </p>
        </div>

        {/* Model Provenance Badge */}
        <div className="inline-flex items-center gap-2 px-3 py-2 rounded-xl bg-rose-50 border border-rose-200 text-rose-950 text-xs font-bold shrink-0">
          <ShieldCheck className="w-4 h-4 text-rose-700" />
          <span>{health?.model_version || 'Thermal-GDD-v1.0'}</span>
        </div>
      </div>

      {/* Loading State */}
      {isLoading && (
        <div className="p-8 text-center bg-white border border-slate-200 rounded-2xl space-y-3">
          <Loader2 className="w-8 h-8 text-rose-700 animate-spin mx-auto" />
          <p className="text-xs font-bold text-slate-700">Computing crop phenology & pest emergence GDD...</p>
        </div>
      )}

      {/* Error State */}
      {isError && (
        <div className="p-4 bg-red-50 border border-red-200 rounded-2xl flex items-center gap-3 text-xs font-bold text-red-900">
          <AlertCircle className="w-5 h-5 text-red-700 shrink-0" />
          <span>{error?.message || 'Could not load crop health data.'}</span>
        </div>
      )}

      {/* Dynamic Crop Health Overview */}
      {!isLoading && !isError && health && (
        <>
          {/* Metadata Strip */}
          <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
            <div className="p-3 bg-white border border-slate-200 rounded-xl shadow-2xs space-y-0.5">
              <span className="text-[10px] font-extrabold uppercase text-slate-500 flex items-center gap-1">
                <Calendar className="w-3 h-3 text-rose-600" />
                Days After Sowing
              </span>
              <p className="text-xl font-black text-slate-900">{health.days_after_sowing} Days</p>
            </div>

            <div className="p-3 bg-white border border-slate-200 rounded-xl shadow-2xs space-y-0.5">
              <span className="text-[10px] font-extrabold uppercase text-slate-500 flex items-center gap-1">
                <Layers className="w-3 h-3 text-emerald-600" />
                Growth Stage
              </span>
              <p className="text-sm font-black text-slate-900 truncate">{health.crop_stage}</p>
            </div>

            <div className="p-3 bg-white border border-slate-200 rounded-xl shadow-2xs space-y-0.5 col-span-2 sm:col-span-1">
              <span className="text-[10px] font-extrabold uppercase text-slate-500 flex items-center gap-1">
                <Bug className="w-3 h-3 text-rose-600" />
                Target Pest Species
              </span>
              <p className="text-sm font-black text-slate-900 truncate">{health.pest}</p>
            </div>
          </div>

          {/* Primary Pest Risk Overview Card */}
          <div className={`p-5 rounded-2xl border-2 shadow-xs space-y-4 ${
            isRiskTriggered ? 'bg-rose-50/70 border-rose-400' : 'bg-emerald-50/70 border-emerald-300'
          }`}>
            <div className="flex items-start justify-between gap-3">
              <div className="space-y-1">
                <div className="flex items-center gap-2">
                  <span className={`inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-black ${
                    isRiskTriggered ? 'bg-rose-600 text-white' : 'bg-emerald-700 text-white'
                  }`}>
                    {isRiskTriggered ? <AlertTriangle className="w-3.5 h-3.5" /> : <CheckCircle2 className="w-3.5 h-3.5" />}
                    <span>{isRiskTriggered ? 'PEST EMERGENCE RISK HIGH' : 'PEST RISK NOMINAL'}</span>
                  </span>
                </div>
                <h3 className="text-lg font-black text-slate-900 pt-1">
                  Target Pest: {health.pest}
                </h3>
                <p className="text-xs text-slate-700 font-semibold">
                  Current Crop Stage: <span className="font-extrabold text-slate-900 uppercase">{health.crop_stage}</span>
                </p>
              </div>
            </div>

            {/* GDD Gauge & Meter */}
            <div className="space-y-2 pt-1">
              <div className="flex items-center justify-between text-xs font-bold">
                <span className="text-slate-700">Cumulative Heat Units (GDD)</span>
                <span className="text-slate-900 font-extrabold">{accumulatedGdd.toFixed(0)} / {gddThreshold.toFixed(0)} GDD ({pestPercent}%)</span>
              </div>
              <div className="w-full bg-slate-200 h-3 rounded-full overflow-hidden">
                <div
                  className={`h-full transition-all duration-500 rounded-full ${
                    isRiskTriggered ? 'bg-rose-600' : 'bg-emerald-600'
                  }`}
                  style={{ width: `${pestPercent}%` }}
                />
              </div>
            </div>
          </div>
        </>
      )}

      {/* Field Scouting Protocol Card */}
      <div className="p-4 sm:p-5 bg-white border border-slate-200 rounded-2xl shadow-xs space-y-3">
        <h3 className="text-sm font-extrabold text-slate-900 flex items-center gap-2">
          <Search className="w-4 h-4 text-emerald-700" />
          <span>Recommended Field Scouting Protocol</span>
        </h3>
        <ul className="text-xs text-slate-700 space-y-2 list-disc list-inside font-medium">
          <li>Inspect 20 randomly selected plant organs / green bolls per acre for entry holes or chlorosis.</li>
          <li>Deploy biological pheromone traps (5 traps per hectare) at crop canopy height for pest monitoring.</li>
          <li>Observe wind conditions before executing any foliar spray; sustained wind &gt;15 km/h causes off-target drift.</li>
        </ul>
      </div>

      {/* Provenance & Models Info */}
      <div className="p-4 bg-slate-100 border border-slate-200 rounded-2xl flex items-center justify-between text-xs text-slate-700">
        <span className="font-bold">Authoritative Models Used:</span>
        <span className="font-mono text-[11px] text-slate-900 font-bold">{health?.provenance || 'Member 1 Thermal GDD + Member 2 Engine'}</span>
      </div>
    </div>
  );
};
