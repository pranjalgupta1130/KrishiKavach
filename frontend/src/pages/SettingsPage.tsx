import React from 'react';
import {
  Settings as SettingsIcon,
  Globe,
  MapPin,
  ShieldCheck,
  Smartphone,
  Layers,
  Database,
  CheckCircle2,
  Sparkles
} from 'lucide-react';
import { useLanguage } from '../contexts/LanguageContext';
import { useFieldContext } from '../contexts/FieldContext';
import { Language } from '../types/language';
import { OfflineBadge } from '../components/OfflineBadge';

export const SettingsPage: React.FC = () => {
  const { language, setLanguage, t } = useLanguage();
  const { activePlot, activePlotId } = useFieldContext();

  const languages: { code: Language; label: string; name: string }[] = [
    { code: 'en', label: 'EN', name: 'English' },
    { code: 'mr', label: 'मराठी', name: 'मराठी (Marathi)' },
    { code: 'hi', label: 'हिंदी', name: 'हिंदी (Hindi)' },
  ];

  return (
    <div className="space-y-4 sm:space-y-6 animate-fade-in">
      {/* Title Header */}
      <div className="bg-white border border-slate-200 rounded-2xl p-4 sm:p-5 shadow-xs flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div className="space-y-1">
          <div className="flex items-center gap-1.5 text-xs font-bold text-slate-700 uppercase tracking-wider">
            <SettingsIcon className="w-4 h-4 text-slate-600" />
            <span>{t.navSettings || 'Settings & Application Configuration'}</span>
          </div>
          <h2 className="text-xl sm:text-2xl font-black text-slate-900">
            Platform Settings
          </h2>
          <p className="text-xs text-slate-600 font-medium">
            Language preferences, field parameters, and scientific model provenance.
          </p>
        </div>

        <div className="inline-flex items-center gap-2 px-3 py-2 rounded-xl bg-slate-100 border border-slate-200 text-slate-900 text-xs font-bold shrink-0">
          <ShieldCheck className="w-4 h-4 text-emerald-700" />
          <span>SU HACKS 2026</span>
        </div>
      </div>

      {/* 1. Language Preferences Card */}
      <div className="bg-white border border-slate-200 rounded-2xl p-5 shadow-xs space-y-3">
        <h3 className="text-sm font-extrabold text-slate-900 flex items-center gap-2">
          <Globe className="w-4 h-4 text-emerald-700" />
          <span>Language Preference</span>
        </h3>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
          {languages.map((lang) => (
            <button
              key={lang.code}
              onClick={() => setLanguage(lang.code)}
              className={`p-3.5 rounded-xl border text-left transition-all cursor-pointer flex items-center justify-between ${
                language === lang.code
                  ? 'border-emerald-600 bg-emerald-50/80 ring-2 ring-emerald-600/30'
                  : 'border-slate-200 bg-white hover:bg-slate-50'
              }`}
            >
              <div>
                <p className="text-sm font-bold text-slate-900">{lang.name}</p>
                <p className="text-[10px] font-semibold text-slate-500 uppercase">{lang.code}</p>
              </div>
              {language === lang.code && (
                <CheckCircle2 className="w-5 h-5 text-emerald-700" />
              )}
            </button>
          ))}
        </div>
      </div>

      {/* 2. Active Field Summary Card */}
      <div className="bg-white border border-slate-200 rounded-2xl p-5 shadow-xs space-y-3">
        <h3 className="text-sm font-extrabold text-slate-900 flex items-center gap-2">
          <MapPin className="w-4 h-4 text-emerald-700" />
          <span>Active Field Overview</span>
        </h3>
        {activePlot ? (
          <div className="p-3 bg-slate-50 rounded-xl border border-slate-200/80 grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs">
            <div>
              <span className="text-[10px] font-bold text-slate-500 uppercase block">Farmer</span>
              <span className="font-extrabold text-slate-900">{activePlot.farmer_name}</span>
            </div>
            <div>
              <span className="text-[10px] font-bold text-slate-500 uppercase block">District</span>
              <span className="font-bold text-slate-800">{activePlot.location.district}</span>
            </div>
            <div>
              <span className="text-[10px] font-bold text-slate-500 uppercase block">Coordinates</span>
              <span className="font-mono text-[11px] font-semibold text-slate-700">
                {activePlot.location.latitude.toFixed(2)}°, {activePlot.location.longitude.toFixed(2)}°
              </span>
            </div>
            <div>
              <span className="text-[10px] font-bold text-slate-500 uppercase block">Plot ID</span>
              <span className="font-mono text-[11px] text-slate-600">{activePlot.plot_id}</span>
            </div>
          </div>
        ) : (
          <p className="text-xs text-slate-500">Active plot ID: {activePlotId}</p>
        )}
      </div>

      {/* 3. System & Scientific Provenance */}
      <div className="bg-white border border-slate-200 rounded-2xl p-5 shadow-xs space-y-3">
        <h3 className="text-sm font-extrabold text-slate-900 flex items-center gap-2">
          <Database className="w-4 h-4 text-purple-700" />
          <span>Scientific Models & System Provenance</span>
        </h3>
        <div className="space-y-2 text-xs text-slate-700 font-medium">
          <div className="flex items-center justify-between p-2.5 bg-slate-50 rounded-xl border border-slate-200">
            <span>Conflict Arbitration Engine</span>
            <span className="font-mono font-bold text-purple-900">Arbitration-Engine-v2.0</span>
          </div>
          <div className="flex items-center justify-between p-2.5 bg-slate-50 rounded-xl border border-slate-200">
            <span>Soil Water Balance Model</span>
            <span className="font-mono font-bold text-emerald-900">FAO-56-v1.0 (Vertisol)</span>
          </div>
          <div className="flex items-center justify-between p-2.5 bg-slate-50 rounded-xl border border-slate-200">
            <span>Pest Phenology Model</span>
            <span className="font-mono font-bold text-rose-900">Thermal-GDD-v1.0</span>
          </div>
          <div className="flex items-center justify-between p-2.5 bg-slate-50 rounded-xl border border-slate-200">
            <span>SU HACKS Team</span>
            <span className="font-bold text-slate-900">Team SH-039 (Member 1 + Member 2)</span>
          </div>
        </div>
      </div>
    </div>
  );
};
