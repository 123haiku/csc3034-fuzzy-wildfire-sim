# Intelligent Forest Fire Risk Assessment and UAV Dispatch Using Mamdani Fuzzy Logic in NVIDIA Isaac Sim

**Course**: CSC3034 Computational Intelligence  
**Institution**: School of Mathematical Sciences & Computing, Sunway University  
**Supervisor / Lecturer**: Dr. Tang Tiong Yew  
**Authors**: Pang Wei Sheng (24035115), Roshan A/L Sivakumar (23028285), Dinesswar A/L Sathasivam (23096910), Yeoh Choon Hern (23100795)  
**Submission Date**: November 2026  

---

## Abstract
Wildfires pose catastrophic ecological and atmospheric hazards, threatening terrestrial ecosystems and contributing significantly to global carbon emissions. Real-time fire risk assessment is challenging due to the continuous non-linear interactions among ambient temperature, relative humidity, localized wind velocity, and combustible vegetation fuel moisture. Traditional binary alarm systems exhibit high false-positive rates during benign summer heat and dangerous response latencies when moderate conditions are compounded by high winds and drought-stressed undergrowth. 

This paper proposes an explainable **Mamdani Fuzzy Logic Inference System** coupled with **NVIDIA Isaac Sim (OpenUSD)** for dynamic forest fire risk estimation and autonomous unmanned aerial vehicle (UAV) surveillance response. The fuzzy controller maps four continuous environmental inputs into a normalized **Fire Risk Index (FRI)**, an autonomous **UAV Patrol Urgency Throttle**, and a discrete suppression alert status. A procedural 3D forest simulation stage was created in Isaac Sim containing forest terrain, varied vegetation moisture distributions, thermal wildfire hotspots, and an animated surveillance drone. Through a 12-waypoint simulated flight mission, the system demonstrated smooth, deterministic transitions between benign patrol speeds ($20.0\%$ urgency, $\text{FRI}=45.0$) and rapid emergency response ($89.5\%$ throttle urgency, $\text{FRI}=91.4$) upon entering active thermal hazard zones. The fuzzy inference system was validated through automated unit tests ($100\%$ pass rate) and benchmarked against multiple defuzzification methods, confirming its efficacy for real-time robotic deployment in alignment with **United Nations Sustainable Development Goals 13 (Climate Action)** and **15 (Life on Land)**.

**Keywords**: Computational Intelligence, Mamdani Fuzzy Inference, Wildfire Risk Modeling, Autonomous UAV Surveillance, NVIDIA Isaac Sim, OpenUSD, Sustainable Development Goals.

---

## 1. Introduction

### 1.1 Background & Motivation
Wildfires represent one of the most volatile and destructive natural hazards globally. The acceleration of global climate change has lengthened wildfire seasons and heightened ignition frequencies worldwide. The Canadian, Mediterranean, and Southeast Asian forest fire crises have demonstrated that early detection within the initial 15 to 30 minutes of ignition is critical for containment.

However, environmental data collected in remote forest biomes is inherently noisy, incomplete, and highly non-linear:
* A high ambient temperature ($38^\circ\text{C}$) in a tropical rain forest with $85\%$ relative humidity poses low immediate combustion hazard.
* Conversely, a moderate temperature ($26^\circ\text{C}$) accompanied by $15\%$ relative humidity, severe wind gusts ($65\text{ km/h}$), and desiccated brush represents a critical firestorm risk.

Binary threshold triggers (e.g., if $\text{Temp} > 40^\circ\text{C}$ then sound alarm) fail to capture these interdependent gradients, causing excessive false alarms or missed early-stage hazards. Fuzzy logic provides an ideal mathematical paradigm for this problem by modeling continuous linguistic uncertainty with rigorous, explainable inference.

### 1.2 Alignment with UN Sustainable Development Goals (SDGs)
This research is directly aligned with two United Nations Sustainable Development Goals:
1. **SDG 13: Climate Action (Target 13.1)**: Minimizes massive greenhouse gas emissions produced by uncontrolled wildfires through proactive early aerial detection.
2. **SDG 15: Life on Land (Target 15.2)**: Preserves forest ecosystems, protects endangered wildlife habitats, and combats soil degradation.

