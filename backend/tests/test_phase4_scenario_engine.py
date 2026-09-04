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


def test_causal_chain_safe_wind_removes_wind_rule(client):
    """Verify Safe Wind override (wind = 8 km/h) removes RULE_PEST_WIND_01."""
    payload = {
        "plot_id": "tukaram_beed_01",
        "overrides": {"wind_speed_kmh": 8.0}
    }
    res = client.post("/api/v1/decision/simulate", json=payload)
    assert res.status_code == 200
    data = res.json()

    assert "RULE_PEST_WIND_01" in data["triggered_rules_before"]
    assert "RULE_PEST_WIND_01" not in data["triggered_rules_after"]
    rc_map = {rc["rule_id"]: rc for rc in data["rule_changes"]}
    assert "RULE_PEST_WIND_01" in rc_map
    assert rc_map["RULE_PEST_WIND_01"]["previous"] is True
    assert rc_map["RULE_PEST_WIND_01"]["simulated"] is False
    assert data["is_flipped"] is True


def test_causal_chain_clear_rain_removes_hydro_rule(client):
    """Verify Clear Rain override (36h = 0, 12h = 0, 6h prob = 0) removes RULE_HYDRO_01 and allows RULE_HYDRO_02."""
    payload = {
        "plot_id": "tukaram_beed_01",
        "overrides": {
            "rain_next_36h_mm": 0.0,
            "rain_next_12h_mm": 0.0,
            "rain_prob_next_6h": 0.0
        }
    }
    res = client.post("/api/v1/decision/simulate", json=payload)
    assert res.status_code == 200
    data = res.json()

    assert "RULE_HYDRO_01" in data["triggered_rules_before"]
    assert "RULE_HYDRO_01" not in data["triggered_rules_after"]
    assert "RULE_HYDRO_02" in data["triggered_rules_after"]
    rc_map = {rc["rule_id"]: rc for rc in data["rule_changes"]}
    assert "RULE_HYDRO_01" in rc_map
    assert rc_map["RULE_HYDRO_01"]["previous"] is True
    assert rc_map["RULE_HYDRO_01"]["simulated"] is False
    assert data["is_flipped"] is True


def test_causal_chain_combined_safe_wind_and_clear_rain(client):
    """Verify Combined Safe Wind (8 km/h) + Clear Rain (0 mm) removes both blocking rules, triggers approval rules, and produces unprohibited decision card."""
    payload = {
        "plot_id": "tukaram_beed_01",
        "overrides": {
            "wind_speed_kmh": 8.0,
            "rain_next_36h_mm": 0.0,
            "rain_next_12h_mm": 0.0,
            "rain_prob_next_6h": 0.0
        }
    }
    res = client.post("/api/v1/decision/simulate", json=payload)
    assert res.status_code == 200
    data = res.json()

    assert "RULE_HYDRO_01" in data["triggered_rules_before"]
    assert "RULE_PEST_WIND_01" in data["triggered_rules_before"]

    assert "RULE_HYDRO_01" not in data["triggered_rules_after"]
    assert "RULE_PEST_WIND_01" not in data["triggered_rules_after"]
    assert "RULE_HYDRO_02" in data["triggered_rules_after"]
    assert "RULE_PEST_SPRAY_OK" in data["triggered_rules_after"]

    assert "NO CRITICAL PROHIBITIONS" in data["simulated_decision"]["critical_prohibition"]
    assert data["is_flipped"] is True
    assert data["simulated_decision"]["primary_action"] != data["original_decision"]["primary_action"]


def test_simulation_does_not_return_baseline_on_threshold_crossing_override(client):
    """Guardrail test: Fails if simulation returns exact baseline decision despite threshold-crossing override."""
    payload = {
        "plot_id": "tukaram_beed_01",
        "overrides": {
            "wind_speed_kmh": 8.0,
            "rain_next_36h_mm": 0.0,
            "rain_next_12h_mm": 0.0,
            "rain_prob_next_6h": 0.0
        }
    }
    res = client.post("/api/v1/decision/simulate", json=payload)
    assert res.status_code == 200
    data = res.json()

    orig = data["original_decision"]
    sim = data["simulated_decision"]

    assert sim["primary_action"] != orig["primary_action"], "Simulated primary_action must differ from baseline!"
    assert sim["critical_prohibition"] != orig["critical_prohibition"], "Simulated critical_prohibition must differ from baseline!"
    assert data["is_flipped"] is True, "is_flipped must be True when thresholds are crossed!"


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


# -----------------------------------------------------------------------------
# Refined 2-Tier Model Tests: Cases A through G Specification Matrix
# -----------------------------------------------------------------------------

def test_case_a_high_wind_low_pest_gdd(client):
    """Case A: Wind 40 km/h, GDD 34 (pest not triggered). RULE_ENV_WIND_SAFETY + RULE_ENV_RAIN_SAFETY + RULE_HYDRO_01 trigger, is_flipped == True."""
    res = client.post("/api/v1/decision/simulate", json={
        "plot_id": "tukaram_beed_01",
        "overrides": {
            "wind_speed_kmh": 40.0,
            "accumulated_gdd": 34.0
        }
    })
    assert res.status_code == 200
    data = res.json()
    assert "RULE_ENV_WIND_SAFETY" in data["triggered_rules_after"]
    assert "RULE_ENV_RAIN_SAFETY" in data["triggered_rules_after"]
    assert "RULE_HYDRO_01" in data["triggered_rules_after"]
    assert data["simulated_decision"]["critical_prohibition"] == "DO NOT IRRIGATE TODAY; DO NOT SPRAY CHEMICALS (HIGH WIND DRIFT & RAIN WASH-OFF RISK)"
    assert data["is_flipped"] is True


