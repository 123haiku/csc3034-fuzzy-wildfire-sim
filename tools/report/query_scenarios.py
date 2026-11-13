import sys
sys.path.insert(0, 'src')
from fuzzy_system.controller import WildfireFuzzyController

c = WildfireFuzzyController()
cases = [
    (22, 65, 12, 25),
    (32, 40, 30, 55),
    (39, 22, 55, 82),
    (46, 12, 85, 95),
    (28, 45, 25, 40),
    (31, 42, 32, 52),
]
for s in cases:
    r = c.compute(*s)
    print(f"{s} FRI={r['fire_risk_index']:6.2f} URG={r['patrol_urgency_speed']:6.2f} "
          f"ALERT={r['suppression_alert_level']:.3f} {r['alert_name']:8s} peak={r['rule_firing_peak']:.3f}")
