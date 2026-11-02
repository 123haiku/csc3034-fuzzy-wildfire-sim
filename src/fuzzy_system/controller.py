"""Wildfire Fuzzy Logic Inference Engine (Mamdani Model).

Aligned with SDG 13 (Climate Action) and SDG 15 (Life on Land).
Provides risk assessment and autonomous agent dispatch signals.
"""

from typing import Dict, Tuple
import numpy as np


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

        def apply_rule(weight: float, risk_conseq: str, speed_conseq: str):
            nonlocal agg_risk, agg_speed
            if weight > 0:
                clipped_risk = np.minimum(weight, self.mf_risk[risk_conseq])
                clipped_speed = np.minimum(weight, self.mf_speed[speed_conseq])
                agg_risk = np.maximum(agg_risk, clipped_risk)
                agg_speed = np.maximum(agg_speed, clipped_speed)

        # Rule Base Matrix (Domain expert rules)
        # Rule 1: Wet conditions / Low temp -> Low Risk
        w1 = min(deg_hum["high"], deg_fuel["wet"])
        apply_rule(w1, "low", "standard")

        # Rule 2: Low temp & moderate humidity -> Low Risk
        w2 = min(deg_temp["low"], deg_hum["moderate"])
        apply_rule(w2, "low", "standard")

        # Rule 3: Moderate temp + Moderate fuel -> Moderate Risk
        w3 = min(deg_temp["moderate"], deg_fuel["moderate"])
        apply_rule(w3, "moderate", "standard")

        # Rule 4: Moderate temp + High wind + Dry fuel -> High Risk
        w4 = min(deg_temp["moderate"], deg_wind["high"], deg_fuel["dry"])
        apply_rule(w4, "high", "accelerated")

        # Rule 5: High temp + Low humidity -> High Risk
        w5 = min(deg_temp["high"], deg_hum["low"])
        apply_rule(w5, "high", "accelerated")

        # Rule 6: High temp + Severe wind -> Extreme Risk
        w6 = min(deg_temp["high"], deg_wind["severe"])
        apply_rule(w6, "extreme", "emergency")

        # Rule 7: Extreme temp + Very Low humidity -> Extreme Risk
        w7 = min(deg_temp["extreme"], deg_hum["very_low"])
        apply_rule(w7, "extreme", "emergency")

        # Rule 8: Critical fuel dryness + High wind -> Extreme Risk
        w8 = min(deg_fuel["critical"], deg_wind["high"])
        apply_rule(w8, "extreme", "emergency")

        # Rule 9: Extreme temp + Critical fuel dryness -> Extreme Risk
        w9 = min(deg_temp["extreme"], deg_fuel["critical"])
        apply_rule(w9, "extreme", "emergency")

        # Rule 10: Calm wind + High humidity -> Low Risk
        w10 = min(deg_wind["calm"], deg_hum["high"])
        apply_rule(w10, "low", "standard")

        # 3. Defuzzification (Centroid Method)
        crisp_risk = defuzz_centroid(self.x_risk, agg_risk, default=10.0)
        crisp_speed = defuzz_centroid(self.x_speed, agg_speed, default=20.0)

        # Determine Alert Category
        if crisp_risk < 30.0:
            alert_level = 0  # Low / Normal Advisory
            alert_name = "NORMAL"
        elif crisp_risk < 60.0:
            alert_level = 1  # Moderate / Watch
            alert_name = "WATCH"
        elif crisp_risk < 80.0:
            alert_level = 2  # High / Warning
            alert_name = "WARNING"
        else:
            alert_level = 3  # Extreme / Critical Evacuate
            alert_name = "CRITICAL"

        return {
            "fire_risk_index": round(crisp_risk, 2),
            "patrol_urgency_speed": round(crisp_speed, 2),
            "alert_level": alert_level,
            "alert_name": alert_name,
        }
