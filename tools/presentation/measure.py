"""Measures every number the deliverables quote and writes docs/measurements.json.

    python tools/presentation/measure.py

The poster, the report and the deck all read this file instead of carrying their own
transcribed constants. A figure that appears in three deliverables therefore comes from
one measurement, and `tools/verify_values.py` can diff the shipped documents against it.

Blocks written:

  engine     structure facts read from the controller and the generator source
  mission    the 12-waypoint telemetry log for seed = 0
  defuzz     the three-method benchmark behind report Table 3
  latency    median and p99 of one evaluation loop, per scenario and pooled
  reference  scikit-fuzzy cross-check, worst absolute deviation
"""

from __future__ import annotations

import argparse
import json
import re
import statistics
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, List

REPO = Path(__file__).resolve().parent.parent.parent
OUT = REPO / "docs" / "measurements.json"

sys.path.insert(0, str(REPO / "src"))

from create_wildfire_stage import run_stage_patrol_simulation  # noqa: E402
from fuzzy_system.controller import WildfireFuzzyController  # noqa: E402

BENIGN = (22.0, 65.0, 12.0, 25.0)
CRITICAL = (46.0, 12.0, 85.0, 95.0)


def engine_facts() -> Dict[str, object]:
    controller = WildfireFuzzyController()
    stage_src = (REPO / "src" / "create_wildfire_stage.py").read_text(encoding="utf-8")
    controller_src = (REPO / "src" / "fuzzy_system" / "controller.py").read_text(encoding="utf-8")
    stage_usd = (REPO / "assets" / "wildfire_forest_uav_stage.usda").read_text(encoding="utf-8")

    # Frames are read from the baked translate timeSamples, not from the format string
    # that produces them, so the figure describes the shipped asset.
    block = re.search(
        r"float3 xformOp:translate\.timeSamples = \{\s*(.*?)\}", stage_usd, re.S)
    frames = [int(m) for m in re.findall(r"(\d+): \(", block.group(1))] if block else []
    trees_in_asset = len(re.findall(r'def Xform "Tree_\d+"', stage_usd))
    hotspots_in_asset = len(re.findall(r'def Xform "Hotspot_\d+"', stage_usd))
    rules = len(re.findall(r"# Rule \d+:", controller_src))

    return {
        "resolution": controller.resolution,
        "input_sets": sum(len(mf) for mf in (
            controller.mf_temp, controller.mf_humidity, controller.mf_wind, controller.mf_fuel)),
        "output_universes": 3,
        "rules": rules,
        "alert_universe_samples": int(controller.x_alert.size),
        "alert_universe_step": round(float(controller.x_alert[1] - controller.x_alert[0]), 4),
        "trees_requested": 48,
        "trees_in_asset": trees_in_asset,
        "hotspots": hotspots_in_asset,
        "uav_keyframes": len(frames),
        "frame_start": min(frames),
        "frame_end": max(frames),
        "fps": 30,
        "clip_seconds": round(max(frames) / 30.0, 2),
        "waypoints_simulated": 12,
    }


def mission() -> List[Dict[str, float]]:
    rows = run_stage_patrol_simulation(
        REPO / "assets" / "wildfire_forest_uav_stage.usda", steps=12, seed=0
    )
    out = []
    for r in rows:
        out.append({
            "step": r["step"],
            "x": r["x"], "y": r["y"], "z": r["z"],
            "temperature": round(r["temperature"], 1),
            "humidity": round(r["humidity"], 1),
            "wind_speed": round(r["wind_speed"], 1),
            "vegetation_dryness": round(r["vegetation_dryness"], 1),
            "fire_risk_index": round(r["fire_risk_index"], 1),
            "patrol_urgency": round(r["patrol_speed"], 1),
            "suppression_alert": round(r["suppression_alert_level"], 3),
            "alert_name": r["alert_name"],
        })
    return out


def defuzz(repeats: int) -> List[Dict[str, object]]:
    from fuzzy_system.defuzz_benchmark import METHODS, SCENARIOS, _evaluate, _systems

    systems = _systems()
    rows = []
    for name, inputs in SCENARIOS:
        r = {m: _evaluate(systems[m], inputs, repeats) for m in METHODS}
        rows.append({
            "scenario": name,
            "inputs": list(inputs),
            "centroid": round(r["centroid"][0], 1),
            "bisector": round(r["bisector"][0], 1),
            "mom": round(r["mom"][0], 1),
        })
    return rows


def latency(warmup: int, repeats: int) -> Dict[str, float]:
    controller = WildfireFuzzyController()
    result: Dict[str, float] = {}
    for label, inputs in (("benign", BENIGN), ("critical", CRITICAL)):
        for _ in range(warmup):
            controller.compute(*inputs)
        samples = []
        for _ in range(repeats):
            t0 = time.perf_counter()
            controller.compute(*inputs)
            samples.append((time.perf_counter() - t0) * 1000.0)
        samples.sort()
        result[f"{label}_median_ms"] = round(statistics.median(samples), 3)
        result[f"{label}_p99_ms"] = round(samples[int(len(samples) * 0.99)], 3)
    return result


def reference() -> Dict[str, object]:
    proc = subprocess.run(
        [sys.executable, "-m", "src.fuzzy_system.reference_engine"],
        cwd=str(REPO), capture_output=True, text=True, check=False,
    )
    text = proc.stdout + proc.stderr
    worst = re.search(r"worst absolute deviation: ([\d.]+)", text)
    passed = re.search(r"(\d+)/(\d+) scenarios within tolerance", text)
    return {
        "worst_deviation": float(worst.group(1)) if worst else None,
        "scenarios_passed": int(passed.group(1)) if passed else None,
        "scenarios_total": int(passed.group(2)) if passed else None,
    }


def tests() -> Dict[str, object]:
    proc = subprocess.run(
        [sys.executable, "-m", "pytest", "tests", "-q"],
        cwd=str(REPO), capture_output=True, text=True, check=False,
    )
    m = re.search(r"(\d+) passed", proc.stdout + proc.stderr)
    return {"passed": int(m.group(1)) if m else None, "exit_code": proc.returncode}


def main() -> int:
    parser = argparse.ArgumentParser(description="Regenerate docs/measurements.json.")
    parser.add_argument("--warmup", type=int, default=2000)
    parser.add_argument("--repeats", type=int, default=20000)
    parser.add_argument("--defuzz-repeats", type=int, default=60)
    args = parser.parse_args()

    payload = {
        "generated_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "python": sys.version.split()[0],
        "engine": engine_facts(),
        "mission": mission(),
        "defuzz": defuzz(args.defuzz_repeats),
        "latency": latency(args.warmup, args.repeats),
        "reference": reference(),
        "tests": tests(),
    }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    print(f"\n[measure] wrote {OUT}")
    for key, value in payload["latency"].items():
        print(f"[measure] latency.{key} = {value}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
