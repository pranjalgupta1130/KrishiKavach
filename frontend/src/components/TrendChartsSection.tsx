import React from 'react';
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, ReferenceLine, Cell } from 'recharts';
import { TrendingUp, Droplets, Bug, Info } from 'lucide-react';
import { useLanguage } from '../contexts/LanguageContext';
import { useExplainability } from '../hooks/useDecision';

interface TrendChartsSectionProps {
  decisionId: string | null;
}

export const TrendChartsSection: React.FC<TrendChartsSectionProps> = ({ decisionId }) => {
  const { t } = useLanguage();
  const { data: explainability } = useExplainability(decisionId);

  if (!explainability) {
    return null;
  }

  // 1. Soil Data
  const soilDepletion = explainability.soil_metrics?.depletion_mm || 48.0;
  const rawLimit = explainability.soil_metrics?.raw_mm || 45.0;
  const tawCapacity = explainability.soil_metrics?.taw_mm || 70.0;

  const soilChartData = [
    { name: 'Depletion', value: soilDepletion, limit: rawLimit },
    { name: 'RAW Limit', value: rawLimit, limit: rawLimit },
    { name: 'TAW Capacity', value: tawCapacity, limit: rawLimit },
  ];

  // 2. Pest GDD Data
  const accumulatedGdd = explainability.pest_metrics?.accumulated_gdd || 462.0;
  const gddThreshold = explainability.pest_metrics?.gdd_threshold || 450.0;

  const pestChartData = [
    { name: 'Accumulated GDD', gdd: accumulatedGdd },
    { name: 'Emergence Threshold', gdd: gddThreshold },
  ];

  // 3. Market Data
  const modalPrice = explainability.market_metrics?.modal_price_inr || 7450.0;
  const sma7Price = explainability.market_metrics?.sma_7_inr || 7200.0;

  const marketChartData = [
    { name: 'Daily Price', price: modalPrice },
    { name: '7-Day SMA', price: sma7Price },
  ];

  return (
    <div className="farmer-card bg-white space-y-5 border border-slate-200 shadow-sm">
      {/* Section Header */}
      <div className="flex items-center gap-2 pb-3 border-b border-slate-200">
        <div className="w-8 h-8 rounded-lg bg-emerald-100 text-emerald-800 flex items-center justify-center font-bold">
          <TrendingUp className="w-4 h-4 text-emerald-700" />
        </div>
        <div>
          <h3 className="text-lg font-bold text-slate-900 leading-tight">
            {t.trendsTitle}
          </h3>
          <p className="text-xs text-slate-600 font-medium">
            {t.trendsSubtitle}
          </p>
        </div>
      </div>

      {/* Grid of Farmer Charts */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {/* Chart 1: Soil Water Depletion */}
        <div className="p-3.5 rounded-xl bg-slate-50 border border-slate-200 space-y-2">
          <div className="flex items-center justify-between">
            <h4 className="text-xs font-bold text-slate-900 flex items-center gap-1">
              <Droplets className="w-3.5 h-3.5 text-emerald-700" />
              {t.soilChartTitle}
            </h4>
            <span className="text-[10px] bg-amber-100 text-amber-900 font-bold px-1.5 py-0.5 rounded">
              RAW: {rawLimit} mm
            </span>
          </div>
          <p className="text-[11px] text-slate-600 font-medium">{t.soilChartSubtitle}</p>
          
          <div className="h-44 w-full pt-1">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={soilChartData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <XAxis dataKey="name" tick={{ fontSize: 10, fontWeight: 700 }} />
                <YAxis tick={{ fontSize: 10 }} />
                <Tooltip formatter={(value: number) => [`${value} mm`, 'Water']} />
                <ReferenceLine y={rawLimit} stroke="#d97706" strokeDasharray="3 3" label={{ value: 'RAW Limit', fill: '#b45309', fontSize: 10 }} />
                <Bar dataKey="value" radius={[4, 4, 0, 0]}>
                  <Cell fill={soilDepletion >= rawLimit ? '#d97706' : '#059669'} />
                  <Cell fill="#64748b" />
                  <Cell fill="#94a3b8" />
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Chart 2: Pest Risk GDD */}
        <div className="p-3.5 rounded-xl bg-slate-50 border border-slate-200 space-y-2">
          <div className="flex items-center justify-between">
            <h4 className="text-xs font-bold text-slate-900 flex items-center gap-1">
              <Bug className="w-3.5 h-3.5 text-amber-700" />
              {t.pestChartTitle}
            </h4>
            <span className="text-[10px] bg-red-100 text-red-900 font-bold px-1.5 py-0.5 rounded">
              Limit: {gddThreshold} GDD
            </span>
          </div>
          <p className="text-[11px] text-slate-600 font-medium">{t.pestChartSubtitle}</p>
          
          <div className="h-44 w-full pt-1">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={pestChartData} margin={{ top: 10, right: 10, left: -10, bottom: 0 }}>
                <XAxis dataKey="name" tick={{ fontSize: 10, fontWeight: 700 }} />
                <YAxis tick={{ fontSize: 10 }} />
                <Tooltip formatter={(value: number) => [`${value} GDD`, 'Heat Units']} />
                <ReferenceLine y={gddThreshold} stroke="#dc2626" strokeDasharray="3 3" label={{ value: 'Emergence', fill: '#dc2626', fontSize: 10 }} />
                <Bar dataKey="gdd" radius={[4, 4, 0, 0]}>
                  <Cell fill={accumulatedGdd >= gddThreshold ? '#dc2626' : '#059669'} />
                  <Cell fill="#64748b" />
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Chart 3: Mandi Price Momentum */}
        <div className="p-3.5 rounded-xl bg-slate-50 border border-slate-200 space-y-2">
          <div className="flex items-center justify-between">
            <h4 className="text-xs font-bold text-slate-900 flex items-center gap-1">
              <TrendingUp className="w-3.5 h-3.5 text-emerald-700" />
              {t.marketChartTitle}
            </h4>
            <span className="text-[10px] bg-emerald-100 text-emerald-900 font-bold px-1.5 py-0.5 rounded">
              ₹{modalPrice} / q
            </span>
          </div>
          <p className="text-[11px] text-slate-600 font-medium">{t.marketChartSubtitle}</p>
          
          <div className="h-44 w-full pt-1">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={marketChartData} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
                <XAxis dataKey="name" tick={{ fontSize: 10, fontWeight: 700 }} />
                <YAxis tick={{ fontSize: 10 }} domain={['dataMin - 500', 'dataMax + 500']} />
                <Tooltip formatter={(value: number) => [`₹${value} / q`, 'Price']} />
                <Bar dataKey="price" radius={[4, 4, 0, 0]}>
                  <Cell fill="#059669" />
                  <Cell fill="#64748b" />
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Real Data Notice */}
      <div className="p-2.5 rounded-lg bg-slate-50 border border-slate-200 flex items-center gap-2 text-xs text-slate-600 font-medium">
        <Info className="w-4 h-4 text-slate-500 shrink-0" />
        <span>{t.historicalNotice}</span>
      </div>
    </div>
  );
};
