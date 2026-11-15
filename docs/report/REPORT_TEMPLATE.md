# Intelligent Forest Fire Risk Assessment and UAV Dispatch Using Mamdani Fuzzy Logic in NVIDIA Isaac Sim

**Course**: CSC3034 Computational Intelligence  
**Institution**: School of Mathematical Sciences & Computing, Sunway University  
**Supervisor / Lecturer**: Dr. Tang Tiong Yew  
**Authors**: Pang Wei Sheng (24035115), Roshan A/L Sivakumar (23028285), Dinesswar A/L Sathasivam (23096910), Yeoh Choon Hern (23100795)  
**Submission Date**: November 2026  

---

## Abstract
Wildfires destroy ecosystems and return stored carbon to the atmosphere, and the earlier a hotspot is reported the cheaper it is to contain. Detection is hard because temperature, humidity, wind and fuel moisture interact non-linearly: no single threshold ranks two conditions correctly. This paper presents an explainable Mamdani fuzzy inference system inside NVIDIA Isaac Sim that maps four environmental scalars into three defuzzified consequents — a Fire Risk Index, a UAV patrol urgency throttle, and a continuous suppression alert level — so an aerial patrol reacts to graded hazard instead of a binary alarm. A procedural OpenUSD forest with three thermal hotspots was built, and a deterministic 12-waypoint mission (seed 0) drives the patrol from $20.1\%$ throttle at benign waypoints to $89.5\%$ at the hotspot, with alert $2.826$ of $3$. The engine is validated against a scikit-fuzzy reference (worst deviation ${{reference.worst_deviation}}$ over {{reference.scenarios_total}} scenarios) and {{tests.passed}} unit tests, and costs ${{latency.benign_median_ms}}\ \text{ms}$ per evaluation loop. The work targets SDG 13 (Climate Action) and SDG 15 (Life on Land).

**Keywords**: Computational Intelligence, Mamdani Fuzzy Inference, Wildfire Risk, UAV Surveillance, NVIDIA Isaac Sim, Sustainable Development Goals.
---

## 1. Introduction

### 1.1 Problem Definition and Motivation
Wildfires are among the most destructive natural hazards, and longer fire seasons have raised ignition frequency. Detection latency dominates containment cost: every minute between ignition and first report is paid for in hectares, in suppression budget, and in the carbon the fire returns to the atmosphere. The design target adopted here is therefore a continuous risk estimate that updates at patrol cadence, not a single alarm that fires once.

Remote forest telemetry arrives as four scalars whose effect on ignition is not additive, and no single threshold ranks them correctly:
* A high ambient temperature ($38^\circ\text{C}$) in a tropical rain forest at $85\%$ relative humidity poses little immediate combustion hazard.
* A moderate temperature ($26^\circ\text{C}$) with $15\%$ relative humidity, $65\text{ km/h}$ gusts and desiccated brush is a critical firestorm risk.

The two readings differ by $12^\circ\text{C}$, yet the cooler one is the dangerous one: through the controller of Section 2 the $38^\circ\text{C}$ / $85\%$ case scores $\text{FRI}=14.0$ (`NORMAL`) and the $26^\circ\text{C}$ / $15\%$ / $65\text{ km/h}$ case scores $\text{FRI}=71.4$ (`WARNING`), so any rule keyed on temperature alone inverts the pair. A binary trigger such as "if $\text{Temp} > 40^\circ\text{C}$ then alarm" consequently fires on benign summer heat and stays silent when moderate conditions are compounded by wind and drought-stressed fuel. Fuzzy set theory answers exactly this: membership functions replace the comparison against a constant, so uncertainty is carried through the inference instead of being collapsed at the input [2].

The work is aligned with two United Nations Sustainable Development Goals [6]:
1. **SDG 13, Climate Action (Target 13.1)**: earlier aerial detection shortens the burn, and with it the greenhouse gas the fire releases.
2. **SDG 15, Life on Land (Target 15.2)**: containment protects forest habitat, endangered wildlife and soil cover, and the patrol decision is auditable by the park authority that has to justify it.

### 1.2 Existing Solutions
Three families of solutions are in operational use, and each leaves a gap this project targets.

**Deterministic fire danger indices.** The McArthur Forest Fire Danger Index fuses temperature, humidity, wind and a drought factor into one continuous score, and its category boundaries still anchor Australian fire-weather warnings [3]. The index is transparent to a duty officer, but it is calibrated to eucalypt fuel and its warning tiers are hard cuts: a score of 49.9 and a score of 50.1 land in different categories although the hazard is indistinguishable. The discontinuity is the problem — near a boundary the reported danger jumps while the forest does not change.

