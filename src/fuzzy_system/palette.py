"""Shared NVIDIA-palette plotting style for the report figures.

The deck and the A1 poster are drawn in NVIDIA black/green, so the report figures use the
same ramp. On a white page the severity of a fuzzy set is encoded by luminance: pale lime
for the least hazardous term, black for the most hazardous. Every membership dictionary in
the controller is declared from the least to the most hazardous term, so the ramp can be
applied by declaration order without per-variable colour tables.
"""

from __future__ import annotations

from typing import List

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

GREEN = "#76B900"
LIME = "#B4DB2A"
OLIVE = "#4A7A00"
INK = "#0A0A0A"
BODY = "#1F1F1F"
GREY = "#6E6E6E"
RULE = "#B8BDB2"
GRID = "#E4E7DE"
PANEL = "#F8FAF4"
SPINE = "#C8CCC2"

# Least hazardous term first.
RAMP = [LIME, GREEN, OLIVE, INK]

# Single-series colours used by the telemetry dashboard.
SERIES = {
    "risk": GREEN,
    "throttle": OLIVE,
    "dryness": OLIVE,
    "wind": BODY,
    "path": GREY,
    "hotspot": INK,
}

RISK_CMAP = LinearSegmentedColormap.from_list("nvidia_risk", [LIME, GREEN, OLIVE, INK])


def ramp(n: int) -> List[str]:
    """n colours from the NVIDIA ramp, least hazardous first."""
    if n <= 1:
        return [GREEN]
    if n > len(RAMP):
        n = len(RAMP)
    if n == len(RAMP):
        return list(RAMP)
    # Keep both ends of the ramp and space the rest evenly across it.
    picks = [round(i * (len(RAMP) - 1) / (n - 1)) for i in range(n)]
    return [RAMP[i] for i in picks]


def apply_report_style() -> None:
    """rcParams for a figure that will be printed on a white page."""
    plt.rcParams.update({
        "font.family": "DejaVu Sans",
        "figure.facecolor": "white",
        "savefig.facecolor": "white",
        "axes.facecolor": "white",
        "axes.edgecolor": SPINE,
        "axes.linewidth": 0.8,
        "axes.labelcolor": BODY,
        "axes.titlecolor": INK,
        "axes.titlesize": 8.5,
        "axes.titleweight": "bold",
        "axes.labelsize": 7.5,
        "axes.grid": True,
        "grid.color": GRID,
        "grid.linewidth": 0.7,
        "xtick.color": GREY,
        "ytick.color": GREY,
        "xtick.labelsize": 6.5,
        "ytick.labelsize": 6.5,
        "text.color": BODY,
        "legend.frameon": False,
        "legend.fontsize": 6.2,
        "legend.labelcolor": BODY,
        "lines.linewidth": 1.8,
    })


def style_axes(ax, grid: bool = True) -> None:
    """Recessive spines and grid, so the membership curves carry the figure."""
    for side, spine in ax.spines.items():
        spine.set_color(SPINE)
        spine.set_linewidth(0.8)
    ax.grid(grid, color=GRID, linewidth=0.7)
    ax.set_axisbelow(True)
    ax.tick_params(colors=GREY, labelsize=6.5, length=2.5, width=0.7)
