import React from 'react';
import { User, MapPin, Sprout, Layers, Calendar, Edit3, Maximize2, Loader2, AlertCircle } from 'lucide-react';
import { useLanguage } from '../contexts/LanguageContext';
import { PlotProfile } from '../types/api';

interface PlotProfileCardProps {
  plot?: PlotProfile | null;
  isLoading?: boolean;
  isError?: boolean;
  onEditClick?: () => void;
}

export const PlotProfileCard: React.FC<PlotProfileCardProps> = ({
  plot,
  isLoading,
  isError,
  onEditClick,
}) => {
  const { t } = useLanguage();

  if (isLoading) {
    return (
      <div className="farmer-card bg-white flex items-center justify-center p-6 text-slate-700 font-semibold gap-2">
        <Loader2 className="w-5 h-5 animate-spin text-emerald-700" />
        <span>Loading field profile...</span>
      </div>
    );
  }

  if (isError || !plot) {
    return (
      <div className="farmer-card bg-amber-50/70 border-amber-300 flex flex-col sm:flex-row items-center justify-between gap-3 p-4">
        <div className="flex items-center gap-2.5 text-amber-900 font-semibold text-xs sm:text-sm">
          <AlertCircle className="w-5 h-5 text-amber-700 shrink-0" />
          <span>No active field profile found or server offline.</span>
        </div>
        {onEditClick && (
          <button
            type="button"
            onClick={onEditClick}
            className="px-3.5 py-2 rounded-lg bg-emerald-700 text-white font-bold text-xs shadow-xs hover:bg-emerald-800 transition-colors cursor-pointer min-h-[38px]"
          >
            {t.onboardingTitle}
          </button>
        )}
      </div>
    );
  }

  const cropDisplayName = plot.crop_type === 'bt_cotton' ? t.cropBtCotton : (plot.crop_type === 'soybean' ? t.cropSoybean : plot.crop_type);
  const soilDisplayName = plot.soil_type === 'medium_black_vertisol' ? t.soilMediumBlack : plot.soil_type;

  return (
    <div className="farmer-card bg-gradient-to-r from-emerald-50/80 via-white to-slate-50 border-emerald-200 shadow-xs">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 border-b border-slate-200">
        <div className="flex items-center gap-2.5">
          <div className="w-10 h-10 rounded-full bg-emerald-700 text-white flex items-center justify-center font-bold text-base shadow-xs">
            <User className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-base sm:text-lg font-bold text-slate-900 leading-tight">
              {plot.farmer_name}
            </h2>
            <p className="text-xs font-semibold text-emerald-800">
              {t.subHeading}
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2 self-start sm:self-auto">
          <span className="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-semibold bg-emerald-100 text-emerald-900 border border-emerald-300">
            ID: {plot.plot_id}
          </span>
          {onEditClick && (
            <button
              type="button"
              onClick={onEditClick}
              className="inline-flex items-center gap-1 px-2.5 py-1 rounded-lg bg-slate-100 hover:bg-slate-200 text-slate-800 text-xs font-bold border border-slate-300 transition-colors cursor-pointer min-h-[34px]"
              aria-label="Edit farm profile"
            >
              <Edit3 className="w-3.5 h-3.5 text-slate-700" />
              <span>{t.editFarmButton}</span>
            </button>
          )}
        </div>
      </div>

      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 pt-3">
        <div className="flex items-center gap-2">
          <MapPin className="w-4 h-4 text-emerald-700 shrink-0" />
          <div>
            <p className="text-[10px] sm:text-[11px] font-bold text-slate-700 uppercase tracking-wider">{t.location}</p>
            <p className="text-xs sm:text-sm font-bold text-slate-900">{plot.location.district}</p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <Sprout className="w-4 h-4 text-emerald-700 shrink-0" />
          <div>
            <p className="text-[10px] sm:text-[11px] font-bold text-slate-700 uppercase tracking-wider">{t.crop}</p>
            <p className="text-xs sm:text-sm font-bold text-slate-900">{cropDisplayName}</p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <Layers className="w-4 h-4 text-emerald-700 shrink-0" />
          <div>
            <p className="text-[10px] sm:text-[11px] font-bold text-slate-700 uppercase tracking-wider">{t.soilType}</p>
            <p className="text-xs sm:text-sm font-bold text-slate-900">{soilDisplayName}</p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <Calendar className="w-4 h-4 text-emerald-700 shrink-0" />
          <div>
            <p className="text-[10px] sm:text-[11px] font-bold text-slate-700 uppercase tracking-wider">{t.sowingDate}</p>
            <p className="text-xs sm:text-sm font-bold text-slate-900">{plot.sowing_date}</p>
          </div>
        </div>
      </div>

      <div className="mt-3 pt-2.5 border-t border-slate-200/80 flex items-center justify-between text-xs font-semibold text-slate-600">
        <span className="flex items-center gap-1">
          <Maximize2 className="w-3.5 h-3.5 text-slate-500" />
          {t.farmArea}: <strong className="text-slate-900">{plot.plot_area_ha} {t.farmAreaUnit}</strong>
        </span>
        <span className="text-[11px] font-medium text-emerald-800">
          GPS: {plot.location.latitude}, {plot.location.longitude}
        </span>
      </div>
    </div>
  );
};
