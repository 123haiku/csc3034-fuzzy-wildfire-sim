"""Reference cross-check of the hand-written Mamdani engine against scikit-fuzzy.

This module is validation only. It rebuilds the same universes, membership
functions and rule antecedents with `skfuzzy`, runs the same scenarios through
both engines, and reports the per-output absolute deviation. It is used by
tests/test_reference_engine.py and can be executed directly:

    python -m src.fuzzy_system.reference_engine

The production path never imports scikit-fuzzy; requirements.txt keeps it
listed solely so the cross-check can run.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np

try:
    import skfuzzy as fuzz
    from skfuzzy import control as ctrl
    from skfuzzy.control.controlsystem import EmptyMembershipError, NoTermMembershipsError

    SKFUZZY_AVAILABLE = True
except ImportError:  # pragma: no cover - optional dependency
    SKFUZZY_AVAILABLE = False

    class NoTermMembershipsError(Exception):
        """Placeholder so the module imports without scikit-fuzzy."""

    class EmptyMembershipError(Exception):
        """Placeholder so the module imports without scikit-fuzzy."""

# Falling strength below this means no rule fired; both engines report the
# controller's own fallback defaults rather than an empty aggregation.
FALLBACK_AGGREGATED = {"fire_risk_index": 10.0, "patrol_urgency_speed": 20.0, "suppression_alert_level": 0.0}

from .controller import WildfireFuzzyController

# Rule antecedents shared by both engines: (weight expression, risk, alert)
RuleWeight = Tuple[Tuple[str, str], ...]


def build_variables(risk_method: str = "centroid"):
    """Builds the four antecedents and three consequents with the model's membership sets.

    `risk_method` selects the defuzzification method of the fire risk consequent only,
    which is what the defuzzification benchmark varies.
    """
    temp = ctrl.Antecedent(np.linspace(0, 50, 500), "temperature")
    hum = ctrl.Antecedent(np.linspace(0, 100, 500), "humidity")
    wind = ctrl.Antecedent(np.linspace(0, 100, 500), "wind_speed")
    fuel = ctrl.Antecedent(np.linspace(0, 100, 500), "vegetation_dryness")

    risk = ctrl.Consequent(np.linspace(0, 100, 500), "fire_risk_index", defuzzify_method=risk_method)
    speed = ctrl.Consequent(np.linspace(0, 100, 500), "patrol_urgency_speed", defuzzify_method="centroid")
    alert = ctrl.Consequent(np.linspace(0, 3, 500), "suppression_alert", defuzzify_method="centroid")

    temp["low"] = fuzz.trapmf(temp.universe, (0, 0, 15, 22))
    temp["moderate"] = fuzz.trimf(temp.universe, (18, 26, 34))
    temp["high"] = fuzz.trimf(temp.universe, (30, 38, 44))
    temp["extreme"] = fuzz.trapmf(temp.universe, (40, 45, 50, 50))

    hum["very_low"] = fuzz.trapmf(hum.universe, (0, 0, 15, 25))
    hum["low"] = fuzz.trimf(hum.universe, (20, 35, 50))
    hum["moderate"] = fuzz.trimf(hum.universe, (40, 60, 75))
    hum["high"] = fuzz.trapmf(hum.universe, (70, 85, 100, 100))

    wind["calm"] = fuzz.trapmf(wind.universe, (0, 0, 10, 20))
    wind["moderate"] = fuzz.trimf(wind.universe, (15, 30, 45))
    wind["high"] = fuzz.trimf(wind.universe, (40, 60, 75))
    wind["severe"] = fuzz.trapmf(wind.universe, (70, 85, 100, 100))

    fuel["wet"] = fuzz.trapmf(fuel.universe, (0, 0, 20, 35))
    fuel["moderate"] = fuzz.trimf(fuel.universe, (30, 50, 70))
    fuel["dry"] = fuzz.trimf(fuel.universe, (65, 80, 90))
    fuel["critical"] = fuzz.trapmf(fuel.universe, (85, 95, 100, 100))

    risk["low"] = fuzz.trapmf(risk.universe, (0, 0, 20, 35))
    risk["moderate"] = fuzz.trimf(risk.universe, (25, 45, 65))
    risk["high"] = fuzz.trimf(risk.universe, (55, 75, 85))
    risk["extreme"] = fuzz.trapmf(risk.universe, (80, 90, 100, 100))

    speed["standard"] = fuzz.trapmf(speed.universe, (0, 0, 25, 45))
    speed["accelerated"] = fuzz.trimf(speed.universe, (40, 60, 80))
    speed["emergency"] = fuzz.trapmf(speed.universe, (75, 90, 100, 100))

    alert["advisory"] = fuzz.trapmf(alert.universe, (0, 0, 0, 0.6))
    alert["watch"] = fuzz.trimf(alert.universe, (0.4, 1, 1.6))
    alert["warning"] = fuzz.trimf(alert.universe, (1.4, 2, 2.6))
    alert["evacuate"] = fuzz.trapmf(alert.universe, (2.4, 3, 3, 3))

    return {"temp": temp, "hum": hum, "wind": wind, "fuel": fuel}, risk, speed, alert


def build_rules(variables, risk, speed, alert):
    """Returns the ten Rule objects binding each antecedent to a consequence triple."""
    temp, hum, wind, fuel = variables["temp"], variables["hum"], variables["wind"], variables["fuel"]
    triples = [
        (hum["high"] & fuel["wet"], risk["low"], speed["standard"], alert["advisory"]),
        (temp["low"] & hum["moderate"], risk["low"], speed["standard"], alert["advisory"]),
        (temp["moderate"] & fuel["moderate"], risk["moderate"], speed["standard"], alert["watch"]),
        (temp["moderate"] & wind["high"] & fuel["dry"], risk["high"], speed["accelerated"], alert["warning"]),
        (temp["high"] & hum["low"], risk["high"], speed["accelerated"], alert["warning"]),
        (temp["high"] & wind["severe"], risk["extreme"], speed["emergency"], alert["evacuate"]),
        (temp["extreme"] & hum["very_low"], risk["extreme"], speed["emergency"], alert["evacuate"]),
        (fuel["critical"] & wind["high"], risk["extreme"], speed["emergency"], alert["evacuate"]),
        (temp["extreme"] & fuel["critical"], risk["extreme"], speed["emergency"], alert["evacuate"]),
        (wind["calm"] & hum["high"], risk["low"], speed["standard"], alert["advisory"]),
    ]
    return [ctrl.Rule(a, [r, s, al]) for a, r, s, al in triples]


class SkfuzzyReferenceEngine:
    """Same model expressed through scikit-fuzzy's ControlSystemSimulation."""

    def __init__(self) -> None:
        if not SKFUZZY_AVAILABLE:
            raise RuntimeError("scikit-fuzzy is not installed; install requirements.txt")

        variables, risk, speed, alert = build_variables()
        rules = build_rules(variables, risk, speed, alert)

        self.system = ctrl.ControlSystem(rules)
        self.sim = ctrl.ControlSystemSimulation(self.system)

    def compute(self, temperature: float, humidity: float, wind_speed: float,
                vegetation_dryness: float) -> Dict[str, float]:
        self.sim.input["temperature"] = float(np.clip(temperature, 0, 50))
        self.sim.input["humidity"] = float(np.clip(humidity, 0, 100))
        self.sim.input["wind_speed"] = float(np.clip(wind_speed, 0, 100))
        self.sim.input["vegetation_dryness"] = float(np.clip(vegetation_dryness, 0, 100))
        try:
            self.sim.compute()
        except (NoTermMembershipsError, EmptyMembershipError):
            return dict(FALLBACK_AGGREGATED)
        # With lenient=True the simulation swallows the empty-aggregation error and
        # returns an empty dict, so the fallback has to be checked on the result.
        if "fire_risk_index" not in self.sim.output:
            return dict(FALLBACK_AGGREGATED)
        return {
            "fire_risk_index": float(self.sim.output["fire_risk_index"]),
            "patrol_urgency_speed": float(self.sim.output["patrol_urgency_speed"]),
            "suppression_alert_level": float(self.sim.output["suppression_alert"]),
        }


