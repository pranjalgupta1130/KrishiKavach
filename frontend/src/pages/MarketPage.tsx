import React from 'react';
import {
  TrendingUp,
  Store,
  MapPin,
  Sparkles,
  Info,
  DollarSign,
  ArrowUpRight,
  ArrowDownRight
} from 'lucide-react';
import { useFieldContext } from '../contexts/FieldContext';
import { useDailyDecision, useExplainability } from '../hooks/useDecision';
import { useLanguage } from '../contexts/LanguageContext';
import { TrendChartsSection } from '../components/TrendChartsSection';

export const MarketPage: React.FC = () => {
  const { activePlotId, activePlot } = useFieldContext();
  const { data: decision } = useDailyDecision(activePlotId);
  const { data: explainability } = useExplainability(decision?.explainability_id || null);
  const { t } = useLanguage();

  const marketMetrics = explainability?.market_metrics || {};
  const modalPrice = marketMetrics.modal_price_inr || 7150;
  const sma7 = marketMetrics.sma_7_inr || 6980;
  const momentumPct = marketMetrics.price_momentum_percent || 2.43;
  const isPositive = momentumPct >= 0;
  const cropLabel = activePlot?.crop_type === 'bt_cotton' ? 'Bt Cotton' : activePlot?.crop_type === 'soybean' ? 'Soybean' : activePlot?.crop_type || 'Crop';
  const mandiName = activePlot ? `${activePlot.location.district} APMC` : 'Local APMC Mandi';

  return (
    <div className="space-y-4 sm:space-y-6 animate-fade-in">
      {/* Title Header */}
      <div className="bg-white border border-slate-200 rounded-2xl p-4 sm:p-5 shadow-xs flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div className="space-y-1">
          <div className="flex items-center gap-1.5 text-xs font-bold text-emerald-800 uppercase tracking-wider">
            <TrendingUp className="w-4 h-4 text-emerald-700" />
            <span>{t.navMarket || 'APMC Mandi Market Intelligence'}</span>
          </div>
          <h2 className="text-xl sm:text-2xl font-black text-slate-900">
            {cropLabel} Market Trends — {mandiName}
          </h2>
          <p className="text-xs text-slate-600 font-medium flex items-center gap-1.5">
            <MapPin className="w-3.5 h-3.5 text-emerald-700 shrink-0" />
            <span>Market Context for {activePlot?.farmer_name}'s Plot ({activePlot?.location.district})</span>
          </p>
        </div>

        <div className="inline-flex items-center gap-2 px-3 py-2 rounded-xl bg-emerald-50 border border-emerald-200 text-emerald-950 text-xs font-bold shrink-0">
          <Store className="w-4 h-4 text-emerald-700" />
          <span>Agmarknet API</span>
        </div>
      </div>

      {/* Key Market Indicators Strip */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        {/* Current Modal Price */}
        <div className="p-4 bg-white border border-slate-200 rounded-2xl shadow-xs space-y-1">
          <span className="text-xs font-bold text-slate-500 uppercase tracking-wider block">
            Current Mandi Modal Price
          </span>
          <p className="text-3xl font-black text-slate-900">
            ₹{modalPrice.toLocaleString('en-IN')} <span className="text-xs font-bold text-slate-500">/ quintal</span>
          </p>
          <p className="text-xs text-slate-600 font-medium">
            Modal rate at {mandiName}
          </p>
        </div>

        {/* 7-Day Moving Average */}
        <div className="p-4 bg-white border border-slate-200 rounded-2xl shadow-xs space-y-1">
          <span className="text-xs font-bold text-slate-500 uppercase tracking-wider block">
            7-Day Moving Average
          </span>
          <p className="text-3xl font-black text-slate-900">
            ₹{sma7.toLocaleString('en-IN')} <span className="text-xs font-bold text-slate-500">/ quintal</span>
          </p>
          <p className="text-xs text-slate-600 font-medium">
            7-day baseline price trend
          </p>
        </div>

        {/* Price Momentum */}
        <div className="p-4 bg-white border border-slate-200 rounded-2xl shadow-xs space-y-1">
          <span className="text-xs font-bold text-slate-500 uppercase tracking-wider block">
            Price Momentum
          </span>
          <div className="flex items-center gap-2">
            <p className={`text-3xl font-black ${isPositive ? 'text-emerald-700' : 'text-rose-700'}`}>
              {isPositive ? `+${momentumPct.toFixed(2)}%` : `${momentumPct.toFixed(2)}%`}
            </p>
            {isPositive ? (
              <ArrowUpRight className="w-6 h-6 text-emerald-700" />
            ) : (
              <ArrowDownRight className="w-6 h-6 text-rose-700" />
            )}
          </div>
          <p className="text-xs text-slate-600 font-medium">
            {isPositive ? 'Favorable market price momentum' : 'Market price below 7-day average'}
          </p>
        </div>
      </div>

      {/* Recharts Visualization Section */}
      <TrendChartsSection decisionId={decision?.explainability_id || decision?.decision_id || null} />

      {/* Market Safety Policy Notice */}
      <div className="p-4 bg-slate-100 border border-slate-200 rounded-2xl flex items-start gap-3 text-xs text-slate-700">
        <Info className="w-5 h-5 text-slate-600 shrink-0 mt-0.5" />
        <div className="space-y-1">
          <p className="font-extrabold text-slate-900">Market Signal Priority Rule</p>
          <p>
            Market price signals provide secondary financial context to farmers. In KrishiKavach, market signals
            <strong> NEVER override agronomic or biochemical safety constraints</strong>.
          </p>
        </div>
      </div>
    </div>
  );
};
