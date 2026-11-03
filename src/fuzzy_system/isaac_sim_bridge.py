"""NVIDIA Isaac Sim Integration Bridge.

This module demonstrates interfacing the WildfireFuzzyController with
synthetic sensors (virtual thermometer, hygrometer, anemometer, and thermal cameras)
within an NVIDIA Isaac Sim / Isaac Lab Omniverse stage.
"""

import argparse
from typing import Dict, Optional, Tuple

# Import fuzzy controller
from .controller import WildfireFuzzyController


class IsaacSimFuzzyBridge:
    """Bridges synthetic environmental sensors in Isaac Sim with the Fuzzy Controller."""

    def __init__(self, stage_path: Optional[str] = None):
        self.stage_path = stage_path
        self.controller = WildfireFuzzyController()
        self.is_connected = False
        self.step_number = 0
        self.uav_position = [0.0, 0.0]
        self.scenario = "worsening"

    def initialize_omniverse_context(self):
        """Attempts to attach to active Omniverse / Isaac Sim USD stage."""
        try:
            # Isaac Sim USD API imports
            import omni.usd  # type: ignore
            self.stage = omni.usd.get_context().get_stage()
            self.is_connected = True
            print("[IsaacSimBridge] Successfully connected to active Isaac Sim stage.")
        except ImportError:
            print("[IsaacSimBridge] Running in Standalone / Mock Simulation mode.")
            self.stage = None
            self.is_connected = False

    def read_synthetic_sensors(self, step: Optional[int] = None) -> Dict[str, float]:
        """Reads simulated ambient conditions from the virtual Isaac Sim environment.

        In full Isaac Sim deployment, these are polled from USD prim attributes,
        anemometer extensions, or synthetic weather physics graphs.
        """
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
        alert = outputs["alert_name"]

        # In standalone mode, patrol speed advances the UAV along its mock route.
        if not self.is_connected:
            self.uav_position[0] += speed / 100.0
            self.uav_position[1] += 0.5

        print(f"\n--- [Isaac Sim Action Graph Execution] Step {self.step_number} ---")
        print(f"Computed Wildfire Risk Index : {risk_index:.2f} / 100")
        print(f"Patrol Urgency / Drone Speed : {speed:.2f} %")
        print(f"Dispatched System Status     : [{alert}]")
        print(f"Mock UAV Position            : ({self.uav_position[0]:.2f}, {self.uav_position[1]:.2f})")

        if self.is_connected:
            # When inside Isaac Sim, update prim velocities or Action Graph variables:
            # Example:
            # drone_prim.GetAttribute("drive:linear:velocity").Set(speed * 0.1)
            pass
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

    def run_mock_simulation(self, scenario: str = "worsening", steps: int = 10):
        """Run a deterministic multi-step simulation without Isaac Sim hardware."""
        if steps < 1:
            raise ValueError("steps must be at least 1")
        self.scenario = scenario
        self.step_number = 0
        self.uav_position = [0.0, 0.0]
        self.is_connected = False

        print(f"[IsaacSimBridge] Running '{scenario}' mock scenario for {steps} steps.")
        results = []
        for _ in range(steps):
            results.append(self.run_step())
        return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the Isaac Sim wildfire mock bridge.")
    parser.add_argument(
        "--scenario",
        choices=("normal", "worsening", "critical"),
        default="worsening",
        help="synthetic weather trajectory to simulate",
    )
    parser.add_argument("--steps", type=int, default=10, help="number of simulation steps")
    args = parser.parse_args()

    bridge = IsaacSimFuzzyBridge()
    bridge.initialize_omniverse_context()
    bridge.run_mock_simulation(scenario=args.scenario, steps=args.steps)