def test_case_b_high_wind_high_pest_gdd(client):
    """Case B: Wind 40 km/h, GDD 500 (pest triggered). RULE_PEST_WIND_01 triggers, decision identical to baseline (is_flipped == False)."""
    res = client.post("/api/v1/decision/simulate", json={
        "plot_id": "tukaram_beed_01",
        "overrides": {
            "wind_speed_kmh": 40.0,
            "accumulated_gdd": 500.0
        }
    })
    assert res.status_code == 200
    data = res.json()
    assert "RULE_PEST_WIND_01" in data["triggered_rules_after"]
    assert "RULE_HYDRO_01" in data["triggered_rules_after"]
    assert data["simulated_decision"]["primary_action"] == data["original_decision"]["primary_action"]
    assert data["simulated_decision"]["critical_prohibition"] == data["original_decision"]["critical_prohibition"]
    assert data["is_flipped"] is False


def test_case_c_safe_wind_high_pest_gdd_clear_rain(client):
    """Case C: Wind 8 km/h, GDD 500, Rain 0 mm. Triggers RULE_PEST_SPRAY_OK and RULE_HYDRO_02 (is_flipped == True)."""
    res = client.post("/api/v1/decision/simulate", json={
        "plot_id": "tukaram_beed_01",
        "overrides": {
            "wind_speed_kmh": 8.0,
            "accumulated_gdd": 500.0,
            "rain_next_36h_mm": 0.0,
            "rain_next_12h_mm": 0.0,
            "rain_prob_next_6h": 0.0
        }
    })
    assert res.status_code == 200
    data = res.json()
    assert "RULE_PEST_SPRAY_OK" in data["triggered_rules_after"]
    assert "RULE_HYDRO_02" in data["triggered_rules_after"]
    assert data["is_flipped"] is True


def test_case_d_heavy_rain_adequate_soil_low_gdd_high_wind(client):
    """Case D: Rain 60 mm, Depletion 0 mm, GDD 34, Wind 18.5 km/h. Triggers RULE_ENV_RAIN_SAFETY + RULE_ENV_WIND_SAFETY (is_flipped == True)."""
    res = client.post("/api/v1/decision/simulate", json={
        "plot_id": "tukaram_beed_01",
        "overrides": {
            "rain_next_36h_mm": 60.0,
            "soil_depletion_mm": 0.0,
            "accumulated_gdd": 34.0,
            "wind_speed_kmh": 18.5
        }
    })
    assert res.status_code == 200
    data = res.json()
    assert "RULE_ENV_RAIN_SAFETY" in data["triggered_rules_after"]
    assert "RULE_ENV_WIND_SAFETY" in data["triggered_rules_after"]
    assert "RULE_HYDRO_01" not in data["triggered_rules_after"]
    assert data["simulated_decision"]["critical_prohibition"] == "DO NOT SPRAY CHEMICALS (HIGH WIND DRIFT & RAIN WASH-OFF RISK)"
    assert data["is_flipped"] is True


def test_case_e_heavy_rain_stressed_soil_high_gdd_high_wind(client):
    """Case E: Rain 60 mm, Depletion 120 mm, GDD 1170, Wind 18.5 km/h. Triggers RULE_HYDRO_01 + RULE_PEST_WIND_01 (is_flipped == False)."""
    res = client.post("/api/v1/decision/simulate", json={
        "plot_id": "tukaram_beed_01",
        "overrides": {
            "rain_next_36h_mm": 60.0
        }
    })
    assert res.status_code == 200
    data = res.json()
    assert "RULE_HYDRO_01" in data["triggered_rules_after"]
    assert "RULE_PEST_WIND_01" in data["triggered_rules_after"]
    assert data["simulated_decision"]["primary_action"] == data["original_decision"]["primary_action"]
    assert data["simulated_decision"]["critical_prohibition"] == data["original_decision"]["critical_prohibition"]
    assert data["is_flipped"] is False


def test_case_f_clear_rain_stressed_soil_low_gdd_safe_wind(client):
    """Case F: Rain 0 mm, Depletion 120 mm, GDD 34, Wind 8 km/h. Triggers RULE_HYDRO_02 + weather safe (is_flipped == True)."""
    res = client.post("/api/v1/decision/simulate", json={
        "plot_id": "tukaram_beed_01",
        "overrides": {
            "rain_next_36h_mm": 0.0,
            "rain_next_12h_mm": 0.0,
            "rain_prob_next_6h": 0.0,
            "soil_depletion_mm": 120.0,
            "accumulated_gdd": 34.0,
            "wind_speed_kmh": 8.0
        }
    })
    assert res.status_code == 200
    data = res.json()
    assert "RULE_HYDRO_02" in data["triggered_rules_after"]
    assert "NO CRITICAL PROHIBITIONS" in data["simulated_decision"]["critical_prohibition"]
    assert data["is_flipped"] is True


def test_case_g_safe_wind_clear_rain_high_gdd_stressed_soil(client):
    """Case G: Wind 8 km/h, Rain 0 mm, GDD 500, Depletion 120 mm. Triggers RULE_HYDRO_02 + RULE_PEST_SPRAY_OK (is_flipped == True)."""
    res = client.post("/api/v1/decision/simulate", json={
        "plot_id": "tukaram_beed_01",
        "overrides": {
            "wind_speed_kmh": 8.0,
            "rain_next_36h_mm": 0.0,
            "rain_next_12h_mm": 0.0,
            "rain_prob_next_6h": 0.0,
            "accumulated_gdd": 500.0,
            "soil_depletion_mm": 120.0
        }
    })
    assert res.status_code == 200
    data = res.json()
    assert "RULE_HYDRO_02" in data["triggered_rules_after"]
    assert "RULE_PEST_SPRAY_OK" in data["triggered_rules_after"]
    assert data["is_flipped"] is True

