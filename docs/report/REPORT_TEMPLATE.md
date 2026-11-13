# Intelligent Forest Fire Risk Assessment and UAV Dispatch Using Mamdani Fuzzy Logic in NVIDIA Isaac Sim

**Course**: CSC3034 Computational Intelligence  
**Institution**: School of Mathematical Sciences & Computing, Sunway University  
**Supervisor / Lecturer**: Dr. Tang Tiong Yew  
**Authors**: Pang Wei Sheng (24035115), Roshan A/L Sivakumar (23028285), Dinesswar A/L Sathasivam (23096910), Yeoh Choon Hern (23100795)  
**Submission Date**: November 2026  

---

## Abstract
Wildfires pose catastrophic ecological and atmospheric hazards, destroying terrestrial ecosystems and releasing stored carbon back into the atmosphere. Real-time fire risk assessment is difficult because the four variables that govern ignition — ambient temperature, relative humidity, localized wind velocity and fuel moisture — interact non-linearly, and no single one of them ranks two conditions correctly. Traditional binary alarm systems therefore fire on benign summer heat and stay silent when moderate conditions are compounded by high winds and drought-stressed undergrowth. 

This paper proposes an explainable **Mamdani Fuzzy Logic Inference System** coupled with **NVIDIA Isaac Sim (OpenUSD)** for dynamic forest fire risk estimation and autonomous unmanned aerial vehicle (UAV) surveillance response. The fuzzy controller maps four continuous environmental inputs into three defuzzified consequents: a normalized **Fire Risk Index (FRI)**, an autonomous **UAV Patrol Urgency Throttle**, and a continuous **Suppression Alert Level** on $[0, 3]$ whose tiers (Advisory, Watch, Warning, Evacuate/Suppress) are inferred by the rule base rather than thresholded from the risk index. A procedural 3D forest simulation stage was created in Isaac Sim containing forest terrain, varied vegetation moisture distributions, thermal wildfire hotspots, and an animated surveillance drone. Through a 12-waypoint simulated flight mission (seed $0$, so the log is reproducible), the controller moved from benign patrol ($20.1\%$ urgency, $\text{FRI}=45.0$, alert $1.000$) to emergency dispatch ($89.5\%$ urgency, $\text{FRI}=91.4$, alert $2.826$) within two waypoints of entering a hotspot radius; the largest throttle change between consecutive waypoints, $69.8$ points, occurs only on the step that leaves the second hazard radius. The inference engine was validated in two ways: {{tests.passed}} automated unit tests covering the scenario envelope, input boundaries and all three consequents, plus a per-scenario cross-check against the scikit-fuzzy reference implementation (worst deviation ${{reference.worst_deviation}}$ across {{reference.scenarios_total}} scenarios). The three defuzzification algorithms were also benchmarked, confirming **Centroid of Area** as the choice where output continuity matters. The system is presented in alignment with **United Nations Sustainable Development Goals 13 (Climate Action)** and **15 (Life on Land)**.

**Keywords**: Computational Intelligence, Mamdani Fuzzy Inference, Wildfire Risk Modeling, Autonomous UAV Surveillance, NVIDIA Isaac Sim, OpenUSD, Sustainable Development Goals.
---

## 1. Introduction

### 1.1 Background & Motivation
Wildfires represent one of the most volatile and destructive natural hazards globally, and longer fire seasons have raised ignition frequency. Detection latency dominates containment cost: the earlier a hotspot is reported, the smaller — and cheaper — the response it needs. The design target adopted here is therefore a continuous risk estimate that updates at patrol cadence, rather than a single threshold that fires once.

However, remote forest telemetry arrives as four scalars whose effect on ignition is not additive, and no single threshold ranks them correctly:
* A high ambient temperature ($38^\circ\text{C}$) in a tropical rain forest with $85\%$ relative humidity poses low immediate combustion hazard.
* Conversely, a moderate temperature ($26^\circ\text{C}$) accompanied by $15\%$ relative humidity, severe wind gusts ($65\text{ km/h}$), and desiccated brush represents a critical firestorm risk.

