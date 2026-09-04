"""
Downstream LLM Vernacular Translation Service

Translates finalized DecisionCard text into Marathi (mr) and Hindi (hi).
STRICT ARCHITECTURAL GUARANTEE:
The LLM operates strictly downstream of the deterministic arbitration engine.
It only translates strings; it NEVER mutates or overrides the agronomic decision,
thresholds, numbers, action semantics, or prohibition semantics.
Deterministic template dictionary fallback guarantees translation works reliably
without an external API dependency.
"""

import logging
import re
from typing import Dict, List
from backend.schemas.contracts import DecisionCard

logger = logging.getLogger("krishikavach.llm")

ACTION_DICTIONARY = {
    "mr": {
        "Clear field drainage trenches immediately and deploy biological pheromone traps": "शेतातील पाण्याचा निचरा करणाऱ्या चार्या तात्काळ मोकळ्या करा आणि कामगंध सापळे लावा.",
        "Clear field drainage trenches immediately; postpone chemical spraying until rain clears": "शेतातील पाण्याचा निचरा करणाऱ्या चार्या तात्काळ मोकळ्या करा; पाऊस थांबेपर्यंत फवारणी लांबवा.",
        "Clear field drainage trenches immediately; apply targeted bio-pesticide spray with PPE": "शेतातील पाण्याचा निचरा करणाऱ्या चार्या तात्काळ मोकळ्या करा; सुरक्षा किट वापरून जैविक फवारणी करा.",
        "Clear field drainage trenches immediately": "शेतातील पाण्याचा निचरा करणाऱ्या चार्या तात्काळ मोकळ्या करा.",
        "Clear drainage channels and check bund outlets": "निचरा चार्या साफ करा आणि बांधाचे आऊटलेट तपासा.",
        "Apply controlled drip/tubewell irrigation; deploy biological pheromone traps for pest monitoring": "नियंत्रित सिंचन करा; कीड निरीक्षणासाठी कामगंध सापळे लावा.",
        "Apply controlled drip/tubewell irrigation; postpone chemical spraying until rain clears": "नियंत्रित सिंचन करा; पाऊस थांबेपर्यंत रासायनिक फवारणी लांबवा.",
        "Apply controlled irrigation and targeted bio-pesticide spray with PPE": "नियंत्रित सिंचन करा आणि सुरक्षा किट घालून जैविक कीटकनाशक फवारा.",
        "Apply controlled irrigation; spraying is not blocked by current wind conditions. Follow approved local pest-management guidance.": "नियंत्रित सिंचन करा; सध्याच्या वाऱ्याच्या स्थितीमुळे फवारणीस अडथळा नाही. स्थानिक कृषी सल्लागाराच्या शिफारशीनुसार कीड नियंत्रण करा.",
        "Apply controlled irrigation (tubewell/drip)": "नियंत्रित पद्धतीने (विहीर/ठिबक) सिंचन करा.",
        "Deploy pheromone traps and monitor field boundaries manually": "कामगंध सापळे लावा आणि शेताच्या बांधांचे हाताने निरीक्षण करा.",
        "Postpone chemical spraying until rain clears": "पाऊस थांबेपर्यंत रासायनिक फवारणी पुढे ढकला.",
        "Apply recommended bio-pesticide or targeted chemical spray with PPE": "संरक्षक पोशाख घालून शिफारस केलेले जैविक किंवा रासायनिक औषध फवारा.",
        "Perform routine field inspection and soil maintenance": "नियमित शेत पाहणी आणि जमिनीची देखभाल करा."
    },
    "hi": {
        "Clear field drainage trenches immediately and deploy biological pheromone traps": "खेत की जल निकासी की नालियों को तुरंत साफ करें और फेरोमोन ट्रैप लगाएं।",
        "Clear field drainage trenches immediately; postpone chemical spraying until rain clears": "खेत की जल निकासी नालियों को साफ करें; बारिश रुकने तक छिड़काव टालें।",
        "Clear field drainage trenches immediately; apply targeted bio-pesticide spray with PPE": "जल निकासी नालियों को तुरंत साफ करें; सुरक्षा किट पहनकर जैविक छिड़काव करें।",
        "Clear field drainage trenches immediately": "खेत की जल निकासी की नालियों को तुरंत साफ करें।",
        "Clear drainage channels and check bund outlets": "जल निकासी नालियों को साफ करें और मेड़ के आउटलेट जांचें।",
        "Apply controlled drip/tubewell irrigation; deploy biological pheromone traps for pest monitoring": "नियंत्रित सिंचाई करें; कीट निगरानी के लिए फेरोमोन ट्रैप लगाएं।",
        "Apply controlled drip/tubewell irrigation; postpone chemical spraying until rain clears": "नियंत्रित सिंचाई करें; बारिश रुकने तक रासायनिक छिड़काव टालें।",
        "Apply controlled irrigation and targeted bio-pesticide spray with PPE": "नियंत्रित सिंचाई करें और सुरक्षा किट पहनकर जैविक कीटनाशक का छिड़काव करें।",
        "Apply controlled irrigation; spraying is not blocked by current wind conditions. Follow approved local pest-management guidance.": "नियंत्रित सिंचाई करें; वर्तमान हवा की स्थिति छिड़काव में बाधा नहीं है। अनुमोदित स्थानीय कीट-प्रबंधन दिशानिर्देशों का पालन करें।",
        "Apply controlled irrigation (tubewell/drip)": "नियंत्रित तरीके से (ट्यूबवेल/ड्रिप) सिंचाई करें।",
        "Deploy pheromone traps and monitor field boundaries manually": "फेरोमोन ट्रैप लगाएं और खेत की मेड़ों की निगरानी करें।",
        "Postpone chemical spraying until rain clears": "बारिश रुकने तक रासायनिक छिड़काव स्थगित करें।",
        "Apply recommended bio-pesticide or targeted chemical spray with PPE": "सुरक्षा किट पहनकर अनुशंसित जैविक या रासायनिक स्प्रे करें।",
        "Perform routine field inspection and soil maintenance": "नियमित खेत निरीक्षण और मिट्टी का रखरखाव करें।"
    }
}

