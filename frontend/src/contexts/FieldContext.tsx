import React, { createContext, useContext, useState, useEffect } from 'react';
import { PlotProfile } from '../types/api';
import { usePlotProfile, useListPlots } from '../hooks/usePlot';

const STORAGE_PLOT_KEY = 'krishikavach_active_plot_id';

interface FieldContextType {
  activePlotId: string;
  setActivePlotId: (plotId: string) => void;
  activePlot: PlotProfile | undefined;
  plots: PlotProfile[] | undefined;
  isLoadingPlot: boolean;
  isLoadingPlots: boolean;
  selectPlot: (plotId: string) => void;
}

const FieldContext = createContext<FieldContextType | undefined>(undefined);

export const FieldProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [activePlotId, setActivePlotIdState] = useState<string>(() => {
    try {
      return localStorage.getItem(STORAGE_PLOT_KEY) || 'tukaram_beed_01';
    } catch {
      return 'tukaram_beed_01';
    }
  });

  const { data: activePlot, isLoading: isLoadingPlot } = usePlotProfile(activePlotId);
  const { data: plots, isLoading: isLoadingPlots } = useListPlots();

  const setActivePlotId = (plotId: string) => {
    try {
      localStorage.setItem(STORAGE_PLOT_KEY, plotId);
    } catch {
      // Ignore storage errors
    }
    setActivePlotIdState(plotId);
  };

  const selectPlot = (plotId: string) => {
    setActivePlotId(plotId);
  };

  // Auto-sync if activePlotId is not in list but list has items
  useEffect(() => {
    if (plots && plots.length > 0 && !plots.some(p => p.plot_id === activePlotId) && activePlotId === 'tukaram_beed_01') {
      // Keep tukaram_beed_01 if it's default demo
    }
  }, [plots, activePlotId]);

  return (
    <FieldContext.Provider
      value={{
        activePlotId,
        setActivePlotId,
        activePlot,
        plots,
        isLoadingPlot,
        isLoadingPlots,
        selectPlot,
      }}
    >
      {children}
    </FieldContext.Provider>
  );
};

export const useFieldContext = () => {
  const context = useContext(FieldContext);
  if (!context) {
    throw new Error('useFieldContext must be used within a FieldProvider');
  }
  return context;
};
