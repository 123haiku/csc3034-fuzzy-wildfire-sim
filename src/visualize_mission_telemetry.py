"""Generates publication-quality 3D flight path and telemetry charts for CSC3034 report/poster."""

from __future__ import annotations

import os
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np

# Import stage simulator
from create_wildfire_stage import run_stage_patrol_simulation

REPO_ROOT = Path(__file__).resolve().parent.parent
PLOTS_DIR = REPO_ROOT / "plots"


def plot_mission_telemetry(output_dir: Path = PLOTS_DIR):
    output_dir.mkdir(parents=True, exist_ok=True)
    stage_path = REPO_ROOT / "assets" / "wildfire_forest_uav_stage.usda"

    # Run the waypoint simulation
    data = run_stage_patrol_simulation(stage_path, steps=12)

    steps = [d["step"] for d in data]
    xs = [d["x"] for d in data]
    ys = [d["y"] for d in data]
    zs = [d["z"] for d in data]
    temps = [d["temperature"] for d in data]
    humidities = [d["humidity"] for d in data]
    winds = [d["wind_speed"] for d in data]
    dryness = [d["vegetation_dryness"] for d in data]
    fri = [d["fire_risk_index"] for d in data]
    speed = [d["patrol_speed"] for d in data]
    alerts = [d["alert_name"] for d in data]

    # Setup publication figure
    plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")
    fig = plt.figure(figsize=(16, 10))

    # --- 1. 3D Trajectory & Hotspot Heatmap ---
    ax1 = fig.add_subplot(2, 2, 1, projection="3d")
    scatter = ax1.scatter(xs, ys, zs, c=fri, cmap="YlOrRd", s=90, edgecolors="k", linewidth=1.2, zorder=5)
    ax1.plot(xs, ys, zs, color="darkslategray", linestyle="--", alpha=0.7, linewidth=1.8, label="UAV Flight Path")

    # Mark wildfire hotspots on ground
    hotspots = [
        (14.0, 16.0, "Hotspot 1 (Severe)"),
        (-18.0, 10.0, "Hotspot 2 (Moderate)"),
        (8.0, -20.0, "Hotspot 3 (Emerging)"),
    ]
    for hx, hy, hname in hotspots:
        ax1.scatter([hx], [hy], [0.0], color="red", s=140, marker="^", edgecolors="black", label=hname)

    cbar = plt.colorbar(scatter, ax=ax1, shrink=0.55, pad=0.1)
    cbar.set_label("Fire Risk Index (FRI)", fontsize=10, fontweight="bold")
    ax1.set_title("3D Autonomous UAV Patrol & Hazard Trajectory", fontsize=12, fontweight="bold")
    ax1.set_xlabel("X (meters)")
    ax1.set_ylabel("Y (meters)")
    ax1.set_zlabel("Altitude Z (m)")
    ax1.view_init(elev=28, azim=-55)

    # --- 2. Environmental Sensor Readings ---
    ax2 = fig.add_subplot(2, 2, 2)
    ax2.plot(steps, temps, "r-o", linewidth=2.2, label="Ambient Temp (°C)")
    ax2.plot(steps, humidities, "b-s", linewidth=2.2, label="Relative Humidity (%)")
    ax2.set_title("Atmospheric Sensor Ingestion Over Patrol Path", fontsize=12, fontweight="bold")
    ax2.set_xlabel("Waypoint Step")
    ax2.set_ylabel("Sensor Reading")
    ax2.set_xticks(steps)
    ax2.grid(True, linestyle=":", alpha=0.6)
    ax2.legend(loc="upper right")

    # --- 3. Fuel & Wind Velocity ---
    ax3 = fig.add_subplot(2, 2, 3)
    ax3.plot(steps, dryness, color="saddlebrown", marker="^", linewidth=2.2, label="Vegetation Dryness (%)")
    ax3.plot(steps, winds, color="teal", marker="d", linewidth=2.2, label="Wind Velocity (km/h)")
    ax3.set_title("Fuel Moisture & Aerodynamic Dynamics", fontsize=12, fontweight="bold")
    ax3.set_xlabel("Waypoint Step")
    ax3.set_ylabel("Value (%) / (km/h)")
    ax3.set_xticks(steps)
    ax3.grid(True, linestyle=":", alpha=0.6)
    ax3.legend(loc="upper left")

    # --- 4. Fuzzy Controller Output & Drone Throttle Urgency ---
    ax4 = fig.add_subplot(2, 2, 4)
    ax4.plot(steps, fri, color="crimson", marker="o", linewidth=2.5, label="Computed Fire Risk Index (0-100)")
    ax4.plot(steps, speed, color="darkorange", linestyle="-.", marker="x", linewidth=2.2, label="UAV Urgency Throttle (%)")

    # Annotate critical events
    for i, alert in enumerate(alerts):
        if alert == "CRITICAL":
            ax4.scatter([i], [fri[i]], color="darkred", s=120, zorder=6)
            ax4.annotate(
                "CRITICAL\nDISPATCH",
                (i, fri[i]),
                textcoords="offset points",
                xytext=(-15, 12),
                ha="center",
                fontsize=8,
                fontweight="bold",
                color="darkred",
                arrowprops=dict(arrowstyle="->", color="darkred", lw=1.2),
            )

    ax4.set_title("Fuzzy Mamdani Inference & Actuation Dispatch", fontsize=12, fontweight="bold")
    ax4.set_xlabel("Waypoint Step")
    ax4.set_ylabel("Fuzzy Output Index")
    ax4.set_xticks(steps)
    ax4.set_ylim(0, 115)
    ax4.grid(True, linestyle=":", alpha=0.6)
    ax4.legend(loc="lower right")

    plt.suptitle("CSC3034 Computational Intelligence — Autonomous UAV Wildfire Surveillance System", fontsize=14, fontweight="bold", y=0.98)
    plt.tight_layout(rect=[0, 0.03, 1, 0.95])

    chart_file = output_dir / "mission_telemetry_dashboard.png"
    plt.savefig(chart_file, dpi=300)
    plt.close()
    print(f"\n[Dashboard Generated] High-res telemetry dashboard saved to: {chart_file}")


if __name__ == "__main__":
    plot_mission_telemetry()
