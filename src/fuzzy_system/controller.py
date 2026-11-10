"""Wildfire Fuzzy Logic Inference Engine (Mamdani Model).

Aligned with SDG 13 (Climate Action) and SDG 15 (Life on Land).
Provides risk assessment and autonomous agent dispatch signals.

Three outputs are defuzzified by centroid over continuous universes:
  1. Fire Risk Index            (0-100)
  2. UAV Patrol Urgency/Speed   (0-100 %)
  3. Suppression Alert Level    (0-3)

The alert level is a genuine fuzzy consequent, not a threshold applied to the
risk index. The discrete tier (`alert_level`, `alert_name`) is obtained by
rounding the defuzzified alert centroid to its nearest integer band and is
reported alongside the continuous value as a downstream reporting convenience.
"""

from typing import Dict, Tuple
import numpy as np

# Suppression alert tiers, indexed by their integer band on the [0, 3] universe.
ALERT_TIERS = (
    {"name": "NORMAL", "label": "Advisory", "action": "Standard patrol, log the reading"},
    {"name": "WATCH", "label": "Watch", "action": "Tighten the patrol orbit, prepare a sortie"},
    {"name": "WARNING", "label": "Warning", "action": "Divert to the sector, ground crew on standby"},
    {"name": "CRITICAL", "label": "Evacuate/Suppress", "action": "Emergency dispatch and evacuation call"},
)


def trimf(x: np.ndarray, params: Tuple[float, float, float]) -> np.ndarray:
    """Triangular membership function."""
    a, b, c = params
    y = np.zeros_like(x, dtype=float)
    if a != b:
        idx1 = (a <= x) & (x <= b)
        y[idx1] = (x[idx1] - a) / (b - a)
    else:
        y[x == a] = 1.0

    if b != c:
        idx2 = (b <= x) & (x <= c)
        y[idx2] = (c - x[idx2]) / (c - b)
    else:
        y[x == c] = 1.0

    y[x == b] = 1.0
    return np.clip(y, 0.0, 1.0)


def trapmf(x: np.ndarray, params: Tuple[float, float, float, float]) -> np.ndarray:
    """Trapezoidal membership function."""
    a, b, c, d = params
    y = np.zeros_like(x, dtype=float)

    if a != b:
        idx1 = (a <= x) & (x < b)
        y[idx1] = (x[idx1] - a) / (b - a)
    else:
        y[x < b] = 1.0

    idx2 = (b <= x) & (x <= c)
    y[idx2] = 1.0

    if c != d:
        idx3 = (c < x) & (x <= d)
        y[idx3] = (d - x[idx3]) / (d - c)
    else:
        y[x > c] = 0.0

    return np.clip(y, 0.0, 1.0)


def defuzz_centroid(x: np.ndarray, mf: np.ndarray, default: float = 0.0) -> float:
    """Defuzzification using the Center of Gravity (Centroid) method."""
    sum_mf = np.sum(mf)
    if sum_mf == 0:
        return default
    return float(np.sum(x * mf) / sum_mf)