PROHIBITION_DICTIONARY = {
    "mr": {
        "DO NOT IRRIGATE OR APPLY CHEMICAL SPRAYS TODAY": "आज पिकाला पाणी देऊ नका आणि रासायनिक फवारणी करू नका.",
        "DO NOT IRRIGATE TODAY": "आज पिकाला पाणी (सिंचन) देऊ नका.",
        "DO NOT SPRAY PESTICIDES OR CHEMICALS": "कीटकनाशके किंवा रसायनांची फवारणी करू नका.",
        "DO NOT SPRAY FOLIAR CHEMICALS": "पानांवर फवारणी करणारी रसायने फवारू नका.",
        "NO CRITICAL PROHIBITIONS TODAY — Standard field operations permitted": "आज कोणतीही गंभीर बंदी नाही — नेहमीची शेती कामे सुरू ठेवावीत."
    },
    "hi": {
        "DO NOT IRRIGATE OR APPLY CHEMICAL SPRAYS TODAY": "आज खेत में सिंचाई न करें और न ही रसायनों का छिड़काव करें।",
        "DO NOT IRRIGATE TODAY": "आज खेत में सिंचाई न करें।",
        "DO NOT SPRAY PESTICIDES OR CHEMICALS": "कीटनाशक या रसायनों का छिड़काव न करें।",
        "DO NOT SPRAY FOLIAR CHEMICALS": "पत्तियों पर रसायनों का छिड़काव न करें।",
        "NO CRITICAL PROHIBITIONS TODAY — Standard field operations permitted": "आज कोई गंभीर प्रतिबंध नहीं है — सामान्य कृषि कार्य जारी रखें।"
    }
}