SCENARIOS: List[Tuple[str, Tuple[float, float, float, float]]] = [
    ("moist_cool_monsoon", (16.0, 88.0, 10.0, 15.0)),
    ("normal_warm_afternoon", (28.0, 55.0, 25.0, 45.0)),
    ("dry_windy_autumn", (34.0, 30.0, 50.0, 72.0)),
    ("extreme_heatwave_gale", (46.0, 12.0, 75.0, 95.0)),
    ("hotspot_waypoint_08", (42.9, 18.7, 44.9, 86.8)),
    ("moderate_watch", (30.0, 50.0, 35.0, 55.0)),
    ("high_wind_warning", (30.0, 50.0, 85.0, 70.0)),
    ("lower_bound", (0.0, 0.0, 0.0, 0.0)),
    ("upper_bound", (50.0, 100.0, 100.0, 100.0)),
]


def cross_check() -> List[Dict[str, object]]:
    """Return one comparison row per scenario."""
    engine = WildfireFuzzyController()
    ref = SkfuzzyReferenceEngine()
    rows: List[Dict[str, object]] = []
    for name, (t, h, w, f) in SCENARIOS:
        ours = engine.compute(temperature=t, humidity=h, wind_speed=w, vegetation_dryness=f)
        theirs = ref.compute(temperature=t, humidity=h, wind_speed=w, vegetation_dryness=f)
        rows.append({
            "scenario": name,
            "inputs": (t, h, w, f),
            "fri_ours": ours["fire_risk_index"],
            "fri_ref": theirs["fire_risk_index"],
            "fri_delta": abs(ours["fire_risk_index"] - theirs["fire_risk_index"]),
            "speed_ours": ours["patrol_urgency_speed"],
            "speed_ref": theirs["patrol_urgency_speed"],
            "speed_delta": abs(ours["patrol_urgency_speed"] - theirs["patrol_urgency_speed"]),
            "alert_ours": ours["suppression_alert_level"],
            "alert_ref": theirs["suppression_alert_level"],
            "alert_delta": abs(ours["suppression_alert_level"] - theirs["suppression_alert_level"]),
        })
    return rows


