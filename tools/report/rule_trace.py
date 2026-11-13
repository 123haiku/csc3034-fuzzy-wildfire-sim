"""Prints per-rule firing strengths and set overlaps for a scenario.

    python tools/report/rule_trace.py --inputs 42.8 18.9 45.2 86.8

Used to support claims about which rule carries a waypoint rather than guessing which
one does. The rule list is re-read from the same source the controller uses.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO / "src"))

import numpy as np  # noqa: E402

from fuzzy_system.controller import WildfireFuzzyController  # noqa: E402

rule_source_labels = [
    "R1  humidity high + fuel wet            -> low / standard / advisory",
    "R2  temperature low + humidity moderate -> low / standard / advisory",
    "R3  temperature moderate + fuel moderate-> moderate / standard / watch",
    "R4  temperature moderate + wind high + fuel dry -> high / accelerated / warning",
    "R5  temperature high + humidity low      -> high / accelerated / warning",
    "R6  temperature high + wind severe       -> extreme / emergency / evacuate",
    "R7  temperature extreme + humidity very low -> extreme / emergency / evacuate",
    "R8  fuel critical + wind high            -> extreme / emergency / evacuate",
    "R9  temperature extreme + fuel critical  -> extreme / emergency / evacuate",
    "R10 wind calm + humidity high            -> low / standard / advisory",
]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--inputs", nargs=4, type=float, required=True,
                        metavar=("T", "RH", "W", "F"))
    args = parser.parse_args()
    t, rh, w, f = args.inputs

    c = WildfireFuzzyController()
    deg_t = {k: c._interp_degree(t, c.x_temp, mf) for k, mf in c.mf_temp.items()}
    deg_h = {k: c._interp_degree(rh, c.x_humidity, mf) for k, mf in c.mf_humidity.items()}
    deg_w = {k: c._interp_degree(w, c.x_wind, mf) for k, mf in c.mf_wind.items()}
    deg_f = {k: c._interp_degree(f, c.x_fuel, mf) for k, mf in c.mf_fuel.items()}

    strengths = [
        min(deg_h["high"], deg_f["wet"]),
        min(deg_t["low"], deg_h["moderate"]),
        min(deg_t["moderate"], deg_f["moderate"]),
        min(deg_t["moderate"], deg_w["high"], deg_f["dry"]),
        min(deg_t["high"], deg_h["low"]),
        min(deg_t["high"], deg_w["severe"]),
        min(deg_t["extreme"], deg_h["very_low"]),
        min(deg_f["critical"], deg_w["high"]),
        min(deg_t["extreme"], deg_f["critical"]),
        min(deg_w["calm"], deg_h["high"]),
    ]

    print(f"inputs: T={t} RH={rh} W={w} F={f}")
    print("membership degrees")
    for name, group in (("temperature", deg_t), ("humidity", deg_h),
                        ("wind", deg_w), ("fuel", deg_f)):
        parts = ", ".join(f"{k}={v:.3f}" for k, v in group.items())
        print(f"  {name:<12}{parts}")

    print("rule firing strengths")
    for label, s in zip(rule_source_labels, strengths):
        flag = " <== peak" if s == max(strengths) else ""
        print(f"  {label}  alpha={s:.3f}{flag}")

    out = c.compute(t, rh, w, f)
    print("outputs")
    for key in ("fire_risk_index", "patrol_urgency_speed", "suppression_alert_level", "alert_name"):
        print(f"  {key:<24}{out[key]}")

    print("set overlaps per input universe")
    for name, mf_dict, universe in (
        ("temperature", c.mf_temp, c.x_temp),
        ("humidity", c.mf_humidity, c.x_humidity),
        ("wind", c.mf_wind, c.x_wind),
        ("fuel", c.mf_fuel, c.x_fuel),
    ):
        uncovered = np.ones_like(universe, dtype=bool)
        for mf in mf_dict.values():
            uncovered &= mf <= 0
        print(f"  {name:<12}sets={len(mf_dict)} uncovered samples={int(uncovered.sum())}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
