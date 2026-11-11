"""Measures one full controller evaluation loop and prints median / p99 in milliseconds.

    python tools/presentation/latency_probe.py

The figure this prints is pinned as LOOP_MEDIAN_MS / LOOP_P99_MS in build_poster.py and
quoted verbatim in the report and the deck, so the three deliverables cannot disagree.
"""

from __future__ import annotations

import statistics
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO / "src"))

from fuzzy_system.controller import WildfireFuzzyController  # noqa: E402

BENIGN = (22.0, 65.0, 12.0, 25.0)
CRITICAL = (46.0, 12.0, 85.0, 95.0)


def probe(inputs, warmup=2000, repeats=20000):
    controller = WildfireFuzzyController()
    for _ in range(warmup):
        controller.compute(*inputs)
    samples = []
    for _ in range(repeats):
        t0 = time.perf_counter()
        controller.compute(*inputs)
        samples.append((time.perf_counter() - t0) * 1000.0)
    samples.sort()
    return statistics.median(samples), samples[int(len(samples) * 0.99)]


def main() -> int:
    print(f"{'scenario':<10}{'median ms':>12}{'p99 ms':>10}")
    for label, inputs in (("benign", BENIGN), ("critical", CRITICAL)):
        med, p99 = probe(inputs)
        print(f"{label:<10}{med:>12.3f}{p99:>10.3f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