### 1.3 Contributions & Objectives
The key objectives of this project are:
1. To formulate a multi-variable Mamdani fuzzy inference system with four environmental inputs and two continuous control outputs.
2. To construct an OpenUSD procedural forest simulation in NVIDIA Isaac Sim equipped with realistic terrain, varied fuel vegetation, and dynamic wildfire hotspots.
3. To establish a real-time software bridge linking Isaac Sim synthetic sensors with the fuzzy inference engine to autonomously throttle drone speed and dispatch early alerts.
4. To evaluate the mathematical stability and defuzzification characteristics of the controller across diverse environmental trajectories.

---

## 2. System Design & Mathematical Formulation

### 2.1 System Architecture
The computational pipeline comprises three interconnected modules:
```
+-----------------------------------------------------------------------------------------+
|                                 NVIDIA Isaac Sim (OpenUSD)                              |
|  - 65m x 65m Forest Terrain Stage with Procedural Tree Clusters                         |
|  - Active Wildfire Ignition Hotspots (Thermal Heat Radiators)                           |
|  - Kinematic Quadcopter UAV Prim (/World/UAV_Drone) with Sensor Attributes              |
+-----------------------------------------------------------------------------------------+
                                           |
                   Synthetic Telemetry Polling (T, RH, W, F)
                                           v
+-----------------------------------------------------------------------------------------+
|                             Mamdani Fuzzy Logic Inference Engine                         |
|  1. Fuzzification: 16 Linguistic Membership Sets (Trapezoidal & Triangular)              |
|  2. Rule Base: Multi-antecedent fuzzy associative matrix with min-max operators          |
|  3. Implication & Aggregation: Minimum clipping and maximum union                        |
|  4. Defuzzification: Center of Gravity (Centroid / COG) calculation                     |
+-----------------------------------------------------------------------------------------+
                                           |
                     Computed FRI & Actuation Throttle Command
                                           v
+-----------------------------------------------------------------------------------------+
|                               Actuation & Telemetry Sync                                |
|  - Dynamic Patrol Speed Throttling (20% -> 90% Flight Urgency)                          |
|  - Stage Attribute Synchronization (fuzzy:fire_risk_index, fuzzy:alert_status)          |
|  - Multi-tier Emergency Dispatch Broadcast ([WATCH], [WARNING], [CRITICAL])             |
+-----------------------------------------------------------------------------------------+
```

### 2.2 Linguistic Input Variables & Membership Functions
The controller incorporates four input variables spanning realistic meteorological boundaries:

#### 1. Ambient Temperature ($T \in [0, 50]^\circ\text{C}$):
* $\text{Low}(T) = \text{trapmf}(T; 0, 0, 15, 25)$
* $\text{Moderate}(T) = \text{trimf}(T; 20, 28, 35)$
* $\text{High}(T) = \text{trimf}(T; 30, 38, 44)$
* $\text{Extreme}(T) = \text{trapmf}(T; 40, 45, 50, 50)$

#### 2. Relative Humidity ($RH \in [0, 100]\%$):
* $\text{High}(RH) = \text{trapmf}(RH; 60, 75, 100, 100)$
* $\text{Moderate}(RH) = \text{trimf}(RH; 35, 50, 65)$
* $\text{Low}(RH) = \text{trimf}(RH; 15, 28, 40)$
* $\text{Very Low}(RH) = \text{trapmf}(RH; 0, 0, 12, 20)$

#### 3. Wind Velocity ($W \in [0, 100]\text{ km/h}$):
* $\text{Calm}(W) = \text{trapmf}(W; 0, 0, 10, 20)$
* $\text{Moderate}(W) = \text{trimf}(W; 15, 30, 45)$
* $\text{High}(W) = \text{trimf}(W; 40, 55, 70)$
* $\text{Severe}(W) = \text{trapmf}(W; 65, 80, 100, 100)$

#### 4. Vegetation / Fuel Moisture Dryness ($F \in [0, 100]\%$):
* $\text{Wet}(F) = \text{trapmf}(F; 0, 0, 20, 35)$
* $\text{Moderate}(F) = \text{trimf}(F; 30, 45, 60)$
* $\text{Dry}(F) = \text{trimf}(F; 55, 70, 85)$
* $\text{Critically Dry}(F) = \text{trapmf}(F; 80, 90, 100, 100)$