**Learning-based perception.** Multi-sensor UAV payloads now report fire fronts from fused thermal and visual perception [4], and deep models reach a higher performance ceiling than hand-written rules. Their decision surface, however, is a weight matrix that cannot be read back to a fire officer. On a decision that dispatches an aircraft and mobilises a crew, "the network scored this 0.91" is not an explanation that can be defended after the fact.

**Simulation-only studies.** Many fuzzy wildfire controllers are evaluated on synthetic data with no actuation loop, so the reported risk index is never connected to a platform that has to move. NVIDIA Isaac Sim closes that loop with a physically based OpenUSD stage, synthetic sensor publication and Action Graph actuation [5], which makes sense-infer-actuate reproducible and inspectable.

The gap is therefore a controller that keeps the interpretability of a rule base, replaces the threshold of an index with graded membership, and is demonstrated inside a simulation that closes the loop. Mamdani inference supplies the first two properties [1]; Isaac Sim supplies the third.

### 1.3 Objectives and Contributions
1. Formulate a Mamdani fuzzy system with four environmental inputs and three continuous control outputs.
2. Build a procedural OpenUSD forest stage in NVIDIA Isaac Sim with terrain, drought-stressed canopy and dynamic thermal hotspots.
3. Bridge synthetic Isaac Sim sensors to the inference engine so patrol speed and alert tier are dispatched autonomously.
4. Evaluate the controller on a reproducible mission and benchmark its defuzzification choice against two alternatives.

---

## 2. System Design

### 2.1 Architecture
The pipeline is a single loop (Figure 1). Isaac Sim publishes four synthetic sensor scalars, the fuzzy engine defuzzifies three consequents, and the actuation stage writes the result back onto the same stage. The counts in the figure are read from the controller and the stage builder at figure-build time, so they cannot drift from the code.

*(Figure 1 below is generated from the controller and the stage builder, so its counts cannot drift from the code.)*

### 2.2 Input Variables and Membership Functions
Four input universes cover the meteorological range a forest weather station reports. Each is partitioned into four linguistic terms, with trapezoids closing the outer sets so that a reading past the sensor range saturates instead of running off the universe.

| Variable (universe) | Linguistic sets | Membership parameters |
|---|---|---|
| Ambient temperature $T$ ($0$–$50\ ^\circ\text{C}$) | Low, Moderate, High, Extreme | trapmf(0, 0, 15, 22), trimf(18, 26, 34), trimf(30, 38, 44), trapmf(40, 45, 50, 50) |
| Relative humidity $RH$ ($0$–$100\ \%$) | High, Moderate, Low, Very Low | trapmf(70, 85, 100, 100), trimf(40, 60, 75), trimf(20, 35, 50), trapmf(0, 0, 15, 25) |
| Wind speed $W$ ($0$–$100\ \text{km/h}$) | Calm, Moderate, High, Severe | trapmf(0, 0, 10, 20), trimf(15, 30, 45), trimf(40, 60, 75), trapmf(70, 85, 100, 100) |
| Fuel dryness $F$ ($0$–$100\ \%$) | Wet, Moderate, Dry, Critically Dry | trapmf(0, 0, 20, 35), trimf(30, 50, 70), trimf(65, 80, 90), trapmf(85, 95, 100, 100) |

Adjacent terms overlap by $4^\circ\text{C}$ between temperature sets, $5$ percentage points between humidity sets, $5\text{ km/h}$ between wind sets and $5$ points between fuel sets, so a reading near a boundary belongs partially to both terms and its output moves continuously rather than switching. Triangular and trapezoidal membership are the standard forms:

$$\text{trimf}(x; a, b, c) = \max\Big(0,\ \min\big((x - a)/(b - a),\ (c - x)/(c - b)\big)\Big)$$

$$\text{trapmf}(x; a, b, c, d) = \max\Big(0,\ \min\big((x - a)/(b - a),\ 1,\ (d - x)/(d - c)\big)\Big)$$

### 2.3 Output Variables
Three Mamdani consequents are defuzzified. Each rule fires one term in every output universe, so the alert tier is inferred by the rule base rather than thresholded from the risk index.

