# CSC3034 Computational Intelligence: Fuzzy Wildfire Risk Monitoring & Autonomous Patrol System

[![SDG 13 - Climate Action](https://img.shields.io/badge/SDG-13%20Climate%20Action-green)](https://sdgs.un.org/goals/goal13)
[![SDG 15 - Life on Land](https://img.shields.io/badge/SDG-15%20Life%20on%20Land-darkgreen)](https://sdgs.un.org/goals/goal15)
[![NVIDIA Isaac Sim](https://img.shields.io/badge/NVIDIA-Isaac%20Sim%20%2F%20Isaac%20Lab-76B900?logo=nvidia)](https://developer.nvidia.com/isaac-sim)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)](https://www.python.org/)

This project develops a **Mamdani Fuzzy Logic Inference System** coupled with **NVIDIA Isaac Sim / Isaac Lab** for dynamic forest fire risk estimation and autonomous surveillance response. Developed for **CSC3034 Computational Intelligence** at Sunway University.

---

## 📌 Project Overview & SDG Alignment

Wildfire management is characterized by high uncertainty, continuous environmental variability, and complex non-linear interactions among atmospheric and fuel conditions. This system addresses two United Nations Sustainable Development Goals:
* **SDG 13: Climate Action** — Mitigates greenhouse gas emissions and environmental degradation by enabling early detection and swift containment of wildfires.
* **SDG 15: Life on Land** — Protects terrestrial biodiversity, forest ecosystems, and habitat conservation.

---

## 🧠 Fuzzy System Architecture

### 1. Linguistic Input Variables
1. **Ambient Temperature ($^\circ$C)**: $[0, 50]$
   * Sets: `Low`, `Moderate`, `High`, `Extreme`
2. **Relative Humidity (%)**: $[0, 100]$
   * Sets: `High`, `Moderate`, `Low`, `Very Low`
3. **Wind Speed (km/h)**: $[0, 100]$
   * Sets: `Calm`, `Moderate`, `High`, `Severe`
4. **Vegetation Dryness (%)**: $[0, 100]$
   * Sets: `Wet`, `Moderate`, `Dry`, `Critically Dry`

### 2. Linguistic Output Variables
1. **Fire Risk Index (FRI)**: $[0, 100]$
   * Sets: `Low`, `Moderate`, `High`, `Extreme`
2. **Patrol Urgency / Drone Speed (%)**: $[0, 100]$
   * Sets: `Standard Patrol`, `Accelerated`, `Emergency Dispatch`
3. **Suppression Alert Level**: $[0, 3]$
   * Sets: `Advisory (0)`, `Watch (1)`, `Warning (2)`, `Evacuate/Suppress (3)`

---

## 📂 Repository Structure

```
csc3034-fuzzy-wildfire-sim/
├── README.md                      # Project documentation and setup guide
├── requirements.txt               # Python package dependencies
├── .gitignore                     # Git ignore rules for Python & Omniverse
├── src/
│   ├── __init__.py
│   ├── fuzzy_system/
│   │   ├── __init__.py
│   │   ├── controller.py          # Core Mamdani Fuzzy Inference Engine
│   │   └── isaac_sim_bridge.py    # Interface bridge for NVIDIA Isaac Sim / Action Graph
│   ├── run_demo.py                # Interactive CLI demo to test fuzzy inference
│   └── visualize_membership.py    # Generates plots for report and A1 poster
├── tests/
│   ├── __init__.py
│   └── test_fuzzy_controller.py   # Automated unit tests for rule validation
└── docs/
    ├── proposal/
    │   └── CSC3034_Group_Proposal_Form.md   # Project proposal submission template
    ├── report/
    │   └── REPORT_TEMPLATE.md               # 10-page report template (LaTeX/Markdown)
    └── poster/
        └── POSTER_GUIDE.md                  # A1 infographic design guidelines
```

---

## 🚀 Quickstart & Installation

### 1. Local Python Environment (Standalone Testing)
```bash
# Clone the repository
git clone https://github.com/Ipaidforwinrar1/csc3034-fuzzy-wildfire-sim.git
cd csc3034-fuzzy-wildfire-sim

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate # Linux/macOS

# Install dependencies
pip install -r requirements.txt

# Run the fuzzy inference demo
python src/run_demo.py

# Generate visualization plots for the report and poster
python src/visualize_membership.py
```

### 2. NVIDIA Isaac Sim Integration
1. Open **Omniverse Launcher** and launch **Isaac Sim**.
2. Open the scene asset (forest terrain / UAV drone stage).
3. Use the integrated Python environment or Isaac Sim Python executable (`python.bat` / `python.sh`) to execute `src/fuzzy_system/isaac_sim_bridge.py`.

---

## 🧪 Running Unit Tests
```bash
pytest tests/ -v
```

---

## 👥 Course & Team Information
* **Course**: CSC3034 Computational Intelligence
* **Institution**: Sunway University, School of Mathematical Sciences / Computing
* **Instructor**: Dr. Tang Tiong Yew
* **Submission Deadline**: 15 November 2026, 11:59 PM
