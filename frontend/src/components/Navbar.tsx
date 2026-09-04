import React, { useState } from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import {
  ShieldCheck,
  Globe,
  MapPin,
  Menu,
  X,
  LayoutDashboard,
  Sprout,
  CloudSun,
  Bug,
  TrendingUp,
  History,
  Camera,
  Settings
} from 'lucide-react';
import { useLanguage } from '../contexts/LanguageContext';
import { useFieldContext } from '../contexts/FieldContext';
import { Language } from '../types/language';
import { OfflineBadge } from './OfflineBadge';

export const Navbar: React.FC = () => {
  const { language, setLanguage, t } = useLanguage();
  const { activePlotId, selectPlot, activePlot, plots } = useFieldContext();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const navigate = useNavigate();

  const languages: { code: Language; label: string }[] = [
    { code: 'en', label: 'EN' },
    { code: 'mr', label: 'मराठी' },
    { code: 'hi', label: 'हिंदी' },
  ];

  const navLinks = [
    { to: '/dashboard', label: t.navDashboard, icon: LayoutDashboard },
    { to: '/fields', label: t.navFields, icon: Sprout },
    { to: '/weather', label: t.navWeather, icon: CloudSun },
    { to: '/crop-health', label: t.navCropHealth, icon: Bug },
    { to: '/market', label: t.navMarket, icon: TrendingUp },
    { to: '/history', label: t.navHistory, icon: History },
    { to: '/scan', label: t.navScan, icon: Camera },
    { to: '/settings', label: t.navSettings, icon: Settings },
  ];

  return (
    <header className="sticky top-0 z-50 bg-white border-b border-slate-200 shadow-xs">
      <div className="max-w-5xl mx-auto px-4 py-2.5 sm:py-3 flex items-center justify-between gap-3">
        {/* Brand Header */}
        <div
          onClick={() => navigate('/dashboard')}
          className="flex items-center gap-2 cursor-pointer group shrink-0"
        >
          <div className="w-9 h-9 sm:w-10 sm:h-10 rounded-lg bg-emerald-700 text-white flex items-center justify-center shadow-xs group-hover:bg-emerald-800 transition-colors">
            <ShieldCheck className="w-5 h-5 sm:w-6 sm:h-6 stroke-[2.2]" />
          </div>
          <div>
            <h1 className="text-lg sm:text-xl font-bold tracking-tight text-slate-900 leading-tight">
              {t.brandName}
            </h1>
            <p className="text-[10px] sm:text-xs text-slate-600 font-medium hidden sm:block">
              {t.tagline}
            </p>
          </div>
        </div>

        {/* Visible Active Field Selector Dropdown */}
        <div className="flex items-center gap-1.5 bg-slate-100 border border-slate-200 rounded-lg px-2 py-1 max-w-[200px] sm:max-w-[260px]">
          <MapPin className="w-4 h-4 text-emerald-700 shrink-0" />
          <select
            value={activePlotId}
            onChange={(e) => {
              if (e.target.value === 'NEW') {
                navigate('/fields');
              } else {
                selectPlot(e.target.value);
              }
            }}
            aria-label={t.activeFieldLabel}
            className="bg-transparent text-xs font-bold text-slate-900 focus:outline-none cursor-pointer truncate w-full"
          >
            {plots && plots.length > 0 ? (
              plots.map((p) => (
                <option key={p.plot_id} value={p.plot_id}>
                  {p.farmer_name} - {p.location.district} ({p.crop_type === 'bt_cotton' ? 'Cotton' : p.crop_type})
                </option>
              ))
            ) : (
              <option value={activePlotId}>
                {activePlot ? `${activePlot.farmer_name} - ${activePlot.location.district}` : 'Default Field (Beed)'}
              </option>
            )}
            <option value="NEW">+ {t.editFarmButton || 'Add / Manage Fields'}</option>
          </select>
        </div>

        {/* Right Controls: Offline Badge + Language Selector + Mobile Toggle */}
        <div className="flex items-center gap-2 ml-auto">
          <OfflineBadge />

          {/* Language Selector Switcher */}
          <div className="inline-flex items-center p-0.5 bg-slate-100 border border-slate-200 rounded-lg" role="group" aria-label="Select Language">
            <Globe className="w-3.5 h-3.5 text-slate-700 ml-1 mr-0.5 hidden sm:block" />
            {languages.map((lang) => (
              <button
                key={lang.code}
                onClick={() => setLanguage(lang.code)}
                className={`px-2 py-1 text-[11px] font-bold rounded-md transition-colors min-h-[30px] min-w-[32px] flex items-center justify-center ${
                  language === lang.code
                    ? 'bg-emerald-700 text-white shadow-xs'
                    : 'text-slate-700 hover:text-emerald-800 hover:bg-slate-200/70'
                }`}
                aria-pressed={language === lang.code}
              >
                {lang.label}
              </button>
            ))}
          </div>

          {/* Mobile Hamburger Button */}
          <button
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            className="md:hidden p-1.5 rounded-lg text-slate-700 hover:bg-slate-100 transition-colors"
            aria-label="Toggle menu"
          >
            {mobileMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
          </button>
        </div>
      </div>

      {/* Desktop Main Navigation Bar */}
      <nav className="hidden md:block bg-slate-50 border-t border-slate-200">
        <div className="max-w-5xl mx-auto px-4 flex items-center gap-1 overflow-x-auto py-1">
          {navLinks.map((link) => {
            const Icon = link.icon;
            return (
              <NavLink
                key={link.to}
                to={link.to}
                className={({ isActive }) =>
                  `flex items-center gap-1.5 px-3 py-2 text-xs font-bold rounded-md transition-colors whitespace-nowrap ${
                    isActive
                      ? 'bg-emerald-700 text-white shadow-xs'
                      : 'text-slate-700 hover:text-emerald-900 hover:bg-slate-200/60'
                  }`
                }
              >
                <Icon className="w-4 h-4" />
                <span>{link.label}</span>
              </NavLink>
            );
          })}
        </div>
      </nav>

      {/* Mobile Drawer Menu */}
      {mobileMenuOpen && (
        <div className="md:hidden bg-white border-t border-slate-200 px-4 py-3 space-y-1 shadow-lg animate-fade-in">
          {navLinks.map((link) => {
            const Icon = link.icon;
            return (
              <NavLink
                key={link.to}
                to={link.to}
                onClick={() => setMobileMenuOpen(false)}
                className={({ isActive }) =>
                  `flex items-center gap-2.5 px-3 py-2.5 text-sm font-bold rounded-lg transition-colors ${
                    isActive
                      ? 'bg-emerald-700 text-white'
                      : 'text-slate-800 hover:bg-slate-100'
                  }`
                }
              >
                <Icon className="w-5 h-5 text-current" />
                <span>{link.label}</span>
              </NavLink>
            );
          })}
        </div>
      )}
    </header>
  );
};
