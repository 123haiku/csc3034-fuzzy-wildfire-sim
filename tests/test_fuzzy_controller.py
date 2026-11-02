"""Unit tests for Wildfire Fuzzy Controller."""

import pytest
import sys
import os

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
