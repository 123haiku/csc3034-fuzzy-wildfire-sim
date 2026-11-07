"""Slide figures in NVIDIA black/green at *literal display size*.

Previous versions were drawn on a 12-14 inch canvas and shrunk into a 6-7 inch frame,
which scales every label down by ~0.5. These are drawn at the size they are placed at,
so a 9 pt label in the figure is a 9 pt label on the slide.
"""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

REPO = Path(r"C:\Users\pangw\.gemini\antigravity\scratch\csc3034-fuzzy-wildfire-sim")
OUT = REPO / "docs" / "presentation" / "assets"
sys.path.insert(0, str(REPO / "src"))

BG = "#0A0A0A"
PANEL = "#0C0C0C"
GRID = "#1E1E1E"
SPINE = "#2A2A2A"
TXT = "#FFFFFF"
MUTED = "#9A9A9A"
GREEN = "#76B900"
LIME = "#C6F26A"
OLIVE = "#4A7A00"
DPI = 320

SERIES = [(TXT, "-", 1.8), (LIME, "-", 1.6), (GREEN, "-", 1.8), (OLIVE, "--", 1.6)]

plt.rcParams.update({
    "font.family": "Arial",
    "figure.facecolor": BG,
    "savefig.facecolor": BG,
    "axes.facecolor": PANEL,
    "text.color": TXT,
    "axes.labelcolor": MUTED,
    "xtick.color": MUTED,
    "ytick.color": MUTED,
})

NV_CMAP = LinearSegmentedColormap.from_list("nvidia", ["#2A2A2A", GREEN, LIME, "#FFFFFF"])


def frame(ax, title, xlabel, ylabel, tick=6.8, label=7.5, title_sz=9.5, legend_sz=6.8, grid=True, legend=True):
    ax.set_facecolor(PANEL)
    for s in ax.spines.values():
        s.set_color(SPINE)
        s.set_linewidth(0.6)
    ax.tick_params(colors=MUTED, labelsize=tick, length=2, width=0.6)
    if grid:
        ax.grid(True, color=GRID, linewidth=0.6)
        ax.set_axisbelow(True)
    ax.set_title(title, color=TXT, fontsize=title_sz, fontweight="bold", pad=5)
    ax.set_xlabel(xlabel, fontsize=label, labelpad=2)
    ax.set_ylabel(ylabel, fontsize=label, labelpad=2)
    if legend:
        ax.legend(loc="center left", bbox_to_anchor=(1.015, 0.5), fontsize=legend_sz,
                  labelcolor=MUTED, handlelength=1.8, borderaxespad=0.0, frameon=False)


def membership() -> Path:
    from fuzzy_system.controller import WildfireFuzzyController

    c = WildfireFuzzyController()
    fig, axes = plt.subplots(2, 2, figsize=(6.8, 5.0))

    panels = [
        (axes[0, 0], c.x_temp, c.mf_temp, "Temperature (input)", "deg C"),
        (axes[0, 1], c.x_fuel, c.mf_fuel, "Fuel dryness (input)", "%"),
        (axes[1, 0], c.x_risk, c.mf_risk, "Fire risk index (output)", "0-100"),
        (axes[1, 1], c.x_speed, c.mf_speed, "Throttle urgency (output)", "%"),
    ]
    for ax, x, mfs, title, unit in panels:
        for (color, ls, lw), (name, mf) in zip(SERIES, mfs.items()):
            ax.plot(x, mf, color=color, linestyle=ls, linewidth=lw,
                    label=name.replace("_", " ").capitalize())
        frame(ax, title, "risk index" if "risk" in title else unit, "degree of membership")
        ax.set_ylim(-0.05, 1.14)
        ax.set_yticks([0, 0.5, 1.0])

    fig.tight_layout(pad=0.45, w_pad=2.6, h_pad=1.1)
    dst = OUT / "membership_nvidia.png"
    fig.savefig(dst, dpi=DPI, bbox_inches="tight", pad_inches=0.06)
    plt.close(fig)
    print(f"[membership] {dst.name}  {dst.stat().st_size/1024:.0f} KB")
    return dst


