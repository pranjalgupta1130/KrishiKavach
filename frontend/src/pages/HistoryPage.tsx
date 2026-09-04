import React, { useState } from 'react';
import {
  History as HistoryIcon,
  Calendar,
  AlertOctagon,
  CheckCircle2,
  HelpCircle,
  Clock,
  Sparkles,
  Loader2,
  AlertCircle
} from 'lucide-react';
import { useFieldContext } from '../contexts/FieldContext';
import { useDecisionHistory, useSeedDecisionHistory } from '../hooks/useDecision';
import { useLanguage } from '../contexts/LanguageContext';
import { ExplainabilityDrawer } from '../components/ExplainabilityDrawer';
import { DecisionHistoryItem } from '../types/api';

export const HistoryPage: React.FC = () => {
  const { activePlotId, activePlot } = useFieldContext();
  const { data: history, isLoading, isError, error, refetch } = useDecisionHistory(activePlotId);
  const seedMutation = useSeedDecisionHistory();
  const { t } = useLanguage();

  const [selectedExplainabilityId, setSelectedExplainabilityId] = useState<string | null>(null);

  const handleSeedHistory = () => {
    if (!activePlotId) return;
    seedMutation.mutate(activePlotId, {
      onSuccess: () => {
        refetch();
      }
    });
  };

  return (
    <div className="space-y-4 sm:space-y-6 animate-fade-in">
      {/* Page Title Header */}
      <div className="bg-white border border-slate-200 rounded-2xl p-4 sm:p-5 shadow-xs flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div className="space-y-1">
          <div className="flex items-center gap-1.5 text-xs font-bold text-purple-800 uppercase tracking-wider">
            <HistoryIcon className="w-4 h-4 text-purple-700" />
            <span>{t.navHistory || 'Decision History & Audit Trail'}</span>
          </div>
          <h2 className="text-xl sm:text-2xl font-black text-slate-900">
            {activePlot ? `${activePlot.farmer_name}'s Decision History` : 'Plot Decision History'}
          </h2>
          <p className="text-xs text-slate-600 font-medium">
            Persisted historical decision cards ordered newest first. Zero recomputation using current weather.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={handleSeedHistory}
            disabled={seedMutation.isPending}
            className="inline-flex items-center gap-1.5 px-3 py-2 rounded-xl bg-purple-700 hover:bg-purple-800 disabled:bg-purple-300 text-white text-xs font-bold transition-colors cursor-pointer"
          >
            {seedMutation.isPending ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : (
              <Sparkles className="w-4 h-4" />
            )}
            <span>Seed Demo History</span>
          </button>
        </div>
      </div>

      {/* Loading State */}
      {isLoading && (
        <div className="p-8 text-center bg-white border border-slate-200 rounded-2xl space-y-3">
          <Loader2 className="w-8 h-8 text-purple-700 animate-spin mx-auto" />
          <p className="text-xs font-bold text-slate-700">Loading historical decision records...</p>
        </div>
      )}

      {/* Error State */}
      {isError && (
        <div className="p-4 bg-red-50 border border-red-200 rounded-2xl flex items-center gap-3 text-xs font-bold text-red-900">
          <AlertCircle className="w-5 h-5 text-red-700 shrink-0" />
          <span>{error?.message || 'Could not load decision history.'}</span>
        </div>
      )}

      {/* Empty State */}
      {!isLoading && !isError && (!history || history.length === 0) && (
        <div className="p-8 text-center bg-white border border-slate-200 rounded-2xl space-y-3">
          <HistoryIcon className="w-10 h-10 text-slate-400 mx-auto" />
          <h3 className="text-sm font-bold text-slate-900">No Historical Decisions Recorded Yet</h3>
          <p className="text-xs text-slate-600 max-w-md mx-auto">
            Decisions generated on the dashboard are automatically persisted. Click below to populate demo historical benchmarks for testing.
          </p>
          <button
            onClick={handleSeedHistory}
            disabled={seedMutation.isPending}
            className="inline-flex items-center gap-1.5 px-4 py-2 rounded-xl bg-purple-700 hover:bg-purple-800 text-white text-xs font-bold transition-colors cursor-pointer"
          >
            <Sparkles className="w-4 h-4" />
            <span>Seed Demo Historical Scenarios</span>
          </button>
        </div>
      )}

      {/* Historical Decision Cards List */}
      {!isLoading && history && history.length > 0 && (
        <div className="space-y-4">
          {history.map((item: DecisionHistoryItem) => {
            const hasProhibition = item.critical_prohibition && !item.critical_prohibition.includes('NO CRITICAL PROHIBITIONS');
            const createdDateStr = new Date(item.created_at || item.date).toLocaleDateString('en-IN', {
              year: 'numeric',
              month: 'short',
              day: 'numeric',
              hour: '2-digit',
              minute: '2-digit'
            });

            return (
              <div
                key={item.decision_id}
                className="bg-white border border-slate-200 rounded-2xl p-4 sm:p-5 shadow-xs space-y-3 hover:border-purple-300 transition-colors"
              >
                {/* Header Metadata */}
                <div className="flex flex-wrap items-center justify-between gap-2 pb-2.5 border-b border-slate-100 text-xs">
                  <div className="flex items-center gap-2">
                    <span className="font-extrabold text-slate-900 flex items-center gap-1.5">
                      <Calendar className="w-3.5 h-3.5 text-purple-700" />
                      {item.date}
                    </span>
                    <span className="text-slate-400">•</span>
                    <span className="text-slate-500 font-semibold flex items-center gap-1">
                      <Clock className="w-3 h-3 text-slate-400" />
                      {createdDateStr}
                    </span>
                  </div>

                  <span className="text-[11px] font-mono text-purple-900 font-bold bg-purple-50 border border-purple-200 px-2 py-0.5 rounded-md">
                    ID: {item.decision_id}
                  </span>
                </div>

                {/* Primary Action */}
                <div className="space-y-1">
                  <span className="text-[10px] font-extrabold uppercase tracking-wider text-emerald-800 flex items-center gap-1">
                    <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
                    Primary Action
                  </span>
                  <p className="text-sm font-black text-slate-900 leading-snug">
                    {item.primary_action}
                  </p>
                </div>

                {/* Critical Prohibition */}
                {hasProhibition && (
                  <div className="p-3 bg-red-50 border border-red-200 rounded-xl flex items-start gap-2 text-xs">
                    <AlertOctagon className="w-4 h-4 text-red-700 shrink-0 mt-0.5" />
                    <div>
                      <span className="font-extrabold text-red-950 uppercase text-[10px] block">Critical Prohibition</span>
                      <span className="font-bold text-red-900">{item.critical_prohibition}</span>
                    </div>
                  </div>
                )}

                {/* Scientific Rationale */}
                <p className="text-xs text-slate-700 font-medium leading-relaxed bg-slate-50 p-2.5 rounded-xl border border-slate-200/70">
                  <span className="font-bold text-slate-900">Rationale: </span>
                  {item.scientific_rationale}
                </p>

                {/* Footer Action */}
                <div className="flex items-center justify-between pt-1 text-xs">
                  <span className="text-slate-500 font-medium text-[11px]">
                    {item.confidence_indicator}
                  </span>

                  {item.explainability_id && (
                    <button
                      onClick={() => setSelectedExplainabilityId(item.explainability_id)}
                      className="inline-flex items-center gap-1 px-3 py-1.5 rounded-lg bg-purple-50 hover:bg-purple-100 text-purple-900 text-xs font-bold border border-purple-200 transition-colors cursor-pointer"
                    >
                      <HelpCircle className="w-3.5 h-3.5 text-purple-700" />
                      <span>Inspect Audit Log</span>
                    </button>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Historical Explainability Drawer Modal */}
      {selectedExplainabilityId && (
        <ExplainabilityDrawer
          decisionId={selectedExplainabilityId}
          isOpen={!!selectedExplainabilityId}
          onClose={() => setSelectedExplainabilityId(null)}
        />
      )}
    </div>
  );
};
