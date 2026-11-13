"""Procedural USD Forest Terrain and UAV Drone Stage Generator.

Generates an OpenUSD (.usda) scene asset for NVIDIA Isaac Sim, containing:
1. Forest terrain ground plane with environmental materials.
2. Procedurally distributed pine and deciduous trees with foliage variations.
3. Fire hazard hotspots with emissive thermal radiation markers.
4. Quadcopter UAV drone with body, arms, propellers, and thermal camera.
5. Real-time telemetry attributes for WildfireFuzzyController integration.
"""

from __future__ import annotations

import argparse
import math
import os
import random
import sys
from pathlib import Path
from typing import Dict, List, Tuple

# Add parent directory to path for fuzzy system imports
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "src"))

from fuzzy_system.controller import WildfireFuzzyController


def generate_tree_usda(tree_id: int, x: float, y: float, height: float, radius: float, is_dry: bool) -> str:
    """Generates a tree prim with trunk and foliage cone/sphere."""
    trunk_height = height * 0.45
    trunk_radius = radius * 0.22
    foliage_mat = "FoliageDry" if is_dry else "FoliageHealthy"

    return f"""
    def Xform "Tree_{tree_id:03d}" (
        prepend apiSchemas = ["PhysicsCollisionAPI"]
    )
    {{
        float3 xformOp:translate = ({x:.2f}, {y:.2f}, 0.0)
        uniform token[] xformOpOrder = ["xformOp:translate"]

        def Cylinder "Trunk"
        {{
            uniform token axis = "Z"
            double height = {trunk_height:.2f}
            double radius = {trunk_radius:.2f}
            float3 xformOp:translate = (0.0, 0.0, {trunk_height / 2.0:.2f})
            uniform token[] xformOpOrder = ["xformOp:translate"]
            rel material:binding = </World/Materials/BarkMaterial>
        }}

        def Cone "Canopy_Lower"
        {{
            uniform token axis = "Z"
            double height = {height * 0.4:.2f}
            double radius = {radius:.2f}
            float3 xformOp:translate = (0.0, 0.0, {trunk_height + height * 0.2:.2f})
            uniform token[] xformOpOrder = ["xformOp:translate"]
            rel material:binding = </World/Materials/{foliage_mat}>
        }}

        def Cone "Canopy_Upper"
        {{
            uniform token axis = "Z"
            double height = {height * 0.35:.2f}
            double radius = {radius * 0.75:.2f}
            float3 xformOp:translate = (0.0, 0.0, {trunk_height + height * 0.45:.2f})
            uniform token[] xformOpOrder = ["xformOp:translate"]
            rel material:binding = </World/Materials/{foliage_mat}>
        }}
    }}"""


def generate_hotspot_usda(hotspot_id: int, x: float, y: float, intensity: float, radius: float) -> str:
    """Generates a wildfire hotspot ignition zone with emissive thermal glow."""
    return f"""
    def Xform "Hotspot_{hotspot_id:02d}"
    {{
        float3 xformOp:translate = ({x:.2f}, {y:.2f}, 0.05)
        uniform token[] xformOpOrder = ["xformOp:translate"]

        def Cylinder "HeatZone"
        {{
            uniform token axis = "Z"
            double height = 0.1
            double radius = {radius:.2f}
            rel material:binding = </World/Materials/HotspotFire>
        }}

        def Sphere "CoreFlame"
        {{
            double radius = {radius * 0.4:.2f}
            float3 xformOp:translate = (0.0, 0.0, {radius * 0.3:.2f})
            uniform token[] xformOpOrder = ["xformOp:translate"]
            rel material:binding = </World/Materials/HotspotFire>
        }}
    }}"""


# Sensor synthesis shared by the baked stage telemetry and the mission log. Keeping one
# implementation means the attributes authored onto the UAV prim and the numbers in the
# report's mission table are produced by the same model; they used to be two separate
# copies with different boost coefficients.
BASE_TEMP = 28.0
BASE_HUMIDITY = 48.0
BASE_WIND = 25.0
BASE_DRYNESS = 40.0
HOTSPOT_RADIUS = 12.0