def telemetry() -> Path:
    from create_wildfire_stage import run_stage_patrol_simulation

    data = run_stage_patrol_simulation(REPO / "assets" / "wildfire_forest_uav_stage.usda", steps=12)
    g = lambda k: [d[k] for d in data]
    steps, fri, spd, alerts = g("step"), g("fire_risk_index"), g("patrol_speed"), g("alert_name")

    fig = plt.figure(figsize=(7.2, 5.0))

    ax1 = fig.add_subplot(2, 2, 1, projection="3d")
    ax1.set_facecolor(PANEL)
    sc = ax1.scatter(g("x"), g("y"), g("z"), c=fri, cmap=NV_CMAP, s=26, edgecolors=BG, linewidths=0.5)
    ax1.plot(g("x"), g("y"), g("z"), color=MUTED, linestyle="--", alpha=0.8, linewidth=1.0)
    for hx, hy in ((14.0, 16.0), (-18.0, 10.0), (8.0, -20.0)):
        ax1.scatter([hx], [hy], [0.0], color=TXT, s=34, marker="^", edgecolors=GREEN, linewidths=0.8)
    cb = plt.colorbar(sc, ax=ax1, shrink=0.55, pad=0.11)
    cb.set_label("fire risk", fontsize=6.5, color=MUTED, labelpad=2)
    cb.ax.tick_params(colors=MUTED, labelsize=5.8, length=2, width=0.5)
    cb.outline.set_edgecolor(SPINE)
    for axis in (ax1.xaxis, ax1.yaxis, ax1.zaxis):
        axis.pane.set_facecolor(PANEL)
        axis.pane.set_edgecolor(SPINE)
        axis._axinfo["grid"]["color"] = GRID
    ax1.tick_params(colors=MUTED, labelsize=5.6, length=2, width=0.5, pad=0)
    ax1.set_title("3D patrol and hotspots", color=TXT, fontsize=9, fontweight="bold", pad=1)
    ax1.set_xlabel("X (m)", fontsize=6, color=MUTED, labelpad=-2)
    ax1.set_ylabel("Y (m)", fontsize=6, color=MUTED, labelpad=-2)
    ax1.set_zlabel("Z (m)", fontsize=6, color=MUTED, labelpad=-2)
    ax1.view_init(elev=26, azim=-58)

    ax2 = fig.add_subplot(2, 2, 2)
    ax2.plot(steps, g("temperature"), color=TXT, marker="o", linewidth=1.5, markersize=3.2)
    ax2.plot(steps, g("humidity"), color=GREEN, marker="s", linewidth=1.5, markersize=3.0)
    frame(ax2, "Atmospheric sensors", "waypoint step", "reading", legend_sz=6.2, legend=False)
    ax2.legend(loc="center left", bbox_to_anchor=(1.015, 0.5), fontsize=6.2, labelcolor=MUTED,
               handlelength=1.6, borderaxespad=0, frameon=False,
               labels=["Temperature (C)", "Humidity (%)"])
    ax2.set_xticks(steps)

    ax3 = fig.add_subplot(2, 2, 3)
    ax3.plot(steps, g("vegetation_dryness"), color=LIME, marker="^", linewidth=1.5, markersize=3.4)
    ax3.plot(steps, g("wind_speed"), color=GREEN, marker="d", linewidth=1.5, markersize=3.0)
    frame(ax3, "Fuel and wind loading", "waypoint step", "value", legend_sz=6.2, legend=False)
    ax3.legend(loc="center left", bbox_to_anchor=(1.015, 0.5), fontsize=6.2, labelcolor=MUTED,
               handlelength=1.6, borderaxespad=0, frameon=False,
               labels=["Fuel dryness (%)", "Wind speed (km/h)"])
    ax3.set_xticks(steps)

    ax4 = fig.add_subplot(2, 2, 4)
    ax4.plot(steps, fri, color=GREEN, marker="o", linewidth=1.6, markersize=3.2)
    ax4.plot(steps, spd, color=TXT, linestyle="-.", marker="x", linewidth=1.3, markersize=3.2)
    for i, a in enumerate(alerts):
        if a == "CRITICAL" and (i == 0 or alerts[i - 1] != "CRITICAL"):
            ax4.scatter([i], [fri[i]], color=LIME, s=26, zorder=6)
            ax4.annotate("CRITICAL", (i, fri[i]), textcoords="offset points", xytext=(0, 8),
                         ha="center", fontsize=5.8, fontweight="bold", color=LIME,
                         arrowprops=dict(arrowstyle="-", color=LIME, lw=0.6))
    frame(ax4, "Inference and dispatch", "waypoint step", "0-100", legend_sz=6.2, legend=False)
    ax4.legend(loc="center left", bbox_to_anchor=(1.015, 0.34), fontsize=6.2, labelcolor=MUTED,
               handlelength=1.6, borderaxespad=0, frameon=False,
               labels=["Fire risk index", "Throttle urgency"])
    ax4.set_xticks(steps)
    ax4.set_ylim(0, 122)

    fig.tight_layout(pad=0.5, w_pad=2.4, h_pad=1.0)
    dst = OUT / "telemetry_nvidia.png"
    fig.savefig(dst, dpi=DPI, bbox_inches="tight", pad_inches=0.06)
    plt.close(fig)
    print(f"[telemetry ] {dst.name}  {dst.stat().st_size/1024:.0f} KB")
    return dst


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    membership()
    telemetry()
