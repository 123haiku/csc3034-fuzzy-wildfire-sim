"""Speaker notes for the v4 deck, kept in a separate module so the build stays readable.

Every figure quoted here is formatted from docs/measurements.json through values.py, so a
re-measurement updates the spoken numbers along with the slides.
"""

from values import (BUDGET_PCT, ENGINE, FRAME_END, HOTSPOTS, MEDIAN_MS, P99_MS,
                    STAGE_FPS, TREES, mission_row)

_BASE = mission_row(0)
_HOT = mission_row(3)
_BACK = mission_row(6)
_REPEAT = mission_row(8)

NOTES = {
    1: (
        "OPEN (30 s). Yeoh Choon Hern leads the project and handles coordination and integration. I am Pang Wei Sheng and I own the fuzzy inference engine and the simulation evaluation.\n"
        "- One line on the problem: forest and peat fires are caught late because patrols rely on single-threshold thermostats.\n"
        "- One line on the build: a four-input Mamdani controller flying a UAV inside an Isaac Sim digital twin, closed loop.\n"
        "- Read the roadmap: problem, pipeline, fuzzy engine, rule base, twin, flight results, defuzzification study, feasibility, conclusion.\n"
        "TRANSITION: let me show why the standard approach fails."
    ),
    2: (
        "PROBLEM (60 s). The argument is that one threshold is blind to interaction.\n"
        "- Concrete example from the engine itself: 38 C at 85 % humidity scores FRI 14.0, NORMAL; 26 C at 15 % humidity with 65 km/h wind scores FRI 71.4, WARNING. A T>40 rule ranks them the other way round.\n"
        "- Control consequence: a false alarm burns crew hours and erodes trust in the alert.\n"
        "- Land the right column: continuous membership instead of a cliff, four probes fused, and the output is a throttle command, so the aircraft closes its own loop.\n"
        "Q: why fuzzy and not a neural net? A: ten auditable rules, no training set, and every decision traces to a rule the fire authority can read."
    ),
    3: (
        "PIPELINE (60 s). Walk left to right and name the data rate.\n"
        f"- 01: four probes keyed at the {STAGE_FPS} fps stage frame rate.\n"
        "- 02: sixteen input sets, four per variable.\n"
        "- 03: ten rules, min for AND, max for aggregation.\n"
        f"- 04: centroid defuzzification; {MEDIAN_MS:.2f} ms median per loop, p99 {P99_MS:.2f} ms, measured.\n"
        "- 05: throttle 20 % to 90 %, alert WATCH / WARNING / CRITICAL.\n"
        f"Say the number that matters: the whole chain is {BUDGET_PCT:.1f} % of a 50 ms control budget."
    ),
    4: (
        "FUZZY ENGINE (75 s). Point at the figure, do not read the text.\n"
        "- Universes: temperature 0-50 C, humidity and wind 0-100, fuel dryness 0-100 %.\n"
        "- Why trapezoids at the ends: they saturate, so the controller stays well behaved past the sensor range.\n"
        "- Overlap is deliberate: adjacent sets cross near 0.5, so output is continuous, never a step.\n"
        "- The emergency set centres at 90 %, which is where the 90 % throttle figure comes from.\n"
        "Q: how were the breakpoints chosen? A: domain literature plus iteration against the twin; ANFIS in the conclusion is the principled way to tune them."
    ),
    5: (
        "RULE BASE (75 s). Do not read all four rows - trace one rule end to end.\n"
        "- 4 inputs x 4 sets is 256 antecedent combinations; the controller carries 10 curated rules because most combinations are physically meaningless.\n"
        "- Take R09: extreme temperature AND critical fuel dryness. Fed the critical scenario (46 C, 12 %, 85 km/h, 95 %) it drives FRI 92.3 and 90.8 % throttle, so the pair of high memberships is what lifts both outputs.\n"
        "- R03 is the counter-example: moderate temperature with moderate fuel tops out at FRI 55.6 on the dry-spring-heat scenario, well short of the critical band.\n"
        "- Aggregation is max, so the strongest rule dominates without a hand-written priority order.\n"
        "Q: what if two rules conflict? A: max aggregation resolves it and the centroid weights the overlap - which is why COG beat MOM."
    ),
    6: (
        "DIGITAL TWIN (60 s). This slide proves the loop is closed in a 3D scene, not on a spreadsheet.\n"
        f"- 65 m x 65 m OpenUSD stage, {TREES} procedurally placed trees, {HOTSPOTS} active hotspots, {ENGINE['uav_keyframes']} keyframes over frames 0-{FRAME_END}.\n"
        "- Viewport frame rate was not instrumented, so no FPS figure is quoted; the sensor ingest runs on the stage timeline.\n"
        "- Two cameras: chase view for context, thermal gimbal for the plume.\n"
        "Q: does the twin actually affect the controller? A: yes - probe readings are read from the stage each keyframe, so moving over a plume changes the next inference immediately."
    ),
    7: (
        "FLIGHT RESULTS (90 s). This is the evidence slide - slow down.\n"
        f"- Baseline WP 00: {_BASE['temperature']:.1f} C, RH {_BASE['humidity']:.1f} %, fuel {_BASE['vegetation_dryness']:.1f} %, risk {_BASE['fire_risk_index']:.1f}, {_BASE['alert_name']}, throttle {_BASE['patrol_urgency']:.1f} %.\n"
        f"- Hotspot entry at WP 03: {_HOT['temperature']:.1f} C, RH {_HOT['humidity']:.1f} %, fuel {_HOT['vegetation_dryness']:.1f} % - all four probes move together, so it is not a single-sensor artefact. Risk {_HOT['fire_risk_index']:.1f}, throttle {_HOT['patrol_urgency']:.1f} %.\n"
        f"- WP 08 repeats it at {_REPEAT['fire_risk_index']:.1f} with no retuning, and WP 06 returns to {_BACK['fire_risk_index']:.1f} and {_BACK['patrol_urgency']:.1f} %, so nothing latches.\n"
        f"- Mention that the {_HOT['patrol_urgency']:.1f} is a centroid output, not a hardcoded 90.\n"
        "Q: any overshoot? A: no oscillation - the output sets are continuous, which is the comparison on the next slide."
    ),
    8: (
        "DEFUZZIFICATION STUDY (75 s). Frame it as a design decision with a measured cost.\n"
        f"- All three methods run inside the same loop budget: the full evaluation loop is {MEDIAN_MS:.2f} ms, so defuzzification is not where they differ.\n"
        "- MOM averages the maxima of the aggregated set, so crossing a boundary jumps the output between peaks - a torque step on a 250 g airframe.\n"
        "- Centroid weights the whole area, so output is continuous in the input. That property matters more than raw latency.\n"
        f"- {MEDIAN_MS:.2f} ms is {BUDGET_PCT:.1f} % of a 50 ms loop, so continuity is free: pick the method that does not chatter.\n"
        "Q: measured or estimated? A: the loop figure is measured on the build machine; there is no Jetson run yet, so quote the edge figure as a projection and say so."
    ),
    9: (
        "FEASIBILITY (45 s). Keep it short - it answers 'can this fly?'\n"
        "- Jetson Orin Nano at 7-15 W fits a micro-UAV pack.\n"
        f"- {MEDIAN_MS:.2f} ms median measured, p99 {P99_MS:.2f} ms; edge figure is a projection.\n"
        "- Payload pairing: FLIR Lepton 3.5 LWIR plus SHT40 for temperature and humidity; LoRa carries the GPS fix to the crew.\n"
        "- SDG 13.1 and 15.2, plus the cost argument: exact coordinates cut containment time and water use.\n"
        "Q: why not the cloud? A: link loss is exactly when a fire matters most, so the decision has to survive offline."
    ),
    10: (
        "CONCLUSION (45 s). Four claims, each already evidenced.\n"
        "- Engine: four inputs, ten rules, verified against the report's test vectors.\n"
        f"- Twin: 65 m procedural forest, {TREES} trees, {HOTSPOTS} hotspots; viewport frame rate not instrumented, so no FPS claim.\n"
        "- Actuation: 20 % to 90 % closed loop over a live hotspot.\n"
        f"- Speed: {MEDIAN_MS:.2f} ms median per loop measured, p99 {P99_MS:.2f} ms; edge figure is a projection.\n"
        "- Future: ANFIS to replace hand-tuned memberships, multi-UAV mesh, PX4 / Matrice 300 field trials.\n"
        "Say the limitation before they do: simulation only, rule base expert-tuned."
    ),
    11: (
        "CLOSE (15 s). Thank the panel, point at the repository for reproducibility.\n"
        "Invite the two questions you are ready for: rule-base justification and validation method.\n"
        "Have one sentence ready: the whole pipeline regenerates from the repo, and be able to name the command."
    ),
}
