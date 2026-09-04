import { PlotProfile, DecisionCard, ExplainabilityDetails } from '../types/api';

const CACHE_KEYS = {
  PLOT: 'krishikavach_offline_plot',
  DECISION: 'krishikavach_offline_decision',
  EXPLAINABILITY: 'krishikavach_offline_explainability',
  LAST_UPDATED: 'krishikavach_offline_timestamp',
};

export interface OfflineState {
  plot: PlotProfile | null;
  decision: DecisionCard | null;
  explainability: ExplainabilityDetails | null;
  lastUpdated: string | null;
}

export const offlineStorage = {
  savePlot(plot: PlotProfile) {
    try {
      localStorage.setItem(CACHE_KEYS.PLOT, JSON.stringify(plot));
    } catch {
      // Storage full or unavailable
    }
  },

  getPlot(): PlotProfile | null {
    try {
      const data = localStorage.getItem(CACHE_KEYS.PLOT);
      return data ? JSON.parse(data) : null;
    } catch {
      return null;
    }
  },

  saveDecision(decision: DecisionCard) {
    try {
      localStorage.setItem(CACHE_KEYS.DECISION, JSON.stringify(decision));
      localStorage.setItem(CACHE_KEYS.LAST_UPDATED, new Date().toISOString());
    } catch {
      // Storage error
    }
  },

  getDecision(): DecisionCard | null {
    try {
      const data = localStorage.getItem(CACHE_KEYS.DECISION);
      return data ? JSON.parse(data) : null;
    } catch {
      return null;
    }
  },

  saveExplainability(details: ExplainabilityDetails) {
    try {
      localStorage.setItem(CACHE_KEYS.EXPLAINABILITY, JSON.stringify(details));
    } catch {
      // Storage error
    }
  },

  getExplainability(): ExplainabilityDetails | null {
    try {
      const data = localStorage.getItem(CACHE_KEYS.EXPLAINABILITY);
      return data ? JSON.parse(data) : null;
    } catch {
      return null;
    }
  },

  getLastUpdated(): string | null {
    try {
      return localStorage.getItem(CACHE_KEYS.LAST_UPDATED);
    } catch {
      return null;
    }
  },
};