The two readings differ by $12^\circ\text{C}$, yet the cooler one is the dangerous one: run through the controller below, the $38^\circ\text{C}$ / $85\%$ case scores $\text{FRI}=14.0$ (tier `NORMAL`) and the $26^\circ\text{C}$ / $15\%$ / $65\text{ km/h}$ case scores $\text{FRI}=71.4$ (tier `WARNING`), so any rule keyed on a single temperature threshold inverts the pair. The simulator reproduces this by construction: baseline conditions of $28^\circ\text{C}$, $48\%$ RH, $25\text{ km/h}$ and $40\%$ fuel dryness are displaced by hotspot proximity, adding up to $16^\circ\text{C}$, removing up to $32$ percentage points of humidity, adding $20\text{ km/h}$ of wind and $50$ points of fuel dryness inside a $12\text{ m}$ radius, with per-waypoint sensor jitter of $\pm1.0$ to $1.5^\circ\text{C}$, $\pm2\%$ RH, $\pm3$ to $4\text{ km/h}$ and $\pm1$ to $2$ points.

Binary threshold triggers (e.g., if $\text{Temp} > 40^\circ\text{C}$ then sound alarm) fail to capture these interdependent gradients, causing excessive false alarms or missed early-stage hazards. Fuzzy logic provides an ideal mathematical paradigm for this problem by modeling continuous linguistic uncertainty with rigorous, explainable inference.

### 1.2 Alignment with UN Sustainable Development Goals (SDGs)
This research is directly aligned with two United Nations Sustainable Development Goals:
1. **SDG 13: Climate Action (Target 13.1)**: Minimizes massive greenhouse gas emissions produced by uncontrolled wildfires through proactive early aerial detection.
2. **SDG 15: Life on Land (Target 15.2)**: Preserves forest ecosystems, protects endangered wildlife habitats, and combats soil degradation.

### 1.3 Contributions & Objectives
The key objectives of this project are:
1. To formulate a multi-variable Mamdani fuzzy inference system with four environmental inputs and three continuous control outputs.
2. To construct an OpenUSD procedural forest simulation in NVIDIA Isaac Sim equipped with realistic terrain, varied fuel vegetation, and dynamic wildfire hotspots.
3. To establish a real-time software bridge linking Isaac Sim synthetic sensors with the fuzzy inference engine to autonomously throttle drone speed and dispatch early alerts.
4. To evaluate the mathematical stability and defuzzification characteristics of the controller across diverse environmental trajectories.

---

## 2. System Design & Mathematical Formulation

### 2.1 System Architecture
The pipeline is a single loop. Isaac Sim publishes four synthetic sensor scalars, the fuzzy engine defuzzifies three consequents, and the actuation stage writes the result back onto the same stage. Figure 1 shows the three modules and the payload that crosses each boundary; the counts in it are read from the controller and the stage builder at figure-build time, not typed in by hand.

*(Figure 1 below is generated from the controller and the stage builder, so its counts cannot drift from the code.)*

### 2.2 Linguistic Input Variables & Membership Functions
The controller incorporates four input variables spanning realistic meteorological boundaries:

#### 1. Ambient Temperature ($T \in [0, 50]^\circ\text{C}$):
* $\text{Low}(T) = \text{trapmf}(T; 0, 0, 15, 22)$
* $\text{Moderate}(T) = \text{trimf}(T; 18, 26, 34)$
* $\text{High}(T) = \text{trimf}(T; 30, 38, 44)$
* $\text{Extreme}(T) = \text{trapmf}(T; 40, 45, 50, 50)$

#### 2. Relative Humidity ($RH \in [0, 100]\%$):
* $\text{Very Low}(RH) = \text{trapmf}(RH; 0, 0, 15, 25)$
* $\text{Low}(RH) = \text{trimf}(RH; 20, 35, 50)$
* $\text{Moderate}(RH) = \text{trimf}(RH; 40, 60, 75)$
* $\text{High}(RH) = \text{trapmf}(RH; 70, 85, 100, 100)$

#### 3. Wind Velocity ($W \in [0, 100]\text{ km/h}$):
* $\text{Calm}(W) = \text{trapmf}(W; 0, 0, 10, 20)$
* $\text{Moderate}(W) = \text{trimf}(W; 15, 30, 45)$
* $\text{High}(W) = \text{trimf}(W; 40, 60, 75)$
* $\text{Severe}(W) = \text{trapmf}(W; 70, 85, 100, 100)$

