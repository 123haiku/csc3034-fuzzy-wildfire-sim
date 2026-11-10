"""Unit tests for Wildfire Fuzzy Controller."""

import pytest
import sys
import os

import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from fuzzy_system.controller import WildfireFuzzyController


@pytest.fixture
def controller():
    return WildfireFuzzyController()


def test_mild_scenario_returns_low_risk(controller):
    """Mild temperature and high humidity should yield low wildfire risk."""
    out = controller.compute(temperature=15.0, humidity=85.0, wind_speed=10.0, vegetation_dryness=20.0)
    assert out["fire_risk_index"] < 40.0
    assert out["alert_level"] in [0, 1]


def test_extreme_scenario_returns_critical_risk(controller):
    """Extreme heat, low humidity, severe winds, and dry brush should trigger critical hazard."""
    out = controller.compute(temperature=48.0, humidity=10.0, wind_speed=80.0, vegetation_dryness=95.0)
    assert out["fire_risk_index"] > 75.0
    assert out["alert_level"] >= 2
    assert out["patrol_urgency_speed"] > 70.0


def test_monotonicity_temperature(controller):
    """Holding other variables constant, rising temperature should not decrease risk."""
    out_low = controller.compute(temperature=18.0, humidity=40.0, wind_speed=30.0, vegetation_dryness=50.0)
    out_high = controller.compute(temperature=42.0, humidity=40.0, wind_speed=30.0, vegetation_dryness=50.0)
    assert out_high["fire_risk_index"] >= out_low["fire_risk_index"]


def test_moderate_scenario_returns_watch_alert(controller):
    """Moderate heat and dryness should produce a watch-level assessment."""
    out = controller.compute(temperature=30.0, humidity=50.0, wind_speed=35.0, vegetation_dryness=55.0)
    assert 30.0 <= out["fire_risk_index"] < 60.0
    assert out["alert_level"] == 1
    assert out["alert_name"] == "WATCH"


def test_high_wind_scenario_returns_warning(controller):
    """High wind combined with dry vegetation should produce a warning."""
    out = controller.compute(temperature=30.0, humidity=50.0, wind_speed=85.0, vegetation_dryness=70.0)
    assert out["fire_risk_index"] >= 60.0
    assert out["alert_level"] >= 2
    assert out["patrol_urgency_speed"] > 40.0


def test_high_temperature_with_low_humidity_returns_critical_alert(controller):
    """High temperature and low humidity should trigger an urgent response."""
    out = controller.compute(temperature=45.0, humidity=20.0, wind_speed=30.0, vegetation_dryness=60.0)
    assert out["fire_risk_index"] > 80.0
    assert out["alert_level"] == 3
    assert out["patrol_urgency_speed"] > 80.0


@pytest.mark.parametrize(
    "temperature, humidity, wind_speed, vegetation_dryness, expected_alert",
    [
        (0.0, 0.0, 0.0, 0.0, "NORMAL"),
        (50.0, 100.0, 100.0, 100.0, "CRITICAL"),
    ],
)
def test_boundary_inputs_are_handled(controller, temperature, humidity, wind_speed, vegetation_dryness, expected_alert):
    """The controller should handle the inclusive limits of every input range."""
    out = controller.compute(
        temperature=temperature,
        humidity=humidity,
        wind_speed=wind_speed,
        vegetation_dryness=vegetation_dryness,
    )
    assert 0.0 <= out["fire_risk_index"] <= 100.0
    assert 0.0 <= out["patrol_urgency_speed"] <= 100.0
    assert out["alert_name"] == expected_alert


# ---------------------------------------------------------------------------
# Suppression alert as a third fuzzy consequent
# ---------------------------------------------------------------------------


def test_alert_output_is_a_fuzzy_consequent(controller):
    """The alert level must come from a defuzzified membership set on [0, 3]."""
    assert "advisory" in controller.mf_alert
    assert "watch" in controller.mf_alert
    assert "warning" in controller.mf_alert
    assert "evacuate" in controller.mf_alert
    assert controller.x_alert[0] == 0 and controller.x_alert[-1] == 3
    for name, mf in controller.mf_alert.items():
        assert mf.shape == controller.x_alert.shape, name
        assert 0.0 <= mf.max() <= 1.0


def test_alert_output_is_continuous(controller):
    """Alert output must vary between integer tiers, not snap onto them."""
    graded = [
        controller.compute(temperature=20.0 + 1.5 * i, humidity=70.0 - 3.0 * i,
                           wind_speed=10.0 + 4.0 * i, vegetation_dryness=20.0 + 5.0 * i)
        for i in range(12)
    ]
    values = [r["suppression_alert_level"] for r in graded]
    assert values == sorted(values), "alert output must be monotone in the ramp"
    fractional = [v for v in values if abs(v - round(v)) > 0.02]
    assert fractional, f"alert output never graded: {values}"


def test_alert_output_agrees_with_risk_output(controller):
    """Risk and alert are separate consequents but must not contradict each other."""
    for temp, hum, wind, fuel in [
        (16.0, 88.0, 10.0, 15.0),
        (28.0, 55.0, 25.0, 45.0),
        (34.0, 30.0, 50.0, 72.0),
        (46.0, 12.0, 75.0, 95.0),
    ]:
        out = controller.compute(temperature=temp, humidity=hum, wind_speed=wind, vegetation_dryness=fuel)
        if out["fire_risk_index"] < 40.0:
            assert out["alert_level"] == 0, out
        if out["fire_risk_index"] > 85.0:
            assert out["alert_level"] == 3, out


def test_alert_tier_tracks_continuous_value(controller):
    """The discrete tier is the nearest integer band of the fuzzy alert output."""
    for temp in (10.0, 25.0, 33.0, 38.0, 44.0, 48.0):
        out = controller.compute(temperature=temp, humidity=45.0, wind_speed=40.0, vegetation_dryness=70.0)
        assert out["alert_level"] == min(3, max(0, round(out["suppression_alert_level"])))
        assert 0 <= out["alert_level"] <= 3


def test_alert_universe_is_fully_covered(controller):
    """Every point on the [0, 3] universe belongs to at least one alert set."""
    coverage = np.zeros_like(controller.x_alert)
    for mf in controller.mf_alert.values():
        coverage = np.maximum(coverage, mf)
    uncovered = controller.x_alert[coverage <= 0.0]
    assert uncovered.size == 0, f"alert universe leaves gaps at {uncovered[:5]}"


def test_each_alert_set_reaches_full_membership(controller):
    """All four tiers are reachable, otherwise a rule consequent can never fire."""
    for name, mf in controller.mf_alert.items():
        assert mf.max() == pytest.approx(1.0), f"{name} peaks at {mf.max()}"


def test_alert_result_payload_is_complete(controller):
    """Every consumer reads the same four alert keys."""
    out = controller.compute(temperature=40.0, humidity=25.0, wind_speed=70.0, vegetation_dryness=90.0)
    for key in ("suppression_alert_level", "alert_level", "alert_name", "alert_label", "alert_action"):
        assert key in out, key
    assert out["alert_name"] in {"NORMAL", "WATCH", "WARNING", "CRITICAL"}
    assert out["rule_firing_peak"] > 0.0