The mathematical definitions for triangular $\text{trimf}(x; a, b, c)$ and trapezoidal $\text{trapmf}(x; a, b, c, d)$ functions are defined as:
$$\text{trimf}(x; a, b, c) = \max\left(0, \min\left(\frac{x - a}{b - a}, \frac{c - x}{c - b}\right)\right)$$
$$\text{trapmf}(x; a, b, c, d) = \max\left(0, \min\left(\frac{x - a}{b - a}, 1, \frac{d - x}{d - c}\right)\right)$$

### 2.3 Linguistic Output Variables

1. **Fire Risk Index ($\text{FRI} \in [0, 100]$)**:
   * $\text{Low} = \text{trapmf}(0, 0, 20, 35)$
   * $\text{Moderate} = \text{trimf}(30, 48, 65)$
   * $\text{High} = \text{trimf}(60, 75, 88)$
   * $\text{Extreme} = \text{trapmf}(82, 92, 100, 100)$

2. **UAV Patrol Speed & Urgency ($S \in [0, 100]\%$)**:
   * $\text{Standard Patrol} = \text{trapmf}(0, 0, 25, 45)$
   * $\text{Accelerated} = \text{trimf}(40, 60, 80)$
   * $\text{Emergency Dispatch} = \text{trapmf}(75, 90, 100, 100)$

*(Visual plot of all membership functions is illustrated in `plots/membership_functions.png`).*

### 2.4 Fuzzy Rule Base & Inference Logic
The system implements a domain-expert rule matrix formulated in consultation with standard wildfire behavior models (e.g., McArthur Forest Fire Danger Index). Representative rules include:

| Rule ID | Temperature ($T$) | Humidity ($RH$) | Wind Speed ($W$) | Fuel Dryness ($F$) | Resulting Fire Risk | UAV Patrol Urgency | Status |
|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **R1** | Low | High | Calm | Wet | Low | Standard Patrol | Advisory |
| **R2** | Moderate | Moderate | Moderate | Moderate | Moderate | Standard Patrol | Watch |
| **R3** | Moderate | Low | High | Dry | High | Accelerated | Warning |
| **R4** | High | Low | High | Critically Dry | Extreme | Emergency Dispatch | Critical |
| **R5** | Extreme | Very Low | Severe | Critically Dry | Extreme | Emergency Dispatch | Critical |
| **R6** | Extreme | Moderate | High | Dry | High | Accelerated | Warning |
| **R7** | High | High | Calm | Wet | Moderate | Standard Patrol | Watch |

Under Mamdani inference, rule firing strength $\alpha_k$ for rule $k$ is computed using the t-norm (minimum operator):
$$\alpha_k = \min\Big(\mu_{T, k}(T), \mu_{RH, k}(RH), \mu_{W, k}(W), \mu_{F, k}(F)\Big)$$
The aggregated output fuzzy subset $\mu_{\text{agg}}(y)$ is formed through the s-norm (maximum union):
$$\mu_{\text{agg}}(y) = \max_{k} \Big(\min\big(\alpha_k, \mu_{\text{output}, k}(y)\big)\Big)$$

### 2.5 Defuzzification Formulation
To generate deterministic crisp values for drone velocity actuation and risk indexing, Center of Gravity (Centroid / COG) defuzzification is applied:
$$y^* = \frac{\int_{y_{\min}}^{y_{\max}} y \cdot \mu_{\text{agg}}(y) \, dy}{\int_{y_{\min}}^{y_{\max}} \mu_{\text{agg}}(y) \, dy}$$

---

## 3. NVIDIA Isaac Sim Integration

### 3.1 Scene Architecture & Procedural Stage Design
An OpenUSD scene asset (`assets/wildfire_forest_uav_stage.usda`) was created to simulate an authentic aerial surveillance mission:
* **Terrain Grid**: $65\text{m} \times 65\text{m}$ ground plane rendered with mossy forest ground shader (`UsdPreviewSurface`).
* **Vegetation Canopy**: 48 procedurally distributed pine and deciduous trees with randomized trunk heights ($3.5\text{m} - 7.5\text{m}$) and two canopy tiers. Foliage shaders alternate between healthy green (`diffuseColor = (0.09, 0.32, 0.12)`) and drought-stressed amber (`diffuseColor = (0.55, 0.44, 0.18)`).
* **Thermal Ignition Hotspots**: Three hazard epicenters positioned across the grid:
  * Hotspot 1 (Severe): Position $(14.0\text{m}, 16.0\text{m})$, radius $3.5\text{m}$, emissive flame core.
  * Hotspot 2 (Moderate): Position $(-18.0\text{m}, 10.0\text{m})$, radius $2.8\text{m}$.
  * Hotspot 3 (Emerging): Position $(8.0\text{m}, -20.0\text{m})$, radius $2.2\text{m}$.
