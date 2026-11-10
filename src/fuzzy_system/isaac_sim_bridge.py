"""NVIDIA Isaac Sim Integration Bridge.

This module interfaces the WildfireFuzzyController with synthetic sensors
(virtual thermometer, hygrometer, anemometer, and thermal cameras)
within an NVIDIA Isaac Sim / Isaac Lab Omniverse stage.
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Import fuzzy controller
from .controller import WildfireFuzzyController

REPO_ROOT = Path(__file__).resolve().parent.parent.parent


class IsaacSimFuzzyBridge:
    """Bridges synthetic environmental sensors in Isaac Sim with the Fuzzy Controller."""

    def __init__(self, stage_path: Optional[str] = None):
        default_stage = REPO_ROOT / "assets" / "wildfire_forest_uav_stage.usda"
        self.stage_path = str(stage_path) if stage_path else str(default_stage)
        self.controller = WildfireFuzzyController()
        self.is_connected = False
        self.step_number = 0
        self.uav_position = [0.0, 0.0, 5.0]
        self.scenario = "worsening"
        self.stage = None
        self.drone_prim = None

    def initialize_omniverse_context(self):
        """Attempts to attach to active Omniverse / Isaac Sim USD stage."""
        try:
            import omni.usd  # type: ignore

            context = omni.usd.get_context()
            self.stage = context.get_stage()
            if self.stage:
                self.drone_prim = self.stage.GetPrimAtPath("/World/UAV_Drone")
                self.is_connected = True
                print(f"[IsaacSimBridge] Connected to live Omniverse stage. Drone Prim: {self.drone_prim.IsValid()}")
            else:
                print(f"[IsaacSimBridge] Omniverse context initialized, but no active stage loaded yet.")
                self.is_connected = False
        except ImportError:
            print("[IsaacSimBridge] Running in Standalone / Mock Simulation mode.")
            self.stage = None
            self.is_connected = False

    def read_synthetic_sensors(self, step: Optional[int] = None) -> Dict[str, float]:
        """Reads simulated ambient conditions from the virtual Isaac Sim environment.

        If connected to a live stage with custom attributes, reads from the drone prim;
        otherwise synthesizes dynamic conditions based on the active scenario profile.
        """
        if self.is_connected and self.drone_prim and self.drone_prim.IsValid():
            try:
                temp_attr = self.drone_prim.GetAttribute("fuzzy:temperature")
                hum_attr = self.drone_prim.GetAttribute("fuzzy:humidity")
                wind_attr = self.drone_prim.GetAttribute("fuzzy:wind_speed")
                dry_attr = self.drone_prim.GetAttribute("fuzzy:vegetation_dryness")

                if all(a.IsValid() for a in [temp_attr, hum_attr, wind_attr, dry_attr]):
                    return {
                        "temperature": float(temp_attr.Get()),
                        "humidity": float(hum_attr.Get()),
                        "wind_speed": float(wind_attr.Get()),
                        "vegetation_dryness": float(dry_attr.Get()),
                    }
            except Exception as e:
                print(f"[IsaacSimBridge] Could not read live USD attributes: {e}")

        # Scenario profiles for mock/standalone simulation
        profiles: Dict[str, Tuple[Tuple[float, ...], Tuple[float, ...]]] = {
            "normal": (
                (24.0, 55.0, 18.0, 35.0),
                (26.0, 50.0, 25.0, 45.0),
            ),
            "worsening": (
                (24.0, 70.0, 15.0, 30.0),
                (44.0, 20.0, 75.0, 90.0),
            ),
            "critical": (
                (42.0, 25.0, 70.0, 85.0),
                (48.0, 10.0, 95.0, 100.0),
            ),
        }
        if self.scenario not in profiles:
            raise ValueError(f"Unknown mock scenario: {self.scenario}")

        start, end = profiles[self.scenario]
        current_step = self.step_number if step is None else step
        progress = min(max(current_step, 0), 9) / 9
        values = [initial + (final - initial) * progress for initial, final in zip(start, end)]
        return dict(zip(
            ("temperature", "humidity", "wind_speed", "vegetation_dryness"),
            values,
        ))

    def dispatch_agent_commands(self, outputs: dict):
        """Dispatches computed fuzzy control targets to Isaac Sim agents."""
        risk_index = outputs["fire_risk_index"]
        speed = outputs["patrol_urgency_speed"]
        alert_value = outputs["suppression_alert_level"]
        alert = outputs["alert_level"]

        # Advance UAV position along patrol grid
        self.uav_position[0] += speed / 50.0
        self.uav_position[1] += 0.8

        print(f"\n--- [Isaac Sim Action Graph Execution] Step {self.step_number} ---")
        print(f"Computed Wildfire Risk Index : {risk_index:.2f} / 100")
        print(f"Patrol Urgency / Drone Speed : {speed:.2f} %")
        print(f"Suppression Alert Level      : {alert_value:.3f} / 3  [{alert}]")
        print(f"Dispatched System Status     : [{outputs['alert_name']}] {outputs['alert_label']}")
        print(f"UAV Patrol Position          : ({self.uav_position[0]:.2f}, {self.uav_position[1]:.2f}, {self.uav_position[2]:.2f}m)")

        if self.is_connected and self.drone_prim and self.drone_prim.IsValid():
            try:
                # Update custom USD attributes on the live drone prim
                self.drone_prim.GetAttribute("fuzzy:fire_risk_index").Set(risk_index)
                self.drone_prim.GetAttribute("fuzzy:patrol_urgency_speed").Set(speed)
                self.drone_prim.GetAttribute("fuzzy:alert_level").Set(alert)
                self.drone_prim.GetAttribute("fuzzy:alert_status").Set(outputs["alert_name"])
                print("[IsaacSimBridge] Synchronized telemetry to live USD Stage attributes.")
            except Exception as e:
                print(f"[IsaacSimBridge] USD attribute sync notice: {e}")
        else:
            print("[Notice] Synthetic actuation simulated in headless test harness.")

    def run_step(self):
        """Execute one evaluation loop."""
        sensors = self.read_synthetic_sensors()
        outputs = self.controller.compute(
            temperature=sensors["temperature"],
            humidity=sensors["humidity"],
            wind_speed=sensors["wind_speed"],
            vegetation_dryness=sensors["vegetation_dryness"],
        )
        self.dispatch_agent_commands(outputs)
        self.step_number += 1
        return outputs

    def run_mock_simulation(self, scenario: str = "worsening", steps: int = 10) -> List[Dict]:
        """Run a deterministic multi-step simulation."""
        if steps < 1:
            raise ValueError("steps must be at least 1")
        self.scenario = scenario
        self.step_number = 0
        self.uav_position = [0.0, 0.0, 5.0]

        print(f"[IsaacSimBridge] Running '{scenario}' scenario for {steps} steps.")
        print(f"[IsaacSimBridge] Bound Stage Asset: {self.stage_path}")
        results = []
        for _ in range(steps):
            results.append(self.run_step())
        return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the Isaac Sim wildfire simulation bridge.")
    parser.add_argument(
        "--scenario",
        choices=("normal", "worsening", "critical"),
        default="worsening",
        help="synthetic weather trajectory to simulate",
    )
    parser.add_argument("--steps", type=int, default=10, help="number of simulation steps")
    parser.add_argument("--stage", type=str, default=None, help="path to custom USD stage asset")
    args = parser.parse_args()

    bridge = IsaacSimFuzzyBridge(stage_path=args.stage)
    bridge.initialize_omniverse_context()
    bridge.run_mock_simulation(scenario=args.scenario, steps=args.steps)
