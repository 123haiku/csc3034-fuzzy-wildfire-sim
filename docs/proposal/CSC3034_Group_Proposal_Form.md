# CSC3034 Computational Intelligence — Group Project Proposal

**Lecturer**: Dr. Tang Tiong Yew  
**Institution**: Sunway University  
**Submission Deadline**: 15 November 2026, 11:59 PM  
**Group Leader**: Yeoh Choon Hern  
**Project Status**: Approved & Simulation Validated  

---

## 1. Group Details (Max 4 Members)

| No. | Full Name | Student ID | Sunway Email | Role / Responsibility |
|:---:|:---|:---:|:---|:---|
| 1 | **Yeoh Choon Hern** | 23100795 | 23100795@imail.sunway.edu.my | **Project Lead**: Coordination, Integration & Project Management |
| 2 | **Pang Wei Sheng** | 24035115 | 24035115@imail.sunway.edu.my | **Fuzzy Inference Engine & Simulation**: Mamdani Engine, Benchmark Scenarios, Telemetry Evaluation & A1 Poster |
| 3 | **Roshan A/L Sivakumar** | 23028285 | 23028285@imail.sunway.edu.my | Technical Report Writing, Documentation & Defuzzification Analysis |
| 4 | **Dinesswar A/L Sathasivam** | 23096910 | 23096910@imail.sunway.edu.my | NVIDIA Isaac Sim Scene Assets & Synthetic Sensor Bridge |

---

## 2. Project Title & Target SDGs
* **Project Title**: Autonomous Wildfire Risk Assessment and UAV Surveillance Dispatch using Mamdani Fuzzy Logic in NVIDIA Isaac Sim
* **Target Sustainable Development Goals (SDGs)**:
  * **SDG 13: Climate Action** (Target 13.1): Strengthen resilience and adaptive capacity to climate-related hazards and natural disasters by enabling early aerial wildfire detection before catastrophic spread.
  * **SDG 15: Life on Land** (Target 15.2): Halt deforestation, safeguard biodiversity, and preserve terrestrial ecosystems through proactive aerial surveillance and rapid hazard containment.

---

## 3. Problem Statement & Motivation
Wildfires exhibit highly non-linear, stochastic fire-spread dynamics governed by complex micro-climate variables: atmospheric heat, relative humidity, localized wind shear, and fuel moisture content. Conventional binary threshold alarms (e.g., alert if $T > 40^\circ\text{C}$) suffer from:
1. High false-positive rates during benign hot-and-humid days.
2. Dangerous false-negative delays when moderate temperatures are amplified by severe winds and desiccated vegetation.
3. Vulnerability to sensor noise in remote forest environments.

This project implements a **Mamdani Fuzzy Logic Inference System** interfaced with an **NVIDIA Isaac Sim (OpenUSD)** 3D simulation environment. Synthetic sensors on an autonomous surveillance drone continuously ingest environmental parameters, compute a continuous **Fire Risk Index (FRI)**, and dynamically adjust UAV patrol speed and emergency suppression alerts.

---

## 4. Fuzzy Linguistic Variables & Mathematical Formulation

### 4.1 Linguistic Inputs (Universes of Discourse)

1. **Ambient Temperature ($T$)**: Range $[0, 50]^\circ\text{C}$
   * $\text{Low} = \text{trapmf}(0, 0, 15, 25)$
   * $\text{Moderate} = \text{trimf}(20, 28, 35)$
   * $\text{High} = \text{trimf}(30, 38, 44)$
   * $\text{Extreme} = \text{trapmf}(40, 45, 50, 50)$

2. **Relative Humidity ($RH$)**: Range $[0, 100]\%$
   * $\text{High} = \text{trapmf}(60, 75, 100, 100)$
   * $\text{Moderate} = \text{trimf}(35, 50, 65)$
   * $\text{Low} = \text{trimf}(15, 28, 40)$
   * $\text{Very Low} = \text{trapmf}(0, 0, 12, 20)$

3. **Wind Speed ($W$)**: Range $[0, 100]\text{ km/h}$
   * $\text{Calm} = \text{trapmf}(0, 0, 10, 20)$
   * $\text{Moderate} = \text{trimf}(15, 30, 45)$
   * $\text{High} = \text{trimf}(40, 55, 70)$
   * $\text{Severe} = \text{trapmf}(65, 80, 100, 100)$