def synthesise_sensors(x: float, y: float, hotspots, rng: random.Random | None = None):
    """Returns (temperature, humidity, wind, fuel dryness) for a position on the stage.

    A hotspot displaces the baseline readings in proportion to proximity; passing an rng
    adds the per-waypoint sensor jitter used by the mission log.
    """
    min_dist = min(math.hypot(x - h["x"], y - h["y"]) for h in hotspots)
    proximity = max(0.0, 1.0 - (min_dist / HOTSPOT_RADIUS))

    jitter_temp = rng.uniform(-1.0, 1.5) if rng else 0.0
    jitter_hum = rng.uniform(-2.0, 2.0) if rng else 0.0
    jitter_wind = rng.uniform(-3.0, 4.0) if rng else 0.0
    jitter_dry = rng.uniform(-1.0, 2.0) if rng else 0.0

    temperature = min(50.0, BASE_TEMP + 16.0 * proximity + jitter_temp)
    humidity = max(5.0, BASE_HUMIDITY - 32.0 * proximity + jitter_hum)
    wind = min(95.0, BASE_WIND + 20.0 * proximity + jitter_wind)
    dryness = min(100.0, BASE_DRYNESS + 50.0 * proximity + jitter_dry)
    return temperature, humidity, wind, dryness


def generate_uav_drone_usda() -> str:
    """Generates a detailed quadcopter UAV drone with a baked flight path.

    The rotors are static discs: this build does not animate blade rotation, so no blade
    rate is authored and none is reported.
    """
    arm_length = 0.55
    prop_radius = 0.24

    wps = [
        (0, (0.0, 0.0, 5.0)),
        (40, (4.0, 5.0, 5.5)),
        (80, (8.0, 10.0, 6.0)),
        (120, (13.5, 15.5, 5.0)),   # Approaching Hotspot 1
        (160, (15.0, 17.0, 4.5)),   # Scanning Hotspot 1
        (200, (10.0, 18.0, 6.5)),
        (240, (0.0, 15.0, 7.0)),
        (280, (-10.0, 12.0, 6.0)),
        (320, (-17.5, 9.8, 4.5)),   # Scanning Hotspot 2
        (380, (-10.0, 0.0, 6.0)),
        (440, (0.0, -10.0, 6.5)),
        (500, (7.8, -19.5, 5.0)),   # Scanning Hotspot 3
        (560, (5.0, -10.0, 5.5)),
        (620, (0.0, 0.0, 5.0)),     # Return to Base
    ]

    trans_samples = []
    rot_samples = []
    temp_samples = []
    risk_samples = []
    speed_samples = []

    controller = WildfireFuzzyController()
    hotspots = [
        {"x": 14.0, "y": 16.0},
        {"x": -18.0, "y": 10.0},
        {"x": 8.0, "y": -20.0},
    ]

    for i, (frame, (x, y, z)) in enumerate(wps):
        trans_samples.append(f"            {frame}: ({x:.2f}, {y:.2f}, {z:.2f}),")

        # Compute heading
        if i < len(wps) - 1:
            _, (nx, ny, _) = wps[i + 1]
        else:
            _, (nx, ny, _) = wps[0]
        dx = nx - x
        dy = ny - y
        yaw = math.degrees(math.atan2(dy, dx)) if (dx != 0 or dy != 0) else 0.0
        pitch = 5.0 if math.hypot(dx, dy) > 0.1 else 0.0
        rot_samples.append(f"            {frame}: ({pitch:.1f}, 0.0, {yaw:.1f}),")

        # Compute telemetry based on distance to hotspots
        t, rh, w, dry = synthesise_sensors(x, y, hotspots)
        out = controller.compute(temperature=t, humidity=rh, wind_speed=w, vegetation_dryness=dry)

        temp_samples.append(f"            {frame}: {t:.1f},")
        risk_samples.append(f"            {frame}: {out['fire_risk_index']:.1f},")
        speed_samples.append(f"            {frame}: {out['patrol_urgency_speed']:.1f},")

    trans_str = "\n".join(trans_samples)
    rot_str = "\n".join(rot_samples)
    temp_str = "\n".join(temp_samples)
    risk_str = "\n".join(risk_samples)
    speed_str = "\n".join(speed_samples)

    return f"""
    def Xform "UAV_Drone"
    {{
        float3 xformOp:translate.timeSamples = {{
{trans_str}
        }}
        float3 xformOp:rotateXYZ.timeSamples = {{
{rot_str}
        }}
        float3 xformOp:scale = (1.0, 1.0, 1.0)
        uniform token[] xformOpOrder = ["xformOp:translate", "xformOp:rotateXYZ", "xformOp:scale"]

        # Real-time Fuzzy Telemetry Attributes (Keyframed with flight position)
        custom double fuzzy:temperature.timeSamples = {{
{temp_str}
        }}
        custom double fuzzy:fire_risk_index.timeSamples = {{
{risk_str}
        }}
        custom double fuzzy:patrol_urgency_speed.timeSamples = {{
{speed_str}
        }}
        custom double fuzzy:humidity = 18.0
        custom double fuzzy:wind_speed = 62.0
        custom double fuzzy:vegetation_dryness = 88.0
        custom string fuzzy:alert_status = "PATROLLING"
        custom int fuzzy:alert_level = 1
        custom string fuzzy:defuzz_method = "centroid"

        # Central Fuselage
        def Cube "Fuselage"
        {{
            double size = 1.0
            float3 xformOp:scale = (0.35, 0.35, 0.14)
            uniform token[] xformOpOrder = ["xformOp:scale"]
            rel material:binding = </World/Materials/DroneChassis>
        }}

        # Avionics & Battery Top Dome
        def Sphere "AvionicsDome"
        {{
            double radius = 0.16
            float3 xformOp:scale = (1.0, 1.0, 0.6)
            float3 xformOp:translate = (0.0, 0.0, 0.08)
            uniform token[] xformOpOrder = ["xformOp:translate", "xformOp:scale"]
            rel material:binding = </World/Materials/DroneAccent>
        }}

        # Forward Sensor Pod / Thermal Camera
        def Cylinder "ThermalSensorPod"
        {{
            uniform token axis = "X"
            double height = 0.15
            double radius = 0.06
            float3 xformOp:translate = (0.22, 0.0, -0.04)
            uniform token[] xformOpOrder = ["xformOp:translate"]
            rel material:binding = </World/Materials/DroneSensorLens>
        }}

        # Third-Person Drone Chase Camera (Locks to UAV flight path)
        def Camera "ChaseCamera"
        {{
            float2 clippingRange = (0.05, 2000.0)
            float focalLength = 18.0
            float horizontalAperture = 20.955
            float verticalAperture = 11.787
            float3 xformOp:translate = (-2.2, 0.0, 0.8)
            float3 xformOp:rotateXYZ = (75.0, 0.0, -90.0)
            uniform token[] xformOpOrder = ["xformOp:translate", "xformOp:rotateXYZ"]
        }}

        # First-Person Thermal Surveillance Camera (Forward-down view)
        def Camera "ThermalGimbalCamera"
        {{
            float2 clippingRange = (0.05, 2000.0)
            float focalLength = 24.0
            float horizontalAperture = 20.955
            float verticalAperture = 11.787
            float3 xformOp:translate = (0.28, 0.0, -0.06)
            float3 xformOp:rotateXYZ = (60.0, 0.0, -90.0)
            uniform token[] xformOpOrder = ["xformOp:translate", "xformOp:rotateXYZ"]
        }}

        # 4 Quadcopter Arms
        def Cube "Arm_FL"
        {{
            double size = 1.0
            float3 xformOp:translate = ({arm_length * 0.5 * 0.707:.3f}, {arm_length * 0.5 * 0.707:.3f}, 0.0)
            float3 xformOp:rotateXYZ = (0.0, 0.0, 45.0)
            float3 xformOp:scale = ({arm_length:.3f}, 0.04, 0.03)
            uniform token[] xformOpOrder = ["xformOp:translate", "xformOp:rotateXYZ", "xformOp:scale"]
            rel material:binding = </World/Materials/DroneChassis>
        }}

        def Cube "Arm_FR"
        {{
            double size = 1.0
            float3 xformOp:translate = ({arm_length * 0.5 * 0.707:.3f}, {-arm_length * 0.5 * 0.707:.3f}, 0.0)
            float3 xformOp:rotateXYZ = (0.0, 0.0, -45.0)
            float3 xformOp:scale = ({arm_length:.3f}, 0.04, 0.03)
            uniform token[] xformOpOrder = ["xformOp:translate", "xformOp:rotateXYZ", "xformOp:scale"]
            rel material:binding = </World/Materials/DroneChassis>
        }}

        def Cube "Arm_RL"
        {{
            double size = 1.0
            float3 xformOp:translate = ({-arm_length * 0.5 * 0.707:.3f}, {arm_length * 0.5 * 0.707:.3f}, 0.0)
            float3 xformOp:rotateXYZ = (0.0, 0.0, -45.0)
            float3 xformOp:scale = ({arm_length:.3f}, 0.04, 0.03)
            uniform token[] xformOpOrder = ["xformOp:translate", "xformOp:rotateXYZ", "xformOp:scale"]
            rel material:binding = </World/Materials/DroneChassis>
        }}

        def Cube "Arm_RR"
        {{
            double size = 1.0
            float3 xformOp:translate = ({-arm_length * 0.5 * 0.707:.3f}, {-arm_length * 0.5 * 0.707:.3f}, 0.0)
            float3 xformOp:rotateXYZ = (0.0, 0.0, 45.0)
            float3 xformOp:scale = ({arm_length:.3f}, 0.04, 0.03)
            uniform token[] xformOpOrder = ["xformOp:translate", "xformOp:rotateXYZ", "xformOp:scale"]
            rel material:binding = </World/Materials/DroneChassis>
        }}

        # 4 Rotors with High-Speed Animated Spin
        def Cylinder "Rotor_FL"
        {{
            uniform token axis = "Z"
            double height = 0.015
            double radius = {prop_radius:.2f}
            float3 xformOp:translate = ({arm_length * 0.707:.3f}, {arm_length * 0.707:.3f}, 0.04)
            float3 xformOp:scale = (1.0, 1.0, 1.0)
            uniform token[] xformOpOrder = ["xformOp:translate"]
            rel material:binding = </World/Materials/DroneRotor>
        }}

        def Cylinder "Rotor_FR"
        {{
            uniform token axis = "Z"
            double height = 0.015
            double radius = {prop_radius:.2f}
            float3 xformOp:translate = ({arm_length * 0.707:.3f}, {-arm_length * 0.707:.3f}, 0.04)
            float3 xformOp:scale = (1.0, 1.0, 1.0)
            uniform token[] xformOpOrder = ["xformOp:translate"]
            rel material:binding = </World/Materials/DroneRotor>
        }}

        def Cylinder "Rotor_RL"
        {{
            uniform token axis = "Z"
            double height = 0.015
            double radius = {prop_radius:.2f}
            float3 xformOp:translate = ({-arm_length * 0.707:.3f}, {arm_length * 0.707:.3f}, 0.04)
            float3 xformOp:scale = (1.0, 1.0, 1.0)
            uniform token[] xformOpOrder = ["xformOp:translate"]
            rel material:binding = </World/Materials/DroneRotor>
        }}

        def Cylinder "Rotor_RR"
        {{
            uniform token axis = "Z"
            double height = 0.015
            double radius = {prop_radius:.2f}
            float3 xformOp:translate = ({-arm_length * 0.707:.3f}, {-arm_length * 0.707:.3f}, 0.04)
            float3 xformOp:scale = (1.0, 1.0, 1.0)
            uniform token[] xformOpOrder = ["xformOp:translate"]
            rel material:binding = </World/Materials/DroneRotor>
        }}
    }}"""