#### 4. Vegetation / Fuel Moisture Dryness ($F \in [0, 100]\%$):
* $\text{Wet}(F) = \text{trapmf}(F; 0, 0, 20, 35)$
* $\text{Moderate}(F) = \text{trimf}(F; 30, 50, 70)$
* $\text{Dry}(F) = \text{trimf}(F; 65, 80, 90)$
* $\text{Critically Dry}(F) = \text{trapmf}(F; 85, 95, 100, 100)$

The mathematical definitions for triangular $\text{trimf}(x; a, b, c)$ and trapezoidal $\text{trapmf}(x; a, b, c, d)$ functions are defined as:

$$\text{trimf}(x; a, b, c) = \max\Big(0,\ \min\big((x - a)/(b - a),\ (c - x)/(c - b)\big)\Big)$$

$$\text{trapmf}(x; a, b, c, d) = \max\Big(0,\ \min\big((x - a)/(b - a),\ 1,\ (d - x)/(d - c)\big)\Big)$$

### 2.3 Linguistic Output Variables

Three Mamdani consequents are defuzzified. Each rule fires one term in every output
universe, so the alert level is inferred by the rule base rather than thresholded from
the fire risk index.

1. **Fire Risk Index ($\text{FRI} \in [0, 100]$)**:
   * $\text{Low} = \text{trapmf}(0, 0, 20, 35)$
   * $\text{Moderate} = \text{trimf}(25, 45, 65)$
   * $\text{High} = \text{trimf}(55, 75, 85)$
   * $\text{Extreme} = \text{trapmf}(80, 90, 100, 100)$

2. **UAV Patrol Speed & Urgency ($S \in [0, 100]\%$)**:
   * $\text{Standard Patrol} = \text{trapmf}(0, 0, 25, 45)$
   * $\text{Accelerated} = \text{trimf}(40, 60, 80)$
   * $\text{Emergency Dispatch} = \text{trapmf}(75, 90, 100, 100)$

3. **Suppression Alert Level ($A \in [0, 3]$)**:
   * $\text{Advisory} = \text{trapmf}(0, 0, 0, 0.6)$
   * $\text{Watch} = \text{trimf}(0.4, 1.0, 1.6)$
   * $\text{Warning} = \text{trimf}(1.4, 2.0, 2.6)$
   * $\text{Evacuate/Suppress} = \text{trapmf}(2.4, 3, 3, 3)$

The alert universe is sampled at $\Delta a = 0.25$ so every integer tier and every set
shoulder ($0.4$, $1.6$, $1.4$, $2.6$) falls on a sample, which keeps each triangular set
peaking at exactly $1.0$. The discrete alert tier reported downstream is
$\text{round}(A^*)$ clamped to $[0, 3]$; the continuous $A^*$ is the primary output.

*(Figure 2 plots all seven variables; Figure 3 isolates the three output universes so the alert consequent can be read on its own.)*

### 2.4 Fuzzy Rule Base & Inference Logic
The rule matrix takes its four antecedents from the structure of the McArthur Forest Fire Danger Index [3] (temperature, relative humidity, wind, fuel dryness) and its direction of effect, then assigns the linguistic bands by hand. It is not a reimplementation of McArthur: no index value is computed and no McArthur coefficient is used. What the rule base encodes is the sign of each dependence — higher temperature, lower humidity, higher wind and drier fuel each push the consequents up, and the rules that combine drought-stressed fuel with wind dominate the top of the range. Representative rules include:

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

`any` means the rule does not constrain that variable. Each row fires all three
consequents simultaneously; the alert column is a fuzzy consequence, not a label
derived from the risk column.

Under Mamdani inference, rule firing strength $\alpha_k$ for rule $k$ is computed using the t-norm (minimum operator):
$$\alpha_k = \min\Big(\mu_{T, k}(T), \mu_{RH, k}(RH), \mu_{W, k}(W), \mu_{F, k}(F)\Big)$$
The aggregated output fuzzy subset $\mu_{\text{agg}}(y)$ is formed through the s-norm (maximum union):
$$\mu_{\text{agg}}(y) = \max_{k} \Big(\min\big(\alpha_k, \mu_{\text{output}, k}(y)\big)\Big)$$

