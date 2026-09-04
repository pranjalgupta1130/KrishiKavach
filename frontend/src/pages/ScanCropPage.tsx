import React, { useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Camera,
  Upload,
  RefreshCw,
  Trash2,
  Sparkles,
  ShieldAlert,
  CheckCircle2,
  AlertTriangle,
  Loader2,
  Info,
  ArrowRight,
  MapPin
} from 'lucide-react';
import { useFieldContext } from '../contexts/FieldContext';
import { useLanguage } from '../contexts/LanguageContext';
import { CropScanResult } from '../types/api';

export const ScanCropPage: React.FC = () => {
  const { activePlotId, activePlot } = useFieldContext();
  const { t } = useLanguage();
  const navigate = useNavigate();

  const [imageSrc, setImageSrc] = useState<string | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [scanResult, setScanResult] = useState<CropScanResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  const fileInputRef = useRef<HTMLInputElement>(null);
  const cameraInputRef = useRef<HTMLInputElement>(null);

  const handleImageSelected = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (event) => {
        setImageSrc(event.target?.result as string);
        setScanResult(null);
        setError(null);
      };
      reader.readAsDataURL(file);
    }
  };

  const handleAnalyze = () => {
    if (!imageSrc) return;

    setIsAnalyzing(true);
    setError(null);

    // Simulate structured safety image analysis matching crop context
    setTimeout(() => {
      setIsAnalyzing(false);
      const isCotton = activePlot?.crop_type === 'bt_cotton' || !activePlot;
      setScanResult({
        observations: isCotton ? [
          'Visual leaf damage consistent with early pink bollworm larval feeding',
          'Small entry pinholes detected on young squares/flowers',
          'No severe foliar necrosis or fungal rust observed'
        ] : [
          'Scattered yellowing chlorosis on lower leaves',
          'Mild caterpillar leaf chewing damage on outer canopy'
        ],
        possible_issue: isCotton ? 'Pink Bollworm (Pectinophora gossypiella) Early Activity' : 'Tobacco Caterpillar Leaf Feeding',
        confidence: 0.88,
        severity: 'MEDIUM',
        needs_field_scouting: true,
        recommendation_note: 'Visual indications only. Chemical treatments are strictly governed by daily environmental arbitration.'
      });
    }, 1500);
  };

  const handleReset = () => {
    setImageSrc(null);
    setScanResult(null);
    setError(null);
  };

  return (
    <div className="space-y-4 sm:space-y-6 animate-fade-in">
      {/* Title Header */}
      <div className="bg-white border border-slate-200 rounded-2xl p-4 sm:p-5 shadow-xs flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div className="space-y-1">
          <div className="flex items-center gap-1.5 text-xs font-bold text-emerald-800 uppercase tracking-wider">
            <Camera className="w-4 h-4 text-emerald-700" />
            <span>{t.navScan || 'Scan My Crop'}</span>
          </div>
          <h2 className="text-xl sm:text-2xl font-black text-slate-900">
            Pest & Disease Image Diagnosis
          </h2>
          <p className="text-xs text-slate-600 font-medium flex items-center gap-1.5">
            <MapPin className="w-3.5 h-3.5 text-emerald-700 shrink-0" />
            <span>Scanning for {activePlot ? `${activePlot.farmer_name}'s Field (${activePlot.location.district})` : 'Selected Field'}</span>
          </p>
        </div>

        <div className="inline-flex items-center gap-2 px-3 py-2 rounded-xl bg-emerald-50 border border-emerald-200 text-emerald-950 text-xs font-bold shrink-0">
          <ShieldAlert className="w-4 h-4 text-emerald-700" />
          <span>Safety Isolated AI</span>
        </div>
      </div>

      {/* Hidden File Inputs */}
      <input
        type="file"
        accept="image/*"
        capture="environment"
        ref={cameraInputRef}
        onChange={handleImageSelected}
        className="hidden"
      />
      <input
        type="file"
        accept="image/*"
        ref={fileInputRef}
        onChange={handleImageSelected}
        className="hidden"
      />

      {/* Image Upload / Capture Controls */}
      {!imageSrc ? (
        <div className="p-8 border-2 border-dashed border-slate-300 bg-white rounded-2xl text-center space-y-4 shadow-xs">
          <div className="w-16 h-16 rounded-full bg-emerald-50 text-emerald-700 flex items-center justify-center mx-auto shadow-2xs">
            <Camera className="w-8 h-8" />
          </div>

          <div className="space-y-1">
            <h3 className="text-base font-extrabold text-slate-900">Take or Upload a Crop Photo</h3>
            <p className="text-xs text-slate-600 max-w-md mx-auto">
              Photograph affected leaves, bolls, or stems to extract visual observations for decision arbitration.
            </p>
          </div>

          <div className="flex flex-col sm:flex-row items-center justify-center gap-3 pt-2">
            <button
              onClick={() => cameraInputRef.current?.click()}
              className="w-full sm:w-auto px-5 py-3 rounded-xl bg-emerald-700 hover:bg-emerald-800 text-white font-extrabold text-xs sm:text-sm shadow-md transition-colors cursor-pointer flex items-center justify-center gap-2"
            >
              <Camera className="w-4 h-4" />
              <span>Take Photo with Camera</span>
            </button>

            <button
              onClick={() => fileInputRef.current?.click()}
              className="w-full sm:w-auto px-5 py-3 rounded-xl bg-slate-100 hover:bg-slate-200 border border-slate-300 text-slate-800 font-extrabold text-xs sm:text-sm transition-colors cursor-pointer flex items-center justify-center gap-2"
            >
              <Upload className="w-4 h-4 text-slate-700" />
              <span>Upload from Gallery</span>
            </button>
          </div>
        </div>
      ) : (
        <div className="space-y-4">
          {/* Image Preview Card */}
          <div className="bg-white border border-slate-200 rounded-2xl p-4 shadow-xs space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold text-slate-700 uppercase">Crop Image Preview</span>
              <button
                onClick={handleReset}
                className="inline-flex items-center gap-1 text-xs font-bold text-red-600 hover:text-red-800"
              >
                <Trash2 className="w-3.5 h-3.5" />
                <span>Remove Photo</span>
              </button>
            </div>

            <div className="relative rounded-xl overflow-hidden max-h-80 bg-slate-900 flex items-center justify-center">
              <img
                src={imageSrc}
                alt="Crop preview"
                className="max-h-80 w-auto object-contain rounded-xl"
              />
            </div>

            {!scanResult && (
              <button
                onClick={handleAnalyze}
                disabled={isAnalyzing}
                className="w-full py-3.5 px-4 rounded-xl bg-emerald-700 hover:bg-emerald-800 disabled:bg-slate-400 text-white font-extrabold text-sm shadow-md transition-colors cursor-pointer flex items-center justify-center gap-2"
              >
                {isAnalyzing ? (
                  <>
                    <Loader2 className="w-5 h-5 animate-spin text-white" />
                    <span>Extracting Visual Observations...</span>
                  </>
                ) : (
                  <>
                    <Sparkles className="w-5 h-5 text-white" />
                    <span>Analyze Crop Image</span>
                  </>
                )}
              </button>
            )}
          </div>

          {/* Analysis Results Card */}
          {scanResult && (
            <div className="bg-white border border-slate-200 rounded-2xl p-5 shadow-xs space-y-4 animate-fade-in">
              <div className="flex items-start justify-between gap-3 pb-3 border-b border-slate-100">
                <div className="space-y-1">
                  <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full bg-amber-100 text-amber-900 text-[10px] font-black uppercase">
                    <AlertTriangle className="w-3 h-3 text-amber-700" />
                    <span>Severity: {scanResult.severity}</span>
                  </span>
                  <h3 className="text-lg font-black text-slate-900 leading-tight">
                    {scanResult.possible_issue}
                  </h3>
                  <p className="text-xs text-slate-600 font-semibold">
                    Confidence Match: {(scanResult.confidence * 100).toFixed(0)}%
                  </p>
                </div>

                <button
                  onClick={handleReset}
                  className="p-2 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-bold transition-colors"
                >
                  Scan Another
                </button>
              </div>

              {/* Structured Visual Observations */}
              <div className="space-y-2">
                <h4 className="text-xs font-extrabold text-slate-900 uppercase tracking-wider">
                  Extracted Visual Observations:
                </h4>
                <ul className="text-xs text-slate-700 space-y-1.5 list-disc list-inside font-medium bg-slate-50 p-3 rounded-xl border border-slate-200">
                  {scanResult.observations.map((obs, idx) => (
                    <li key={idx}>{obs}</li>
                  ))}
                </ul>
              </div>

              {/* Safety Isolation Notice */}
              <div className="p-3 bg-amber-50 border border-amber-200 rounded-xl flex items-start gap-2.5 text-xs text-amber-900">
                <Info className="w-4 h-4 text-amber-700 shrink-0 mt-0.5" />
                <div className="space-y-0.5">
                  <p className="font-extrabold">Safety Policy Enforcement</p>
                  <p className="font-medium text-[11px]">
                    {scanResult.recommendation_note}
                  </p>
                </div>
              </div>

              {/* Return to Dashboard */}
              <button
                onClick={() => navigate('/dashboard')}
                className="w-full py-3 px-4 rounded-xl bg-slate-900 hover:bg-slate-800 text-white font-bold text-xs shadow-xs transition-colors flex items-center justify-center gap-2"
              >
                <span>View Today's Arbitrated Decision Card</span>
                <ArrowRight className="w-4 h-4" />
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
