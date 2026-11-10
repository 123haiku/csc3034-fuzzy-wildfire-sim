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

All three outputs are Mamdani consequents: every rule fires one term in each output
universe, the clipped sets are aggregated with `max`, and each output is defuzzified
by centroid. The alert level is therefore a fuzzy variable like the other two, not a
threshold applied to the Fire Risk Index.

| Output | Universe | Sets (membership peaks) |
|---|---|---|
| **Fire Risk Index (FRI)** | $[0, 100]$ | `Low` (trapezoid 0–20/35), `Moderate` (triangle 25–45–65), `High` (triangle 55–75–85), `Extreme` (trapezoid 80–90–100) |
| **Patrol Urgency / Drone Speed** | $[0, 100]$ % | `Standard Patrol` (trapezoid 0–25/45), `Accelerated` (triangle 40–60–80), `Emergency Dispatch` (trapezoid 75–90–100) |
| **Suppression Alert Level** | $[0, 3]$ | `Advisory` (trapezoid 0–0/0–0.6, peak at 0), `Watch` (triangle 0.4–1–1.6), `Warning` (triangle 1.4–2–2.6), `Evacuate/Suppress` (trapezoid 2.4–3–3) |

The alert universe is sampled at 0.25 intervals so every integer tier and every set
shoulder falls on a sample; this keeps each triangular set peaking at exactly 1.0.

### 3. Rule Base (10 Mamdani Rules)

Each rule binds an antecedent to a triple of consequents, one per output universe.

| # | Antecedent (min) | FRI | Throttle | Alert |
|---|---|---|---|---|
| 1 | Humidity `High` **and** Fuel `Wet` | `Low` | `Standard` | `Advisory` |
| 2 | Temp `Low` **and** Humidity `Moderate` | `Low` | `Standard` | `Advisory` |
| 3 | Temp `Moderate` **and** Fuel `Moderate` | `Moderate` | `Standard` | `Watch` |
| 4 | Temp `Moderate` **and** Wind `High` **and** Fuel `Dry` | `High` | `Accelerated` | `Warning` |
| 5 | Temp `High` **and** Humidity `Low` | `High` | `Accelerated` | `Warning` |
| 6 | Temp `High` **and** Wind `Severe` | `Extreme` | `Emergency` | `Evacuate` |
| 7 | Temp `Extreme` **and** Humidity `Very Low` | `Extreme` | `Emergency` | `Evacuate` |
| 8 | Fuel `Critical` **and** Wind `High` | `Extreme` | `Emergency` | `Evacuate` |
| 9 | Temp `Extreme` **and** Fuel `Critical` | `Extreme` | `Emergency` | `Evacuate` |
| 10 | Wind `Calm` **and** Humidity `High` | `Low` | `Standard` | `Advisory` |

### 4. Controller Result Payload

`WildfireFuzzyController.compute()` returns:

| Key | Type | Meaning |
|---|---|---|
| `fire_risk_index` | float | Defuzzified FRI, 0–100 |
| `patrol_urgency_speed` | float | Defuzzified throttle, 0–100 % |
| `suppression_alert_level` | float | Defuzzified alert, continuous 0–3 |
| `alert_level` | int | `round(suppression_alert_level)` clamped to 0–3 |
| `alert_name` | str | `NORMAL` / `WATCH` / `WARNING` / `CRITICAL` |
| `alert_label` | str | `Advisory` / `Watch` / `Warning` / `Evacuate/Suppress` |
| `alert_action` | str | Recommended response for the tier |
| `rule_firing_peak` | float | Largest antecedent firing strength (0 means no rule fired) |

`alert_level` and `alert_name` are a reporting convenience derived from the fuzzy
alert output. When no rule fires at all (`rule_firing_peak == 0`) all three outputs
return their low-risk fallback: FRI 10.0, throttle 20.0, alert 0.0.

### 5. Validation Against scikit-fuzzy

The production engine is hand-written on NumPy and does not import scikit-fuzzy.
`src/fuzzy_system/reference_engine.py` rebuilds the same universes, membership
functions and rules with `skfuzzy.control` and compares both engines:

```bash
python -m src.fuzzy_system.reference_engine --tolerance 0.5
```

Latest run: worst absolute deviation 0.069 across 9 scenarios, all within tolerance.
`tests/test_reference_engine.py` asserts the same under pytest.

---

## 📂 Repository Structure

