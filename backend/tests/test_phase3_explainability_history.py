"""
Phase 3 Tests — Explainability Enhancement & Decision History
Verifies:
1. Explainability endpoint HTTP 200 response & presentation structures (why, why_not, conflicts, inputs, provenance).
2. Decision history endpoint GET /api/v1/decision/history/{plot_id} ordering & plot isolation.
3. History limit validation (1 <= limit <= 100).
4. What-changed diff engine against previous decision for the same plot.
5. 100% determinism of explainability output across repeated calls.
"""

import pytest
from datetime import datetime, timezone, timedelta
from sqlalchemy.orm import Session

from backend.models.db_models import DBPlot, DBDecisionRecord
from backend.schemas.contracts import (
    SoilState,
    PestState,
    WeatherForecast,
    MarketState,
    ExplainabilityDetails
)
from backend.engines.arbitration import arbitrate_daily_plan


def test_explainability_endpoint_returns_200_and_presentation_fields(client):
    """Verify GET /api/v1/explainability/{decision_id} returns HTTP 200 with structured why, why_not, conflicts, inputs."""
    res_dec = client.get("/api/v1/decision/daily/tukaram_beed_01")
    assert res_dec.status_code == 200
    dec_data = res_dec.json()
    exp_id = dec_data["explainability_id"]

    res_exp = client.get(f"/api/v1/explainability/{exp_id}")
    assert res_exp.status_code == 200
    exp_data = res_exp.json()

    assert "summary" in exp_data and exp_data["summary"] is not None
    assert exp_data["summary"]["primary_action"] == dec_data["primary_action"]
    assert exp_data["summary"]["critical_prohibition"] == dec_data["critical_prohibition"]

    assert "why" in exp_data and exp_data["why"] is not None
    assert isinstance(exp_data["why"]["selected_rules"], list)
    assert len(exp_data["why"]["selected_rules"]) > 0

    assert "why_not" in exp_data and isinstance(exp_data["why_not"], list)
    assert "conflicts" in exp_data and isinstance(exp_data["conflicts"], list)
    assert "inputs" in exp_data and exp_data["inputs"] is not None
    assert "soil" in exp_data["inputs"]
    assert "weather" in exp_data["inputs"]
    assert "pest" in exp_data["inputs"]
    assert "market" in exp_data["inputs"]
    assert "model_provenance" in exp_data and exp_data["model_provenance"] is not None


def test_decision_history_endpoint_and_limit_validation(client, db_session: Session):
    """Verify GET /api/v1/decision/history/{plot_id} ordering, plot isolation, and limit validation."""
    plot_a = "plot_history_test_a"
    plot_b = "plot_history_test_b"

    now = datetime.now(timezone.utc)
    for i in range(5):
        rec_a = DBDecisionRecord(
            decision_id=f"dec_a_{i}",
            plot_id=plot_a,
            date="2026-09-04",
            primary_action=f"Action A {i}",
            critical_prohibition="PROHIBITION A",
            scientific_rationale="Rationale A",
            confidence_indicator="Live Open-Meteo",
            explainability_id=f"exp_a_{i}",
            explainability_json="{}",
            created_at=now + timedelta(minutes=i)
        )
        rec_b = DBDecisionRecord(
            decision_id=f"dec_b_{i}",
            plot_id=plot_b,
            date="2026-09-04",
            primary_action=f"Action B {i}",
            critical_prohibition="PROHIBITION B",
            scientific_rationale="Rationale B",
            confidence_indicator="Live Open-Meteo",
            explainability_id=f"exp_b_{i}",
            explainability_json="{}",
            created_at=now + timedelta(minutes=i)
        )
        db_session.add(rec_a)
        db_session.add(rec_b)
    db_session.commit()

    # Query history for plot_a
    res = client.get(f"/api/v1/decision/history/{plot_a}?limit=3")
    assert res.status_code == 200
    items = res.json()
    assert len(items) == 3
    # Check newest first (index 4 created last -> Action A 4)
    assert items[0]["decision_id"] == "dec_a_4"
    assert items[1]["decision_id"] == "dec_a_3"
    assert items[2]["decision_id"] == "dec_a_2"
    # Ensure no plot_b items present
    for item in items:
        assert item["plot_id"] == plot_a

    # Test limit validation: limit = 0 (invalid) -> HTTP 422
    res_bad1 = client.get(f"/api/v1/decision/history/{plot_a}?limit=0")
    assert res_bad1.status_code == 422

    # Test limit validation: limit = 101 (invalid) -> HTTP 422
    res_bad2 = client.get(f"/api/v1/decision/history/{plot_a}?limit=101")
    assert res_bad2.status_code == 422


