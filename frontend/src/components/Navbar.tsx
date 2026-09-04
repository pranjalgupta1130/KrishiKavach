import React from 'react';
import { ShieldCheck, Globe } from 'lucide-react';
import { useLanguage } from '../contexts/LanguageContext';
import { Language } from '../types/language';
import { OfflineBadge } from './OfflineBadge';

export const Navbar: React.FC = () => {
  const { language, setLanguage, t } = useLanguage();

  const languages: { code: Language; label: string }[] = [
    { code: 'en', label: 'EN' },
    { code: 'mr', label: 'मराठी' },
    { code: 'hi', label: 'हिंदी' },
  ];

  return (
    <header className="sticky top-0 z-50 bg-white border-b border-slate-200 shadow-xs">
      <div className="max-w-4xl mx-auto px-4 py-3 sm:py-3.5 flex flex-wrap items-center justify-between gap-3">
        {/* Brand Header */}
        <div className="flex items-center gap-2.5">
          <div className="w-10 h-10 rounded-lg bg-emerald-700 text-white flex items-center justify-center shadow-xs">
            <ShieldCheck className="w-6 h-6 stroke-[2.2]" />
          </div>
          <div>
            <h1 className="text-xl font-bold tracking-tight text-slate-900 leading-tight">
              {t.brandName}
            </h1>
            <p className="text-xs text-slate-700 font-medium hidden sm:block">
              {t.tagline}
            </p>
          </div>
        </div>

        {/* Controls: Language Selector + Offline Badge */}
        <div className="flex items-center gap-2.5 ml-auto">
          <OfflineBadge />

          {/* Language Selector Switcher */}
          <div className="inline-flex items-center p-1 bg-slate-100 border border-slate-200 rounded-lg" role="group" aria-label="Select Language">
            <Globe className="w-3.5 h-3.5 text-slate-700 ml-1.5 mr-1 hidden sm:block" />
            {languages.map((lang) => (
              <button
                key={lang.code}
                onClick={() => setLanguage(lang.code)}
                className={`px-2.5 py-1.5 text-xs font-bold rounded-md transition-colors min-h-[36px] min-w-[38px] flex items-center justify-center ${
                  language === lang.code
                    ? 'bg-emerald-700 text-white shadow-xs'
                    : 'text-slate-900 hover:text-emerald-800 hover:bg-slate-200/70'
                }`}
                aria-pressed={language === lang.code}
              >
                {lang.label}
              </button>
            ))}
          </div>
        </div>
      </div>
    </header>
  );
};
