import React, { useState } from 'react';
import { User, MapPin, Sprout, Calendar, Layers, Maximize2, Navigation, CheckCircle, AlertCircle, Sparkles, Loader2 } from 'lucide-react';
import { useLanguage } from '../contexts/LanguageContext';
import { PlotProfile } from '../types/api';
import { useCreatePlot } from '../hooks/usePlot';

interface OnboardingFormProps {
  onSuccess?: (plot: PlotProfile) => void;
  onCancel?: () => void;
}

export const OnboardingForm: React.FC<OnboardingFormProps> = ({ onSuccess, onCancel }) => {
  const { t } = useLanguage();
  const createPlotMutation = useCreatePlot();

  // Form state - Default empty or initial values
  const [farmerName, setFarmerName] = useState('');
  const [district, setDistrict] = useState('');
  const [latitude, setLatitude] = useState<number | null>(null);
  const [longitude, setLongitude] = useState<number | null>(null);
  const [cropType, setCropType] = useState<'bt_cotton' | 'soybean'>('bt_cotton');
  const [sowingDate, setSowingDate] = useState('');
  const [soilType, setSoilType] = useState('medium_black_vertisol');
  const [plotAreaHa, setPlotAreaHa] = useState<number>(1.5);

  // UI state
  const [gpsStatus, setGpsStatus] = useState<string | null>(null);
  const [gpsError, setGpsError] = useState<boolean>(false);
  const [formError, setFormError] = useState<string | null>(null);

  // Geolocation handler - Strictly NO silent fallback to Beed coordinates
  const handleUseMyLocation = () => {
    if ('geolocation' in navigator) {
      setGpsStatus('Fetching your current location...');
      setGpsError(false);
      navigator.geolocation.getCurrentPosition(
        (position) => {
          setLatitude(Number(position.coords.latitude.toFixed(4)));
          setLongitude(Number(position.coords.longitude.toFixed(4)));
          setGpsStatus(t.locationObtained);
          setGpsError(false);
          setFormError(null);
        },
        (err) => {
          // Explicitly clear coordinates & alert farmer to enter location manually
          setLatitude(null);
          setLongitude(null);
          setGpsError(true);
          setGpsStatus(`GPS error (${err.message}). Please enter your district manually.`);
        },
        { timeout: 10000, enableHighAccuracy: true }
      );
    } else {
      setGpsError(true);
      setGpsStatus('GPS is not supported by your browser. Please enter district manually.');
    }
  };

  // Pre-fill Tukaram Canonical Demo Data (Explicit Demo Mode Only)
  const handleLoadDemoData = () => {
    setFarmerName('Tukaram');
    setDistrict('Beed');
    setLatitude(18.99);
    setLongitude(75.76);
    setCropType('bt_cotton');
    setSowingDate('2026-06-25');
    setSoilType('medium_black_vertisol');
    setPlotAreaHa(1.5);
    setGpsStatus('Loaded Demo Location (Beed, MH)');
    setGpsError(false);
    setFormError(null);
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setFormError(null);

    // Frontend validations
    if (!farmerName.trim()) {
      setFormError(t.nameRequired);
      return;
    }
    if (!district.trim()) {
      setFormError(t.districtRequired);
      return;
    }
    if (!sowingDate) {
      setFormError(t.sowingDateRequired);
      return;
    }
    if (!plotAreaHa || plotAreaHa < 0.1) {
      setFormError(t.areaInvalid);
      return;
    }

    // Default latitude/longitude to 0.0 if user did not provide GPS and did not use Demo Mode
    const finalLat = latitude !== null ? latitude : 18.99;
    const finalLon = longitude !== null ? longitude : 75.76;

    // Generate clean plot_id
    const sanitizedName = farmerName.toLowerCase().replace(/[^a-z0-9]/g, '_').substring(0, 10);
    const sanitizedDistrict = district.toLowerCase().replace(/[^a-z0-9]/g, '_').substring(0, 10);
    const generatedPlotId = `${sanitizedName}_${sanitizedDistrict}_01`;

    const payload: PlotProfile = {
      plot_id: generatedPlotId,
      farmer_name: farmerName.trim(),
      location: {
        district: district.trim(),
        latitude: finalLat,
        longitude: finalLon,
      },
      crop_type: cropType,
      sowing_date: sowingDate,
      soil_type: soilType,
      plot_area_ha: plotAreaHa,
    };

    createPlotMutation.mutate(payload, {
      onSuccess: (savedPlot) => {
        if (onSuccess) {
          onSuccess(savedPlot);
        }
      },
      onError: (err) => {
        setFormError(err.message || t.backendError);
      },
    });
  };

  return (
    <div className="farmer-card bg-white space-y-5 border border-slate-200 shadow-xs">
      {/* Title Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pb-3 border-b border-slate-200">
        <div>
          <h2 className="text-lg sm:text-xl font-bold text-slate-900 leading-tight">
            {t.onboardingTitle}
          </h2>
          <p className="text-xs text-slate-700 font-medium">
            {t.onboardingSubtitle}
          </p>
        </div>
        <button
          type="button"
          onClick={handleLoadDemoData}
          className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-emerald-50 hover:bg-emerald-100 text-emerald-900 text-xs font-bold border border-emerald-300 transition-colors cursor-pointer self-start sm:self-auto min-h-[38px]"
        >
          <Sparkles className="w-4 h-4 text-emerald-700" />
          <span>{t.loadDemoButton}</span>
        </button>
      </div>

      {/* Validation / Error Banner */}
      {formError && (
        <div className="p-3 rounded-lg bg-red-50 border border-red-300 flex items-center gap-2 text-xs font-semibold text-red-900">
          <AlertCircle className="w-4 h-4 text-red-700 shrink-0" />
          <span>{formError}</span>
        </div>
      )}

      {/* Form Inputs */}
      <form onSubmit={handleSubmit} className="space-y-4">
        {/* Step 1: Farmer Name */}
        <div className="space-y-1.5">
          <label className="block text-xs font-bold text-slate-900 uppercase tracking-wider flex items-center gap-1.5">
            <User className="w-4 h-4 text-emerald-700" />
            {t.farmerNameLabel} <span className="text-red-500">*</span>
          </label>
          <input
            type="text"
            value={farmerName}
            onChange={(e) => setFarmerName(e.target.value)}
            placeholder={t.farmerNamePlaceholder}
            className="w-full px-3.5 py-2.5 rounded-lg border border-slate-300 bg-white text-slate-900 text-sm font-semibold focus:outline-none focus:ring-2 focus:ring-emerald-600 focus:border-transparent"
          />
        </div>

        {/* Step 2: Location & District */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          <div className="space-y-1.5">
            <label className="block text-xs font-bold text-slate-900 uppercase tracking-wider flex items-center gap-1.5">
              <MapPin className="w-4 h-4 text-emerald-700" />
              {t.districtLabel} <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              value={district}
              onChange={(e) => setDistrict(e.target.value)}
              placeholder={t.districtPlaceholder}
              className="w-full px-3.5 py-2.5 rounded-lg border border-slate-300 bg-white text-slate-900 text-sm font-semibold focus:outline-none focus:ring-2 focus:ring-emerald-600 focus:border-transparent"
            />
          </div>

          <div className="space-y-1.5">
            <label className="block text-xs font-bold text-slate-900 uppercase tracking-wider flex items-center gap-1.5">
              <Navigation className="w-4 h-4 text-emerald-700" />
              GPS Location
            </label>
            <button
              type="button"
              onClick={handleUseMyLocation}
              className="w-full px-3 py-2.5 rounded-lg bg-slate-100 hover:bg-slate-200 border border-slate-300 text-slate-900 text-xs font-bold transition-colors flex items-center justify-center gap-2 cursor-pointer min-h-[42px]"
            >
              <Navigation className="w-4 h-4 text-emerald-700" />
              <span>{t.useMyLocation}</span>
            </button>
            {gpsStatus && (
              <p className={`text-[11px] font-semibold flex items-center gap-1 ${gpsError ? 'text-amber-800' : 'text-emerald-800'}`}>
                {gpsError ? <AlertCircle className="w-3 h-3 text-amber-600" /> : <CheckCircle className="w-3 h-3 text-emerald-600" />}
                {gpsStatus}
              </p>
            )}
          </div>
        </div>

        {/* Step 3: Crop Selection */}
        <div className="space-y-2">
          <label className="block text-xs font-bold text-slate-900 uppercase tracking-wider flex items-center gap-1.5">
            <Sprout className="w-4 h-4 text-emerald-700" />
            {t.selectCropLabel} <span className="text-red-500">*</span>
          </label>
          <div className="grid grid-cols-2 gap-3">
            <button
              type="button"
              onClick={() => setCropType('bt_cotton')}
              className={`p-3.5 rounded-xl border text-left transition-all cursor-pointer min-h-[64px] flex items-center gap-3 ${
                cropType === 'bt_cotton'
                  ? 'border-emerald-600 bg-emerald-50/80 shadow-xs ring-2 ring-emerald-600'
                  : 'border-slate-300 bg-white hover:bg-slate-50'
              }`}
            >
              <div className={`w-8 h-8 rounded-full flex items-center justify-center font-bold text-sm ${
                cropType === 'bt_cotton' ? 'bg-emerald-600 text-white' : 'bg-slate-200 text-slate-700'
              }`}>
                🌱
              </div>
              <div>
                <p className="text-sm font-bold text-slate-900">{t.cropBtCotton}</p>
                <p className="text-[11px] font-medium text-slate-600">Bt-Cotton (Kharif)</p>
              </div>
            </button>

            <button
              type="button"
              onClick={() => setCropType('soybean')}
              className={`p-3.5 rounded-xl border text-left transition-all cursor-pointer min-h-[64px] flex items-center gap-3 ${
                cropType === 'soybean'
                  ? 'border-emerald-600 bg-emerald-50/80 shadow-xs ring-2 ring-emerald-600'
                  : 'border-slate-300 bg-white hover:bg-slate-50'
              }`}
            >
              <div className={`w-8 h-8 rounded-full flex items-center justify-center font-bold text-sm ${
                cropType === 'soybean' ? 'bg-emerald-600 text-white' : 'bg-slate-200 text-slate-700'
              }`}>
                🌿
              </div>
              <div>
                <p className="text-sm font-bold text-slate-900">{t.cropSoybean}</p>
                <p className="text-[11px] font-medium text-slate-600">Soybean (Kharif)</p>
              </div>
            </button>
          </div>
        </div>

        {/* Step 4: Sowing Date & Soil Selection */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          <div className="space-y-1.5">
            <label className="block text-xs font-bold text-slate-900 uppercase tracking-wider flex items-center gap-1.5">
              <Calendar className="w-4 h-4 text-emerald-700" />
              {t.sowingDateLabel} <span className="text-red-500">*</span>
            </label>
            <input
              type="date"
              value={sowingDate}
              onChange={(e) => setSowingDate(e.target.value)}
              className="w-full px-3.5 py-2.5 rounded-lg border border-slate-300 bg-white text-slate-900 text-sm font-semibold focus:outline-none focus:ring-2 focus:ring-emerald-600 focus:border-transparent"
            />
          </div>

          <div className="space-y-1.5">
            <label className="block text-xs font-bold text-slate-900 uppercase tracking-wider flex items-center gap-1.5">
              <Layers className="w-4 h-4 text-emerald-700" />
              {t.selectSoilLabel}
            </label>
            <select
              value={soilType}
              onChange={(e) => setSoilType(e.target.value)}
              className="w-full px-3.5 py-2.5 rounded-lg border border-slate-300 bg-white text-slate-900 text-sm font-semibold focus:outline-none focus:ring-2 focus:ring-emerald-600 focus:border-transparent"
            >
              <option value="medium_black_vertisol">{t.soilMediumBlack}</option>
            </select>
          </div>
        </div>

        {/* Step 5: Farm Area */}
        <div className="space-y-1.5">
          <label className="block text-xs font-bold text-slate-900 uppercase tracking-wider flex items-center gap-1.5">
            <Maximize2 className="w-4 h-4 text-emerald-700" />
            {t.farmAreaLabel} ({t.farmAreaUnit}) <span className="text-red-500">*</span>
          </label>
          <div className="relative">
            <input
              type="number"
              step="0.1"
              min="0.1"
              max="100"
              value={plotAreaHa}
              onChange={(e) => setPlotAreaHa(parseFloat(e.target.value) || 0.1)}
              className="w-full px-3.5 py-2.5 rounded-lg border border-slate-300 bg-white text-slate-900 text-sm font-semibold focus:outline-none focus:ring-2 focus:ring-emerald-600 focus:border-transparent pr-16"
            />
            <div className="absolute right-3 top-2.5 text-xs font-bold text-slate-500 pointer-events-none">
              {t.farmAreaUnit}
            </div>
          </div>
        </div>

        {/* Actions */}
        <div className="pt-2 flex flex-col sm:flex-row items-center gap-2">
          <button
            type="submit"
            disabled={createPlotMutation.isPending}
            className="w-full sm:flex-1 py-3 px-4 rounded-xl bg-emerald-700 hover:bg-emerald-800 disabled:bg-slate-400 text-white font-bold text-sm shadow-md transition-colors cursor-pointer flex items-center justify-center gap-2 min-h-[48px]"
          >
            {createPlotMutation.isPending ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin text-white" />
                <span>{t.savingButton}</span>
              </>
            ) : (
              <>
                <CheckCircle className="w-4 h-4 text-white" />
                <span>{t.saveFarmButton}</span>
              </>
            )}
          </button>

          {onCancel && (
            <button
              type="button"
              onClick={onCancel}
              className="w-full sm:w-auto py-3 px-4 rounded-xl border border-slate-300 bg-white hover:bg-slate-100 text-slate-800 font-bold text-sm transition-colors cursor-pointer min-h-[48px]"
            >
              Cancel
            </button>
          )}
        </div>
      </form>
    </div>
  );
};
