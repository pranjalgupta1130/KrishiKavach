import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Sprout,
  Plus,
  MapPin,
  Calendar,
  Layers,
  CheckCircle2,
  Trash2,
  Sparkles,
  ArrowRight,
  ShieldCheck
} from 'lucide-react';
import { useFieldContext } from '../contexts/FieldContext';
import { useLanguage } from '../contexts/LanguageContext';
import { OnboardingForm } from '../components/OnboardingForm';
import { PlotProfile } from '../types/api';

export const FieldsPage: React.FC = () => {
  const { activePlotId, selectPlot, activePlot, plots } = useFieldContext();
  const { t } = useLanguage();
  const navigate = useNavigate();
  const [showAddForm, setShowAddForm] = useState(false);
  const [customFields, setCustomFields] = useState<PlotProfile[]>([]);

  const handleFieldCreated = (savedPlot: PlotProfile) => {
    setCustomFields((prev) => [...prev.filter(p => p.plot_id !== savedPlot.plot_id), savedPlot]);
    selectPlot(savedPlot.plot_id);
    setShowAddForm(false);
  };

  const handleRemoveField = (plotId: string, e: React.MouseEvent) => {
    e.stopPropagation();
    setCustomFields((prev) => prev.filter(p => p.plot_id !== plotId));
    if (activePlotId === plotId && plots && plots.length > 0) {
      const nextPlot = plots.find(p => p.plot_id !== plotId);
      if (nextPlot) selectPlot(nextPlot.plot_id);
    }
  };

  // Combine fetched plots with any transient created fields
  const allPlotsMap = new Map<string, PlotProfile>();
  if (plots) {
    plots.forEach(p => allPlotsMap.set(p.plot_id, p));
  }
  customFields.forEach(p => allPlotsMap.set(p.plot_id, p));
  if (activePlot) {
    allPlotsMap.set(activePlot.plot_id, activePlot);
  }
  const allPlots = Array.from(allPlotsMap.values());

  return (
    <div className="space-y-4 sm:space-y-6 animate-fade-in">
      {/* Header Bar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 border-b border-slate-200">
        <div>
          <h2 className="text-xl sm:text-2xl font-black text-slate-900 flex items-center gap-2">
            <Sprout className="w-6 h-6 text-emerald-700" />
            <span>{t.navFields || 'My Fields'}</span>
          </h2>
          <p className="text-xs text-slate-600 font-medium">
            Manage your agricultural plot profiles and location coordinates.
          </p>
        </div>

        <button
          onClick={() => setShowAddForm(!showAddForm)}
          className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl bg-emerald-700 hover:bg-emerald-800 text-white font-bold text-xs sm:text-sm shadow-xs transition-colors cursor-pointer self-start sm:self-auto"
        >
          <Plus className="w-4 h-4" />
          <span>{showAddForm ? 'Close Form' : 'Add New Field'}</span>
        </button>
      </div>

      {/* Add / Edit Form Modal Container */}
      {showAddForm && (
        <div className="animate-fade-in">
          <OnboardingForm
            onSuccess={handleFieldCreated}
            onCancel={() => setShowAddForm(false)}
          />
        </div>
      )}

      {/* Fields List */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {allPlots.map((plot) => {
          const isSelected = plot.plot_id === activePlotId;
          return (
            <div
              key={plot.plot_id}
              onClick={() => selectPlot(plot.plot_id)}
              className={`p-4 rounded-2xl border-2 transition-all cursor-pointer relative space-y-3 ${
                isSelected
                  ? 'border-emerald-600 bg-emerald-50/60 shadow-md ring-2 ring-emerald-600/30'
                  : 'border-slate-200 bg-white hover:border-slate-300 hover:shadow-xs'
              }`}
            >
              {/* Card Top */}
              <div className="flex items-start justify-between gap-2">
                <div className="space-y-0.5">
                  <div className="flex items-center gap-2">
                    <h3 className="text-base font-extrabold text-slate-900">
                      {plot.farmer_name}'s Field
                    </h3>
                    {isSelected && (
                      <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full bg-emerald-700 text-white text-[10px] font-bold">
                        <CheckCircle2 className="w-3 h-3" />
                        <span>Active</span>
                      </span>
                    )}
                  </div>
                  <p className="text-xs font-semibold text-slate-600 flex items-center gap-1">
                    <MapPin className="w-3.5 h-3.5 text-emerald-700 shrink-0" />
                    <span>{plot.location.district} ({plot.location.latitude.toFixed(2)}°, {plot.location.longitude.toFixed(2)}°)</span>
                  </p>
                </div>

                {!isSelected && (
                  <button
                    onClick={(e) => handleRemoveField(plot.plot_id, e)}
                    className="p-1.5 rounded-lg text-slate-400 hover:text-red-600 hover:bg-red-50 transition-colors"
                    title="Remove field"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                )}
              </div>

              {/* Field Attributes Grid */}
              <div className="grid grid-cols-3 gap-2 p-2.5 bg-slate-100/70 rounded-xl text-xs">
                <div>
                  <span className="text-[10px] font-bold text-slate-500 uppercase block">Crop</span>
                  <span className="font-extrabold text-slate-900">
                    {plot.crop_type === 'bt_cotton' ? 'Bt Cotton' : plot.crop_type === 'soybean' ? 'Soybean' : plot.crop_type}
                  </span>
                </div>
                <div>
                  <span className="text-[10px] font-bold text-slate-500 uppercase block">Sowing Date</span>
                  <span className="font-bold text-slate-800">{plot.sowing_date}</span>
                </div>
                <div>
                  <span className="text-[10px] font-bold text-slate-500 uppercase block">Area</span>
                  <span className="font-bold text-slate-800">{plot.plot_area_ha} Ha</span>
                </div>
              </div>

              {/* Action Bar */}
              <div className="flex items-center justify-between pt-1 text-xs">
                <span className="text-slate-500 font-medium">ID: {plot.plot_id}</span>
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    selectPlot(plot.plot_id);
                    navigate('/dashboard');
                  }}
                  className="inline-flex items-center gap-1 text-xs font-extrabold text-emerald-800 hover:text-emerald-950"
                >
                  <span>View Today's Decision</span>
                  <ArrowRight className="w-3.5 h-3.5" />
                </button>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