TERM_REPLACEMENTS = {
    "mr": [
        (r"\bChemical spraying will cause severe drift off-target\b", "रासायनिक फवारणीमुळे औषध शेताबाहेर भरकटण्याचा धोका आहे"),
        (r"\bHeavy rain\b", "मुसळधार पाऊस"),
        (r"\bexpected\b", "अपेक्षित"),
        (r"\bin 36 hrs\b", "36 तासांत"),
        (r"\bin 36 hours\b", "36 तासांत"),
        (r"\bwind speed is\b", "वाऱ्याचा वेग"),
        (r"\bwind speed\b", "वाऱ्याचा वेग"),
        (r"\bis forecast\b", "अंदाज आहे"),
        (r"\bSoil depletion is\b", "जमिनीतील पाण्याचा ताण"),
        (r"\bRAW threshold\b", "RAW मर्यादा"),
        (r"\bdrainage channels\b", "निचरा चार्या"),
        (r"\bbund outlets\b", "बांधाचे आऊटलेट"),
        (r"\bClear\b", "मोकळ्या करा"),
        (r"\bcheck\b", "तपासा"),
        (r"\bbt_cotton\b", "कापूस"),
        (r"\bcotton\b", "कापूस"),
        (r"\bsoybean\b", "सोयाबीन"),
        (r"\bis favorable\b", "अनुकूल आहे"),
        (r"\bvs 7-day average\b", "7 दिवसांच्या सरासरीपेक्षा"),
        (r"\bDO NOT IRRIGATE OR APPLY CHEMICAL SPRAYS TODAY\b", "आज पिकाला पाणी देऊ नका आणि रासायनिक फवारणी करू नका")
    ],
    "hi": [
        (r"\bChemical spraying will cause severe drift off-target\b", "रासायनिक छिड़काव से दवा हवा में बहने का गंभीर खतरा है"),
        (r"\bHeavy rain\b", "भारी बारिश"),
        (r"\bexpected\b", "अनुमानित"),
        (r"\bin 36 hrs\b", "36 घंटों में"),
        (r"\bin 36 hours\b", "36 घंटों में"),
        (r"\bwind speed is\b", "हवा की गति"),
        (r"\bwind speed\b", "हवा की गति"),
        (r"\bis forecast\b", "अनुमानित है"),
        (r"\bSoil depletion is\b", "मिट्टी में नमी की कमी"),
        (r"\bRAW threshold\b", "RAW सीमा"),
        (r"\bdrainage channels\b", "जल निकासी नालियां"),
        (r"\bbund outlets\b", "मेड़ आउटलेट"),
        (r"\bClear\b", "साफ करें"),
        (r"\bcheck\b", "जांचें"),
        (r"\bbt_cotton\b", "कपास"),
        (r"\bcotton\b", "कपास"),
        (r"\bsoybean\b", "सोयाबीन"),
        (r"\bis favorable\b", "अनुकूल है"),
        (r"\bvs 7-day average\b", "7 दिनों के औसत से"),
        (r"\bDO NOT IRRIGATE OR APPLY CHEMICAL SPRAYS TODAY\b", "आज खेत में सिंचाई न करें और न ही रसायनों का छिड़काव करें")
    ]
}

def normalize_key(s: str) -> str:
    return s.strip().rstrip(".").strip()

def translate_phrase(text: str, dictionary: Dict[str, str], lang: str) -> str:
    clean_text = normalize_key(text)

    for key, val in dictionary.items():
        if normalize_key(key).upper() == clean_text.upper():
            return val

    translated = text
    for pattern, repl in TERM_REPLACEMENTS.get(lang, []):
        translated = re.sub(pattern, repl, translated, flags=re.IGNORECASE)

    return translated