class WildfireFuzzyController:
    """Mamdani Fuzzy Controller for Forest Fire Risk & Autonomous UAV Dispatch."""

    def __init__(self, resolution: int = 500):
        self.resolution = resolution

        # Universes of Discourse
        self.x_temp = np.linspace(0, 50, resolution)
        self.x_humidity = np.linspace(0, 100, resolution)
        self.x_wind = np.linspace(0, 100, resolution)
        self.x_fuel = np.linspace(0, 100, resolution)

        self.x_risk = np.linspace(0, 100, resolution)
        self.x_speed = np.linspace(0, 100, resolution)
        # Four samples per integer tier, ending on 3: the endpoints, every integer
        # boundary and every set shoulder (0.4, 1.6, 1.4, 2.6) land on a sample.
        self.x_alert = np.arange(0.0, 3.0 + 0.25, 0.25)

        # Build Membership Functions
        self._init_membership_functions()

    def _init_membership_functions(self):
        # 1. Temperature (deg C)
        self.mf_temp = {
            "low": trapmf(self.x_temp, (0, 0, 15, 22)),
            "moderate": trimf(self.x_temp, (18, 26, 34)),
            "high": trimf(self.x_temp, (30, 38, 44)),
            "extreme": trapmf(self.x_temp, (40, 45, 50, 50)),
        }

        # 2. Relative Humidity (%)
        self.mf_humidity = {
            "very_low": trapmf(self.x_humidity, (0, 0, 15, 25)),
            "low": trimf(self.x_humidity, (20, 35, 50)),
            "moderate": trimf(self.x_humidity, (40, 60, 75)),
            "high": trapmf(self.x_humidity, (70, 85, 100, 100)),
        }

        # 3. Wind Speed (km/h)
        self.mf_wind = {
            "calm": trapmf(self.x_wind, (0, 0, 10, 20)),
            "moderate": trimf(self.x_wind, (15, 30, 45)),
            "high": trimf(self.x_wind, (40, 60, 75)),
            "severe": trapmf(self.x_wind, (70, 85, 100, 100)),
        }

        # 4. Vegetation / Fuel Dryness (%)
        self.mf_fuel = {
            "wet": trapmf(self.x_fuel, (0, 0, 20, 35)),
            "moderate": trimf(self.x_fuel, (30, 50, 70)),
            "dry": trimf(self.x_fuel, (65, 80, 90)),
            "critical": trapmf(self.x_fuel, (85, 95, 100, 100)),
        }

        # Output 1: Fire Risk Index (0 - 100)
        self.mf_risk = {
            "low": trapmf(self.x_risk, (0, 0, 20, 35)),
            "moderate": trimf(self.x_risk, (25, 45, 65)),
            "high": trimf(self.x_risk, (55, 75, 85)),
            "extreme": trapmf(self.x_risk, (80, 90, 100, 100)),
        }

        # Output 2: UAV Patrol Urgency / Speed (0 - 100%)
        self.mf_speed = {
            "standard": trapmf(self.x_speed, (0, 0, 25, 45)),
            "accelerated": trimf(self.x_speed, (40, 60, 80)),
            "emergency": trapmf(self.x_speed, (75, 90, 100, 100)),
        }

        # Output 3: Suppression Alert Level (0 - 3)
        # Centres sit exactly on the integer tiers so the defuzzified centroid is a
        # graded position between them rather than a class label.
        self.mf_alert = {
            "advisory": trapmf(self.x_alert, (0, 0, 0, 0.6)),
            "watch": trimf(self.x_alert, (0.4, 1.0, 1.6)),
            "warning": trimf(self.x_alert, (1.4, 2.0, 2.6)),
            "evacuate": trapmf(self.x_alert, (2.4, 3, 3, 3)),
        }

    def _interp_degree(self, val: float, universe: np.ndarray, mf: np.ndarray) -> float:
        """Find membership degree for a crisp scalar value."""
        val = np.clip(val, universe[0], universe[-1])
        return float(np.interp(val, universe, mf))

    def compute(
        self,
        temperature: float,
        humidity: float,
        wind_speed: float,
        vegetation_dryness: float,
    ) -> Dict[str, float]:
        """Compute Mamdani fuzzy inference given sensor inputs."""
        # 1. Fuzzification
        deg_temp = {
            k: self._interp_degree(temperature, self.x_temp, mf)
            for k, mf in self.mf_temp.items()
        }
        deg_hum = {
            k: self._interp_degree(humidity, self.x_humidity, mf)
            for k, mf in self.mf_humidity.items()
        }
        deg_wind = {
            k: self._interp_degree(wind_speed, self.x_wind, mf)
            for k, mf in self.mf_wind.items()
        }
        deg_fuel = {
            k: self._interp_degree(vegetation_dryness, self.x_fuel, mf)
            for k, mf in self.mf_fuel.items()
        }

        # 2. Rule Evaluation (Mamdani min operator for antecedents)
        # Aggregation profiles initialized to zeros
        agg_risk = np.zeros_like(self.x_risk)
        agg_speed = np.zeros_like(self.x_speed)
        agg_alert = np.zeros_like(self.x_alert)

        def apply_rule(weight: float, risk_conseq: str, speed_conseq: str, alert_conseq: str):
            nonlocal agg_risk, agg_speed, agg_alert
            if weight > 0:
                agg_risk = np.maximum(agg_risk, np.minimum(weight, self.mf_risk[risk_conseq]))
                agg_speed = np.maximum(agg_speed, np.minimum(weight, self.mf_speed[speed_conseq]))
                agg_alert = np.maximum(agg_alert, np.minimum(weight, self.mf_alert[alert_conseq]))

        # Rule Base Matrix (Domain expert rules)
        # Each rule fires a triple of consequents across the three output universes.
        rules = (
            # Rule 1: High humidity + Wet fuel -> Low risk / standard throttle / advisory
            (min(deg_hum["high"], deg_fuel["wet"]), "low", "standard", "advisory"),
            # Rule 2: Low temp + Moderate humidity -> Low risk / standard throttle / advisory
            (min(deg_temp["low"], deg_hum["moderate"]), "low", "standard", "advisory"),
            # Rule 3: Moderate temp + Moderate fuel -> Moderate risk / standard throttle / watch
            (min(deg_temp["moderate"], deg_fuel["moderate"]), "moderate", "standard", "watch"),
            # Rule 4: Moderate temp + High wind + Dry fuel -> High risk / accelerated / warning
            (min(deg_temp["moderate"], deg_wind["high"], deg_fuel["dry"]), "high", "accelerated", "warning"),
            # Rule 5: High temp + Low humidity -> High risk / accelerated / warning
            (min(deg_temp["high"], deg_hum["low"]), "high", "accelerated", "warning"),
            # Rule 6: High temp + Severe wind -> Extreme risk / emergency / evacuate
            (min(deg_temp["high"], deg_wind["severe"]), "extreme", "emergency", "evacuate"),
            # Rule 7: Extreme temp + Very low humidity -> Extreme risk / emergency / evacuate
            (min(deg_temp["extreme"], deg_hum["very_low"]), "extreme", "emergency", "evacuate"),
            # Rule 8: Critical fuel + High wind -> Extreme risk / emergency / evacuate
            (min(deg_fuel["critical"], deg_wind["high"]), "extreme", "emergency", "evacuate"),
            # Rule 9: Extreme temp + Critical fuel -> Extreme risk / emergency / evacuate
            (min(deg_temp["extreme"], deg_fuel["critical"]), "extreme", "emergency", "evacuate"),
            # Rule 10: Calm wind + High humidity -> Low risk / standard throttle / advisory
            (min(deg_wind["calm"], deg_hum["high"]), "low", "standard", "advisory"),
        )
        for weight, risk_conseq, speed_conseq, alert_conseq in rules:
            apply_rule(weight, risk_conseq, speed_conseq, alert_conseq)

        # Track the peak firing strength so an all-dominance-zero input can be
        # reported as such instead of silently returning a default.
        peak_firing = max(weight for weight, *_ in rules)

        # 3. Defuzzification (Centroid Method)
        # When no rule fires (peak firing strength is zero) the aggregated sets are
        # empty and centroid defuzzification falls back to the low-risk defaults,
        # so every output, including the alert, has to follow that same fallback.
        if peak_firing <= 0.0:
            crisp_risk, crisp_speed, crisp_alert = 10.0, 20.0, 0.0
        else:
            crisp_risk = defuzz_centroid(self.x_risk, agg_risk, default=10.0)
            crisp_speed = defuzz_centroid(self.x_speed, agg_speed, default=20.0)
            crisp_alert = defuzz_centroid(self.x_alert, agg_alert, default=0.0)

        # Discrete reporting tier: the nearest integer band of the fuzzy alert output.
        alert_level = int(min(3, max(0, round(crisp_alert))))
        tier = ALERT_TIERS[alert_level]

        return {
            "fire_risk_index": round(crisp_risk, 2),
            "patrol_urgency_speed": round(crisp_speed, 2),
            "suppression_alert_level": round(crisp_alert, 3),
            "alert_level": alert_level,
            "alert_name": tier["name"],
            "alert_label": tier["label"],
            "alert_action": tier["action"],
            "rule_firing_peak": round(float(peak_firing), 4),
        }
