"""Speaker notes for the v4 deck, kept in a separate module so the build stays readable."""

NOTES = {
    1: (
        "OPEN (30 s). I am Pang Wei Sheng, project lead on the fuzzy inference engine.\n"
        "- One line on the problem: forest and peat fires are caught late because patrols rely on single-threshold thermostats.\n"
        "- One line on the build: a four-input Mamdani controller flying a UAV inside an Isaac Sim digital twin, closed loop.\n"
        "- Read the roadmap: problem, pipeline, fuzzy engine, rule base, twin, flight results, defuzzification study, feasibility, conclusion.\n"
        "TRANSITION: let me show why the standard approach fails."
    ),
    2: (
        "PROBLEM (60 s). The argument is that one threshold is blind to interaction.\n"
        "- Concrete example: 38 C at 15 % humidity with 70 km/h wind is more dangerous than 42 C at 90 % humidity, yet a T>40 rule ranks them the other way round.\n"
        "- Control consequence: a false alarm burns crew hours and erodes trust in the alert.\n"
        "- Land the right column: continuous membership instead of a cliff, four probes fused, and the output is a throttle command, so the aircraft closes its own loop.\n"
        "Q: why fuzzy and not a neural net? A: ten auditable rules, no training set, and every decision traces to a rule the fire authority can read."
    ),
    3: (
        "PIPELINE (60 s). Walk left to right and name the data rate.\n"
        "- 01: four probes sampled at 60 Hz from the USD stage.\n"
        "- 02: sixteen input sets, four per variable.\n"
        "- 03: ten rules, min for AND, max for aggregation.\n"
        "- 04: centroid defuzzification, 0.88 ms on the Jetson target.\n"
        "- 05: throttle 20 % to 90 %, alert WATCH / WARNING / CRITICAL.\n"
        "Say the number that matters: the whole chain is 1.2 % of a 50 ms control budget."
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
        "- Take R09: extreme temperature AND critical fuel dryness gives risk 92 and 90 % throttle. It is an AND, so both memberships must be high before it fires.\n"
        "- R03 is the counter-example: moderate temperature with moderate fuel only reaches 45 and holds cruise throttle.\n"
        "- Aggregation is max, so the strongest rule dominates without a hand-written priority order.\n"
        "Q: what if two rules conflict? A: max aggregation resolves it and the centroid weights the overlap - which is why COG beat MOM."
    ),
    6: (
        "DIGITAL TWIN (60 s). This slide proves the loop is closed in a 3D scene, not on a spreadsheet.\n"
        "- 65 m x 65 m OpenUSD stage, 48 procedurally placed pines, 3 active hotspots.\n"
        "- 67-72 FPS in RTX Real-Time 2.0, so the 60 Hz sensor ingest is fed by a live simulation, not replayed data.\n"
        "- Two cameras: chase view for context, thermal gimbal for the plume.\n"
        "Q: does the twin actually affect the controller? A: yes - probe readings are read from the stage each tick, so moving over a plume changes the next inference immediately."
    ),
    7: (
        "FLIGHT RESULTS (90 s). This is the evidence slide - slow down.\n"
        "- Baseline: 27.9 C, RH 46.4 %, risk 45.0, WATCH, throttle 20 %.\n"
        "- Hotspot entry at WP 03: 42.9 C, RH 18.1 %, fuel 87.4 % - all four probes move together, so it is not a single-sensor artefact. Risk 91.4, throttle 89.6 %.\n"
        "- WP 08 repeats it at 91.5 with no retuning, and WP 06 returns to 45.0 and 19.8 %, so nothing latches.\n"
        "- Mention that the 89.6 is a centroid output, not a hardcoded 90.\n"
        "Q: any overshoot? A: no oscillation - the output sets are continuous, which is the comparison on the next slide."
    ),
    8: (
        "DEFUZZIFICATION STUDY (75 s). Frame it as a design decision with a measured cost.\n"
        "- Centroid 0.884 ms, bisector 0.912 ms, MOM 0.420 ms. MOM is twice as fast and still unusable.\n"
        "- MOM averages the maxima of the aggregated set, so crossing a boundary jumps the output between peaks - a torque step on a 250 g airframe.\n"
        "- Centroid weights the whole area, so output is continuous in the input. That property matters more than raw latency.\n"
        "- 0.884 ms is 1.8 % of the 50 ms budget, so the 0.46 ms premium buys smoothness for free.\n"
        "Q: measured or estimated? A: measured on the workstation and scaled to the Jetson target - say so plainly."
    ),
    9: (
        "FEASIBILITY (45 s). Keep it short - it answers 'can this fly?'\n"
        "- Jetson Orin Nano at 7-15 W fits a micro-UAV pack.\n"
        "- 0.88 ms inference is under 2 % of the 50 ms loop.\n"
        "- Payload pairing: FLIR Lepton 3.5 LWIR plus SHT40 for temperature and humidity; LoRa carries the GPS fix to the crew.\n"
        "- SDG 13.1 and 15.2, plus the cost argument: exact coordinates cut containment time and water use.\n"
        "Q: why not the cloud? A: link loss is exactly when a fire matters most, so the decision has to survive offline."
    ),
    10: (
        "CONCLUSION (45 s). Four claims, each already evidenced.\n"
        "- Engine: four inputs, ten rules, verified against the report's test vectors.\n"
        "- Twin: 65 m procedural forest at 67-72 FPS.\n"
        "- Actuation: 20 % to 90 % closed loop over a live hotspot.\n"
        "- Speed: 0.15 ms workstation, 0.88 ms edge.\n"
        "- Future: ANFIS to replace hand-tuned memberships, multi-UAV mesh, PX4 / Matrice 300 field trials.\n"
        "Say the limitation before they do: simulation only, rule base expert-tuned."
    ),
    11: (
        "CLOSE (15 s). Thank the panel, point at the repository for reproducibility.\n"
        "Invite the two questions you are ready for: rule-base justification and validation method.\n"
        "Have one sentence ready: the whole pipeline regenerates from the repo, and be able to name the command."
    ),
}
