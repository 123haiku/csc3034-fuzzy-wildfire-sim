"""Interactive CLI demonstration of the Fuzzy Wildfire Risk System."""

import argparse

from fuzzy_system.controller import WildfireFuzzyController


def run_scenarios(controller: WildfireFuzzyController):
    scenarios = [
        {
            "name": "Scenario 1: Moist & Cool (Post-Rain Monsoon)",
            "temp": 16.0,
            "humidity": 88.0,
            "wind": 10.0,
            "fuel": 15.0,
        },
        {
            "name": "Scenario 2: Normal Warm Afternoon",
            "temp": 28.0,
            "humidity": 55.0,
            "wind": 25.0,
            "fuel": 45.0,
        },
        {
            "name": "Scenario 3: Dry & Windy Autumn / Elevated Risk",
            "temp": 34.0,
            "humidity": 30.0,
            "wind": 50.0,
            "fuel": 72.0,
        },
        {
            "name": "Scenario 4: Extreme Heatwave & Gusting Gale (Critical Hazard)",
            "temp": 46.0,
            "humidity": 12.0,
            "wind": 75.0,
            "fuel": 95.0,
        },
    ]

    for sc in scenarios:
        res = controller.compute(
            temperature=sc["temp"],
            humidity=sc["humidity"],
            wind_speed=sc["wind"],
            vegetation_dryness=sc["fuel"],
        )

        print(f"\n▶ {sc['name']}")
        print(f"  Inputs  : Temp={sc['temp']}°C | Humidity={sc['humidity']}% | Wind={sc['wind']}km/h | Fuel Dryness={sc['fuel']}%")
        print(f"  Outputs : Fire Risk Index = {res['fire_risk_index']:5.1f} / 100")
        print(f"            Drone Patrol Speed = {res['patrol_urgency_speed']:5.1f} %")
        print(f"            Suppression Alert = {res['suppression_alert_level']:4.2f} / 3  "
              f"[{res['alert_level']}] {res['alert_name']} ({res['alert_label']})")
        print(f"            Action = {res['alert_action']}")


def prompt_for_value(label: str, minimum: float, maximum: float) -> float:
    while True:
        try:
            value = float(input(f"{label} ({minimum:g}-{maximum:g}): "))
        except ValueError:
            print("Please enter a number.")
            continue

        if minimum <= value <= maximum:
            return value

        print(f"Please enter a value from {minimum:g} to {maximum:g}.")


def run_interactive(controller: WildfireFuzzyController):
    print("\nEnter current environmental conditions.")
    temperature = prompt_for_value("Temperature in °C", 0, 50)
    humidity = prompt_for_value("Relative humidity in %", 0, 100)
    wind_speed = prompt_for_value("Wind speed in km/h", 0, 100)
    vegetation_dryness = prompt_for_value("Vegetation dryness in %", 0, 100)

    result = controller.compute(
        temperature=temperature,
        humidity=humidity,
        wind_speed=wind_speed,
        vegetation_dryness=vegetation_dryness,
    )

    print("\n--- Wildfire Assessment ---")
    print(f"Fire Risk Index       : {result['fire_risk_index']:.2f} / 100")
    print(f"Patrol Urgency/Speed  : {result['patrol_urgency_speed']:.2f}%")
    print(f"Suppression Alert     : {result['suppression_alert_level']:.3f} / 3")
    print(f"Alert Tier            : {result['alert_level']} - {result['alert_name']} ({result['alert_label']})")
    print(f"Recommended Action    : {result['alert_action']}")


def main():
    parser = argparse.ArgumentParser(description="Run the fuzzy wildfire risk demo.")
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="enter custom environmental conditions",
    )
    args = parser.parse_args()

    controller = WildfireFuzzyController()

    print("=" * 80)
    print("CSC3034 Computational Intelligence: Fuzzy Wildfire Risk Inference System")
    print("=" * 80)

    if args.interactive:
        run_interactive(controller)
    else:
        run_scenarios(controller)

    print("\n" + "=" * 80)
    print("Execution completed successfully.")
    print("=" * 80)


if __name__ == "__main__":
    main()