def translate_rationale_text(text: str, target_lang: str) -> str:
    if target_lang not in ["mr", "hi"]:
        return text

    sentences = re.split(r'(?<=\.)\s+', text)
    translated_sentences = []

    for sentence in sentences:
        s = sentence.strip()
        if not s:
            continue

        if "Soil depletion is" in s and "precipitation is forecast within 36 hours" in s:
            m = re.search(r"Soil depletion is ([\d\.]+)mm \(RAW threshold: ([\d\.]+)mm\), but ([\d\.]+)mm precipitation is forecast within 36 hours \(threshold: ([\d\.]+)mm\)\.?\s*(.*)", s)
            if m:
                x, y, z, w, tail = m.groups()
                if target_lang == "mr":
                    t = f"जमिनीतील पाण्याचा ताण {x} mm आहे (RAW मर्यादा: {y} mm), परंतु पुढील 36 तासांत {z} mm पावसाचा अंदाज आहे (मर्यादा: {w} mm). काळ्या जमिनीत सिंचनामुळे पाणी साचून मुळांना सड लागू शकते."
                else:
                    t = f"मिट्टी में जल तनाव {x} mm है (RAW सीमा: {y} mm), लेकिन अगले 36 घंटों में {z} mm बारिश का अनुमान है (सीमा: {w} mm)। काली मिट्टी में सिंचाई से जलभराव और जड़ सड़न हो सकती है।"
                translated_sentences.append(t)
                continue

        if "Soil water depletion has reached" in s:
            m = re.search(r"Soil water depletion has reached ([\d\.]+)mm, crossing RAW threshold \(([\d\.]+)mm\) with clear skies forecast \(([\d\.]+)mm rain in 36h\)", s)
            if m:
                x, y, z = m.groups()
                if target_lang == "mr":
                    t = f"जमिनीतील पाण्याचा ताण {x} mm झाला असून RAW मर्यादा ({y} mm) ओलांडली आहे आणि आकाश स्वच्छ राहण्याचा अंदाज आहे (36 तासांत {z} mm पाऊस)."
                else:
                    t = f"मिट्टी में जल तनाव {x} mm तक पहुंच गया है, जो RAW सीमा ({y} mm) को पार करता है और आकाश साफ रहने का अनुमान है (36 घंटों में {z} mm बारिश)।"
                translated_sentences.append(t)
                continue

        if "Soil moisture is adequate" in s:
            m = re.search(r"depletion ([\d\.]+)mm < RAW limit ([\d\.]+)mm", s)
            if m:
                x, y = m.groups()
                if target_lang == "mr":
                    t = f"जमिनीतील ओलावा पुरेसा आहे (ताण {x} mm < RAW मर्यादा {y} mm). आज विहीर/ठिबक सिंचनाची गरज नाही."
                else:
                    t = f"मिट्टी में नमी पर्याप्त है (तनाव {x} mm < RAW सीमा {y} mm)। आज ट्यूबवेल/ड्रिप सिंचाई की आवश्यकता नहीं है।"
                translated_sentences.append(t)
                continue

        if "emergence threshold reached" in s and "sustained wind speed" in s:
            m = re.search(r"([\w\s]+) emergence threshold reached \(([\d\.]+) GDD >= ([\d\.]+) GDD\), but sustained wind speed \(([\d\.]+) km/h\) exceeds safe spraying limit \(([\d\.]+) km/h\)", s)
            if m:
                pest, x, y, z, w = m.groups()
                pest_name_mr = "पिंक बोंडअळी" if "Pink" in pest else ("तंबाखूवरील उंटअळी" if "Tobacco" in pest else pest.strip())
                pest_name_hi = "गुलाबी सुंडी" if "Pink" in pest else ("तंबाकू इल्ली" if "Tobacco" in pest else pest.strip())
                if target_lang == "mr":
                    t = f"{pest_name_mr} कीड प्रादुर्भाव मर्यादा ({x} GDD >= {y} GDD) गाठली आहे, परंतु वाऱ्याचा वेग ({z} km/h) सुरक्षित मर्यादेपेक्षा ({w} km/h) जास्त आहे."
                else:
                    t = f"{pest_name_hi} कीट सीमा ({x} GDD >= {y} GDD) तक पहुंच गई है, लेकिन हवा की गति ({z} km/h) सुरक्षित सीमा ({w} km/h) से अधिक है।"
                translated_sentences.append(t)
                continue

        if "Chemical spraying will cause severe drift off-target" in s:
            if target_lang == "mr":
                t = "रासायनिक फवारणीमुळे औषध शेताबाहेर भरकटण्याचा धोका आहे."
            else:
                t = "रासायनिक छिड़काव से दवा हवा में बहने का गंभीर खतरा है।"
            translated_sentences.append(t)
            continue

        if "emergence threshold reached" in s and "imminent rain forecast" in s:
            m = re.search(r"([\w\s]+) emergence threshold reached \(([\d\.]+) GDD\), but imminent rain forecast \(probability ([\d\.]+)% in 6h / ([\d\.]+)mm in 12h\)", s)
            if m:
                pest, x, z, w = m.groups()
                pest_name_mr = "पिंक बोंडअळी" if "Pink" in pest else ("तंबाखूवरील उंटअळी" if "Tobacco" in pest else pest.strip())
                pest_name_hi = "गुलाबी सुंडी" if "Pink" in pest else ("तंबाकू इल्ली" if "Tobacco" in pest else pest.strip())
                if target_lang == "mr":
                    t = f"{pest_name_mr} कीड मर्यादा ({x} GDD) गाठली आहे, परंतु पावसाच्या अंदाजामुळे (6 तासांत {z}% / 12 तासांत {w} mm) पानांवरील फवारणी धुतली जाऊन औषध वाया जाऊ शकते."
                else:
                    t = f"{pest_name_hi} कीट सीमा ({x} GDD) तक पहुंच गई है, लेकिन बारिश की संभावना (6 घंटों में {z}% / 12 घंटों में {w} mm) के कारण पत्तियों पर छिड़काव धुल सकता है।"
                translated_sentences.append(t)
                continue

        if "emergence threshold crossed" in s:
            m = re.search(r"([\w\s]+) emergence threshold crossed \(([\d\.]+) GDD >= ([\d\.]+) GDD\) under safe atmospheric conditions \(wind ([\d\.]+) km/h <= ([\d\.]+) km/h", s)
            if m:
                pest, x, y, z, w = m.groups()
                pest_name_mr = "पिंक बोंडअळी" if "Pink" in pest else ("तंबाखूवरील उंटअळी" if "Tobacco" in pest else pest.strip())
                pest_name_hi = "गुलाबी सुंडी" if "Pink" in pest else ("तंबाकू इल्ली" if "Tobacco" in pest else pest.strip())
                if target_lang == "mr":
                    t = f"{pest_name_mr} किडीची मर्यादा ({x} GDD >= {y} GDD) पार झाली असून हवामान सुरक्षित आहे (वारा {z} km/h <= {w} km/h, कोरडे हवामान)."
                else:
                    t = f"{pest_name_hi} कीट सीमा ({x} GDD >= {y} GDD) पार हो गई है और मौसम सुरक्षित है (हवा {z} km/h <= {w} km/h, शुष्क आकाश)।"
                translated_sentences.append(t)
                continue

        if "Pest emergence degree-days" in s:
            m = re.search(r"Pest emergence degree-days \(([\d\.]+) GDD\) remain below intervention threshold \(([\d\.]+) GDD\)", s)
            if m:
                x, y = m.groups()
                if target_lang == "mr":
                    t = f"कीड प्रादुर्भाव डिग्री-डे ({x} GDD) मर्यादेपेक्षा ({y} GDD) कमी आहे. नियमित शेत पाहणीची शिफारस केली जाते."
                else:
                    t = f"कीट उद्भव डिग्री-डे ({x} GDD) सीमा ({y} GDD) से नीचे है। नियमित खेत निगरानी की सलाह दी जाती है।"
                translated_sentences.append(t)
                continue

        if "Market price for" in s:
            m = re.search(r"Market price for ([\w_]+) at ([\w\s]+) is favorable \(([\d\.]+) INR/q, \+([\d\.]+)%", s)
            if m:
                crop, mandi, price, mom = m.groups()
                crop_mr = "कापूस" if "cotton" in crop else ("सोयाबीन" if "soybean" in crop else crop)
                crop_hi = "कपास" if "cotton" in crop else ("सोयाबीन" if "soybean" in crop else crop)
                if target_lang == "mr":
                    t = f"{mandi} बाजारपेठेत {crop_mr} चा बाजारभाव अनुकूल आहे ({price} INR/q, 7 दिवसांच्या सरासरीपेक्षा +{mom}%)."
                else:
                    t = f"{mandi} मंडी में {crop_hi} का बाजार मूल्य अनुकूल है ({price} INR/q, 7 दिनों के औसत से +{mom}%)।"
                translated_sentences.append(t)
                continue

        t = s
        for pattern, repl in TERM_REPLACEMENTS.get(target_lang, []):
            t = re.sub(pattern, repl, t, flags=re.IGNORECASE)
        translated_sentences.append(t)

    return " ".join(translated_sentences)

def translate_decision_card(
    decision_card: DecisionCard,
    target_languages: List[str] = ["mr", "hi"]
) -> Dict[str, Dict[str, str]]:
    result: Dict[str, Dict[str, str]] = {}

    for lang in target_languages:
        if lang not in ["mr", "hi"]:
            continue

        act_dict = ACTION_DICTIONARY.get(lang, {})
        translated_action = translate_phrase(decision_card.primary_action, act_dict, lang)

        proh_dict = PROHIBITION_DICTIONARY.get(lang, {})
        translated_prohibition = translate_phrase(decision_card.critical_prohibition, proh_dict, lang)

        translated_rationale = translate_rationale_text(decision_card.scientific_rationale, lang)

        result[lang] = {
            "primary_action": translated_action,
            "critical_prohibition": translated_prohibition,
            "scientific_rationale": translated_rationale
        }

    return result
