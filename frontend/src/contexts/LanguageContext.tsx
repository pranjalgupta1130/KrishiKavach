import React, { createContext, useContext, useState } from 'react';
import { Language, ShellTranslations, TranslationsMap } from '../types/language';

const translations: TranslationsMap = {
  en: {
    brandName: 'KrishiKavach',
    tagline: 'Farmer Decision Support Platform',
    greeting: 'Namaskar, Farmer',
    subHeading: "Your field's daily decision guide",
    myFarm: 'My Field',
    todaysAdvice: "Today's Advice",
    whatIf: 'What if?',
    whyThisAdvice: 'Why this advice?',
    doNotDoThis: 'Do NOT do this',
    language: 'Language',
    offline: 'Offline',
    online: 'Online',
    advicePlaceholder: 'Your decision recommendation will appear here.',
    whatIfDesc: 'Try changing weather conditions to see how the recommendation changes in real-time.',
    whyDesc: "Understand the transparent numbers behind today's advice.",
    location: 'Location',
    district: 'District',
    crop: 'Crop',
    sowingDate: 'Sowing Date',
    soilType: 'Soil Type',
    farmArea: 'Farm Area',
    
    // Onboarding
    onboardingTitle: 'Register Your Field',
    onboardingSubtitle: 'Enter your basic field details to receive daily decision advice.',
    farmerNameLabel: 'Farmer Name',
    farmerNamePlaceholder: 'e.g. Tukaram',
    districtLabel: 'District / Region',
    districtPlaceholder: 'e.g. Beed',
    useMyLocation: 'Use My Current Location',
    locationObtained: 'GPS Location Set',
    selectCropLabel: 'What crop did you sow?',
    cropBtCotton: 'Bt Cotton',
    cropSoybean: 'Soybean',
    selectSoilLabel: 'What is your soil type?',
    soilMediumBlack: 'Medium Black Soil (Vertisol)',
    sowingDateLabel: 'When did you sow?',
    farmAreaLabel: 'Farm Area',
    farmAreaUnit: 'Hectares',
    saveFarmButton: 'Save Field Details',
    savingButton: 'Saving Field Details...',
    loadDemoButton: 'Fill Tukaram Demo Data (Beed)',
    editFarmButton: 'Edit / Change Field',
    
    // Decision Card
    loadingDecision: "Fetching today's advice...",
    errorDecisionTitle: "We couldn't get today's advice.",
    errorDecisionDesc: 'Please check your internet connection and try again.',
    noDataDecision: "No advice recorded for today yet.",
    dataSourceLabel: 'Data Source',
    audioButtonLabel: 'Audio',

    // What-If Simulation
    whatIfTitle: 'What if the weather changes?',
    whatIfSubtitle: "Adjust wind or rainfall to test how today's recommendation changes.",
    windSpeedLabel: 'Wind speed',
    rain36hLabel: 'Rain expected in next 36 hours',
    seeNewAdviceButton: 'See New Advice',
    checkingAdviceButton: 'Checking new advice...',
    resetWeatherButton: "Reset to Today's Weather",
    currentAdviceHeader: "Today's Advice",
    newAdviceHeader: 'New Advice if Conditions Change',
    recommendationFlippedTitle: 'Recommendation Changed!',
    recommendationSameTitle: 'The recommendation stays the same.',
    simErrorTitle: "We couldn't check the new advice.",
    whatIfOfflineNotice: "What-If simulation requires an active internet connection to contact the server.",

    // Explainability Drawer
    explainabilityTitle: "Why this advice?",
    explainabilitySubtitle: "Scientific parameters and arbitration rules backing today's decision.",
    soilSectionTitle: "🌱 Soil Moisture State",
    waterSectionTitle: "🌧️ Rain & Spray Window",
    windSectionTitle: "🌬️ Wind Conditions",
    pestSectionTitle: "🐛 Pest Emergence Risk",
    marketSectionTitle: "📈 Market Momentum",
    ruleTracesTitle: "📋 Decision Arbitration Log",
    closeDrawer: "Close Audit Panel",
    loadingExplainability: "Loading decision scientific breakdown...",
    errorExplainability: "Could not load decision explanation.",
    ruleTriggered: "Rule Triggered",
    ruleNotTriggered: "Rule Nominal",

    // Voice Player
    listenAudio: "Listen",
    playingAudio: "Playing...",
    pausedAudio: "Paused",
    stopAudio: "Stop",
    voiceNotAvailable: "Voice playback is not supported for this language on your device. You can read the advice above.",

    // Trends & Visualizations (Part 5 Demo Correction)
    trendsTitle: "Current Field & Market Metrics",
    trendsSubtitle: "Current soil water depletion, pest heat units, and mandi prices.",
    soilChartTitle: "Current Soil Water Status",
    soilChartSubtitle: "Current root-zone water depletion (mm) vs RAW threshold",
    pestChartTitle: "Current Pest Heat Status",
    pestChartSubtitle: "Accumulated degree-days (GDD) vs 450 GDD emergence threshold",
    marketChartTitle: "Current Mandi Price Status",
    marketChartSubtitle: "Daily modal price vs 7-day moving average (Beed APMC)",
    historicalNotice: "Historical trend data will build as daily advisory data is collected.",

    // Offline PWA Resilience
    offlineBannerTitle: "Offline Mode",
    offlineBannerDesc: "Showing your last saved advice. Connect to the internet to get live updates.",
    lastUpdatedLabel: "Last updated",

    // Validation & Messages
    farmSavedSuccess: 'Your field details have been saved successfully.',
    nameRequired: 'Please enter your name.',
    districtRequired: 'Please enter your district.',
    sowingDateRequired: 'Please select your sowing date.',
    areaInvalid: 'Please enter a valid farm area (at least 0.1 Hectares).',
    backendError: 'Could not save field details. Please check your connection and try again.',
    networkError: 'Network error. The backend server might be offline.',
    retry: 'Try Again',
  },
  mr: {
    brandName: 'कृषि कवच',
    tagline: 'शेतकरी निर्णय सहाय्य प्रणाली',
    greeting: 'नमस्कार, शेतकरी बांधवांनो',
    subHeading: 'तुमच्या शेतासाठी दैनंदिन मार्गदर्शन',
    myFarm: 'माझे शेत',
    todaysAdvice: 'आजचा सल्ला',
    whatIf: 'जर हवामान बदलले तर?',
    whyThisAdvice: 'का हा सल्ला?',
    doNotDoThis: 'आज हे करू नका',
    language: 'भाषा',
    offline: 'ऑफलाइन',
    online: 'ऑनलाइन',
    advicePlaceholder: 'तुमचा दैनिक सल्ला येथे दिसेल.',
    whatIfDesc: 'हवामानात बदल करून पाहा की सल्ला कसा बदलतो.',
    whyDesc: 'आजच्या सल्ल्यामागची पारदर्शक आकडेवारी समजून घ्या.',
    location: 'स्थान',
    district: 'जिल्हा',
    crop: 'पिक',
    sowingDate: 'पेरणी तारीख',
    soilType: 'मातीचा प्रकार',
    farmArea: 'शेताचे क्षेत्रफळ',
    
    // Onboarding
    onboardingTitle: 'तुमच्या शेताची नोंदणी करा',
    onboardingSubtitle: 'दैनंदिन सल्ला मिळवण्यासाठी शेताची माहिती भरा.',
    farmerNameLabel: 'शेतकऱ्याचे नाव',
    farmerNamePlaceholder: 'उदा. तुकाराम',
    districtLabel: 'जिल्हा / भाग',
    districtPlaceholder: 'उदा. बीड',
    useMyLocation: 'माझे सध्याचे स्थान वापरा',
    locationObtained: 'स्थान मिळाले',
    selectCropLabel: 'तुम्ही कोणते पीक घेतले आहे?',
    cropBtCotton: 'बीटी कापूस (Bt Cotton)',
    cropSoybean: 'सोयाबीन (Soybean)',
    selectSoilLabel: 'मातीचा प्रकार कोणता आहे?',
    soilMediumBlack: 'मध्यम काळी माती (Vertisol)',
    sowingDateLabel: 'पेरणी कधी केली होती?',
    farmAreaLabel: 'शेताचे क्षेत्रफळ',
    farmAreaUnit: 'हेक्टर',
    saveFarmButton: 'शेताची माहिती जतन करा',
    savingButton: 'माहिती जतन करत आहे...',
    loadDemoButton: 'तुकाराम डेमो माहिती भरा (बीड)',
    editFarmButton: 'माहिती बदला / नवीन शेत',
    
    // Decision Card
    loadingDecision: 'आजचा सल्ला मिळवत आहोत...',
    errorDecisionTitle: 'आजचा सल्ला मिळू शकला नाही.',
    errorDecisionDesc: 'कृपया तुमचे इंटरनेट तपासा आणि पुन्हा प्रयत्न करा.',
    noDataDecision: 'आजसाठी कोणतीही नोंद आढळली नाही.',
    dataSourceLabel: 'माहिती स्रोत',
    audioButtonLabel: 'ऐका',

    // What-If Simulation
    whatIfTitle: 'जर हवामान बदलले तर?',
    whatIfSubtitle: 'वारा किंवा पाऊस बदलून पाहा की सल्ला कसा बदलतो.',
    windSpeedLabel: 'वाऱ्याचा वेग',
    rain36hLabel: 'पुढील ३६ तासांत पाऊस',
    seeNewAdviceButton: 'नवीन सल्ला तपासा',
    checkingAdviceButton: 'नवीन सल्ला तपासत आहोत...',
    resetWeatherButton: 'मूळ हवामान',
    currentAdviceHeader: 'आजचा मूळ सल्ला',
    newAdviceHeader: 'हवामान बदलल्यास नवीन सल्ला',
    recommendationFlippedTitle: 'सल्ला बदलला!',
    recommendationSameTitle: 'सल्ला तोच राहील.',
    simErrorTitle: 'नवीन सल्ला तपासता आला नाही.',
    whatIfOfflineNotice: 'सिमुलेशनसाठी इंटरनेट कनेक्शन आवश्यक आहे.',

    // Explainability Drawer
    explainabilityTitle: 'का हा सल्ला?',
    explainabilitySubtitle: 'आजच्या निर्णयामागील वैज्ञानिक आकडेवारी आणि नियम.',
    soilSectionTitle: '🌱 जमिनीतील ओलावा स्थिती',
    waterSectionTitle: '🌧️ पाऊस आणि फवारणीची वेळ',
    windSectionTitle: '🌬️ वाऱ्याची स्थिती',
    pestSectionTitle: '🐛 कीड प्रादुर्भाव धोका',
    marketSectionTitle: '📈 बाजारभाव स्थिती',
    ruleTracesTitle: '📋 निर्णय प्रक्रिया ऑडिट',
    closeDrawer: 'बंद करा',
    loadingExplainability: 'वैज्ञानिक माहिती लोड होत आहे...',
    errorExplainability: 'सविस्तर माहिती लोड होऊ शकली नाही.',
    ruleTriggered: 'नियम लागू झाला',
    ruleNotTriggered: 'नियम सामान्य',

    // Voice Player
    listenAudio: 'ऐका',
    playingAudio: 'ऐकवत आहे...',
    pausedAudio: 'थांबवले',
    stopAudio: 'बंद करा',
    voiceNotAvailable: 'या उपकरणावर मराठी आवाज उपलब्ध नाही. तुम्ही वरील सल्ला वाचू शकता.',

    // Trends & Visualizations (Part 5 Demo Correction)
    trendsTitle: 'सध्याची शेतातील स्थिती आणि बाजारभाव दर्जा',
    trendsSubtitle: 'सध्याचा जमिनीतील ओलावा, कीड प्रमाण आणि बाजारभाव तपासा.',
    soilChartTitle: 'सध्याची जमिनीतील पाण्याची स्थिती (mm)',
    soilChartSubtitle: 'जमिनीतील पाण्याचा ताण विरुद्ध RAW मर्यादा',
    pestChartTitle: 'सध्याची कीड प्रादुर्भाव तापमान स्थिती (GDD)',
    pestChartSubtitle: 'एकत्रित GDD विरुद्ध ४५० GDD प्रादुर्भाव मर्यादा',
    marketChartTitle: 'सध्याचा बाजारभाव दर्जा (बीड APMC)',
    marketChartSubtitle: 'दैनिक बाजारभाव विरुद्ध ७ दिवसांची सरासरी',
    historicalNotice: 'दैनंदिन सल्ल्यांनुसार ऐतिहासिक आलेखाची नोंद हळूहळू तयार होईल.',

    // Offline PWA Resilience
    offlineBannerTitle: 'ऑफलाइन मोड',
    offlineBannerDesc: 'तुमचा शेवटचा जतन केलेला सल्ला दाखवत आहोत. थेट अपडेटसाठी इंटरनेट कनेक्ट करा.',
    lastUpdatedLabel: 'शेवटचे अपडेट',

    // Validation & Messages
    farmSavedSuccess: 'तुमच्या शेताची माहिती यशस्वीरित्या जतन झाली आहे.',
    nameRequired: 'कृपया तुमचे नाव टाका.',
    districtRequired: 'कृपया तुमचा जिल्हा टाका.',
    sowingDateRequired: 'कृपया पेरणीची तारीख निवडा.',
    areaInvalid: 'कृपया वैध क्षेत्रफळ टाका (किमान ०.१ हेक्टर).',
    backendError: 'माहिती जतन करता आली नाही. इंटरनेट तपासून पुन्हा प्रयत्न करा.',
    networkError: 'नेटवर्क त्रुटी. सर्व्हर बंद असू शकतो.',
    retry: 'पुन्हा प्रयत्न करा',
  },
  hi: {
    brandName: 'कृषि कवच',
    tagline: 'किसान निर्णय सहायता प्रणाली',
    greeting: 'नमस्कार, किसान भाई',
    subHeading: 'आपके खेत के लिए दैनिक मार्गदर्शन',
    myFarm: 'मेरा खेत',
    todaysAdvice: 'आज की सलाह',
    whatIf: 'अगर मौसम बदले तो?',
    whyThisAdvice: 'यह सलाह क्यों?',
    doNotDoThis: 'आज यह न करें',
    language: 'भाषा',
    offline: 'ऑफलाइन',
    online: 'ऑनलाइन',
    advicePlaceholder: 'आपकी दैनिक सलाह यहां दिखाई देगी।',
    whatIfDesc: 'मौसम की स्थिति बदलकर देखें कि सलाह कैसे बदलती है।',
    whyDesc: 'आज की सलाह के पीछे के पारदर्शी आंकड़ों को समझें।',
    location: 'स्थान',
    district: 'जिला',
    crop: 'फसल',
    sowingDate: 'बुआई तिथि',
    soilType: 'मिट्टी का प्रकार',
    farmArea: 'खेत का क्षेत्रफल',
    
    // Onboarding
    onboardingTitle: 'अपने खेत का विवरण दर्ज करें',
    onboardingSubtitle: 'दैनिक सलाह प्राप्त करने के लिए खेत की जानकारी भरें।',
    farmerNameLabel: 'किसान का नाम',
    farmerNamePlaceholder: 'जैसे तुकाराम',
    districtLabel: 'जिला / क्षेत्र',
    districtPlaceholder: 'जैसे बीड़',
    useMyLocation: 'मेरा वर्तमान स्थान उपयोग करें',
    locationObtained: 'स्थान मिल गया',
    selectCropLabel: 'आपने कौन सी फसल बोई है?',
    cropBtCotton: 'बीटी कपास (Bt Cotton)',
    cropSoybean: 'सोयाबीन (Soybean)',
    selectSoilLabel: 'मिट्टी का प्रकार क्या है?',
    soilMediumBlack: 'मध्यम काली मिट्टी (Vertisol)',
    sowingDateLabel: 'बुआई कब की थी?',
    farmAreaLabel: 'खेत का क्षेत्रफल',
    farmAreaUnit: 'हेक्टेयर',
    saveFarmButton: 'खेत की जानकारी सेव करें',
    savingButton: 'जानकारी सेव हो रही है...',
    loadDemoButton: 'तुकाराम डेमो डेटा भरें (बीड़)',
    editFarmButton: 'जानकारी बदलें / नया खेत',
    
    // Decision Card
    loadingDecision: 'आज की सलाह प्राप्त की जा रही है...',
    errorDecisionTitle: 'आज की सलाह प्राप्त नहीं हो सकी।',
    errorDecisionDesc: 'कृपया अपना इंटरनेट कनेक्शन जांचें और पुनः प्रयास करें।',
    noDataDecision: 'आज के लिए कोई सलाह उपलब्ध नहीं है।',
    dataSourceLabel: 'डेटा स्रोत',
    audioButtonLabel: 'ऑडियो',

    // What-If Simulation
    whatIfTitle: 'अगर मौसम बदले तो?',
    whatIfSubtitle: 'हवा की गति या बारिश बदलकर देखें कि आज की सलाह कैसे बदलती है।',
    windSpeedLabel: 'हवा की गति',
    rain36hLabel: 'अगले ३६ घंटों में बारिश',
    seeNewAdviceButton: 'नई सलाह देखें',
    checkingAdviceButton: 'नई सलाह देख रहे हैं...',
    resetWeatherButton: 'मूल मौसम',
    currentAdviceHeader: 'आज की मूल सलाह',
    newAdviceHeader: 'मौसम बदलने पर नई सलाह',
    recommendationFlippedTitle: 'सलाह बदल गई!',
    recommendationSameTitle: 'सलाह वही रहेगी।',
    simErrorTitle: 'नई सलाह नहीं देखी जा सकी।',
    whatIfOfflineNotice: 'सिमुलेशन के लिए इंटरनेट कनेक्शन आवश्यक है।',

    // Explainability Drawer
    explainabilityTitle: 'यह सलाह क्यों?',
    explainabilitySubtitle: 'आज के निर्णय के पीछे के वैज्ञानिक आंकड़े और नियम।',
    soilSectionTitle: '🌱 मिट्टी में नमी की स्थिति',
    waterSectionTitle: '🌧️ बारिश और छिड़काव का समय',
    windSectionTitle: '🌬️ हवा की स्थिति',
    pestSectionTitle: '🐛 कीट प्रकोप जोखिम',
    marketSectionTitle: '📈 मंडी भाव रुझान',
    ruleTracesTitle: '📋 निर्णय प्रक्रिया ऑडिट',
    closeDrawer: 'बंद करें',
    loadingExplainability: 'वैज्ञानिक विवरण लोड हो रहा है...',
    errorExplainability: 'विस्तृत जानकारी लोड नहीं हो सकी।',
    ruleTriggered: 'नियम लागू हुआ',
    ruleNotTriggered: 'नियम सामान्य',

    // Voice Player
    listenAudio: 'सुनें',
    playingAudio: 'सुनाया जा रहा है...',
    pausedAudio: 'रुका हुआ',
    stopAudio: 'बंद करें',
    voiceNotAvailable: 'आपके डिवाइस पर हिंदी वॉइस उपलब्ध नहीं है। आप ऊपर दी गई सलाह पढ़ सकते हैं।',

    // Trends & Visualizations (Part 5 Demo Correction)
    trendsTitle: 'वर्तमान खेत स्थिति और मंडी रुझान',
    trendsSubtitle: 'वर्तमान मिट्टी में नमी, कीट प्रकोप और मंडी भाव देखें।',
    soilChartTitle: 'वर्तमान मिट्टी में जल स्थिति (mm)',
    soilChartSubtitle: 'वर्तमान जल तनाव बनाम RAW सीमा',
    pestChartTitle: 'वर्तमान कीट प्रकोप स्थिति (GDD)',
    pestChartSubtitle: 'संचित GDD बनाम ४५० GDD प्रकोप सीमा',
    marketChartTitle: 'वर्तमान मंडी भाव स्थिति (बीड़ APMC)',
    marketChartSubtitle: 'दैनिक मंडी मूल्य बनाम ७-दिवसीय औसत',
    historicalNotice: 'दैनिक सलाह के साथ ऐतिहासिक रुझान डेटा धीरे-धीरे जमा होगा।',

    // Offline PWA Resilience
    offlineBannerTitle: 'ऑफलाइन मोड',
    offlineBannerDesc: 'आपकी पिछली सहेजी गई सलाह दिखाई जा रही है। लाइव अपडेट के लिए इंटरनेट कनेक्ट करें।',
    lastUpdatedLabel: 'अंतिम अपडेट',

    // Validation & Messages
    farmSavedSuccess: 'आपके खेत की जानकारी सफलतापूर्वक सेव हो गई है।',
    nameRequired: 'कृपया अपना नाम दर्ज करें।',
    districtRequired: 'कृपया अपना जिला दर्ज करें।',
    sowingDateRequired: 'कृपया बुआई की तारीख चुनें।',
    areaInvalid: 'कृपया सही क्षेत्रफल दर्ज करें (कम से कम 0.1 हेक्टेयर)।',
    backendError: 'जानकारी सेव नहीं हो सकी। कनेक्शन जांच कर पुनः प्रयास करें।',
    networkError: 'नेटवर्क त्रुटि। सर्वर बंद हो सकता है।',
    retry: 'पुनः प्रयास करें',
  },
};

interface LanguageContextType {
  language: Language;
  setLanguage: (lang: Language) => void;
  t: ShellTranslations;
}

const LanguageContext = createContext<LanguageContextType | undefined>(undefined);

const LANGUAGE_KEY = 'krishikavach_language';

export const LanguageProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [language, setLanguageState] = useState<Language>(() => {
    try {
      const saved = localStorage.getItem(LANGUAGE_KEY);
      if (saved === 'en' || saved === 'mr' || saved === 'hi') {
        return saved;
      }
    } catch {
      // Fallback
    }
    return 'mr'; // Default to Marathi
  });

  const setLanguage = (lang: Language) => {
    setLanguageState(lang);
    try {
      localStorage.setItem(LANGUAGE_KEY, lang);
    } catch {
      // Ignore
    }
  };

  return (
    <LanguageContext.Provider value={{ language, setLanguage, t: translations[language] }}>
      {children}
    </LanguageContext.Provider>
  );
};

export const useLanguage = (): LanguageContextType => {
  const context = useContext(LanguageContext);
  if (!context) {
    throw new Error('useLanguage must be used within a LanguageProvider');
  }
  return context;
};
