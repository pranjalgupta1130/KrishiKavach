export type Language = 'en' | 'mr' | 'hi';

export interface ShellTranslations {
  brandName: string;
  tagline: string;
  greeting: string;
  subHeading: string;
  myFarm: string;
  todaysAdvice: string;
  whatIf: string;
  whyThisAdvice: string;
  doNotDoThis: string;
  language: string;
  offline: string;
  online: string;
  advicePlaceholder: string;
  whatIfDesc: string;
  whyDesc: string;
  location: string;
  district: string;
  crop: string;
  sowingDate: string;
  soilType: string;
  farmArea: string;
  
  // Onboarding & Form Labels
  onboardingTitle: string;
  onboardingSubtitle: string;
  farmerNameLabel: string;
  farmerNamePlaceholder: string;
  districtLabel: string;
  districtPlaceholder: string;
  useMyLocation: string;
  locationObtained: string;
  selectCropLabel: string;
  cropBtCotton: string;
  cropSoybean: string;
  selectSoilLabel: string;
  soilMediumBlack: string;
  sowingDateLabel: string;
  farmAreaLabel: string;
  farmAreaUnit: string;
  saveFarmButton: string;
  savingButton: string;
  loadDemoButton: string;
  editFarmButton: string;
  
  // Decision Card & Status
  loadingDecision: string;
  errorDecisionTitle: string;
  errorDecisionDesc: string;
  noDataDecision: string;
  dataSourceLabel: string;
  audioButtonLabel: string;

  // What-If Simulation Labels
  whatIfTitle: string;
  whatIfSubtitle: string;
  windSpeedLabel: string;
  rain36hLabel: string;
  seeNewAdviceButton: string;
  checkingAdviceButton: string;
  resetWeatherButton: string;
  currentAdviceHeader: string;
  newAdviceHeader: string;
  recommendationFlippedTitle: string;
  recommendationSameTitle: string;
  simErrorTitle: string;
  whatIfOfflineNotice: string;

  // Explainability Drawer Labels
  explainabilityTitle: string;
  explainabilitySubtitle: string;
  soilSectionTitle: string;
  waterSectionTitle: string;
  windSectionTitle: string;
  pestSectionTitle: string;
  marketSectionTitle: string;
  ruleTracesTitle: string;
  closeDrawer: string;
  loadingExplainability: string;
  errorExplainability: string;
  ruleTriggered: string;
  ruleNotTriggered: string;

  // Voice Player Labels
  listenAudio: string;
  playingAudio: string;
  pausedAudio: string;
  stopAudio: string;
  voiceNotAvailable: string;

  // Status Gauges & Metrics (Part 5 Correction)
  trendsTitle: string;
  trendsSubtitle: string;
  soilChartTitle: string;
  soilChartSubtitle: string;
  pestChartTitle: string;
  pestChartSubtitle: string;
  marketChartTitle: string;
  marketChartSubtitle: string;
  historicalNotice: string;

  // Offline PWA Resilience
  offlineBannerTitle: string;
  offlineBannerDesc: string;
  lastUpdatedLabel: string;

  // Success & Validation Messages
  farmSavedSuccess: string;
  nameRequired: string;
  districtRequired: string;
  sowingDateRequired: string;
  areaInvalid: string;
  backendError: string;
  networkError: string;
  retry: string;
}

export type TranslationsMap = Record<Language, ShellTranslations>;
