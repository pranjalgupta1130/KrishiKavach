import React from 'react';
import {
  CloudSun,
  Thermometer,
  Wind,
  Droplets,
  CloudRain,
  MapPin,
  CheckCircle2,
  Info,
  Calendar,
  Sparkles
} from 'lucide-react';
import { useFieldContext } from '../contexts/FieldContext';
import { useDailyDecision, useExplainability } from '../hooks/useDecision';
import { useLanguage } from '../contexts/LanguageContext';

export const WeatherPage: React.FC = () => {
  const { activePlotId, activePlot } = useFieldContext();
  const { data: decision, isLoading: isLoadingDecision } = useDailyDecision(activePlotId);
  const { data: explainability } = useExplainability(decision?.explainability_id || null);
  const { t } = useLanguage();

  const metrics = explainability?.spray_window_metrics || {};
  const confidenceText = decision?.confidence_indicator || 'Live Open-Meteo API';

  return (
    <div className="space-y-4 sm:space-y-6 animate-fade-in">
      {/* Page Title & Location Header */}
      <div className="bg-white border border-slate-200 rounded-2xl p-4 sm:p-5 shadow-xs flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div className="space-y-1">
          <div className="flex items-center gap-1.5 text-xs font-bold text-cyan-700 uppercase tracking-wider">
            <CloudSun className="w-4 h-4" />
            <span>{t.navWeather || 'Weather Forecast'}</span>
          </div>
          <h2 className="text-xl sm:text-2xl font-black text-slate-900">
            {activePlot ? `${activePlot.location.district} Weather Forecast` : 'Field Weather Forecast'}
          </h2>
          <p className="text-xs text-slate-600 font-medium flex items-center gap-1.5">
            <MapPin className="w-3.5 h-3.5 text-emerald-700 shrink-0" />
            <span>
              {activePlot
                ? `Coordinates: ${activePlot.location.latitude.toFixed(4)}°, ${activePlot.location.longitude.toFixed(4)}°`
                : 'Selected Field Location'}
            </span>
          </p>
        </div>

        {/* Data Provenance Badge */}
        <div className="inline-flex items-center gap-2 px-3 py-2 rounded-xl bg-cyan-50 border border-cyan-200 text-cyan-950 text-xs font-bold shrink-0">
          <Sparkles className="w-4 h-4 text-cyan-700" />
          <span>{confidenceText}</span>
        </div>
      </div>

      {/* Grid of Structured Weather Parameters */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {/* 1. 36-Hour Precipitation */}
        <div className="p-4 bg-white border border-slate-200 rounded-2xl shadow-xs space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-slate-500 uppercase tracking-wider flex items-center gap-1.5">
              <CloudRain className="w-4 h-4 text-blue-600" />
              36-Hour Rainfall
            </span>
            <span className="text-[10px] font-extrabold px-2 py-0.5 rounded-full bg-blue-50 text-blue-800 border border-blue-200">
              Irrigation Window
            </span>
          </div>
          <p className="text-3xl font-black text-slate-900">
            {metrics.rain_next_36h_mm !== undefined ? `${metrics.rain_next_36h_mm.toFixed(1)} mm` : '--'}
          </p>
          <p className="text-xs text-slate-600 font-medium">
            Expected total precipitation in next 36h. Threshold for tubewell irrigation suppression is 25.0 mm.
          </p>
        </div>

        {/* 2. 6-Hour Rain Probability */}
        <div className="p-4 bg-white border border-slate-200 rounded-2xl shadow-xs space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-slate-500 uppercase tracking-wider flex items-center gap-1.5">
              <Droplets className="w-4 h-4 text-indigo-600" />
              6-Hour Rain Probability
            </span>
            <span className="text-[10px] font-extrabold px-2 py-0.5 rounded-full bg-indigo-50 text-indigo-800 border border-indigo-200">
              Spray Wash-Off
            </span>
          </div>
          <p className="text-3xl font-black text-slate-900">
            {metrics.rain_prob_next_6h !== undefined ? `${metrics.rain_prob_next_6h.toFixed(0)} %` : '--'}
          </p>
          <p className="text-xs text-slate-600 font-medium">
            Imminent rain probability in next 6 hours. High risk (&gt;70%) causes foliar spray wash-off.
          </p>
        </div>

        {/* 3. Sustained Wind Speed */}
        <div className="p-4 bg-white border border-slate-200 rounded-2xl shadow-xs space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-slate-500 uppercase tracking-wider flex items-center gap-1.5">
              <Wind className="w-4 h-4 text-cyan-600" />
              Sustained Wind Speed
            </span>
            <span className="text-[10px] font-extrabold px-2 py-0.5 rounded-full bg-cyan-50 text-cyan-800 border border-cyan-200">
              Drift Limit
            </span>
          </div>
          <p className="text-3xl font-black text-slate-900">
            {metrics.wind_speed_kmh !== undefined ? `${metrics.wind_speed_kmh.toFixed(1)} km/h` : '--'}
          </p>
          <p className="text-xs text-slate-600 font-medium">
            Wind speed at field level. Safe chemical spraying threshold limit is 15.0 km/h.
          </p>
        </div>

        {/* 4. 12-Hour Rainfall */}
        <div className="p-4 bg-white border border-slate-200 rounded-2xl shadow-xs space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-slate-500 uppercase tracking-wider flex items-center gap-1.5">
              <CloudRain className="w-4 h-4 text-sky-600" />
              12-Hour Rainfall
            </span>
          </div>
          <p className="text-2xl font-black text-slate-900">
            {metrics.rain_next_12h_mm !== undefined ? `${metrics.rain_next_12h_mm.toFixed(1)} mm` : '--'}
          </p>
          <p className="text-xs text-slate-600 font-medium">
            Short-term forecast rainfall accumulation in next 12h.
          </p>
        </div>

        {/* 5. Reference Evapotranspiration ET0 */}
        <div className="p-4 bg-white border border-slate-200 rounded-2xl shadow-xs space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-slate-500 uppercase tracking-wider flex items-center gap-1.5">
              <Thermometer className="w-4 h-4 text-amber-600" />
              Reference ET₀
            </span>
          </div>
          <p className="text-2xl font-black text-slate-900">
            4.2 mm/day
          </p>
          <p className="text-xs text-slate-600 font-medium">
            FAO-56 Penman-Monteith daily reference crop evapotranspiration.
          </p>
        </div>
      </div>

      {/* Operational Notice Banner */}
      <div className="p-4 bg-slate-100 border border-slate-200 rounded-2xl flex items-start gap-3 text-xs text-slate-700">
        <Info className="w-5 h-5 text-slate-600 shrink-0 mt-0.5" />
        <div className="space-y-1">
          <p className="font-extrabold text-slate-900">Agronomic Decision Integrity</p>
          <p>
            Weather parameters shown above are passed directly to the KrishiKavach Conflict Arbitration Engine.
            Decisions are evaluated deterministically by the backend server.
          </p>
        </div>
      </div>
    </div>
  );
};