* **Lighting Model**: Sun distant light ($2800\text{ lx}$, $32^\circ$ azimuth) paired with ambient dome sky light ($450\text{ lx}$) utilizing RTX real-time ray tracing.

### 3.2 Quadcopter UAV Prim & Dynamic Flight Keyframing
The surveillance agent (`/World/UAV_Drone`) is constructed from carbon composite fuselage, four cross-spar boom arms, forward optical sensor pod, and four rotating propeller discs.

To prevent unconstrained gravitational free-fall while maintaining deterministic flight fidelity, the drone employs a kinematic trajectory with OpenUSD `.timeSamples` spanning frames $0$ to $620$ ($30\text{ fps}$, $20.6\text{s}$ duration):
* **Translational Trajectory**: $14$ keyframe waypoints cruising at $4.5\text{m} - 7.0\text{m}$ altitude.
* **Attitude Banking**: Real-time yaw alignment $\psi = \arctan2(\Delta y, \Delta x)$ with a $5.0^\circ$ forward cruise pitch.
* **Propeller Propulsion**: Continuous rotor rotation keyframed at $24,800^\circ$ ($40\text{ rev/sec}$).

---

## 4. Experimental Results & Performance Evaluation

### 4.1 Autonomous Surveillance Mission Telemetry
A 12-waypoint autonomous reconnaissance mission was simulated over the forest stage. Atmospheric telemetry was polled at each waypoint based on proximity to active hotspots. The complete mission log is summarized in Table 2:

**Table 2: Real-Time UAV Surveillance Mission Telemetry & Fuzzy Ingestion Log**
| Waypoint | Coordinates $(X, Y, Z)$ | Temp ($^\circ\text{C}$) | Humidity ($\%$) | Wind ($\text{km/h}$) | Fuel Dryness ($\%$) | Fire Risk Index (0-100) | Throttle Urgency ($\%$) | Alert Status |
|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **00** | $(0.0, 0.0, 5.0\text{m})$ | $28.8$ | $47.8$ | $23.2$ | $40.2$ | **45.0** | $20.0\%$ | `WATCH` |
| **01** | $(4.0, 5.0, 5.5\text{m})$ | $28.6$ | $46.9$ | $27.5$ | $40.3$ | **45.0** | $20.0\%$ | `WATCH` |
| **02** | $(8.0, 10.0, 6.0\text{m})$ | $34.0$ | $38.6$ | $29.5$ | $55.2$ | **71.0** | $59.9\%$ | `WARNING` |
| **03** | $(13.5, 15.5, 5.0\text{m})$ | $42.4$ | $19.4$ | $44.8$ | $86.8$ | **91.2** | $89.2\%$ | `CRITICAL` |
| **04** | $(15.0, 17.0, 4.5\text{m})$ | $41.7$ | $18.3$ | $44.1$ | $84.5$ | **90.9** | $88.8\%$ | `CRITICAL` |
| **05** | $(10.0, 18.0, 6.5\text{m})$ | $37.8$ | $26.6$ | $40.7$ | $71.3$ | **71.0** | $60.0\%$ | `WARNING` |
| **06** | $(0.0, 15.0, 7.0\text{m})$ | $28.3$ | $47.4$ | $24.3$ | $39.8$ | **45.0** | $20.1\%$ | `WATCH` |
| **07** | $(-10.0, 12.0, 6.0\text{m})$ | $33.2$ | $38.5$ | $31.7$ | $54.8$ | **63.7** | $50.3\%$ | `WARNING` |
| **08** | $(-17.5, 9.8, 4.5\text{m})$ | $44.5$ | $17.9$ | $47.3$ | $87.3$ | **91.7** | $90.0\%$ | `CRITICAL` |
| **09** | $(-10.0, 0.0, 6.0\text{m})$ | $28.3$ | $46.9$ | $26.5$ | $41.8$ | **45.0** | $19.6\%$ | `WATCH` |
| **10** | $(0.0, -10.0, 6.5\text{m})$ | $28.2$ | $48.5$ | $25.5$ | $39.6$ | **45.0** | $20.1\%$ | `WATCH` |
| **11** | $(7.8, -19.5, 5.0\text{m})$ | $43.0$ | $17.6$ | $47.7$ | $88.9$ | **91.5** | $89.6\%$ | `CRITICAL` |

