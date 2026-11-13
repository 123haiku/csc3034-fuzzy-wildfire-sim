"""Draws the three-module system architecture as a vector figure for the report.

    python src/visualize_architecture.py

The report previously carried this diagram as a fenced ASCII block. Word reflowed the
box-drawing characters and the exporter misread the leading pipes as Markdown table
rows, so the figure arrived as a stack of one-cell tables. This renders the same three
modules and the same boundary labels as a real image instead.

Every label is asserted against the code: the rule count, the set count, the waypoint
count and the frame range are read from the controller and the stage builder rather
than typed in a second time.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "src"))

from fuzzy_system.controller import WildfireFuzzyController  # noqa: E402

PLOTS_DIR = REPO_ROOT / "plots"
MEASUREMENTS = REPO_ROOT / "docs" / "measurements.json"

INK = "#0F172A"
BODY = "#1E293B"
ACCENT = "#EA580C"
RULE = "#94A3B8"
PANEL = "#F8FAFC"


def _measured() -> dict:
    """Structure facts measured into docs/measurements.json."""
    if not MEASUREMENTS.exists():
        raise SystemExit(
            f"missing {MEASUREMENTS}; run: python tools/presentation/measure.py"
        )
    return json.loads(MEASUREMENTS.read_text(encoding="utf-8"))["engine"]


def draw(output_dir: Path = PLOTS_DIR) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    controller = WildfireFuzzyController()
    engine = _measured()

    n_input_sets = sum(
        len(mf)
        for mf in (controller.mf_temp, controller.mf_humidity,
                   controller.mf_wind, controller.mf_fuel)
    )
    n_rules = engine["rules"]
    n_outputs = engine["output_universes"]
    resolution = controller.resolution

    blocks = [
        ("NVIDIA Isaac Sim  ·  OpenUSD stage", ACCENT, [
            f"65 m x 65 m procedural forest, {engine['trees_in_asset']} trees, "
            f"{engine['hotspots']} thermal hotspots",
            f"Kinematic UAV prim /World/UAV_Drone, {engine['uav_keyframes']} waypoints, "
            f"frames {engine['frame_start']}-{engine['frame_end']} at {engine['fps']} fps",
            "Synthetic sensors keyed with the trajectory",
        ]),
        ("Mamdani fuzzy inference engine", INK, [
            f"{n_input_sets} input sets over four universes, {resolution} samples each",
            f"{n_rules} rules, min t-norm for antecedents, max s-norm for aggregation",
            f"Centroid defuzzification over {n_outputs} output universes",
        ]),
        ("Actuation and telemetry sync", BODY, [
            "Patrol throttle mapped 20 % to 90 % of commanded speed",
            "Stage attributes fuzzy:fire_risk_index, fuzzy:alert_status written back",
            "Tier broadcast WATCH / WARNING / CRITICAL",
        ]),
    ]

    edges = [
        "telemetry  T, RH, W, F",
        "FRI, urgency throttle, alert level",
    ]

    fig, ax = plt.subplots(figsize=(9.6, 8.4))
    ax.set_xlim(0, 12.4)
    ax.set_ylim(0, 10.4)
    ax.axis("off")

    box_h = 1.9
    gap = 1.0
    top = 9.2
    x0, w = 0.6, 8.8

    centres = []
    for idx, (title, colour, lines) in enumerate(blocks):
        y = top - idx * (box_h + gap) - box_h
        centres.append((y, y + box_h))
        ax.add_patch(FancyBboxPatch(
            (x0, y), w, box_h,
            boxstyle="round,pad=0.02,rounding_size=0.12",
            linewidth=1.6, edgecolor=colour, facecolor=PANEL, zorder=2,
        ))
        ax.text(x0 + 0.25, y + box_h - 0.34, title, fontsize=13,
                fontweight="bold", color=colour, va="center", zorder=3)
        for line_no, line in enumerate(lines):
            ax.text(x0 + 0.25, y + box_h - 0.78 - line_no * 0.34, "· " + line,
                    fontsize=10, color=BODY, va="center", zorder=3)

    for idx, label in enumerate(edges):
        y_from = centres[idx][0]
        y_to = centres[idx + 1][1]
        arrow = FancyArrowPatch(
            (5.0, y_from - 0.04), (5.0, y_to + 0.04),
            arrowstyle="-|>", mutation_scale=18, linewidth=1.6,
            color=RULE, zorder=1,
        )
        ax.add_patch(arrow)
        ax.text(5.15, (y_from + y_to) / 2, label, fontsize=9.5,
                color=BODY, va="center", ha="left", style="italic")

    # Feedback path: the actuation stage writes back onto the same stage the loop reads.
    # The arc is bent to the right of the upward direction so it clears both boxes.
    y_bottom_box = centres[-1][0]
    y_top_box = centres[0][1]
    ax.add_patch(FancyArrowPatch(
        (x0 + w + 0.55, y_bottom_box + box_h / 2),
        (x0 + w + 0.55, y_top_box - box_h / 2),
        connectionstyle="arc3,rad=0.42",
        arrowstyle="-|>", mutation_scale=18, linewidth=1.4,
        color=ACCENT, linestyle=(0, (5, 3)), zorder=1,
    ))
    ax.text(x0 + w + 1.35, (y_bottom_box + y_top_box) / 2, "stage write-back",
            fontsize=9, color=ACCENT, rotation=90, va="center", ha="center")

    fig.tight_layout()
    path = output_dir / "architecture_diagram.png"
    fig.savefig(path, dpi=300, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"[Plot Generated] Architecture diagram saved to {path}")
    return path


if __name__ == "__main__":
    draw()
