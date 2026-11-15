"""Mission telemetry dashboard for the report: Figure 4.

Drawn at roughly the size it is printed at (6.3 in wide) and in the NVIDIA black/green ramp
shared with the other report figures, the deck and the poster.
"""

from __future__ import annotations

import os
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from create_wildfire_stage import run_stage_patrol_simulation
from fuzzy_system.palette import BODY, GREEN, GREY, INK, OLIVE, RISK_CMAP, apply_report_style, style_axes

REPO_ROOT = Path(__file__).resolve().parent.parent
PLOTS_DIR = REPO_ROOT / "plots"

HOTSPOTS = [
    (14.0, 16.0, "Hotspot 1 (severe)"),
    (-18.0, 10.0, "Hotspot 2 (moderate)"),
    (8.0, -20.0, "Hotspot 3 (emerging)"),
]


def plot_mission_telemetry(output_dir: Path = PLOTS_DIR) -> None:
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    stage_path = REPO_ROOT / "assets" / "wildfire_forest_uav_stage.usda"
    data = run_stage_patrol_simulation(stage_path, steps=12)

    steps = [d["step"] for d in data]
    xs, ys, zs = [d["x"] for d in data], [d["y"] for d in data], [d["z"] for d in data]
    temps = [d["temperature"] for d in data]
    humidities = [d["humidity"] for d in data]
    winds = [d["wind_speed"] for d in data]
    dryness = [d["vegetation_dryness"] for d in data]
    fri = [d["fire_risk_index"] for d in data]
    speed = [d["patrol_speed"] for d in data]
    alerts = [d["alert_name"] for d in data]

    apply_report_style()
    fig = plt.figure(figsize=(7.0, 5.4))

    # --- 1. 3D trajectory, coloured by fire risk index ---
    ax1 = fig.add_subplot(2, 2, 1, projection="3d")
    ax1.set_facecolor("white")
    scatter = ax1.scatter(xs, ys, zs, c=fri, cmap=RISK_CMAP, s=26, edgecolors=INK,
                          linewidth=0.3, zorder=5, depthshade=False)
    ax1.plot(xs, ys, zs, color=GREY, linestyle="--", linewidth=1.0, alpha=0.8,
             label="Flight path")
    for hx, hy, hname in HOTSPOTS:
        ax1.scatter([hx], [hy], [0.0], color=INK, s=34, marker="^",
                    edgecolors=GREEN, linewidth=1.0, label=hname)

    cbar = fig.colorbar(scatter, ax=ax1, shrink=0.55, pad=0.02)
    cbar.set_label("Fire risk index", fontsize=6.2)
    cbar.ax.tick_params(labelsize=5.6, colors=GREY, length=1.8)
    cbar.outline.set_edgecolor("#C8CCC2")
    cbar.outline.set_linewidth(0.6)
    ax1.set_title("3D patrol path and hazard trajectory", fontsize=8.0, fontweight="bold",
                  pad=2)
    ax1.set_xlabel("X (m)", fontsize=6.0, labelpad=-1)
    ax1.set_ylabel("Y (m)", fontsize=6.0, labelpad=-1)
    ax1.set_zlabel("Z (m)", fontsize=6.0, labelpad=-1)
    ax1.tick_params(labelsize=5.4, colors=GREY, pad=0, length=1.5)
    ax1.view_init(elev=26, azim=-56)
    ax1.set_box_aspect(None, zoom=1.22)
    for axis in (ax1.xaxis, ax1.yaxis, ax1.zaxis):
        axis.pane.set_facecolor((1, 1, 1, 1))
        axis.pane.set_edgecolor("#C8CCC2")
        axis.line.set_color("#C8CCC2")

    # --- 2. Atmospheric sensors ---
    ax2 = fig.add_subplot(2, 2, 2)
    ax2.plot(steps, temps, color=GREEN, marker="o", markersize=3.2, linewidth=1.8,
             label="Temperature (\u00b0C)")
    ax2.plot(steps, humidities, color=BODY, marker="s", markersize=2.8, linewidth=1.4,
             linestyle="--", label="Relative humidity (%)")
    ax2.set_title("Atmospheric sensor ingestion", fontsize=8.0, fontweight="bold")
    ax2.set_xlabel("Waypoint", fontsize=6.6)
    ax2.set_ylabel("Reading", fontsize=6.6)
    ax2.set_xticks(steps)
    style_axes(ax2)
    ax2.legend(loc="upper center", bbox_to_anchor=(0.5, -0.26), ncol=2, handlelength=1.3,
               columnspacing=1.0, handletextpad=0.5, borderaxespad=0.0)

    # --- 3. Fuel dryness and wind ---
    ax3 = fig.add_subplot(2, 2, 3)
    ax3.plot(steps, dryness, color=OLIVE, marker="^", markersize=3.0, linewidth=1.8,
             label="Fuel dryness (%)")
    ax3.plot(steps, winds, color=INK, marker="d", markersize=2.6, linewidth=1.3,
             linestyle=":", label="Wind speed (km/h)")
    ax3.set_title("Fuel moisture and wind", fontsize=8.0, fontweight="bold")
    ax3.set_xlabel("Waypoint", fontsize=6.6)
    ax3.set_ylabel("Value (% / km h$^{-1}$)", fontsize=6.6)
    ax3.set_xticks(steps)
    style_axes(ax3)
    ax3.legend(loc="upper center", bbox_to_anchor=(0.5, -0.26), ncol=2, handlelength=1.3,
               columnspacing=1.0, handletextpad=0.5, borderaxespad=0.0)

    # --- 4. Fuzzy outputs and dispatch ---
    ax4 = fig.add_subplot(2, 2, 4)
    ax4.plot(steps, fri, color=GREEN, marker="o", markersize=3.4, linewidth=2.0,
             label="Fire risk index")
    ax4.plot(steps, speed, color=OLIVE, linestyle="-.", marker="x", markersize=3.0,
             linewidth=1.6, label="Patrol urgency (%)")
    for i, alert in enumerate(alerts):
        if alert == "CRITICAL":
            ax4.scatter([i], [fri[i]], color=INK, s=22, zorder=6)
            ax4.annotate(
                "CRITICAL\nDISPATCH",
                (i, fri[i]),
                textcoords="offset points",
                xytext=(-12, 8),
                ha="center",
                fontsize=5.4,
                fontweight="bold",
                color=INK,
                arrowprops=dict(arrowstyle="->", color=INK, lw=0.7),
            )
    ax4.set_title("Fuzzy inference and actuation dispatch", fontsize=8.0, fontweight="bold")
    ax4.set_xlabel("Waypoint", fontsize=6.6)
    ax4.set_ylabel("Fuzzy output", fontsize=6.6)
    ax4.set_xticks(steps)
    ax4.set_ylim(0, 118)
    style_axes(ax4)
    ax4.legend(loc="upper center", bbox_to_anchor=(0.5, -0.26), ncol=2, handlelength=1.3,
               columnspacing=1.0, handletextpad=0.5, borderaxespad=0.0)

    fig.tight_layout(h_pad=0.9, w_pad=0.9)
    chart_file = output_dir / "mission_telemetry_dashboard.png"
    fig.savefig(chart_file, dpi=300)
    plt.close(fig)
    print(f"[Dashboard Generated] Mission telemetry dashboard saved to: {chart_file}")


if __name__ == "__main__":
    plot_mission_telemetry()
