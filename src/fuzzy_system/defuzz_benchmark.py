"""Benchmarks the three defuzzification methods on the wildfire controller.

Rebuilds the FRI consequent through scikit-fuzzy three times, once per method
(centroid, bisector, mean of maximum), and reports the crisp fire risk index each
produces for the four benchmark scenarios plus the end-to-end evaluation loop cost
of the hand-written engine.

    python -m src.fuzzy_system.defuzz_benchmark

The report's Table 3 and the poster's defuzzification panel read their figures
from the output, so the numbers are measured rather than transcribed.
"""

from __future__ import annotations

import argparse
import statistics
import sys
import time
from typing import Dict, List, Tuple

import numpy as np

from .controller import WildfireFuzzyController
from .reference_engine import SKFUZZY_AVAILABLE, SkfuzzyReferenceEngine

SCENARIOS: List[Tuple[str, Tuple[float, float, float, float]]] = [
    ("Benign Clear Day", (22.0, 65.0, 12.0, 25.0)),
    ("Dry Spring Heat", (32.0, 40.0, 30.0, 55.0)),
    ("High Hazard Drought", (39.0, 22.0, 55.0, 82.0)),
    ("Critical Wildfire", (46.0, 12.0, 85.0, 95.0)),
]

METHODS = ("centroid", "bisector", "mom")


def _systems():
    """One scikit-fuzzy system per defuzzification method, sharing the same rule base."""
    if not SKFUZZY_AVAILABLE:
        raise RuntimeError("scikit-fuzzy is not installed; pip install -r requirements.txt")
    from skfuzzy import control as ctrl

    from .reference_engine import build_rules, build_variables

    systems = {}
    for method in METHODS:
        variables, risk, speed, alert = build_variables(risk_method=method)
        rules = build_rules(variables, risk, speed, alert)
        systems[method] = ctrl.ControlSystemSimulation(ctrl.ControlSystem(rules))
    return systems


def _evaluate(sim, inputs: Tuple[float, float, float, float], repeats: int) -> Tuple[float, float, float]:
    """Return median crisp FRI, median crisp speed and median defuzzification-only cost in microseconds."""
    t, rh, w, f = inputs
    fri, speed, defuzz_us = [], [], []
    for _ in range(repeats):
        sim.reset()
        sim.input["temperature"] = t
        sim.input["humidity"] = rh
        sim.input["wind_speed"] = w
        sim.input["vegetation_dryness"] = f
        t0 = time.perf_counter()
        sim.compute()
        dt_us = (time.perf_counter() - t0) * 1e6
        fri.append(float(sim.output["fire_risk_index"]))
        speed.append(float(sim.output["patrol_urgency_speed"]))
        defuzz_us.append(dt_us)
    return statistics.median(fri), statistics.median(speed), statistics.median(defuzz_us)


def loop_cost_microseconds(controller: WildfireFuzzyController, inputs: Tuple[float, float, float, float],
                           repeats: int = 20000) -> float:
    """Median wall-clock cost of one full evaluation loop of the hand-written engine."""
    t, rh, w, f = inputs
    samples = []
    for _ in range(repeats):
        t0 = time.perf_counter()
        controller.compute(temperature=t, humidity=rh, wind_speed=w, vegetation_dryness=f)
        samples.append((time.perf_counter() - t0) * 1e6)
    return statistics.median(samples)


def main() -> int:
    parser = argparse.ArgumentParser(description="Benchmark centroid, bisector and MOM defuzzification.")
    parser.add_argument("--repeats", type=int, default=400, help="scikit-fuzzy repeats per scenario and method")
    parser.add_argument("--loop-repeats", type=int, default=20000, help="repeats for the loop-cost timing")
    args = parser.parse_args()

    systems = _systems()
    controller = WildfireFuzzyController()

    print(f"{'scenario':<22}{'centroid':>10}{'bisector':>10}{'mom':>10}{'loop us':>10}")
    print("-" * 62)
    rows: List[Dict[str, object]] = []
    for name, inputs in SCENARIOS:
        results = {m: _evaluate(systems[m], inputs, args.repeats) for m in METHODS}
        loop_us = loop_cost_microseconds(controller, inputs, args.loop_repeats)
        row = {
            "scenario": name,
            "inputs": inputs,
            "centroid": results["centroid"][0],
            "bisector": results["bisector"][0],
            "mom": results["mom"][0],
            "loop_us": loop_us,
        }
        rows.append(row)
        print(f"{name:<22}{row['centroid']:>10.1f}{row['bisector']:>10.1f}{row['mom']:>10.1f}{loop_us:>10.1f}")

    print("-" * 62)
    worst = max(abs(r["centroid"] - r["mom"]) for r in rows)
    print(f"largest centroid-to-MOM divergence: {worst:.1f} risk points")
    print(f"loop cost range: {min(r['loop_us'] for r in rows):.1f}-{max(r['loop_us'] for r in rows):.1f} us")
    return 0


if __name__ == "__main__":
    sys.exit(main())
