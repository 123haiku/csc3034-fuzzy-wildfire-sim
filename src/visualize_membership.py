"""Membership-function figures for the report, drawn at the size they are printed at.

The report places Figure 2 at 6.3 in and Figure 3 at 5.6 in, so both are drawn near that
width: a 13 in canvas shrunk into a 6.3 in frame halved every label. Colours come from
`fuzzy_system.palette`, the same NVIDIA ramp the deck and poster use.
"""

from __future__ import annotations

import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from fuzzy_system.controller import WildfireFuzzyController
from fuzzy_system.palette import apply_report_style, ramp, style_axes


def _plot_sets(ax, x, memberships, title, xlabel, ylabel) -> None:
    for colour, (name, mf) in zip(ramp(len(memberships)), memberships.items()):
        ax.plot(x, mf, label=name.replace("_", " ").capitalize(), color=colour,
                linewidth=1.7, solid_capstyle="round")
    ax.set_title(title)
    ax.set_xlabel(xlabel, labelpad=1)
    ax.set_ylabel(ylabel)
    style_axes(ax)
    # Below the axes, in columns: every curve spans the full x range, so an in-plot legend
    # always hides part of one.
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.42),
              ncol=min(4, len(memberships)), handlelength=1.1, columnspacing=0.7,
              handletextpad=0.4, borderaxespad=0.0, fontsize=5.4)


def plot_membership_functions(output_dir: str = "plots") -> None:
    """Seven universes in a 3x3 grid: Figure 2 of the report."""
    os.makedirs(output_dir, exist_ok=True)
    apply_report_style()
    c = WildfireFuzzyController()

    fig, axes = plt.subplots(3, 3, figsize=(6.6, 5.9))
    fig.suptitle("Fuzzy Linguistic Membership Functions", fontsize=9.5, fontweight="bold",
                 color="#0A0A0A")

    panels = [
        (axes[0, 0], c.x_temp, c.mf_temp, "Input: Ambient Temperature",
         "Temperature (\u00b0C)", "Membership"),
        (axes[0, 1], c.x_humidity, c.mf_humidity, "Input: Relative Humidity",
         "Humidity (%)", "Membership"),
        (axes[0, 2], c.x_wind, c.mf_wind, "Input: Wind Speed",
         "Wind speed (km/h)", "Membership"),
        (axes[1, 0], c.x_fuel, c.mf_fuel, "Input: Vegetation Dryness",
         "Dryness (%)", "Membership"),
        (axes[1, 1], c.x_risk, c.mf_risk, "Output 1: Fire Risk Index",
         "Risk score (0-100)", "Membership"),
        (axes[1, 2], c.x_speed, c.mf_speed, "Output 2: Patrol Urgency",
         "Speed (%)", "Membership"),
        (axes[2, 0], c.x_alert, c.mf_alert, "Output 3: Suppression Alert",
         "Alert level (0-3)", "Membership"),
    ]
    for ax, x, memberships, title, xlabel, ylabel in panels:
        _plot_sets(ax, x, memberships, title, xlabel, ylabel)

    axes[2, 0].set_xlim(0, 3)
    axes[2, 0].set_xticks([0, 1, 2, 3])

    axes[2, 1].axis("off")
    axes[2, 1].text(
        0.0, 0.92,
        "Fire risk index    [0, 100]  4 sets\n"
        "Patrol urgency     [0, 100] %  3 sets\n"
        "Suppression alert  [0, 3]    4 sets\n\n"
        "Every rule fires one consequent\n"
        "in each of the three universes;\n"
        "the tier is round(A*), not a\n"
        "threshold on the risk index.",
        va="top", ha="left", fontsize=5.8, family="monospace", color="#1F1F1F",
        linespacing=1.5,
    )
    axes[2, 2].axis("off")

    fig.tight_layout(rect=(0, 0, 1, 0.955), h_pad=1.2, w_pad=0.8)
    path = os.path.join(output_dir, "membership_functions.png")
    fig.savefig(path, dpi=300)
    plt.close(fig)
    print(f"[Plot Generated] Membership functions saved to {path}")


def plot_output_membership_functions(output_dir: str = "plots") -> None:
    """The three output universes stacked: Figure 3 of the report."""
    os.makedirs(output_dir, exist_ok=True)
    apply_report_style()
    c = WildfireFuzzyController()

    fig, axes = plt.subplots(3, 1, figsize=(6.2, 8.4))
    fig.suptitle("Fuzzy Output Universes: Risk, Throttle, Suppression Alert",
                 fontsize=9.5, fontweight="bold", color="#0A0A0A")

    _plot_sets(axes[0], c.x_risk, c.mf_risk, "Output 1: Fire Risk Index",
               "Risk score (0-100)", "Degree of membership")
    _plot_sets(axes[1], c.x_speed, c.mf_speed, "Output 2: UAV Patrol Urgency / Speed",
               "Speed actuation (%)", "Degree of membership")
    _plot_sets(axes[2], c.x_alert, c.mf_alert, "Output 3: Suppression Alert Level",
               "Alert level (0 Advisory | 1 Watch | 2 Warning | 3 Evacuate)",
               "Degree of membership")
    axes[2].set_xlim(0, 3)
    axes[2].set_xticks([0, 1, 2, 3])
    for ax in axes:
        ax.set_ylim(-0.05, 1.08)

    fig.tight_layout(rect=(0, 0, 1, 0.965), h_pad=1.6)
    path = os.path.join(output_dir, "output_membership_functions.png")
    fig.savefig(path, dpi=300)
    plt.close(fig)
    print(f"[Plot Generated] Output membership functions saved to {path}")


if __name__ == "__main__":
    plot_membership_functions()
    plot_output_membership_functions()
