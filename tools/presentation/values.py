"""Values shared by the poster and the deck, read from docs/measurements.json.

Both builders quote the same latency, mission rows and stage facts. Loading them here
means a re-measurement propagates to every deliverable instead of leaving three copies
of a number that can drift apart.

    from values import measurement, mission_row, latency

Regenerate the source file with:  python tools/presentation/measure.py
"""

from __future__ import annotations

import json
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
MEASUREMENTS = REPO / "docs" / "measurements.json"


def measurement() -> dict:
    if not MEASUREMENTS.exists():
        raise SystemExit(
            f"missing {MEASUREMENTS}; run: python tools/presentation/measure.py"
        )
    return json.loads(MEASUREMENTS.read_text(encoding="utf-8"))


_DATA = measurement()

ENGINE = _DATA["engine"]
MISSION = _DATA["mission"]
DEFUZZ = _DATA["defuzz"]
REFERENCE = _DATA["reference"]
TESTS = _DATA["tests"]

_latency = _DATA["latency"]
# The worst case across the measured scenarios is what the one-line figure reports.
MEDIAN_MS = max(v for k, v in _latency.items() if k.endswith("_median_ms"))
P99_MS = max(v for k, v in _latency.items() if k.endswith("_p99_ms"))
BUDGET_PCT = MEDIAN_MS / 50.0 * 100.0
STAGE_FPS = ENGINE["fps"]
TREES = ENGINE["trees_in_asset"]
HOTSPOTS = ENGINE["hotspots"]
KEYFRAMES = ENGINE["uav_keyframes"]
FRAME_END = ENGINE["frame_end"]
CLIP_SECONDS = ENGINE["clip_seconds"]


def mission_row(step: int) -> dict:
    return MISSION[step]


def latency() -> tuple:
    """(median ms, p99 ms) as printed to two decimals."""
    return MEDIAN_MS, P99_MS
