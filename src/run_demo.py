"""Interactive CLI demonstration of the Fuzzy Wildfire Risk System."""

from fuzzy_system.controller import WildfireFuzzyController


def main():
    controller = WildfireFuzzyController()

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

    print("=" * 80)
    print("CSC3034 Computational Intelligence: Fuzzy Wildfire Risk Inference System")
    print("=" * 80)

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
        print(f"            Alert Level = {res['alert_level']} ({res['alert_name']})")

    print("\n" + "=" * 80)
    print("Execution completed successfully.")
    print("=" * 80)


if __name__ == "__main__":
    main()