1. **Fire Risk Index ($\text{FRI} \in [0, 100]$)**: Low trapmf(0, 0, 20, 35), Moderate trimf(25, 45, 65), High trimf(55, 75, 85), Extreme trapmf(80, 90, 100, 100).
2. **UAV patrol urgency ($S \in [0, 100]\ \%$)**: Standard Patrol trapmf(0, 0, 25, 45), Accelerated trimf(40, 60, 80), Emergency Dispatch trapmf(75, 90, 100, 100).
3. **Suppression alert ($A \in [0, 3]$)**: Advisory trapmf(0, 0, 0, 0.6), Watch trimf(0.4, 1.0, 1.6), Warning trimf(1.4, 2.0, 2.6), Evacuate/Suppress trapmf(2.4, 3, 3, 3).

The alert universe is sampled at $\Delta a = 0.25$ so every integer tier and every set shoulder falls on a sample, which keeps each triangular set peaking at exactly $1.0$. The discrete tier reported downstream is $\text{round}(A^*)$ clamped to $[0, 3]$; the continuous $A^*$ is the primary output. Figure 2 plots all seven universes.

*(Figure 2 plots all seven universes; severity reads as luminance, lime for the least hazardous term and black for the most hazardous.)*

### 2.4 Rule Base and Inference
The rule matrix takes its four antecedents from the structure of the McArthur index [3] — temperature, humidity, wind, fuel dryness — and its direction of effect, then assigns linguistic bands by hand. It is not a reimplementation of McArthur: no index value is computed and no coefficient is used. What the rule base encodes is the sign of each dependence; rules that combine drought-stressed fuel with wind dominate the top of the range.

**Table 1: The ten Mamdani rules. Each antecedent is a conjunction of linguistic terms, and every rule fires one term in each of the three output universes.**

| Rule ID | Temperature ($T$) | Humidity ($RH$) | Wind Speed ($W$) | Fuel Dryness ($F$) | Fire Risk | Patrol Urgency | Alert Level |
|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **R1** | any | High | any | Wet | Low | Standard Patrol | Advisory |
| **R2** | Low | Moderate | any | any | Low | Standard Patrol | Advisory |
| **R3** | Moderate | any | any | Moderate | Moderate | Standard Patrol | Watch |
| **R4** | Moderate | any | High | Dry | High | Accelerated | Warning |
| **R5** | High | Low | any | any | High | Accelerated | Warning |
| **R6** | High | any | Severe | any | Extreme | Emergency Dispatch | Evacuate/Suppress |
| **R7** | Extreme | Very Low | any | any | Extreme | Emergency Dispatch | Evacuate/Suppress |
| **R8** | any | any | High | Critically Dry | Extreme | Emergency Dispatch | Evacuate/Suppress |
| **R9** | Extreme | any | any | Critically Dry | Extreme | Emergency Dispatch | Evacuate/Suppress |
| **R10** | any | High | Calm | any | Low | Standard Patrol | Advisory |

`any` means the rule does not constrain that variable. Each row fires all three consequents simultaneously, so the alert column is a fuzzy consequence rather than a label derived from the risk column. Rule firing strength $\alpha_k$ uses the minimum t-norm over the antecedents and the consequents aggregate by maximum:

$$\alpha_k = \min\Big(\mu_{T, k}(T), \mu_{RH, k}(RH), \mu_{W, k}(W), \mu_{F, k}(F)\Big)$$

$$\mu_{\text{agg}}(y) = \max_{k} \Big(\min\big(\alpha_k, \mu_{\text{output}, k}(y)\big)\Big)$$

### 2.5 Defuzzification
Crisp outputs come from the centre of gravity of the aggregated set, computed over a 500-sample universe:

$$y^* = \frac{\sum_i y_i \, \mu_{\text{agg}}(y_i)}{\sum_i \mu_{\text{agg}}(y_i)}$$

Centroid is chosen over bisector and mean-of-maximum for continuity, and Section 3.2 measures that difference on this rule base rather than asserting it.

### 2.6 Isaac Sim Stage and UAV Agent
An OpenUSD scene asset (`assets/wildfire_forest_uav_stage.usda`) carries the mission:
* **Terrain**: $65\text{m} \times 65\text{m}$ ground plane with a mossy forest shader (`UsdPreviewSurface`), sun distant light at $2800\text{ lx}$ and a $450\text{ lx}$ dome fill under RTX real-time ray tracing.
* **Canopy**: {{engine.trees_in_asset}} procedurally distributed trees ({{engine.trees_requested}} requested; the generator drops any trunk within $4.0\text{m}$ of the origin, the landing zone), trunk heights $3.5$–$7.5\text{m}$, two canopy tiers, foliage alternating between healthy green `(0.09, 0.32, 0.12)` and drought-stressed amber `(0.55, 0.44, 0.18)`, each tree marked dry at $p = 0.35$ under a fixed seed.
* **Hotspots**: {{engine.hotspots}} ignition centres — $(14.0, 16.0)\text{m}$ radius $3.5\text{m}$ with emissive flame core, $(-18.0, 10.0)\text{m}$ radius $2.8\text{m}$, $(8.0, -20.0)\text{m}$ radius $2.2\text{m}$.