*(The complete 4-panel multi-variable mission telemetry visualization is presented in `plots/mission_telemetry_dashboard.png`).*

### 4.2 Defuzzification Method Comparison
To assess output sensitivity, the controller was benchmarked using three defuzzification algorithms across benign vs. critical conditions:

**Table 3: Defuzzification Algorithm Benchmark**
| Environmental Scenario | Centroid (COG) FRI | Bisector FRI | Mean of Maximum (MOM) FRI | Computational Time ($\mu\text{s}$) | Actuation Smoothness |
|:---|:---:|:---:|:---:|:---:|:---|
| **Benign Clear Day** ($T=22, RH=65, W=12, F=25$) | $20.8$ | $21.0$ | $12.5$ | $142\ \mu\text{s}$ | Highly Smooth |
| **Dry Spring Heat** ($T=32, RH=40, W=30, F=55$) | $52.4$ | $53.0$ | $48.0$ | $148\ \mu\text{s}$ | Smooth |
| **High Hazard Drought** ($T=39, RH=22, W=55, F=82$) | $81.6$ | $82.5$ | $88.0$ | $151\ \mu\text{s}$ | Moderate |
| **Critical Wildfire** ($T=46, RH=12, W=85, F=95$) | $92.3$ | $92.8$ | $96.0$ | $145\ \mu\text{s}$ | Smooth Step Transition |

* **Analysis**: While MOM executes slightly faster, it produces piecewise step discontinuities detrimental to physical drone motor controllers. **Centroid (COG)** provides the smoothest motor throttle curves without mechanical vibration.

### 4.3 Simulation Runtime & Engine Performance
* **Hardware Platform**: NVIDIA GeForce RTX 4060 Laptop GPU, 16 GB RAM, 14-core Intel Core i7-13650HX.
* **Rendering Framerate**: $67.3\text{ fps} - 72.1\text{ fps}$ at $1280 \times 720$ resolution under RTX Real-Time 2.0 lighting.
* **Fuzzy Inference Latency**: $0.15\text{ ms}$ per evaluation loop. This latency is well within standard robotic control frequencies ($50\text{ Hz} - 200\text{ Hz}$), confirming the system's viability for edge deployment on embedded microcomputers (e.g., NVIDIA Jetson Orin Nano).

---

## 5. Discussion & Limitations

### 5.1 Explainability vs. Black-Box Neural Networks
Unlike deep learning perception models whose decision weights cannot be formally verified, Mamdani fuzzy systems offer complete transparency. Every drone speed acceleration or suppression alert can be traced directly to specific linguistic rules (e.g., Rule 5: Extreme Heat + Severe Wind + Low Humidity $\rightarrow$ Critical Fire Risk). This explainability is essential for safety-critical aerospace and municipal fire response deployments.

### 5.2 Sensor Noise Resilience
Physical sensors in forest conditions suffer from thermal drift and anemometer turbulence. The overlapping boundaries of triangular and trapezoidal fuzzy sets prevent rapid chatter at transition thresholds, ensuring stable flight control without oscillatory motor wear.

### 5.3 Limitations
1. **Kinematic vs. Dynamic Flight Dynamics**: In this phase, the drone trajectory is kinematic. Full aerodynamic downwash and rotor blade stall under intense updrafts require coupling with Isaac Sim's advanced PhysX fluid dynamics extensions.
2. **2D Surface Weather Synthesis**: Wind velocity was modeled as a scalar field; complex 3D atmospheric thermal updrafts will be integrated in future phases.

---

## 6. Conclusion & Future Work
This project successfully designed, implemented, and validated an autonomous wildfire risk assessment and UAV surveillance system utilizing Mamdani fuzzy inference integrated with NVIDIA Isaac Sim. The system continuously maps environmental telemetry into risk indices and throttle urgency commands, successfully detecting and responding to simulated forest wildfire hotspots in real-time.

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
