import { useQuery, useMutation } from '@tanstack/react-query';
import { getDailyDecision, simulateDecision, getExplainability, getDecisionHistory, getCropHealth, getMarketData, scanCropImage, seedDecisionHistory } from '../api/client';
import { DecisionCard, SimulationRequest, SimulationResponse, ExplainabilityDetails, DecisionHistoryItem, CropHealthResponse, MarketResponse, ScanResponse } from '../types/api';

export function useDailyDecision(plotId: string | null) {
  return useQuery<DecisionCard, Error>({
    queryKey: ['dailyDecision', plotId],
    queryFn: () => getDailyDecision(plotId!),
    enabled: !!plotId,
    retry: 1,
    staleTime: 1000 * 60 * 5, // 5 minutes cache
  });
}

export function useSimulateDecision() {
  return useMutation<SimulationResponse, Error, SimulationRequest>({
    mutationFn: (req: SimulationRequest) => simulateDecision(req),
  });
}

export function useExplainability(decisionId: string | null) {
  return useQuery<ExplainabilityDetails, Error>({
    queryKey: ['explainability', decisionId],
    queryFn: () => getExplainability(decisionId!),
    enabled: !!decisionId,
    retry: 1,
    staleTime: 1000 * 60 * 10, // 10 minutes cache
  });
}

export function useDecisionHistory(plotId: string | null) {
  return useQuery<DecisionHistoryItem[], Error>({
    queryKey: ['decisionHistory', plotId],
    queryFn: () => getDecisionHistory(plotId!),
    enabled: !!plotId,
    retry: 1,
    staleTime: 1000 * 60 * 5,
  });
}

export function useCropHealth(plotId: string | null) {
  return useQuery<CropHealthResponse, Error>({
    queryKey: ['cropHealth', plotId],
    queryFn: () => getCropHealth(plotId!),
    enabled: !!plotId,
    retry: 1,
    staleTime: 1000 * 60 * 5,
  });
}

export function useMarketData(plotId: string | null) {
  return useQuery<MarketResponse, Error>({
    queryKey: ['marketData', plotId],
    queryFn: () => getMarketData(plotId!),
    enabled: !!plotId,
    retry: 1,
    staleTime: 1000 * 60 * 5,
  });
}

export function useScanCropImage() {
  return useMutation<ScanResponse, Error, File>({
    mutationFn: (file: File) => scanCropImage(file),
  });
}

export function useSeedDecisionHistory() {
  return useMutation<DecisionHistoryItem[], Error, string>({
    mutationFn: (plotId: string) => seedDecisionHistory(plotId),
  });
}

