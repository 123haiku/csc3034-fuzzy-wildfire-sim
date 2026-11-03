# CSC3034 Computational Intelligence — Group Project Proposal

**Lecturer**: Dr. Tang Tiong Yew  
**Institution**: Sunway University  
**Submission Deadline**: 15 November 2026, 11:59 PM  

---

## 1. Group Details (Max 4 Members)

| No. | Full Name | Student ID | Sunway Email | Role / Responsibility |
|:---:|:---|:---:|:---|:---|
| 1 | Pang Wei Sheng | 24035115 | 24035115@imail.sunway.edu.my | Fuzzy Inference Engine & Mathematical Formulation |
| 2 | Roshan A/L Sivakumar | 23028285 | 23028285@imail.sunway.edu.my | Report Writing, Documentation & Defuzzification Analysis |
| 3 | Dinesswar A/ L sathasivam | 23096910 | 23096910@imail.sunway.edu.my | NVIDIA Isaac Sim Scene & Synthetic Sensor Bridge |
| 4 | Yeoh Choon Hern | 23100795 | 23100795@imail.sunway.edu.my | Simulation Evaluation, Benchmark Scenarios & Poster |

---

## 2. Project Title & Target SDGs
* **Project Title**: Autonomous Wildfire Risk Assessment and UAV Surveillance Dispatch using Fuzzy Logic in NVIDIA Isaac Sim
* **Target Sustainable Development Goals (SDGs)**:
  * **SDG 13: Climate Action** — Target 13.1 (Strengthen resilience and adaptive capacity to climate-related hazards and natural disasters).
  * **SDG 15: Life on Land** — Target 15.2 (Halt deforestation, restore degraded forests, and substantially increase afforestation and reforestation).

---

## 3. System Purpose & Problem Statement
Wildfires inflict catastrophic environmental destruction and carbon emissions. Rapid fire spread is driven by dynamic atmospheric interactions (temperature, moisture, wind velocity) with substantial uncertainty and sensor noise. 

This project develops a Mamdani fuzzy logic controller interfaced with NVIDIA Isaac Sim. The system ingests synthetic sensor readings from simulated forest environments to continuously compute a Fire Risk Index (FRI) and dynamically adjust autonomous UAV patrol speed and early suppression dispatch alerts.

---

## 4. Input & Output Variables

### Linguistic Inputs (Universes of Discourse):
1. **Ambient Temperature ($T$)**: Range $[0, 50]^\circ\text{C}$
   * Fuzzy Sets: `Low`, `Moderate`, `High`, `Extreme`
2. **Relative Humidity ($RH$)**: Range $[0, 100]\%$
   * Fuzzy Sets: `High`, `Moderate`, `Low`, `Very Low`
3. **Wind Velocity ($W$)**: Range $[0, 100]\text{ km/h}$
   * Fuzzy Sets: `Calm`, `Moderate`, `High`, `Severe`
4. **Vegetation / Fuel Moisture Dryness ($F$)**: Range $[0, 100]\%$
   * Fuzzy Sets: `Wet`, `Moderate`, `Dry`, `Critically Dry`

### Linguistic Outputs:
1. **Fire Risk Index (FRI)**: Range $[0, 100]$
   * Fuzzy Sets: `Low`, `Moderate`, `High`, `Extreme`
2. **UAV Patrol Speed & Dispatch Urgency**: Range $[0, 100]\%$
   * Fuzzy Sets: `Standard Patrol`, `Accelerated`, `Emergency Dispatch`

---

## 5. Software & Platform Plan
* **Simulation Engine**: NVIDIA Isaac Sim (USD Stage with dynamic terrain and UAV robot asset).
* **Programming Environment**: Python 3.10+, NumPy, Scikit-Fuzzy, Matplotlib.
* **Inference Method**: Mamdani min-max inference with Centroid (Center of Gravity) defuzzification.