```
csc3034-fuzzy-wildfire-sim/
├── README.md                      # Project documentation and setup guide
├── requirements.txt               # Python package dependencies
├── .gitignore                     # Git ignore rules for Python & Omniverse
├── assets/
│   └── wildfire_forest_uav_stage.usda   # OpenUSD stage: terrain, trees, hotspots, UAV
├── src/
│   ├── __init__.py
│   ├── fuzzy_system/
│   │   ├── __init__.py
│   │   ├── controller.py          # Core Mamdani Fuzzy Inference Engine (3 outputs)
│   │   ├── isaac_sim_bridge.py    # Interface bridge for NVIDIA Isaac Sim / Action Graph
│   │   └── reference_engine.py    # scikit-fuzzy cross-check of the hand-written engine
│   ├── create_wildfire_stage.py   # Procedurally builds the USD twin and runs the patrol
│   ├── run_demo.py                # Interactive CLI demo to test fuzzy inference
│   ├── visualize_membership.py    # Membership plots for the report and A1 poster
│   ├── visualize_mission_telemetry.py  # Waypoint telemetry dashboard
│   ├── export_report_docx.py      # Builds the final report DOCX
│   └── generate_poster_html.py    # Builds the A1 poster HTML
├── tests/
│   ├── __init__.py
│   ├── test_fuzzy_controller.py   # Unit tests: scenarios, boundaries, alert consequent
│   └── test_reference_engine.py   # Engine vs scikit-fuzzy agreement per scenario
├── tools/
│   └── presentation/              # Deck build pipeline (figures → pptx → pdf) + verifier
│       ├── README.md              # Rebuild commands and layout conventions
│       ├── nvidia_plots.py        # Regenerates the deck figures in the NVIDIA palette
│       ├── crop_viewport.py       # Cuts Isaac Sim window chrome off the raw captures
│       ├── build_deck_v4.py       # Builds all 11 slides
│       ├── build_poster.py        # Builds the A1 poster PDF/PNG
│       ├── deck_notes.py          # Speaker notes, one block per slide
│       └── verify_deck.py         # Assertion-based check of the .pptx and .pdf
└── docs/
    ├── presentation/
    │   ├── CSC3034_Presentation_Slides.pptx  # 11-slide deck, notes on every slide
    │   ├── CSC3034_Presentation_Slides.pdf   # Same deck as PDF
    │   ├── assets/                           # Figures the deck embeds
    │   └── _archive/                         # Superseded generations (gitignored)
    ├── proposal/
    │   ├── CSC3034_Group_Proposal_Form.md   # Project proposal submission template
    │   └── CSC3034_Group_Proposal_Form.docx # Same, as submitted
    ├── report/
    │   ├── REPORT_TEMPLATE.md               # 10-page report template (LaTeX/Markdown)
    │   ├── CSC3034_Project_Report_Template.docx
    │   ├── CSC3034_Final_Report.docx        # Final submission
    │   └── CSC3034_Final_Report.pdf         # Final submission, PDF export
    └── poster/
        ├── POSTER_GUIDE.md                  # A1 infographic design guidelines
        ├── CSC3034_A1_Poster.html           # Generated poster source
        ├── CSC3034_A1_Poster.pdf            # A1 print-ready PDF
        └── CSC3034_A1_Poster_300DPI.png     # 300 DPI raster for print
```

---

## 🚀 Quickstart & Installation

### 1. Local Python Environment (Standalone Testing)
```bash
# Clone the repository
git clone https://github.com/123haiku/csc3034-fuzzy-wildfire-sim.git
cd csc3034-fuzzy-wildfire-sim

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate # Linux/macOS

# Install dependencies
pip install -r requirements.txt

# Run the fuzzy inference demo
python src/run_demo.py

# Enter custom sensor readings interactively
python src/run_demo.py --interactive

# Generate visualization plots for the report and poster
python src/visualize_membership.py
```

### 2. NVIDIA Isaac Sim Integration
1. Open **Omniverse Launcher** and launch **Isaac Sim**.
2. Open the scene asset (forest terrain / UAV drone stage).
3. Use the integrated Python environment or Isaac Sim Python executable (`python.bat` / `python.sh`) to execute `src/fuzzy_system/isaac_sim_bridge.py`.

Without Isaac Sim hardware, run the deterministic mock bridge from the repository root:
```bash
python -m src.fuzzy_system.isaac_sim_bridge --scenario worsening --steps 10
```
Available scenarios are `normal`, `worsening`, and `critical`. The mock bridge
generates changing environmental readings, updates a simulated UAV position, and
logs patrol responses for each step.

---

## 🧪 Running Unit Tests
```bash
pytest tests/ -v
```

Two test files: `test_fuzzy_controller.py` covers the scenario envelope, input
boundaries, monotonicity and the three output consequents; `test_reference_engine.py`
asserts the hand-written engine agrees with scikit-fuzzy within 0.5 on every scenario.

```bash
# Cross-check the engine against scikit-fuzzy (prints a per-scenario deviation table)
python -m src.fuzzy_system.reference_engine --tolerance 0.5
```

---

## 🎞 Defence Slides

The deck is generated, not hand-edited: `docs/presentation/CSC3034_Presentation_Slides.pptx`
(11 slides, 16:9, speaker notes on every slide) and its `.pdf` export. Editing the `.pptx`
by hand is overwritten by the next build.

```bash
python tools/presentation/nvidia_plots.py   # figures in the NVIDIA palette
python tools/presentation/build_deck_v4.py  # deck
python tools/presentation/verify_deck.py    # 16 assertions on the pptx + pdf
```

See `tools/presentation/README.md` for the full three-step rebuild (figures → deck → PDF)
and the layout conventions the build enforces.

---

## 👥 Course & Team Information
* **Course**: CSC3034 Computational Intelligence
* **Institution**: Sunway University, School of Mathematical Sciences / Computing
* **Instructor**: Dr. Tang Tiong Yew
* **Submission Deadline**: 15 November 2026, 11:59 PM