def build_wildfire_forest_stage(
    output_path: Path,
    num_trees: int = 45,
    area_size: float = 60.0,
    seed: int = 42,
) -> Path:
    """Builds a complete OpenUSD stage for wildfire simulation."""
    random.seed(seed)

    trees_usda_list = []
    # Distribute trees across forest terrain, avoiding center landing zone
    for i in range(num_trees):
        x = random.uniform(-area_size / 2.0, area_size / 2.0)
        y = random.uniform(-area_size / 2.0, area_size / 2.0)
        # Avoid direct center spawn
        if math.hypot(x, y) < 4.0:
            continue
        height = random.uniform(3.5, 7.5)
        radius = random.uniform(1.2, 2.8)
        # 30% chance of dry vegetation (drought-stressed fuel)
        is_dry = random.random() < 0.35
        trees_usda_list.append(generate_tree_usda(i, x, y, height, radius, is_dry))

    trees_block = "\n".join(trees_usda_list)

    # Wildfire hotspots (danger zones)
    hotspots_usda_list = [
        generate_hotspot_usda(1, 14.0, 16.0, intensity=95.0, radius=3.5),
        generate_hotspot_usda(2, -18.0, 10.0, intensity=80.0, radius=2.8),
        generate_hotspot_usda(3, 8.0, -20.0, intensity=60.0, radius=2.2),
    ]
    hotspots_block = "\n".join(hotspots_usda_list)

    uav_block = generate_uav_drone_usda()

    usda_content = f"""#usda 1.0
(
    customLayerData = {{
        string creator = "CSC3034 Computational Intelligence - Wildfire Fuzzy Surveillance"
        string description = "Procedural Forest Terrain and Animated UAV Drone Stage for NVIDIA Isaac Sim"
    }}
    defaultPrim = "World"
    metersPerUnit = 1.0
    upAxis = "Z"
    startTimeCode = 0
    endTimeCode = 620
    timeCodesPerSecond = 30
)

def Xform "World"
{{
    # Physics Scene Configuration
    def PhysicsScene "PhysicsScene"
    {{
        vector3f physics:gravityDirection = (0.0, 0.0, -1.0)
        float physics:gravityMagnitude = 9.81
    }}

    # Lighting: Sun & Skylight
    def DistantLight "SunLight"
    {{
        float inputs:angle = 1.2
        color3f inputs:color = (1.0, 0.96, 0.88)
        float inputs:intensity = 2800.0
        float3 xformOp:rotateXYZ = (-48.0, 32.0, 0.0)
        uniform token[] xformOpOrder = ["xformOp:rotateXYZ"]
    }}

    def DomeLight "SkyLight"
    {{
        color3f inputs:color = (0.75, 0.85, 1.0)
        float inputs:intensity = 450.0
    }}

    # Visual & Physics Materials
    def Scope "Materials"
    {{
        def Material "GroundMaterial"
        {{
            token outputs:surface.connect = </World/Materials/GroundMaterial/Surface.outputs:surface>
            def Shader "Surface"
            {{
                uniform token info:id = "UsdPreviewSurface"
                color3f inputs:diffuseColor = (0.16, 0.22, 0.11)
                float inputs:roughness = 0.85
                token outputs:surface
            }}
        }}

        def Material "BarkMaterial"
        {{
            token outputs:surface.connect = </World/Materials/BarkMaterial/Surface.outputs:surface>
            def Shader "Surface"
            {{
                uniform token info:id = "UsdPreviewSurface"
                color3f inputs:diffuseColor = (0.28, 0.17, 0.10)
                float inputs:roughness = 0.90
                token outputs:surface
            }}
        }}

        def Material "FoliageHealthy"
        {{
            token outputs:surface.connect = </World/Materials/FoliageHealthy/Surface.outputs:surface>
            def Shader "Surface"
            {{
                uniform token info:id = "UsdPreviewSurface"
                color3f inputs:diffuseColor = (0.09, 0.32, 0.12)
                float inputs:roughness = 0.65
                token outputs:surface
            }}
        }}

        def Material "FoliageDry"
        {{
            token outputs:surface.connect = </World/Materials/FoliageDry/Surface.outputs:surface>
            def Shader "Surface"
            {{
                uniform token info:id = "UsdPreviewSurface"
                color3f inputs:diffuseColor = (0.55, 0.44, 0.18)
                float inputs:roughness = 0.75
                token outputs:surface
            }}
        }}

        def Material "HotspotFire"
        {{
            token outputs:surface.connect = </World/Materials/HotspotFire/Surface.outputs:surface>
            def Shader "Surface"
            {{
                uniform token info:id = "UsdPreviewSurface"
                color3f inputs:diffuseColor = (1.0, 0.22, 0.05)
                color3f inputs:emissiveColor = (1.0, 0.35, 0.08)
                float inputs:roughness = 0.2
                token outputs:surface
            }}
        }}

        def Material "DroneChassis"
        {{
            token outputs:surface.connect = </World/Materials/DroneChassis/Surface.outputs:surface>
            def Shader "Surface"
            {{
                uniform token info:id = "UsdPreviewSurface"
                color3f inputs:diffuseColor = (0.08, 0.09, 0.10)
                float inputs:metallic = 0.8
                float inputs:roughness = 0.35
                token outputs:surface
            }}
        }}

        def Material "DroneAccent"
        {{
            token outputs:surface.connect = </World/Materials/DroneAccent/Surface.outputs:surface>
            def Shader "Surface"
            {{
                uniform token info:id = "UsdPreviewSurface"
                color3f inputs:diffuseColor = (0.95, 0.55, 0.08)
                float inputs:roughness = 0.4
                token outputs:surface
            }}
        }}

        def Material "DroneSensorLens"
        {{
            token outputs:surface.connect = </World/Materials/DroneSensorLens/Surface.outputs:surface>
            def Shader "Surface"
            {{
                uniform token info:id = "UsdPreviewSurface"
                color3f inputs:diffuseColor = (0.05, 0.05, 0.08)
                color3f inputs:emissiveColor = (0.1, 0.4, 0.8)
                float inputs:roughness = 0.1
                token outputs:surface
            }}
        }}

        def Material "DroneRotor"
        {{
            token outputs:surface.connect = </World/Materials/DroneRotor/Surface.outputs:surface>
            def Shader "Surface"
            {{
                uniform token info:id = "UsdPreviewSurface"
                color3f inputs:diffuseColor = (0.85, 0.15, 0.15)
                float inputs:roughness = 0.35
                token outputs:surface
            }}
        }}
    }}

    # Forest Ground Plane & Terrain Boundary
    def Cube "GroundPlane" (
        prepend apiSchemas = ["PhysicsCollisionAPI"]
    )
    {{
        double size = 1.0
        float3 xformOp:scale = ({area_size:.1f}, {area_size:.1f}, 0.2)
        float3 xformOp:translate = (0.0, 0.0, -0.1)
        uniform token[] xformOpOrder = ["xformOp:translate", "xformOp:scale"]
        rel material:binding = </World/Materials/GroundMaterial>
    }}

    # Forest Trees Environment
    def Scope "ForestEnvironment"
    {{
{trees_block}
    }}

    # Wildfire Ignition Hotspots
    def Scope "WildfireHotspots"
    {{
{hotspots_block}
    }}

    # Autonomous Surveillance UAV Drone
{uav_block}
}}
"""

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(usda_content, encoding="utf-8")
    return output_path