4. **Vegetation / Fuel Moisture Dryness ($F$)**: Range $[0, 100]\%$
   * $\text{Wet} = \text{trapmf}(0, 0, 20, 35)$
   * $\text{Moderate} = \text{trimf}(30, 45, 60)$
   * $\text{Dry} = \text{trimf}(55, 70, 85)$
   * $\text{Critically Dry} = \text{trapmf}(80, 90, 100, 100)$

### 4.2 Linguistic Outputs

1. **Fire Risk Index (FRI)**: Range $[0, 100]$
   * $\text{Low} = \text{trapmf}(0, 0, 20, 35)$
   * $\text{Moderate} = \text{trimf}(30, 48, 65)$
   * $\text{High} = \text{trimf}(60, 75, 88)$
   * $\text{Extreme} = \text{trapmf}(82, 92, 100, 100)$

2. **UAV Patrol Urgency / Flight Throttle**: Range $[0, 100]\%$
   * $\text{Standard Patrol} = \text{trapmf}(0, 0, 25, 45)$
   * $\text{Accelerated} = \text{trimf}(40, 60, 80)$
   * $\text{Emergency Dispatch} = \text{trapmf}(75, 90, 100, 100)$

3. **Suppression Alert Status (Discrete Levels)**:
   * Level 0: `ADVISORY` ($\text{FRI} < 35$)
   * Level 1: `WATCH` ($35 \le \text{FRI} < 65$)
   * Level 2: `WARNING` ($65 \le \text{FRI} < 85$)
   * Level 3: `CRITICAL DISPATCH` ($\text{FRI} \ge 85$)

---

## 5. Inference Engine & Defuzzification Method
* **Inference Operator**: Mamdani Min-Max (Intersection via $\min$, Union via $\max$).
* **Implication**: Minimum clipping ($\mu_{R}(x) = \min(\alpha_k, \mu_{B}(x))$).
* **Defuzzification Formulation**: Center of Gravity (Centroid / COG):
  $$\text{COG} = \frac{\int x \cdot \mu_{\text{aggregated}}(x) \, dx}{\int \mu_{\text{aggregated}}(x) \, dx}$$
* Comparative analysis benchmarked against **Bisector** and **Mean of Maximum (MOM)** defuzzification strategies.

---

## 6. Software Architecture & Implementation Stack
* **Simulation Engine**: NVIDIA Isaac Sim 6.2.0 (Standalone Workstation Edition)
* **Graphics & Physics**: NVIDIA Omniverse Kit, RTX Real-Time Ray Tracing (DirectX 12 / Vulkan), PhysX 5 SDK
* **Hardware Utilized**: NVIDIA GeForce RTX 4060 Laptop GPU, 13th Gen Intel Core i7-13650HX
* **Scene Description**: OpenUSD (`.usda`) procedural forest stage containing 45+ trees, 3 emissive wildfire ignition hotspots, and kinematic UAV drone prim
* **Programming Environment**: Python 3.12 (integrated into Isaac Sim), NumPy, Scikit-Fuzzy, Matplotlib, Pytest
* **Data Flow**: Drone kinematic flight path $\rightarrow$ Synthetic sensor polling $\rightarrow$ Mamdani fuzzy inference $\rightarrow$ Real-time USD telemetry synchronization (`fuzzy:fire_risk_index`, `fuzzy:patrol_urgency_speed`)

---

## 7. Project Milestones & Validation Status

| Milestone | Target Date | Deliverables | Current Status |
|:---|:---:|:---|:---:|
| **M1: Mathematical Modeling** | 25 Oct 2026 | Membership functions and complete Mamdani rule base | **Completed (100%)** |
| **M2: Controller & Unit Testing** | 29 Oct 2026 | `controller.py`, 8 automated pytest validation test cases | **Completed (100%)** |
| **M3: Isaac Sim USD Stage** | 03 Nov 2026 | Procedural forest terrain, UAV drone model, animated flight path | **Completed (100%)** |
| **M4: Simulation Verification** | 03 Nov 2026 | 12-waypoint autonomous flight simulation, high-res telemetry plots | **Completed (100%)** |
| **M5: Final Report & A1 Poster** | 10 Nov 2026 | 10-page academic report and conference infographic poster | **In Progress** |
| **M6: Project Submission** | 15 Nov 2026 | Final submission on Sunway University portal | Scheduled |
