"""
Downstream Translation Service & API Tests
Verifies Marathi/Hindi vernacular translation accuracy, parameter validation,
preservation of decision semantics and numeric metrics, and error boundary safety.
"""

import re
import pytest
from backend.schemas.contracts import DecisionCard

@pytest.fixture
def sample_decision_card():
    return DecisionCard(
        decision_id="dec_test_12345",
        plot_id="tukaram_beed_01",
        date="2026-09-04",
        primary_action="Clear field drainage trenches immediately and deploy biological pheromone traps",
        critical_prohibition="DO NOT IRRIGATE OR APPLY CHEMICAL SPRAYS TODAY",
        scientific_rationale="Soil depletion is 48.0mm (RAW threshold: 45.0mm), but 28.0mm precipitation is forecast within 36 hours (threshold: 25.0mm). Pink Bollworm emergence threshold reached (462 GDD >= 450 GDD), but sustained wind speed (18.5 km/h) exceeds safe spraying limit (15.0 km/h). Chemical spraying will cause severe drift off-target. Market price for bt_cotton at Beed APMC is favorable (7450 INR/q, +3.5% vs 7-day average).",
        confidence_indicator="Data Freshness: Demo Fixture",
        explainability_id="exp_test_12345"
    )

@pytest.fixture
def user_manual_test_card():
    return DecisionCard(
        decision_id="dec_manual_001",
        plot_id="tukaram_beed_01",
        date="2026-09-04",
        primary_action="Clear drainage channels and check bund outlets.",
        critical_prohibition="DO NOT IRRIGATE OR APPLY CHEMICAL SPRAYS TODAY.",
        scientific_rationale="Heavy rain (28mm) expected in 36 hrs; wind speed is 19 km/h.",
        confidence_indicator="Demo Fixture",
        explainability_id="exp_manual_001"
    )

def test_translation_exact_user_manual_payload_mr(client, user_manual_test_card):
    # REGRESSION TEST: Exact payload from user manual test
    payload = {
        "decision_card": user_manual_test_card.model_dump(),
        "target_language": "mr"
    }

    response = client.post("/api/v1/translate", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert data["decision_id"] == "dec_manual_001"
    assert "mr" in data["translations"]
    assert "hi" not in data["translations"]

    mr_trans = data["translations"]["mr"]

    # 1. Assert Devanagari text is present in all 3 fields
    devanagari_pattern = re.compile(r'[\u0900-\u097F]')
    assert devanagari_pattern.search(mr_trans["primary_action"]) is not None
    assert devanagari_pattern.search(mr_trans["critical_prohibition"]) is not None
    assert devanagari_pattern.search(mr_trans["scientific_rationale"]) is not None

    # 2. Assert output is NOT identical to English input
    assert mr_trans["primary_action"] != user_manual_test_card.primary_action
    assert mr_trans["critical_prohibition"] != user_manual_test_card.critical_prohibition
    assert mr_trans["scientific_rationale"] != user_manual_test_card.scientific_rationale

    # 3. Assert numeric values are strictly preserved
    assert "28" in mr_trans["scientific_rationale"]
    assert "36" in mr_trans["scientific_rationale"]
    assert "19" in mr_trans["scientific_rationale"]

def test_translation_exact_user_manual_payload_hi(client, user_manual_test_card):
    payload = {
        "decision_card": user_manual_test_card.model_dump(),
        "target_language": "hi"
    }

    response = client.post("/api/v1/translate", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert data["decision_id"] == "dec_manual_001"
    assert "hi" in data["translations"]
    assert "mr" not in data["translations"]

    hi_trans = data["translations"]["hi"]

    # 1. Assert Devanagari text is present in all 3 fields
    devanagari_pattern = re.compile(r'[\u0900-\u097F]')
    assert devanagari_pattern.search(hi_trans["primary_action"]) is not None
    assert devanagari_pattern.search(hi_trans["critical_prohibition"]) is not None
    assert devanagari_pattern.search(hi_trans["scientific_rationale"]) is not None

    # 2. Assert output is NOT identical to English input
    assert hi_trans["primary_action"] != user_manual_test_card.primary_action
    assert hi_trans["critical_prohibition"] != user_manual_test_card.critical_prohibition
    assert hi_trans["scientific_rationale"] != user_manual_test_card.scientific_rationale

    # 3. Assert numeric values are strictly preserved
    assert "28" in hi_trans["scientific_rationale"]
    assert "36" in hi_trans["scientific_rationale"]
    assert "19" in hi_trans["scientific_rationale"]

def test_no_leftover_english_fragments_in_rationale(sample_decision_card):
    from backend.services.llm_service import translate_decision_card
    translations = translate_decision_card(sample_decision_card, ["mr", "hi"])

    # Disallowed English words in translated rationale (allowed: units GDD, mm, km/h, INR/q, %, RAW, APMC, Beed)
    disallowed_english = [
        "Chemical", "spraying", "cause", "severe", "drift", "off-target",
        "Market", "price", "favorable", "average", "emergence", "threshold",
        "sustained", "exceeds", "limit", "depletion", "precipitation", "forecast"
    ]

    for lang in ["mr", "hi"]:
        rationale = translations[lang]["scientific_rationale"]
        for word in disallowed_english:
            assert word not in rationale, f"Leftover English word '{word}' found in {lang} rationale: {rationale}"

def test_translation_unsupported_language_returns_422(client, user_manual_test_card):
    # Unsupported language 'fr' must return HTTP 422
    payload = {
        "decision_card": user_manual_test_card.model_dump(),
        "target_language": "fr"
    }
    response = client.post("/api/v1/translate", json=payload)
    assert response.status_code == 422

    # Array of unsupported languages ['fr', 'de']
    payload_arr = {
        "decision_card": user_manual_test_card.model_dump(),
        "target_languages": ["fr", "de"]
    }
    response_arr = client.post("/api/v1/translate", json=payload_arr)
    assert response_arr.status_code == 422

def test_numeric_metrics_and_semantics_preserved(sample_decision_card):
    # Direct service check ensuring numbers (48.0, 45.0, 28.0, 36, 462, 450, 18.5, 15.0) are strictly preserved
    from backend.services.llm_service import translate_decision_card
    translations = translate_decision_card(sample_decision_card, ["mr", "hi"])

    for lang in ["mr", "hi"]:
        rationale = translations[lang]["scientific_rationale"]
        assert "48.0" in rationale
        assert "45.0" in rationale
        assert "28.0" in rationale
        assert "462" in rationale
        assert "450" in rationale
        assert "18.5" in rationale
        assert "15.0" in rationale

def test_translation_failure_does_not_mutate_decision_card(user_manual_test_card):
    # Finalized DecisionCard fields must remain 100% intact even if translation function runs
    from backend.services.llm_service import translate_decision_card

    orig_action = user_manual_test_card.primary_action
    orig_prohibition = user_manual_test_card.critical_prohibition
    orig_rationale = user_manual_test_card.scientific_rationale

    translate_decision_card(user_manual_test_card, ["mr", "hi"])

    assert user_manual_test_card.primary_action == orig_action
    assert user_manual_test_card.critical_prohibition == orig_prohibition
    assert user_manual_test_card.scientific_rationale == orig_rationale
