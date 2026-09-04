import { useQuery, useMutation } from '@tanstack/react-query';
import { getDailyDecision, simulateDecision, getExplainability } from '../api/client';
import { DecisionCard, SimulationRequest, SimulationResponse, ExplainabilityDetails } from '../types/api';

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
