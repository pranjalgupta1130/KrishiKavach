import React, { useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Camera,
  Upload,
  Trash2,
  Sparkles,
  ShieldAlert,
  AlertTriangle,
  Loader2,
  Info,
  ArrowRight,
  MapPin,
  CheckCircle2,
  AlertCircle
} from 'lucide-react';
import { useFieldContext } from '../contexts/FieldContext';
import { useLanguage } from '../contexts/LanguageContext';
import { useScanCropImage } from '../hooks/useDecision';
import { ScanResponse } from '../types/api';

export const ScanCropPage: React.FC = () => {
  const { activePlotId, activePlot } = useFieldContext();
  const { t } = useLanguage();
  const navigate = useNavigate();

  const scanMutation = useScanCropImage();

  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [imageSrc, setImageSrc] = useState<string | null>(null);
  const [scanResult, setScanResult] = useState<ScanResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const fileInputRef = useRef<HTMLInputElement>(null);
  const cameraInputRef = useRef<HTMLInputElement>(null);

  const handleImageSelected = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setSelectedFile(file);
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
    if (!selectedFile) return;

    setError(null);
    scanMutation.mutate(selectedFile, {
      onSuccess: (data) => {
        setScanResult(data);
      },
      onError: (err) => {
        setError(err.message || 'Image analysis failed. Please check image format.');
      },
    });
  };

  const handleReset = () => {
    setSelectedFile(null);
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
          <span>Backend Visual Engine</span>
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
              Photograph affected leaves, bolls, or stems for backend feature extraction and visual observations.
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

            {error && (
              <div className="p-3 bg-red-50 border border-red-200 rounded-xl flex items-center gap-2 text-xs font-bold text-red-900">
                <AlertCircle className="w-4 h-4 text-red-700 shrink-0" />
                <span>{error}</span>
              </div>
            )}

            {!scanResult && (
              <button
                onClick={handleAnalyze}
                disabled={scanMutation.isPending}
                className="w-full py-3.5 px-4 rounded-xl bg-emerald-700 hover:bg-emerald-800 disabled:bg-slate-400 text-white font-extrabold text-sm shadow-md transition-colors cursor-pointer flex items-center justify-center gap-2"
              >
                {scanMutation.isPending ? (
                  <>
                    <Loader2 className="w-5 h-5 animate-spin text-white" />
                    <span>Extracting Visual Feature Metrics...</span>
                  </>
                ) : (
                  <>
                    <Sparkles className="w-5 h-5 text-white" />
                    <span>Analyze Crop Image (Backend API)</span>
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
                  <span className={`inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[10px] font-black uppercase ${
                    scanResult.severity === 'HIGH' ? 'bg-rose-100 text-rose-900' : (scanResult.severity === 'MODERATE' ? 'bg-amber-100 text-amber-900' : 'bg-emerald-100 text-emerald-900')
                  }`}>
                    {scanResult.severity === 'NOMINAL' ? <CheckCircle2 className="w-3 h-3 text-emerald-700" /> : <AlertTriangle className="w-3 h-3" />}
                    <span>Severity: {scanResult.severity}</span>
                  </span>
                  <h3 className="text-lg font-black text-slate-900 leading-tight">
                    {scanResult.possible_issue}
                  </h3>
                  <p className="text-xs text-slate-600 font-semibold">
                    Match Confidence: {(scanResult.confidence * 100).toFixed(0)}% • Affected Area: {scanResult.affected_area_pct}%
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
                  Extracted Visual Observations ({scanResult.analysis_method}):
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