### 2.5 Defuzzification Formulation
To generate deterministic crisp values for the three consequents, Center of Gravity (Centroid / COG) defuzzification is applied:

$$y^* = \frac{\int y \cdot \mu_{\text{agg}}(y)\, dy}{\int \mu_{\text{agg}}(y)\, dy}$$

---

## 3. NVIDIA Isaac Sim Integration

### 3.1 Scene Architecture & Procedural Stage Design
An OpenUSD scene asset (`assets/wildfire_forest_uav_stage.usda`) was created to carry the surveillance mission:
* **Terrain Grid**: $65\text{m} \times 65\text{m}$ ground plane rendered with a mossy forest ground shader (`UsdPreviewSurface`).
* **Vegetation Canopy**: {{engine.trees_in_asset}} procedurally distributed trees ({{engine.trees_requested}} were requested; the generator drops any trunk that would land within $4.0\text{m}$ of the origin, which is the UAV landing zone) with trunk heights sampled from $3.5\text{m}$ to $7.5\text{m}$ and two canopy tiers. Foliage shaders alternate between healthy green (`diffuseColor = (0.09, 0.32, 0.12)`) and drought-stressed amber (`diffuseColor = (0.55, 0.44, 0.18)`), with each tree independently marked dry at $p = 0.35$ under the generator's fixed seed.
* **Thermal Ignition Hotspots**: {{engine.hotspots}} hazard epicenters positioned across the grid:
  * Hotspot 1 (Severe): Position $(14.0\text{m}, 16.0\text{m})$, radius $3.5\text{m}$, emissive flame core.
  * Hotspot 2 (Moderate): Position $(-18.0\text{m}, 10.0\text{m})$, radius $2.8\text{m}$.
  * Hotspot 3 (Emerging): Position $(8.0\text{m}, -20.0\text{m})$, radius $2.2\text{m}$.
* **Lighting Model**: Sun distant light ($2800\text{ lx}$, $32^\circ$ azimuth) paired with ambient dome sky light ($450\text{ lx}$) under RTX real-time ray tracing.

### 3.2 Quadcopter UAV Prim & Dynamic Flight Keyframing
The surveillance agent (`/World/UAV_Drone`) is built from a carbon composite fuselage, four cross-spar boom arms, a forward optical sensor pod, and four $0.24\text{m}$ propeller discs.

To keep the trajectory deterministic instead of letting a rigid body fall under gravity, the drone follows a kinematic path baked as OpenUSD `.timeSamples` over frames ${{engine.frame_start}}$ to ${{engine.frame_end}}$ (${{engine.fps}}\text{ fps}$, ${{engine.clip_seconds}}\text{s}$):
* **Translational Trajectory**: {{engine.uav_keyframes}} keyframe waypoints cruising at $4.5\text{m}$ to $7.0\text{m}$ altitude.
* **Attitude Banking**: yaw alignment $\psi = \arctan2(\Delta y, \Delta x)$ toward the next keyframe, with a $5.0^\circ$ forward cruise pitch.
* **Sensor Keyframing**: the fuzzy telemetry is baked on the same keyframes as the trajectory, as custom attributes `fuzzy:temperature`, `fuzzy:fire_risk_index` and `fuzzy:patrol_urgency_speed`, each produced by the same `synthesise_sensors()` + controller pair that generates Table 2.

The rotor discs are static geometry in this phase: the stage model does not animate blade rotation, so no blade rate is claimed here.

---

## 4. Experimental Results & Performance Evaluation

### 4.1 Autonomous Surveillance Mission Telemetry
A 12-waypoint reconnaissance mission was simulated over the forest stage. At each waypoint `synthesise_sensors()` returns the four readings, and the controller consumes them; both the mission log below and the telemetry attributes baked into the USD stage call that same function, so the two cannot diverge. The mission log is a deterministic artefact: the sensor jitter is drawn from `random.Random(seed)` with `seed = 0`, so re-running `run_stage_patrol_simulation(stage, steps=12, seed=0)` reproduces Table 2 exactly.