def run_stage_patrol_simulation(stage_path: Path, steps: int = 12, seed: int = 0) -> List[Dict[str, float]]:
    """Simulates UAV drone patrolling across the forest stage, computing fuzzy risk at each waypoint.

    The synthetic sensor noise is drawn from a seeded generator local to the call, so a
    given seed always reproduces the same mission log and the report tables stay valid.
    """
    rng = random.Random(seed)
    controller = WildfireFuzzyController()

    # Define a search-and-surveillance flight path over the hotspots
    waypoints = [
        (0.0, 0.0, 5.0),
        (4.0, 5.0, 5.5),
        (8.0, 10.0, 6.0),
        (13.5, 15.5, 5.0),  # Near Hotspot 1 (High hazard)
        (15.0, 17.0, 4.5),  # Core of Hotspot 1
        (10.0, 18.0, 6.5),
        (0.0, 15.0, 7.0),
        (-10.0, 12.0, 6.0),
        (-17.5, 9.8, 4.5),  # Near Hotspot 2 (Moderate-High hazard)
        (-10.0, 0.0, 6.0),
        (0.0, -10.0, 6.5),
        (7.8, -19.5, 5.0),  # Near Hotspot 3
    ]

    hotspots = [
        {"x": 14.0, "y": 16.0, "temp_boost": 18.0, "dry_boost": 45.0},
        {"x": -18.0, "y": 10.0, "temp_boost": 14.0, "dry_boost": 35.0},
        {"x": 8.0, "y": -20.0, "temp_boost": 10.0, "dry_boost": 25.0},
    ]

    print(f"\n==================================================================")
    print(f"  CSC3034 Autonomous UAV Surveillance Mission — Stage Simulation")
    print(f"  Stage Asset: {stage_path.name}")
    print(f"==================================================================")

    results = []
    base_temp = 28.0
    base_humidity = 48.0
    base_wind = 25.0
    base_dryness = 40.0

    for step_idx in range(min(steps, len(waypoints))):
        wx, wy, wz = waypoints[step_idx]

        # Sensor readings are produced by the same model that bakes the stage attributes.
        current_temp, current_humidity, current_wind, current_dryness = synthesise_sensors(
            wx, wy, hotspots, rng
        )

        outputs = controller.compute(
            temperature=current_temp,
            humidity=current_humidity,
            wind_speed=current_wind,
            vegetation_dryness=current_dryness,
        )

        record = {
            "step": step_idx,
            "x": wx,
            "y": wy,
            "z": wz,
            "temperature": current_temp,
            "humidity": current_humidity,
            "wind_speed": current_wind,
            "vegetation_dryness": current_dryness,
            "fire_risk_index": outputs["fire_risk_index"],
            "patrol_speed": outputs["patrol_urgency_speed"],
            "suppression_alert_level": outputs["suppression_alert_level"],
            "alert_level": outputs["alert_level"],
            "alert_name": outputs["alert_name"],
        }
        results.append(record)

        print(
            f"Step {step_idx:02d} | Coord: ({wx:5.1f}, {wy:5.1f}, {wz:3.1f}m) | "
            f"Sensors: [T={current_temp:4.1f}°C, RH={current_humidity:4.1f}%, W={current_wind:4.1f}km/h, FuelDry={current_dryness:4.1f}%] | "
            f"Fuzzy FRI: {outputs['fire_risk_index']:5.1f} | Urgency: {outputs['patrol_urgency_speed']:5.1f}% | "
            f"Alert: {outputs['suppression_alert_level']:4.2f} [{outputs['alert_name']}]"
        )

    print(f"==================================================================")
    print(f"Simulation completed across {len(results)} waypoints successfully.")
    return results


def main():
    parser = argparse.ArgumentParser(description="Build and simulate Isaac Sim USD Forest UAV Stage.")
    parser.add_argument(
        "--output",
        type=str,
        default=str(REPO_ROOT / "assets" / "wildfire_forest_uav_stage.usda"),
        help="Target output USD file path",
    )
    parser.add_argument("--trees", type=int, default=48, help="Number of trees to generate")
    parser.add_argument("--area", type=float, default=65.0, help="Terrain dimension (meters)")
    parser.add_argument("--simulate", action="store_true", default=True, help="Run mission waypoint simulation")
    parser.add_argument("--steps", type=int, default=12, help="Number of surveillance steps")
    args = parser.parse_args()

    out_path = Path(args.output)
    print(f"[StageGenerator] Generating USD stage asset at: {out_path} ...")
    build_wildfire_forest_stage(out_path, num_trees=args.trees, area_size=args.area)
    print(f"[StageGenerator] USD Stage created successfully ({out_path.stat().st_size:,} bytes).")

    if args.simulate:
        run_stage_patrol_simulation(out_path, steps=args.steps)


if __name__ == "__main__":
    main()
