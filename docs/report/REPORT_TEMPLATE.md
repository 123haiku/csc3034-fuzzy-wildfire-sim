# CSC3034 Computational Intelligence — Project Report Template

> **Formatting Constraints**:  
> * Maximum **10 pages** (excluding title page and references).  
> * Minimum font size: **11 pt**.  
> * Standard margins (1 inch / 2.54 cm).  
> * Required Structure: Introduction, System Design, Evaluation, Conclusion.

---

# Title: Intelligent Forest Fire Risk Assessment and UAV Dispatch Using Mamdani Fuzzy Logic in NVIDIA Isaac Sim

**Authors**: [Author Names & Student IDs]  
**Department**: School of Mathematical Sciences / Computing, Sunway University  
**Supervisor / Lecturer**: Dr. Tang Tiong Yew  

---

## Abstract
Brief summary (150-250 words) detailing the problem, SDG alignment (SDGs 13 and 15), fuzzy inference methodology, Isaac Sim integration, and experimental findings.

---

## 1. Introduction
* **1.1 Background & Problem Motivation**: Wildfire risks, atmospheric non-linearities, and sensor inaccuracies.
* **1.2 Alignment with United Nations Sustainable Development Goals (SDGs)**:
  * SDG 13 (Climate Action)
  * SDG 15 (Life on Land)
* **1.3 Objectives of the Project**:
  * Develop an explainable multi-variable fuzzy logic inference system.
  * Integrate with NVIDIA Isaac Sim to demonstrate autonomous UAV patrol actuation under synthetic atmospheric conditions.

---

## 2. System Design & Methodology
* **2.1 Fuzzy System Architecture**: Overall block diagram (Fuzzification $\rightarrow$ Inference Engine $\rightarrow$ Defuzzification).
* **2.2 Input Variables & Membership Functions**:
  * Temperature ($0 - 50^\circ\text{C}$), Relative Humidity ($0 - 100\%$), Wind Speed ($0 - 100\text{ km/h}$), Vegetation Dryness ($0 - 100\%$).
  * Equations for Trapezoidal and Triangular membership functions.
* **2.3 Fuzzy Rule Base & Inference Mechanism**:
  * Discussion of domain expert rules and Mamdani min-max implication.
  * Full rule table matrix.
* **2.4 Defuzzification**:
  * Center of Gravity (Centroid) formulation:
    $$\text{Centroid} = \frac{\int x \cdot \mu(x) \, dx}{\int \mu(x) \, dx}$$
* **2.5 NVIDIA Isaac Sim Integration**:
  * Scene setup, virtual sensors, action graph, and UAV agent velocity control.

---

## 3. Evaluation & Experimental Results
* **3.1 Test Scenarios & Case Studies**:
  * Scenario A: Low risk post-rain condition.
  * Scenario B: Moderate seasonal heat.
  * Scenario C: Elevated dry-wind hazard.
  * Scenario D: Critical wildfire emergency.
* **3.2 Control Surface Analysis**: 3D surface visualizations showing non-linear response curves.
* **3.3 Simulation Performance in Isaac Sim**: Frame rates, response latency, and patrol adaptation.

---

## 4. Discussion & Limitations
* Robustness to synthetic sensor noise.
* Comparison between Mamdani and Sugeno inference.
* Computational footprint on real-time embedded robotic hardware.

---

## 5. Conclusion & Future Work
* Summary of contributions.
* Potential integration with Isaac Lab reinforcement learning policies.

---

## References
[List IEEE or APA formatted references here]