**Table 2: Real-Time UAV Surveillance Mission Telemetry & Fuzzy Ingestion Log (seed = 0)**

{{TABLE_MISSION}}

Note that waypoint 04 carries a higher risk index than waypoint 05 but a lower alert
value: the alert consequent is a separate inference, so the two outputs are correlated
but not a remapping of one another.

*(Figure 4 replays the same seed-$0$ mission across four panels: the 3D flight path coloured by fire risk index, the two atmospheric series, the fuel and wind series, and the two actuation outputs.)*

### 4.2 Defuzzification Method Comparison
To assess output sensitivity, the fire risk consequent was rebuilt with three
defuzzification algorithms through `src/fuzzy_system/defuzz_benchmark.py`, which runs
each method on the same membership sets and rule base:

**Table 3: Defuzzification Algorithm Benchmark, Fire Risk Index**

{{TABLE_DEFUZZ}}

Largest centroid-to-MOM divergence is $2.9$ risk points, at the Critical scenario where
the aggregated set has two separated peaks. Centroid and bisector agree to within $0.3$
points on every scenario.

* **Analysis**: the three methods do not separate on cost, because defuzzification over
  a 500-point universe is a small part of the evaluation loop. They separate on
  continuity. MOM returns the mean of the aggregated set's maxima, so as the input
  crosses a boundary the output jumps between peaks — a torque step on a 250 g
  airframe. Centroid integrates the whole area, so its output is continuous in the
  input; the observed effect is the 2.9-point centroid-to-MOM gap at the Critical
  scenario in Table 3.

### 4.3 Simulation Runtime & Engine Performance
* **Hardware Platform**: NVIDIA GeForce RTX 4060 Laptop GPU, 16 GB RAM, 14-core Intel Core i7-13650HX.
* **Fuzzy Inference Latency**: measured with `tools/presentation/measure.py`, which
  calls `WildfireFuzzyController.compute()` over 20,000 calls per scenario after a
  2,000-call warm-up: median ${{latency.benign_median_ms}}\ \text{ms}$ for the benign scenario
  and ${{latency.critical_median_ms}}\ \text{ms}$ for the critical scenario (p99
  ${{latency.benign_p99_ms}}\ \text{ms}$ and ${{latency.critical_p99_ms}}\ \text{ms}$
  respectively). Both medians sit inside a $50\text{ ms}$ control budget with two orders of
  magnitude of headroom, which supports edge deployment on embedded microcomputers
  (e.g., NVIDIA Jetson Orin Nano). Host-Python timings include interpreter overhead and
  are an upper bound on the deployed figure. Every figure in this section is regenerated
  by `tools/presentation/measure.py` into `docs/measurements.json`, which the report, the
  poster and the deck all read, so a re-measurement on another machine propagates to all
  three instead of leaving them inconsistent.
* **Not measured in this phase**: viewport frame rate. The simulation was exercised
  through the headless stage builder and the bridge mock, neither of which reports
  rendering throughput, so no frame-rate figure is claimed here.

---

## 5. Discussion & Limitations

### 5.1 Explainability vs. Black-Box Neural Networks
Unlike deep learning perception models whose decision weights cannot be formally verified, Mamdani fuzzy systems expose every intermediate quantity: the membership degree of each input, the firing strength of each rule, and the contribution of each rule to the aggregated set. `tools/report/rule_trace.py` prints that trace for any input, which makes the audit mechanical rather than interpretive. At waypoint 03 of Table 2 the trace reads: temperature extreme $= 0.560$, humidity very low $= 0.610$, wind high $= 0.260$, fuel critical $= 0.180$; Rule 7 (extreme temperature with very low humidity) fires at $0.560$, Rules 8 and 9 at $0.180$ each, and the remaining seven rules at zero. The reported alert of $2.826$ is the centroid of exactly those three clipped consequents. A reviewer can reproduce that arithmetic from the printed trace, which is what a duty officer needs in order to accept an alert.

