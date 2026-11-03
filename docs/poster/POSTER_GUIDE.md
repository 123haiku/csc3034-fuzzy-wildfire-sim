# CSC3034 Infographic Poster Guide (A1 Size)

## 📐 Dimensions & Specifications
* **Standard Size**: **A1** (594 mm × 841 mm / 23.39 in × 33.11 in).
* **Orientation**: Portrait (standard) or Landscape.
* **Resolution**: Minimum 300 DPI (7,016 × 9,933 pixels).
* **Color Space**: CMYK (if printed) or high-contrast RGB for digital review.

---

## 🎨 Recommended Color Scheme
* **Primary / Accent**: Fire Ember Orange (`#FF5722`), Forest Green (`#2E7D32`), Tech Slate (`#263238`).
* **Background**: Clean Off-White (`#F8F9FA`) or Dark Tech aesthetic (`#121820`).
* **Visual Hierarchy**:
  * Title: 72–90 pt (bold, readable from 2 meters away).
  * Section Headers: 36–48 pt.
  * Body Text: 20–24 pt (bullet points preferred over long paragraphs).
  * Captions & Footnotes: 14–16 pt.

---

## 🏗 Ready-to-Use Content for Poster Zones

### [ZONE 1] HEADER & TITLE
* **Title**: Autonomous Wildfire Risk Assessment & UAV Surveillance Dispatch Using Mamdani Fuzzy Logic in NVIDIA Isaac Sim
* **Subtitle**: CSC3034 Computational Intelligence | Sunway University
* **Authors**: Pang Wei Sheng (24035115), Roshan A/L Sivakumar (23028285), Dinesswar A/L Sathasivam (23096910), Yeoh Choon Hern (23100795)
* **Supervisor**: Dr. Tang Tiong Yew

---

### [ZONE 2] PROBLEM & UN SDG ALIGNMENT
* **Problem**: Traditional fire alarms rely on brittle binary thresholds ($T > 40^\circ\text{C}$), generating excessive false alarms or missing wind-driven fires in dry brush.
* **Solution**: An explainable Mamdani Fuzzy Logic Controller mapping continuous meteorological gradients into dynamic UAV flight urgency.
* **SDG 13 (Climate Action)**: Early aerial detection halts wildfire propagation, preventing gigatons of carbon emissions.
* **SDG 15 (Life on Land)**: Safeguards terrestrial forest biodiversity, habitat conservation, and soil integrity.

---

### [ZONE 3] SYSTEM ARCHITECTURE & FUZZY LOGIC FORMULATION
* **4 Linguistic Inputs**:
  * Temperature ($0 - 50^\circ\text{C}$): `Low`, `Moderate`, `High`, `Extreme`
  * Relative Humidity ($0 - 100\%$): `High`, `Moderate`, `Low`, `Very Low`
  * Wind Velocity ($0 - 100\text{ km/h}$): `Calm`, `Moderate`, `High`, `Severe`
  * Fuel Dryness ($0 - 100\%$): `Wet`, `Moderate`, `Dry`, `Critically Dry`
* **2 Actuation Outputs**:
  * Fire Risk Index ($\text{FRI} \in [0, 100]$)
  * Drone Throttle Urgency ($S \in [0, 100]\%$)
* **Defuzzification**: Center of Gravity (Centroid / COG):
  $$\text{COG} = \frac{\int y \cdot \mu_{\text{agg}}(y) \, dy}{\int \mu_{\text{agg}}(y) \, dy}$$
* **Image to Include**: `plots/membership_functions.png` (displays all 6 linguistic membership curves).

---

### [ZONE 4] NVIDIA ISAAC SIM 3D SIMULATION
* **Simulation Engine**: NVIDIA Isaac Sim 6.2.0 on NVIDIA GeForce RTX 4060 Laptop GPU.
* **OpenUSD Stage**: $65\text{m} \times 65\text{m}$ terrain, 48 procedurally clustered trees with moisture shaders, and 3 thermal ignition hotspots.
* **Drone Agent**: 4-rotor quadcopter with optical sensor gimbal cruising at $5.0\text{m}$ altitude, synchronizing telemetry attributes in real time.
* **Image to Include**: Screenshot of the Isaac Sim 3D viewport showing the drone hovering above the trees and glowing orange hotspots.

---

### [ZONE 5] EXPERIMENTAL RESULTS & TELEMETRY
* **12-Waypoint Mission Highlights**:
  * **Base Center**: $T=28.8^\circ\text{C}, RH=47.8\% \rightarrow \text{FRI} = 45.0$ (Patrol Urgency $20.0\%$, `[WATCH]`).
  * **Hotspot 1 Core**: $T=42.4^\circ\text{C}, RH=19.4\%, W=44.8\text{km/h}, F=86.8\% \rightarrow \mathbf{\text{FRI} = 91.2}$ (Urgency $89.2\%$, `[CRITICAL DISPATCH]`).
  * **Hotspot 2 Core**: $T=44.5^\circ\text{C}, RH=17.9\%, W=47.3\text{km/h}, F=87.3\% \rightarrow \mathbf{\text{FRI} = 91.7}$ (Urgency $90.0\%$, `[CRITICAL DISPATCH]`).
* **Performance**: $0.15\text{ ms}$ fuzzy inference latency per cycle ($>6000\text{ Hz}$ capacity), easily deployable on embedded UAV computers (NVIDIA Jetson).
* **Image to Include**: `plots/mission_telemetry_dashboard.png` (3D Trajectory + Atmospheric & Actuation Response Timeline).

---

### [ZONE 6] CONCLUSION & FUTURE OUTLOOK
* **Conclusion**: Successfully bridges fuzzy computational intelligence with physically-accurate 3D robotics simulation for proactive environmental protection.
* **Future Work**: Multi-UAV swarm decentralized patrolling and reinforcement learning reward shaping via Isaac Lab.

---

## 🛠 Recommended Tools
1. **Canva**: Search "Academic Poster A1" or "Infographic Poster".
2. **Figma**: Set frame to 594mm × 841mm.
3. **PowerPoint**: Page Setup $\rightarrow$ Custom Slide Dimensions: 59.4 cm × 84.1 cm.