The agent `/World/UAV_Drone` is a carbon fuselage with four boom arms, a forward sensor pod and four $0.24\text{m}$ propeller discs. It follows a kinematic path baked as `.timeSamples` over frames ${{engine.frame_start}}$–${{engine.frame_end}}$ (${{engine.fps}}\text{ fps}$), cruising at $4.5$–$7.0\text{m}$ over {{engine.uav_keyframes}} keyframes, with yaw $\psi = \arctan2(\Delta y, \Delta x)$ toward the next keyframe and $5.0^\circ$ cruise pitch. The fuzzy telemetry is baked on the same keyframes as custom attributes `fuzzy:temperature`, `fuzzy:fire_risk_index` and `fuzzy:patrol_urgency_speed`, produced by the same `synthesise_sensors()` and controller pair that generates Table 2. A kinematic path was chosen over a rigid-body drop so the evaluation is repeatable; the rotors are static geometry and no blade rate is claimed.

---

## 3. Evaluation

### 3.1 Case Study: Twelve-Waypoint Patrol
A 12-waypoint reconnaissance mission was simulated over the forest stage. At each waypoint `synthesise_sensors()` returns the four readings and the controller consumes them; both Table 2 and the attributes baked into the USD stage call that same function, so the two cannot diverge. Sensor jitter is drawn from `random.Random(seed)` with `seed = 0`, so `run_stage_patrol_simulation(stage, steps=12, seed=0)` reproduces the log exactly.

**Table 2: UAV surveillance mission telemetry and fuzzy ingestion log (seed = 0)**

{{TABLE_MISSION}}

Waypoint 04 carries a higher risk index than waypoint 05 but a lower alert value: the alert consequent is a separate inference, so the two outputs correlate without one being a remapping of the other. Figure 3 replays the mission: the 3D path coloured by risk index, the two atmospheric series, the fuel and wind series, and the two actuation outputs.

*(Figure 3 replays the same seed-0 mission across four panels: the 3D flight path coloured by fire risk index, the two atmospheric series, the fuel and wind series, and the two actuation outputs.)*

### 3.2 Defuzzification Comparison
The fire risk consequent was rebuilt with three defuzzification algorithms through `src/fuzzy_system/defuzz_benchmark.py`, each on the same membership sets and rule base.

**Table 3: Defuzzification algorithm benchmark, fire risk index**

{{TABLE_DEFUZZ}}

The largest centroid-to-MOM divergence is $2.9$ risk points, at the Critical scenario where the aggregated set has two separated peaks; centroid and bisector agree within $0.3$ points everywhere. The methods do not separate on cost — defuzzification over a 500-point universe is a small part of the evaluation loop — they separate on continuity. MOM returns the mean of the aggregated maxima, so as an input crosses a boundary the output jumps between peaks, which on a $250\text{ g}$ airframe is a torque step. Centroid integrates the whole area and is continuous in the input, which is why it is used for the throttle.

### 3.3 Runtime Performance
Measurements were taken on a GeForce RTX 4060 laptop GPU with 16 GB RAM and a 14-core i7-13650HX, through `tools/presentation/measure.py`, which calls `WildfireFuzzyController.compute()` for 20,000 evaluations per scenario after a 2,000-call warm-up. Median loop cost is ${{latency.benign_median_ms}}\ \text{ms}$ for the benign scenario and ${{latency.critical_median_ms}}\ \text{ms}$ for the critical one (p99 ${{latency.benign_p99_ms}}\ \text{ms}$ and ${{latency.critical_p99_ms}}\ \text{ms}$). Both medians sit two orders of magnitude inside a $50\ \text{ms}$ control budget, which leaves room for the sensing and actuation around them. Host-Python timings include interpreter overhead and are an upper bound on a deployed figure. Viewport frame rate is not claimed: the stage was exercised through the headless builder and the bridge mock, neither of which reports rendering throughput.