def test_what_changed_diff_engine_first_vs_second_decision(client, db_session: Session):
    """Verify first decision has empty what_changed and second decision correctly identifies differences."""
    plot_id = "plot_diff_test_01"
    now = datetime.now(timezone.utc)

    # 1. Insert first decision record (high wind speed 18.0 km/h)
    soil = SoilState(crop_type="bt_cotton", depletion_mm=10.0, raw_mm=50.0, taw_mm=100.0, moisture_status="MOISTURE_ADEQUATE", volumetric_water_content=0.25)
    pest = PestState(crop_type="bt_cotton", pest_name="pink_bollworm", accumulated_gdd=500.0, gdd_threshold=450.0, risk_triggered=True)
    weather1 = WeatherForecast(date="2026-09-04", temp_max=32.0, temp_min=22.0, temp_mean=27.0, rain_next_12h_mm=0.0, rain_next_24h_mm=0.0, rain_next_36h_mm=0.0, rain_prob_next_6h=10.0, wind_speed_kmh=18.0, wind_gust_kmh=22.0, et0_mm=5.0, humidity_percent=60.0, source="live_api")
    market = MarketState(crop_type="bt_cotton", mandi_name="Beed APMC", modal_price_inr=7200.0, sma_7_inr=7000.0, price_momentum_percent=2.8, trend="FAVORABLE")

    card1, exp1 = arbitrate_daily_plan(plot_id, "2026-09-04", soil, pest, weather1, market)

    rec1 = DBDecisionRecord(
        decision_id=card1.decision_id,
        plot_id=plot_id,
        date="2026-09-04",
        primary_action=card1.primary_action,
        critical_prohibition=card1.critical_prohibition,
        scientific_rationale=card1.scientific_rationale,
        confidence_indicator=card1.confidence_indicator,
        explainability_id=card1.explainability_id,
        explainability_json=exp1.model_dump_json(),
        created_at=now
    )
    db_session.add(rec1)
    db_session.commit()

    # Check explainability for first decision (should have empty what_changed)
    res1 = client.get(f"/api/v1/explainability/{card1.decision_id}")
    assert res1.status_code == 200
    data1 = res1.json()
    assert data1["previous_decision"] is None
    assert len(data1["what_changed"]) == 0

    # 2. Insert second decision record (low wind speed 8.0 km/h -> prohibition removed)
    weather2 = WeatherForecast(date="2026-09-04", temp_max=32.0, temp_min=22.0, temp_mean=27.0, rain_next_12h_mm=0.0, rain_next_24h_mm=0.0, rain_next_36h_mm=0.0, rain_prob_next_6h=10.0, wind_speed_kmh=8.0, wind_gust_kmh=10.0, et0_mm=5.0, humidity_percent=60.0, source="live_api")

    card2, exp2 = arbitrate_daily_plan(plot_id, "2026-09-04", soil, pest, weather2, market)

    rec2 = DBDecisionRecord(
        decision_id=card2.decision_id,
        plot_id=plot_id,
        date="2026-09-04",
        primary_action=card2.primary_action,
        critical_prohibition=card2.critical_prohibition,
        scientific_rationale=card2.scientific_rationale,
        confidence_indicator=card2.confidence_indicator,
        explainability_id=card2.explainability_id,
        explainability_json=exp2.model_dump_json(),
        created_at=now + timedelta(minutes=5)
    )
    db_session.add(rec2)
    db_session.commit()

    # Check explainability for second decision (should detect wind speed change & prohibition flip)
    res2 = client.get(f"/api/v1/explainability/{card2.decision_id}")
    assert res2.status_code == 200
    data2 = res2.json()
    assert data2["previous_decision"] is not None
    assert data2["previous_decision"]["decision_id"] == card1.decision_id

    changes = data2["what_changed"]
    assert len(changes) > 0
    changed_fields = [c["field"] for c in changes]
    assert "wind_speed_kmh" in changed_fields
    assert "critical_prohibition" in changed_fields
    assert "primary_action" in changed_fields


