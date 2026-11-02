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