### 3.4 Discussion
**What the output shows.** The controller does what a threshold cannot: over the seed-0 mission the patrol throttle rises from $20.1\%$ at the benign waypoints to $89.5\%$ at waypoint 03, where the fire risk index reads $91.4$ and the suppression alert $2.826$ of $3$ (`CRITICAL`). The largest throttle change between consecutive waypoints, $69.8$ points, occurs only on the step that leaves the second hotspot radius — the aircraft accelerates into hazard and relaxes on exit, which is the behaviour a patrol policy needs.

**Why an operator can accept it.** Every intermediate quantity is inspectable. `tools/report/rule_trace.py` prints the trace for any input; at waypoint 03 it reads temperature extreme $= 0.560$, humidity very low $= 0.610$, wind high $= 0.260$, fuel critical $= 0.180$, with Rule 7 firing at $0.560$, Rules 8 and 9 at $0.180$ each and the remaining seven at zero. The reported alert is the centroid of exactly those three clipped consequents, so a reviewer can reproduce the arithmetic from the printed trace instead of trusting a weight matrix [1][4].

**Robustness to sensor noise.** Every input universe is fully covered and adjacent sets overlap, so no reading lands where all antecedents are zero and a boundary reading moves the output continuously. The effect is visible in the throttle trace: changes between consecutive waypoints inside a hazard approach are $10.5$ and $19.0$ points, against the $69.8$-point change on exit. A noisy thermometer perturbs the memberships; it does not toggle the tier.

**Impact on the SDGs.** A patrol that accelerates on graded hazard spends airtime where the risk is, which is the mechanism by which SDG 13 (Target 13.1) is served: an earlier report shortens the burn and the associated emissions. Because the rule base is readable, a park authority can adopt the controller without a data-science team, which is what makes the SDG 15 (Target 15.2) protection claim deployable rather than theoretical. Against a deterministic index [3] the gain is at the category boundaries; against a learned model the gain is auditability.

**Limitations.** The trajectory is kinematic; downwash and rotor stall under updrafts would need PhysX fluid coupling. Wind is a scalar field, so the wind antecedent has no vertical component. Rendering throughput is not measured, and the rotor discs are static geometry. Finally, the rule base is expert-authored and validated on a simulated forest, so field calibration against local fuel models remains open.

---

## 4. Conclusion
The project delivered a working Mamdani fuzzy system inside NVIDIA Isaac Sim that turns four environmental scalars into three defuzzified consequents and closes the loop onto an autonomous patrol. On a deterministic 12-waypoint mission the controller moved from $20.1\%$ to $89.5\%$ patrol urgency as the aircraft entered a hotspot, with a suppression alert of $2.826$ of $3$, and it did so with every intermediate quantity exposed for audit. The engine matches a scikit-fuzzy reference to within ${{reference.worst_deviation}}$ across {{reference.scenarios_total}} scenarios, passes {{tests.passed}} unit tests, and costs ${{latency.benign_median_ms}}\ \text{ms}$ per evaluation loop. Compared with a deterministic fire danger index it removes the category cliff; compared with a learned controller it keeps the explanation.

Future work follows the limitations: coupling the trajectory to PhysX for dynamic flight, adding a vertical wind component, calibrating the rule base against a local fuel model, and using the fuzzy index as a dense reward for a reinforcement-learning exploration policy in Isaac Lab, where the learned component would propose waypoints while the rule base keeps veto authority over the alert tier.

---

## References
1. E. H. Mamdani and S. Assilian, "An experiment in linguistic synthesis with a fuzzy logic controller," *International Journal of Man-Machine Studies*, vol. 7, no. 1, pp. 1-13, 1975.
2. L. A. Zadeh, "Fuzzy sets," *Information and Control*, vol. 8, no. 3, pp. 338-353, 1965.
3. A. G. McArthur, "Fire behaviour in eucalypt forests," *Forestry and Timber Bureau Leaflet*, no. 107, 1967.
4. M. Contin, et al., "UAV-based forest fire surveillance using multi-sensor environmental perception," *Sensors*, vol. 22, no. 4, p. 1420, 2022.
5. NVIDIA Corporation, "NVIDIA Isaac Sim: Robotics Simulation and Synthetic Data Generation," *NVIDIA Developer Documentation*, 2026. [Online]. Available: https://docs.isaacsim.omniverse.nvidia.com/
6. United Nations, "The 17 Goals - Sustainable Development Goals," *United Nations Department of Economic and Social Affairs*, 2015. [Online]. Available: https://sdgs.un.org/goals
