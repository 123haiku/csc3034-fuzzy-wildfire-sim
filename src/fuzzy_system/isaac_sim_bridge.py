"""NVIDIA Isaac Sim Integration Bridge.

This module demonstrates interfacing the WildfireFuzzyController with
synthetic sensors (virtual thermometer, hygrometer, anemometer, and thermal cameras)
within an NVIDIA Isaac Sim / Isaac Lab Omniverse stage.
"""

import sys
import time
from typing import Optional

# Import fuzzy controller
from .controller import WildfireFuzzyController


class IsaacSimFuzzyBridge:
    """Bridges synthetic environmental sensors in Isaac Sim with the Fuzzy Controller."""

    def __init__(self, stage_path: Optional[str] = None):
        self.stage_path = stage_path
        self.controller = WildfireFuzzyController()
        self.is_connected = False

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

    def read_synthetic_sensors(self) -> dict:
        """Reads simulated ambient conditions from the virtual Isaac Sim environment.

        In full Isaac Sim deployment, these are polled from USD prim attributes,
        anemometer extensions, or synthetic weather physics graphs.
        """
        # Default mock sensor readings for demonstration & headless testing
        return {
            "temperature": 39.5,         # deg C (High ambient heat)
            "humidity": 18.0,            # % (Very low relative humidity)
            "wind_speed": 62.0,          # km/h (High wind velocity)
            "vegetation_dryness": 88.0,  # % (Critically dry undergrowth)
        }

    def dispatch_agent_commands(self, outputs: dict):
        """Dispatches computed fuzzy control targets to Isaac Sim agents."""
        risk_index = outputs["fire_risk_index"]
        speed = outputs["patrol_urgency_speed"]
        alert = outputs["alert_name"]

        print(f"\n--- [Isaac Sim Action Graph Execution] ---")
        print(f"Computed Wildfire Risk Index : {risk_index:.2f} / 100")
        print(f"Patrol Urgency / Drone Speed : {speed:.2f} %")
        print(f"Dispatched System Status     : [{alert}]")

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
        return outputs


if __name__ == "__main__":
    bridge = IsaacSimFuzzyBridge()
    bridge.initialize_omniverse_context()
    bridge.run_step()
