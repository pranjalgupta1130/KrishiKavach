import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { getPlot, createPlot, listPlots } from '../api/client';
import { PlotProfile } from '../types/api';

export function usePlotProfile(plotId: string | null) {
  return useQuery<PlotProfile, Error>({
    queryKey: ['plot', plotId],
    queryFn: () => getPlot(plotId!),
    enabled: !!plotId,
    retry: 1,
    staleTime: 1000 * 60 * 10, // 10 minutes
  });
}

export function useListPlots() {
  return useQuery<PlotProfile[], Error>({
    queryKey: ['plots'],
    queryFn: listPlots,
    staleTime: 1000 * 60 * 5,
  });
}

export function useCreatePlot() {
  const queryClient = useQueryClient();

  return useMutation<PlotProfile, Error, PlotProfile>({
    mutationFn: (newPlot: PlotProfile) => createPlot(newPlot),
    onSuccess: (data) => {
      queryClient.setQueryData(['plot', data.plot_id], data);
      queryClient.invalidateQueries({ queryKey: ['plots'] });
    },
  });
}
