"""Script to generate publication-grade membership function plots and control surface.

Outputs are saved in the `plots/` directory for inclusion in the 10-page report and A1 poster.
"""

import os
import matplotlib.pyplot as plt
import numpy as np

from fuzzy_system.controller import WildfireFuzzyController


def plot_membership_functions(output_dir: str = "plots"):
    os.makedirs(output_dir, exist_ok=True)
    c = WildfireFuzzyController()

    plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")
    fig, axes = plt.subplots(3, 2, figsize=(14, 12))
    fig.suptitle("Fuzzy Linguistic Membership Functions (CSC3034)", fontsize=16, fontweight="bold")

    # 1. Temperature
    ax = axes[0, 0]
    for name, mf in c.mf_temp.items():
        ax.plot(c.x_temp, mf, label=name.capitalize(), linewidth=2)
    ax.set_title("Input: Ambient Temperature (°C)")
    ax.set_xlabel("Temperature (°C)")
    ax.set_ylabel("Degree of Membership")
    ax.legend()

    # 2. Humidity
    ax = axes[0, 1]
    for name, mf in c.mf_humidity.items():
        ax.plot(c.x_humidity, mf, label=name.replace("_", " ").capitalize(), linewidth=2)
    ax.set_title("Input: Relative Humidity (%)")
    ax.set_xlabel("Humidity (%)")
    ax.set_ylabel("Degree of Membership")
    ax.legend()

    # 3. Wind Speed
    ax = axes[1, 0]
    for name, mf in c.mf_wind.items():
        ax.plot(c.x_wind, mf, label=name.capitalize(), linewidth=2)
    ax.set_title("Input: Wind Speed (km/h)")
    ax.set_xlabel("Wind Speed (km/h)")
    ax.set_ylabel("Degree of Membership")
    ax.legend()

    # 4. Vegetation Dryness
    ax = axes[1, 1]
    for name, mf in c.mf_fuel.items():
        ax.plot(c.x_fuel, mf, label=name.capitalize(), linewidth=2)
    ax.set_title("Input: Vegetation / Fuel Dryness (%)")
    ax.set_xlabel("Dryness (%)")
    ax.set_ylabel("Degree of Membership")
    ax.legend()

    # 5. Output: Fire Risk Index
    ax = axes[2, 0]
    for name, mf in c.mf_risk.items():
        ax.plot(c.x_risk, mf, label=name.capitalize(), linewidth=2)
    ax.set_title("Output: Fire Risk Index (FRI)")
    ax.set_xlabel("Risk Score (0 - 100)")
    ax.set_ylabel("Degree of Membership")
    ax.legend()

    # 6. Output: Drone Patrol Urgency / Speed
    ax = axes[2, 1]
    for name, mf in c.mf_speed.items():
        ax.plot(c.x_speed, mf, label=name.capitalize(), linewidth=2)
    ax.set_title("Output: UAV Patrol Urgency / Speed (%)")
    ax.set_xlabel("Speed Actuation (%)")
    ax.set_ylabel("Degree of Membership")
    ax.legend()

    plt.tight_layout()
    chart_path = os.path.join(output_dir, "membership_functions.png")
    plt.savefig(chart_path, dpi=300)
    plt.close()
    print(f"[Plot Generated] Membership functions saved to {chart_path}")


if __name__ == "__main__":
    plot_membership_functions()