def main() -> int:
    parser = argparse.ArgumentParser(description="Cross-check the hand-written Mamdani engine against scikit-fuzzy.")
    parser.add_argument("--tolerance", type=float, default=0.5, help="max allowed absolute deviation per output")
    args = parser.parse_args()

    rows = cross_check()
    print(f"{'scenario':<24}{'FRI ours':>10}{'ref':>9}{'d':>7}{'  speed ours':>14}{'ref':>9}{'d':>7}{'  alert ours':>14}{'ref':>8}{'d':>7}")
    print("-" * 117)
    failures = 0
    for r in rows:
        print(
            f"{r['scenario']:<24}{r['fri_ours']:>10.2f}{r['fri_ref']:>9.2f}{r['fri_delta']:>7.3f}"
            f"{r['speed_ours']:>14.2f}{r['speed_ref']:>9.2f}{r['speed_delta']:>7.3f}"
            f"{r['alert_ours']:>14.3f}{r['alert_ref']:>8.3f}{r['alert_delta']:>7.3f}"
        )
        if max(r["fri_delta"], r["speed_delta"], r["alert_delta"]) > args.tolerance:
            failures += 1
    worst = max(max(r["fri_delta"], r["speed_delta"], r["alert_delta"]) for r in rows)
    print("-" * 117)
    print(f"worst absolute deviation: {worst:.4f} (tolerance {args.tolerance})")
    print(f"{len(rows) - failures}/{len(rows)} scenarios within tolerance")
    return 0 if failures == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