def test_identical_consecutive_decisions_produce_no_false_changes(client, db_session: Session):
    """Verify that identical consecutive decisions for the same plot produce empty what_changed."""
    plot_id = "plot_identical_test_01"
    now = datetime.now(timezone.utc)

    soil = SoilState(crop_type="bt_cotton", depletion_mm=10.0, raw_mm=50.0, taw_mm=100.0, moisture_status="MOISTURE_ADEQUATE", volumetric_water_content=0.25)
    pest = PestState(crop_type="bt_cotton", pest_name="pink_bollworm", accumulated_gdd=300.0, gdd_threshold=450.0, risk_triggered=False)
    weather = WeatherForecast(date="2026-09-04", temp_max=30.0, temp_min=20.0, temp_mean=25.0, rain_next_12h_mm=0.0, rain_next_24h_mm=0.0, rain_next_36h_mm=0.0, rain_prob_next_6h=5.0, wind_speed_kmh=10.0, wind_gust_kmh=12.0, et0_mm=4.5, humidity_percent=55.0, source="live_api")
    market = MarketState(crop_type="bt_cotton", mandi_name="Beed APMC", modal_price_inr=7000.0, sma_7_inr=7000.0, price_momentum_percent=0.0, trend="NEUTRAL")

    card1, exp1 = arbitrate_daily_plan(plot_id, "2026-09-04", soil, pest, weather, market)
    rec1 = DBDecisionRecord(
        decision_id=card1.decision_id, plot_id=plot_id, date="2026-09-04",
        primary_action=card1.primary_action, critical_prohibition=card1.critical_prohibition,
        scientific_rationale=card1.scientific_rationale, confidence_indicator=card1.confidence_indicator,
        explainability_id=card1.explainability_id, explainability_json=exp1.model_dump_json(),
        created_at=now
    )
    db_session.add(rec1)
    db_session.commit()

    card2, exp2 = arbitrate_daily_plan(plot_id, "2026-09-04", soil, pest, weather, market)
    rec2 = DBDecisionRecord(
        decision_id=card2.decision_id, plot_id=plot_id, date="2026-09-04",
        primary_action=card2.primary_action, critical_prohibition=card2.critical_prohibition,
        scientific_rationale=card2.scientific_rationale, confidence_indicator=card2.confidence_indicator,
        explainability_id=card2.explainability_id, explainability_json=exp2.model_dump_json(),
        created_at=now + timedelta(minutes=1)
    )
    db_session.add(rec2)
    db_session.commit()

    res = client.get(f"/api/v1/explainability/{card2.decision_id}")
    assert res.status_code == 200
    data = res.json()
    assert len(data["what_changed"]) == 0


def test_explainability_determinism_100_runs():
    """Verify explainability structures remain 100% deterministic across 100 iterations."""
    soil = SoilState(crop_type="bt_cotton", depletion_mm=60.0, raw_mm=50.0, taw_mm=100.0, moisture_status="MOISTURE_STRESS", volumetric_water_content=0.18)
    pest = PestState(crop_type="bt_cotton", pest_name="pink_bollworm", accumulated_gdd=500.0, gdd_threshold=450.0, risk_triggered=True)
    weather = WeatherForecast(date="2026-09-04", temp_max=32.0, temp_min=22.0, temp_mean=27.0, rain_next_12h_mm=0.0, rain_next_24h_mm=0.0, rain_next_36h_mm=30.0, rain_prob_next_6h=80.0, wind_speed_kmh=18.0, wind_gust_kmh=24.0, et0_mm=5.0, humidity_percent=70.0, source="live_api")
    market = MarketState(crop_type="bt_cotton", mandi_name="Beed APMC", modal_price_inr=7200.0, sma_7_inr=7000.0, price_momentum_percent=2.8, trend="FAVORABLE")

    _, base_exp = arbitrate_daily_plan("plot_det_test", "2026-09-04", soil, pest, weather, market)
    base_summary = base_exp.summary.model_dump()
    base_conflicts = [c.model_dump() for c in base_exp.conflicts]
    base_why_not = [w.model_dump() for w in base_exp.why_not]

    for _ in range(100):
        _, exp = arbitrate_daily_plan("plot_det_test", "2026-09-04", soil, pest, weather, market)
        assert exp.summary.model_dump() == base_summary
        assert [c.model_dump() for c in exp.conflicts] == base_conflicts
        assert [w.model_dump() for w in exp.why_not] == base_why_not
