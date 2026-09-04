import React from 'react';
import { NavLink } from 'react-router-dom';
import { LayoutDashboard, Sprout, CloudSun, Camera, History } from 'lucide-react';
import { Navbar } from '../components/Navbar';
import { useLanguage } from '../contexts/LanguageContext';

export const AppLayout: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { t } = useLanguage();

  const bottomNavItems = [
    { to: '/dashboard', label: t.navDashboard, icon: LayoutDashboard },
    { to: '/fields', label: t.navFields, icon: Sprout },
    { to: '/weather', label: t.navWeather, icon: CloudSun },
    { to: '/scan', label: t.navScan, icon: Camera },
    { to: '/history', label: t.navHistory, icon: History },
  ];

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col font-sans pb-16 md:pb-0">
      <Navbar />
      <main className="flex-1 max-w-5xl w-full mx-auto px-3 sm:px-4 py-4 space-y-4 sm:space-y-6">
        {children}
      </main>
      <footer className="bg-white border-t border-slate-200 py-3.5 px-4 mt-auto text-center text-xs font-semibold text-slate-700 hidden md:block">
        <div className="max-w-5xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-2">
          <span>KrishiKavach © 2026 — SU HACKS 2026</span>
          <span className="text-emerald-800 font-bold">Deterministic Agronomic Decision Support Platform</span>
        </div>
      </footer>

      {/* Mobile Fixed Bottom Navigation Bar */}
      <div className="md:hidden fixed bottom-0 left-0 right-0 z-40 bg-white border-t border-slate-200 shadow-lg px-2 py-1 flex items-center justify-around">
        {bottomNavItems.map((item) => {
          const Icon = item.icon;
          return (
            <NavLink
              key={item.to}
              to={item.to}
              className={({ isActive }) =>
                `flex flex-col items-center justify-center py-1 px-2 text-[10px] font-bold rounded-lg transition-colors ${
                  isActive ? 'text-emerald-700 font-extrabold' : 'text-slate-600 hover:text-slate-900'
                }`
              }
            >
              <Icon className="w-5 h-5 mb-0.5" />
              <span className="truncate max-w-[64px]">{item.label}</span>
            </NavLink>
          );
        })}
      </div>
    </div>
  );
};
