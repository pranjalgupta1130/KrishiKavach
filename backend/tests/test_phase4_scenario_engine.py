"""
Phase 4 Tests — What-If / Scenario Engine
Verifies:
1. Valid nested override returns HTTP 200 with enriched comparison metadata.
2. Wind and rain overrides reach central arbitration engine.
3. Strict validation: unknown fields, negative numbers, rain prob > 100, and NaN/Infinity return HTTP 422.
4. Causal chain verification for 19 -> 8 km/h wind scenario (is_flipped == True).
5. Causal chain verification for 19 -> 18 km/h wind scenario (is_flipped == False).
6. Hydrological rain forecast threshold boundary testing.
7. Multiple simultaneous overrides in one request.
8. Simulation performs ZERO database writes (record count unchanged).
9. 100-run determinism test.
"""

import pytest
import math
from backend.models.db_models import DBDecisionRecord

def test_valid_nested_override_returns_200(client):
    """Verify POST /api/v1/decision/simulate with valid nested overrides returns HTTP 200."""
    payload = {
        "plot_id": "tukaram_beed_01",
        "overrides": {
            "wind_speed_kmh": 8.0,
            "rain_next_36h_mm": 0.0
        }
    }
    res = client.post("/api/v1/decision/simulate", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["plot_id"] == "tukaram_beed_01"
    assert "wind_speed_kmh" in data["overrides_applied"]
    assert data["overrides_applied"]["wind_speed_kmh"]["simulated"] == 8.0
    assert "triggered_rules_before" in data
    assert "triggered_rules_after" in data
    assert "rule_changes" in data


def test_wind_override_reaches_arbitration(client):
    """Verify wind override reaches central arbitration engine and updates structured decision state."""
    payload = {
        "plot_id": "tukaram_beed_01",
        "overrides": {"wind_speed_kmh": 5.0}
    }
    res = client.post("/api/v1/decision/simulate", json=payload)
    assert res.status_code == 200
    data = res.json()

    # 1. Structured override tracking check
    assert "wind_speed_kmh" in data["overrides_applied"]
    assert data["overrides_applied"]["wind_speed_kmh"]["simulated"] == 5.0

    # 2. Structured rule change and prohibition check
    if "RULE_PEST_WIND_01" in data["triggered_rules_before"]:
        assert "RULE_PEST_WIND_01" not in data["triggered_rules_after"]
        rc_map = {rc["rule_id"]: rc for rc in data["rule_changes"]}
        assert "RULE_PEST_WIND_01" in rc_map
        assert rc_map["RULE_PEST_WIND_01"]["previous"] is True
        assert rc_map["RULE_PEST_WIND_01"]["simulated"] is False
        assert "DO NOT SPRAY PESTICIDES OR CHEMICALS" not in data["simulated_decision"]["critical_prohibition"]


def test_rain_override_reaches_arbitration(client):
    """Verify 36h rain override reaches arbitration and populates overrides_applied."""
    payload = {
        "plot_id": "tukaram_beed_01",
        "overrides": {"rain_next_36h_mm": 35.0}
    }
    res = client.post("/api/v1/decision/simulate", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert "rain_next_36h_mm" in data["overrides_applied"]
    assert data["overrides_applied"]["rain_next_36h_mm"]["simulated"] == 35.0


def test_unsupported_override_field_rejected(client):
    """Verify unknown override fields are rejected with HTTP 422 instead of being silently ignored."""
    payload = {
        "plot_id": "tukaram_beed_01",
        "overrides": {
            "wind_speed_kmh": 8.0,
            "invalid_unknown_parameter": 999.0
        }
    }
    res = client.post("/api/v1/decision/simulate", json=payload)
    assert res.status_code == 422


def test_negative_wind_speed_rejected(client):
    """Verify negative wind speed returns HTTP 422."""
    payload = {
        "plot_id": "tukaram_beed_01",
        "overrides": {"wind_speed_kmh": -5.0}
    }
    res = client.post("/api/v1/decision/simulate", json=payload)
    assert res.status_code == 422


def test_invalid_rain_probability_rejected(client):
    """Verify rain probability > 100 returns HTTP 422."""
    payload = {
        "plot_id": "tukaram_beed_01",
        "overrides": {"rain_prob_next_6h": 105.0}
    }
    res = client.post("/api/v1/decision/simulate", json=payload)
    assert res.status_code == 422


def test_nan_override_value_rejected(client):
    """Verify NaN override value returns HTTP 422."""
    payload = {
        "plot_id": "tukaram_beed_01",
        "overrides": {"wind_speed_kmh": "NaN"}
    }
    res = client.post("/api/v1/decision/simulate", json=payload)
    assert res.status_code == 422


def test_positive_infinity_override_value_rejected(client):
    """Verify positive Infinity override value returns HTTP 422."""
    payload = {
        "plot_id": "tukaram_beed_01",
        "overrides": {"wind_speed_kmh": "Infinity"}
    }
    res = client.post("/api/v1/decision/simulate", json=payload)
    assert res.status_code == 422


def test_negative_infinity_override_value_rejected(client):
    """Verify negative Infinity override value returns HTTP 422."""
    payload = {
        "plot_id": "tukaram_beed_01",
        "overrides": {"wind_speed_kmh": "-Infinity"}
    }
    res = client.post("/api/v1/decision/simulate", json=payload)
    assert res.status_code == 422


def test_causal_chain_wind_flip_19_to_8(client):
    """
    Verify complete causal chain for wind 19 -> 8 km/h demo scenario:
    - wind > 15 before, wind <= 15 after
    - RULE_PEST_WIND_01 triggered before
    - RULE_PEST_WIND_01 not triggered after
    - spray prohibition present before
    - spray prohibition removed after
    - is_flipped == True
    """
    payload = {
        "plot_id": "tukaram_beed_01",
        "overrides": {
            "wind_speed_kmh": 8.0,
            "rain_next_36h_mm": 0.0
        }
    }
    res = client.post("/api/v1/decision/simulate", json=payload)
    assert res.status_code == 200
    data = res.json()

    # 1. Causal rule check
    assert "RULE_PEST_WIND_01" in data["triggered_rules_before"]
    assert "RULE_PEST_WIND_01" not in data["triggered_rules_after"]

    # 2. Causal prohibition check
    assert "DO NOT" in data["original_decision"]["critical_prohibition"]
    assert "NO CRITICAL PROHIBITIONS" in data["simulated_decision"]["critical_prohibition"]

    # 3. Decision flip flag
    assert data["is_flipped"] is True

    # 4. Deterministic flip reason contains boundary reference
    assert "15.0 km/h" in data["flip_reason"] or "spray-safe limit" in data["flip_reason"]


def test_causal_chain_wind_no_flip_19_to_18(client):
    """
    Verify causal chain for wind 19 -> 18 km/h scenario:
    - RULE_PEST_WIND_01 remains triggered
    - spray prohibition remains
    - primary action & prohibition remain materially unchanged
    - is_flipped == False
    """
    payload = {
        "plot_id": "tukaram_beed_01",
        "overrides": {
            "wind_speed_kmh": 18.0
        }
    }
    res = client.post("/api/v1/decision/simulate", json=payload)
    assert res.status_code == 200
    data = res.json()

    assert "RULE_PEST_WIND_01" in data["triggered_rules_before"]
    assert "RULE_PEST_WIND_01" in data["triggered_rules_after"]
    assert "DO NOT" in data["simulated_decision"]["critical_prohibition"]
    assert data["is_flipped"] is False
    assert "remains above the configured spray-safe limit" in data["flip_reason"] or "18.0 km/h" in data["flip_reason"]


def test_hydrological_rain_override_outcome(client):
    """Verify 36h rain override crossing 25mm threshold suppresses irrigation when moisture stressed (depletion >= RAW 78mm)."""
    payload = {
        "plot_id": "tukaram_beed_01",
        "overrides": {
            "soil_depletion_mm": 80.0,
            "rain_next_36h_mm": 30.0
        }
    }
    res = client.post("/api/v1/decision/simulate", json=payload)
    assert res.status_code == 200
    data = res.json()

    assert "RULE_HYDRO_01" in data["triggered_rules_after"]
    assert "DO NOT IRRIGATE" in data["simulated_decision"]["critical_prohibition"]


def test_multiple_overrides_evaluated_together(client):
    """Verify multiple overrides (wind + rain + soil + gdd) evaluated in a single simulated state."""
    payload = {
        "plot_id": "tukaram_beed_01",
        "overrides": {
            "wind_speed_kmh": 8.0,
            "rain_next_36h_mm": 0.0,
            "soil_depletion_mm": 80.0,
            "accumulated_gdd": 500.0
        }
    }
    res = client.post("/api/v1/decision/simulate", json=payload)
    assert res.status_code == 200
    data = res.json()

    ov = data["overrides_applied"]
    assert "wind_speed_kmh" in ov
    assert "rain_next_36h_mm" in ov
    assert "soil_depletion_mm" in ov
    assert "accumulated_gdd" in ov


def test_rule_changes_correctly_identified(client):
    """Verify rule_changes list contains exact before/after trigger statuses."""
    payload = {
        "plot_id": "tukaram_beed_01",
        "overrides": {
            "wind_speed_kmh": 8.0,
            "rain_next_36h_mm": 0.0
        }
    }
    res = client.post("/api/v1/decision/simulate", json=payload)
    assert res.status_code == 200
    data = res.json()

    rc_map = {rc["rule_id"]: rc for rc in data["rule_changes"]}
    assert "RULE_PEST_WIND_01" in rc_map
    assert rc_map["RULE_PEST_WIND_01"]["previous"] is True
    assert rc_map["RULE_PEST_WIND_01"]["simulated"] is False


def test_simulation_performs_zero_db_writes(client, db_session):
    """Verify running a What-If simulation does NOT insert DBDecisionRecord or alter history count."""
    count_before = db_session.query(DBDecisionRecord).count()

    payload = {
        "plot_id": "tukaram_beed_01",
        "overrides": {
            "wind_speed_kmh": 8.0,
            "rain_next_36h_mm": 0.0
        }
    }
    res = client.post("/api/v1/decision/simulate", json=payload)
    assert res.status_code == 200

    count_after = db_session.query(DBDecisionRecord).count()
    assert count_before == count_after


def test_history_remains_unchanged_after_simulation(client, db_session):
    """Verify plot decision history API returns the exact same list before and after simulation."""
    # Ensure baseline decision exists in DB
    client.get("/api/v1/decision/daily/tukaram_beed_01")
    history_before = client.get("/api/v1/decision/history/tukaram_beed_01").json()

    # Run What-If simulation
    sim_res = client.post("/api/v1/decision/simulate", json={
        "plot_id": "tukaram_beed_01",
        "overrides": {"wind_speed_kmh": 5.0}
    })
    assert sim_res.status_code == 200

    history_after = client.get("/api/v1/decision/history/tukaram_beed_01").json()
    assert history_before == history_after


def test_scenario_determinism_repeated_runs(client):
    """Verify 100 consecutive scenario simulation calls return identical substantive outputs."""
    payload = {
        "plot_id": "tukaram_beed_01",
        "overrides": {
            "wind_speed_kmh": 8.0,
            "rain_next_36h_mm": 0.0
        }
    }

    res1 = client.post("/api/v1/decision/simulate", json=payload)
    assert res1.status_code == 200
    base_data = res1.json()

    for _ in range(100):
        res = client.post("/api/v1/decision/simulate", json=payload)
        assert res.status_code == 200
        d = res.json()
        assert d["simulated_decision"]["primary_action"] == base_data["simulated_decision"]["primary_action"]
        assert d["simulated_decision"]["critical_prohibition"] == base_data["simulated_decision"]["critical_prohibition"]
        assert d["is_flipped"] == base_data["is_flipped"]
        assert d["triggered_rules_before"] == base_data["triggered_rules_before"]
        assert d["triggered_rules_after"] == base_data["triggered_rules_after"]
        assert d["rule_changes"] == base_data["rule_changes"]
        assert d["flip_reason"] == base_data["flip_reason"]