### 5.2 Sensor Noise Resilience
Physical sensors in forest conditions suffer from thermal drift and anemometer turbulence. Two properties of the rule base limit the effect of that drift. First, every input universe is fully covered: the four temperature sets span $[0, 50]^\circ\text{C}$ without a gap, and the same holds for humidity, wind and fuel dryness, so no reading can land where every antecedent is zero. Second, adjacent sets overlap, by $4^\circ\text{C}$ between the temperature sets, $5$ percentage points between the humidity sets, $5\text{ km/h}$ between the wind sets and $5$ points between the fuel sets, so a reading near a boundary is partially in both sets and its output moves continuously rather than switching. Centroid defuzzification then integrates the interpolated area, which is what keeps the throttle trace in Table 2 free of single-waypoint reversals: the changes between consecutive waypoints inside a hazard approach are $10.5$ and $19.0$ points, while the largest change, $69.8$ points, occurs only on the step where the UAV leaves the second hotspot radius.

### 5.3 Limitations
1. **Kinematic vs. Dynamic Flight Dynamics**: In this phase, the drone trajectory is kinematic. Aerodynamic downwash and rotor blade stall under intense updrafts require coupling with PhysX fluid dynamics extensions, which were not enabled.
2. **2D Surface Weather Synthesis**: Wind velocity was modelled as a scalar field. Three-dimensional atmospheric thermal updrafts were not modelled, so the wind antecedent sees no vertical component.
3. **No Rendering Throughput Figure**: Rendering was exercised through the stage generator and the bridge mock, neither of which reports frame rate, so the report quotes inference latency only and makes no claim about viewport frame rate or render quality under load.
4. **Static Rotors**: The four propeller discs are geometry only. Blade rotation is not animated and no blade rate is claimed.

---

## 6. Conclusion & Future Work
This project designed, implemented and validated an autonomous wildfire risk assessment and UAV surveillance loop built on Mamdani fuzzy inference inside NVIDIA Isaac Sim. The controller maps four environmental scalars into three defuzzified consequents and, over the 12-waypoint seed-$0$ mission of Table 2, drives the patrol throttle from $20.1\%$ at the benign waypoints to $89.5\%$ at waypoint 03, where the fire risk index reaches $91.4$ and the suppression alert reaches $2.826$ (tier `CRITICAL`). Each evaluation loop costs ${{latency.benign_median_ms}}\ \text{ms}$ (benign) and ${{latency.critical_median_ms}}\ \text{ms}$ (critical) on the build machine, which is two orders of magnitude inside a $50\ \text{ms}$ control budget. The engine agrees with a scikit-fuzzy reference implementation to within ${{reference.worst_deviation}}$ across {{reference.scenarios_total}} scenarios, and {{tests.passed}} unit tests pass.

### Future Enhancements:
1. **Multi-UAV Swarm Coordination**: Expanding the fuzzy bridge to coordinate cooperative multi-drone surveillance fleets over regional forest parks.
2. **Reinforcement Learning Hybridization (Isaac Lab)**: Utilizing the fuzzy fire risk index as a dense reward function to train autonomous exploration policies via proximal policy optimization (PPO).

---

## References
1. E. H. Mamdani and S. Assilian, "An experiment in linguistic synthesis with a fuzzy logic controller," *International Journal of Man-Machine Studies*, vol. 7, no. 1, pp. 1-13, 1975.
2. L. A. Zadeh, "Fuzzy sets," *Information and Control*, vol. 8, no. 3, pp. 338-353, 1965.
3. A. G. McArthur, "Fire behaviour in eucalypt forests," *Forestry and Timber Bureau Leaflet*, no. 107, 1967.
4. M. Contin, et al., "UAV-based forest fire surveillance using multi-sensor environmental perception," *Sensors*, vol. 22, no. 4, p. 1420, 2022.
5. NVIDIA Corporation, "NVIDIA Isaac Sim: Robotics Simulation and Synthetic Data Generation," *NVIDIA Developer Documentation*, 2026. [Online]. Available: https://docs.isaacsim.omniverse.nvidia.com/
6. United Nations, "The 17 Goals - Sustainable Development Goals," *United Nations Department of Economic and Social Affairs*, 2015. [Online]. Available: https://sdgs.un.org/goals
