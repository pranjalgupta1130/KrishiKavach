import React from 'react';
import { Navbar } from '../components/Navbar';

export const AppLayout: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  return (
    <div className="min-h-screen bg-slate-50 flex flex-col font-sans">
      <Navbar />
      <main className="flex-1 max-w-4xl w-full mx-auto px-4 py-4 sm:py-6 space-y-4 sm:space-y-6">
        {children}
      </main>
      <footer className="bg-white border-t border-slate-200 py-3.5 px-4 mt-auto text-center text-xs font-semibold text-slate-700">
        <div className="max-w-4xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-2">
          <span>KrishiKavach © 2026 — SU HACKS 2026</span>
          <span className="text-emerald-800 font-bold">Deterministic Agronomic Decision Support</span>
        </div>
      </footer>
    </div>
  );
};
