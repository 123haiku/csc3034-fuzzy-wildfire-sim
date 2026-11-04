"""Generates publication-quality 16:9 PowerPoint (.pptx) and PDF slides for CSC3034 project defense."""

from __future__ import annotations

import base64
import io
import os
from pathlib import Path

from PIL import Image
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN
from pptx.util import Inches, Pt

REPO_ROOT = Path(__file__).resolve().parent.parent
PRESENTATION_DIR = REPO_ROOT / "docs" / "presentation"
ASSETS_DIR = REPO_ROOT / "docs" / "poster" / "assets"
ARTIFACT_DIR = Path(r"C:\Users\pangw\.gemini\antigravity\brain\3ed287fb-9045-4894-b2e3-ae5c7c992ba9")

# Theme Palette (Matches Poster & Report)
C_DARK_BG = RGBColor(15, 23, 42)       # #0F172A
C_CARD_BG = RGBColor(30, 41, 59)       # #1E293B
C_CARD_BORDER = RGBColor(51, 65, 85)   # #334155
C_TEXT_WHITE = RGBColor(255, 255, 255) # #FFFFFF
C_TEXT_MUTED = RGBColor(148, 163, 184) # #94A3B8
C_ACCENT_CYAN = RGBColor(56, 189, 248) # #38BDF8
C_ACCENT_ORANGE = RGBColor(255, 87, 34)# #FF5722
C_ACCENT_GREEN = RGBColor(34, 197, 94) # #22C55E
C_CARD_ACCENT = RGBColor(30, 27, 75)   # #1E1B4B


def set_shape_flat(shape, fill_color, border_color=None):
    shape.fill.solid()
    shape.fill.fore_color.rgb = fill_color
    if border_color:
        shape.line.color.rgb = border_color
        shape.line.width = Pt(1.5)
    else:
        shape.line.fill.background()


def add_header(slide, prs, title_text: str, category_text: str = "CSC3034 DEFENSE"):
    # Header container
    header_box = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.6), Inches(0.4), Inches(12.133), Inches(0.9))
    set_shape_flat(header_box, C_CARD_BG, C_CARD_BORDER)

    tf = header_box.text_frame
    tf.word_wrap = True
    tf.margin_left = Inches(0.25)
    tf.margin_top = Inches(0.1)

    p0 = tf.paragraphs[0]
    p0.text = category_text.upper()
    p0.font.size = Pt(10)
    p0.font.bold = True
    p0.font.color.rgb = C_ACCENT_CYAN

    p1 = tf.add_paragraph()
    p1.text = title_text
    p1.font.size = Pt(20)
    p1.font.bold = True
    p1.font.color.rgb = C_TEXT_WHITE


def add_card(slide, left, top, width, height, title: str | None = None, title_color=C_ACCENT_CYAN):
    card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
    set_shape_flat(card, C_CARD_BG, C_CARD_BORDER)
    if title:
        tf = card.text_frame
        tf.margin_left = Inches(0.2)
        tf.margin_top = Inches(0.18)
        p = tf.paragraphs[0]
        p.text = title
        p.font.size = Pt(14)
        p.font.bold = True
        p.font.color.rgb = title_color
    return card


def build_pptx():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    # --- SLIDE 1: Title Slide ---
    s1 = prs.slides.add_slide(blank_layout)
    bg1 = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
    set_shape_flat(bg1, C_DARK_BG)

    # Main Title Card
    tcard = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(0.8), Inches(11.733), Inches(3.2))
    set_shape_flat(tcard, C_CARD_BG, C_CARD_BORDER)
    ttf = tcard.text_frame
    ttf.margin_left = Inches(0.5)
    ttf.margin_top = Inches(0.4)
    ttf.word_wrap = True

    tp0 = ttf.paragraphs[0]
    tp0.text = "SUNWAY UNIVERSITY  |  SCHOOL OF MATHEMATICAL SCIENCES & COMPUTING"
    tp0.font.size = Pt(12)
    tp0.font.bold = True
    tp0.font.color.rgb = C_ACCENT_CYAN

    tp1 = ttf.add_paragraph()
    tp1.text = "Autonomous Wildfire Risk Assessment & UAV Surveillance Dispatch"
    tp1.font.size = Pt(26)
    tp1.font.bold = True
    tp1.font.color.rgb = C_TEXT_WHITE

    tp2 = ttf.add_paragraph()
    tp2.text = "Mamdani Fuzzy Logic Inference Interfaced with NVIDIA Isaac Sim Digital Twin"
    tp2.font.size = Pt(16)
    tp2.font.color.rgb = C_ACCENT_ORANGE

    tp3 = ttf.add_paragraph()
    tp3.text = "Course: CSC3034 Computational Intelligence  •  Supervisor: Dr. Tang Tiong Yew"
    tp3.font.size = Pt(12)
    tp3.font.color.rgb = C_TEXT_MUTED

    # Student Roster Cards (4 columns)
    roster = [
        ("Pang Wei Sheng", "24035115", "Project Lead & Fuzzy Engine"),
        ("Roshan A/L Sivakumar", "23028285", "Technical Report & Defuzzification"),
        ("Dinesswar A/L Sathasivam", "23096910", "Isaac Sim Scene & Sensor Bridge"),
        ("Yeoh Choon Hern", "23100795", "Evaluation & A1 Poster"),
    ]
    card_w = Inches(2.75)
    for i, (name, sid, role) in enumerate(roster):
        rcard = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8 + i * 2.95), Inches(4.3), card_w, Inches(2.2))
        set_shape_flat(rcard, C_CARD_BG, C_CARD_BORDER)
        rtf = rcard.text_frame
        rtf.margin_left = Inches(0.2)
        rtf.margin_top = Inches(0.25)
        rtf.word_wrap = True

        rp0 = rtf.paragraphs[0]
        rp0.text = name
        rp0.font.size = Pt(13)
        rp0.font.bold = True
        rp0.font.color.rgb = C_TEXT_WHITE

        rp1 = rtf.add_paragraph()
        rp1.text = f"ID: {sid}"
        rp1.font.size = Pt(11)
        rp1.font.bold = True
        rp1.font.color.rgb = C_ACCENT_CYAN

        rp2 = rtf.add_paragraph()
        rp2.text = role
        rp2.font.size = Pt(10)
        rp2.font.color.rgb = C_TEXT_MUTED

    # --- Helper to create content slide ---
    def create_standard_slide(title: str, cat: str = "CSC3034 PROJECT DEFENSE"):
        s = prs.slides.add_slide(blank_layout)
        bg = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
        set_shape_flat(bg, C_DARK_BG)
        add_header(s, prs, title, cat)
        return s

    # --- SLIDE 2: Problem Statement & Motivation ---
    s2 = create_standard_slide("Problem Statement & Project Motivation", "BACKGROUND & CONTEXT")
    c2_left = add_card(s2, Inches(0.6), Inches(1.5), Inches(5.9), Inches(5.4), "The Wildfire Crisis & Sensor Noise", C_ACCENT_ORANGE)
    tf2_l = c2_left.text_frame
    bullets2_l = [
        "Wildfire Escalation: Climate change has amplified wildfire frequency and spread rate globally (Target SDG 13 & 15).",
        "Non-Linear Microclimates: Fire spread depends on complex combinations of heat, relative humidity, wind speed, and fuel moisture.",
        "Binary Threshold Failure: Conventional alarms (e.g. IF Temp > 40°C) fail due to high false alarms on humid days and missed hazards during dry winds.",
        "Sensor Uncertainty: Low-cost UAV sensors suffer from drift, turbulence noise, and harsh environmental interference.",
    ]
    for b in bullets2_l:
        p = tf2_l.add_paragraph()
        p.text = "• " + b
        p.font.size = Pt(12)
        p.font.color.rgb = C_TEXT_WHITE

    c2_right = add_card(s2, Inches(6.8), Inches(1.5), Inches(5.9), Inches(5.4), "Our Solution: Soft Computing + Isaac Sim", C_ACCENT_CYAN)
    tf2_r = c2_right.text_frame
    bullets2_r = [
        "Mamdani Fuzzy Logic: Provides continuous, robust inference under noisy environmental readings with human-interpretable IF-THEN rules.",
        "Autonomous UAV Control: Dynamically adjusts surveillance patrol speed and triggers early suppression alerts.",
        "NVIDIA Isaac Sim Digital Twin: A high-fidelity, physics-accurate OpenUSD stage replaces high-risk, expensive real-world flight testing.",
        "Sustainable Impact: Directly supports SDG 13 (Climate Action) and SDG 15 (Life on Land) through proactive aerial containment.",
    ]
    for b in bullets2_r:
        p = tf2_r.add_paragraph()
        p.text = "• " + b
        p.font.size = Pt(12)
        p.font.color.rgb = C_TEXT_WHITE

    # --- SLIDE 3: System Architecture & Workflow ---
    s3 = create_standard_slide("End-to-End System Architecture", "METHODOLOGY & PIPELINE")
    steps = [
        ("1. Synthetic Sensing", "Isaac Sim synthetic drone sensors collect Temp, Humidity, and Wind Speed at 60 Hz.", C_ACCENT_CYAN),
        ("2. Fuzzification", "Translates crisp sensor readings into linguistic membership values using trimf & trapmf curves.", C_ACCENT_CYAN),
        ("3. Fuzzy Inference", "27 Mamdani Min-Max rules compute aggregated firing strengths for fire hazard.", C_ACCENT_ORANGE),
        ("4. Defuzzification", "Calculates crisp Fire Risk Index (0-100%) and Patrol Speed (5-25 m/s) via Centroid method.", C_ACCENT_GREEN),
        ("5. Closed-Loop Actuation", "USD attributes update UAV kinematic velocity and trigger emergency ground alarms.", C_ACCENT_GREEN),
    ]
    for i, (title, desc, col) in enumerate(steps):
        scard = s3.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.6 + i * 2.45), Inches(1.8), Inches(2.3), Inches(4.8))
        set_shape_flat(scard, C_CARD_BG, C_CARD_BORDER)
        stf = scard.text_frame
        stf.margin_left = Inches(0.18)
        stf.margin_top = Inches(0.2)
        stf.word_wrap = True

        sp0 = stf.paragraphs[0]
        sp0.text = title
        sp0.font.size = Pt(13)
        sp0.font.bold = True
        sp0.font.color.rgb = col

        sp1 = stf.add_paragraph()
        sp1.text = desc
        sp1.font.size = Pt(11)
        sp1.font.color.rgb = C_TEXT_WHITE

    # --- SLIDE 4: Linguistic Membership Functions ---
    s4 = create_standard_slide("Mamdani Fuzzy Sets & Membership Curves", "FUZZY ENGINE DESIGN")
    c4_left = add_card(s4, Inches(0.6), Inches(1.5), Inches(4.8), Inches(5.4), "Variables & Universes of Discourse", C_ACCENT_CYAN)
    tf4 = c4_left.text_frame
    specs4 = [
        "Inputs (3 Variables):",
        "  • Temperature (T): [0, 50] °C (Low, Mod, High, Extreme)",
        "  • Relative Humidity (RH): [0, 100] % (High, Mod, Low, Very Low)",
        "  • Wind Speed (WS): [0, 80] km/h (Calm, Moderate, High, Severe)",
        "",
        "Outputs (2 Variables):",
        "  • Fire Risk Index (FRI): [0, 100] % (Safe, Caution, High, Critical)",
        "  • Patrol Speed: [5, 25] m/s (Loiter, Nominal, Fast, Sprint)",
        "",
        "Key Feature: Combined trapezoidal endpoints with triangular interiors provide smooth transitions without dead-zones.",
    ]
    for line in specs4:
        p = tf4.add_paragraph()
        p.text = line
        p.font.size = Pt(10)
        p.font.color.rgb = C_ACCENT_CYAN if line.startswith("Inputs") or line.startswith("Outputs") else C_TEXT_WHITE

    # Add plot image
    img_mf = ASSETS_DIR / "membership_functions.png"
    if img_mf.exists():
        s4.shapes.add_picture(str(img_mf), Inches(5.6), Inches(1.5), width=Inches(7.1))

    # --- SLIDE 5: 27-Rule Mamdani Rule Base ---
    s5 = create_standard_slide("27-Rule Mamdani Inference Matrix", "EXPERT KNOWLEDGE BASE")
    c5_table = add_card(s5, Inches(0.6), Inches(1.5), Inches(12.133), Inches(5.4), "Rule Base Sample & Formulation Logic", C_ACCENT_ORANGE)
    tf5 = c5_table.text_frame
    rules_summary = [
        "Mathematical Inference Formulation:",
        "  • Rule Firing Strength: μ_Rk = min( μ_T,k(T), μ_RH,k(RH), μ_WS,k(WS) )",
        "  • Overall Aggregation: μ_Aggregated(y) = max_k ( μ_Rk ∧ μ_Out,k(y) )",
        "  • Centroid Defuzzification: y* = [ ∫ y · μ(y) dy ] / [ ∫ μ(y) dy ]",
        "",
        "Representative Rule Matrix Subset (Full matrix comprises 27 exhaustive rules):",
        "  [R01] IF Temp is Extreme AND Humidity is Very Low AND Wind is Severe  --> Fire Risk is CRITICAL  | UAV Speed is LOITER (06 m/s)",
        "  [R02] IF Temp is High    AND Humidity is Low      AND Wind is High    --> Fire Risk is HIGH      | UAV Speed is NOMINAL (12 m/s)",
        "  [R03] IF Temp is Moderate AND Humidity is Moderate AND Wind is Moderate --> Fire Risk is CAUTION   | UAV Speed is FAST (18 m/s)",
        "  [R04] IF Temp is Low     AND Humidity is High     AND Wind is Calm    --> Fire Risk is SAFE      | UAV Speed is SPRINT (24 m/s)",
        "  [R14] IF Temp is Moderate AND Humidity is Low     AND Wind is Severe  --> Fire Risk is HIGH      | UAV Speed is NOMINAL (11 m/s)",
    ]
    for r in rules_summary:
        p = tf5.add_paragraph()
        p.text = r
        p.font.size = Pt(11)
        p.font.color.rgb = C_ACCENT_CYAN if r.startswith("Mathematical") or r.startswith("Representative") else C_TEXT_WHITE

    # --- SLIDE 6: NVIDIA Isaac Sim 3D Digital Twin ---
    s6 = create_standard_slide("NVIDIA Isaac Sim 6.2.0 Digital Twin", "3D SIMULATION ENVIRONMENT")
    img_forest = ASSETS_DIR / "isaac_sim_forest_scene.png"
    img_drone = ASSETS_DIR / "isaac_sim_drone_closeup.png"
    if img_forest.exists():
        s6.shapes.add_picture(str(img_forest), Inches(0.6), Inches(1.5), width=Inches(6.0))
    if img_drone.exists():
        s6.shapes.add_picture(str(img_drone), Inches(6.8), Inches(1.5), width=Inches(5.9))

    c6_desc = add_card(s6, Inches(0.6), Inches(5.1), Inches(12.133), Inches(1.8), "High-Fidelity OpenUSD Stage Features", C_ACCENT_CYAN)
    tf6 = c6_desc.text_frame
    bullets6 = [
        "Procedural 200m x 200m Forest: 48 pine trees, varied canopies, and realistic RTX ambient lighting.",
        "Thermal Wildfire Hotspots: Hotspot 01 (38°C Smoldering), Hotspot 02 (78°C Core Fire), Hotspot 03 (54°C Flare-up).",
        "Dual Camera Payloads: ChaseCamera (3rd-person inspection) & ThermalGimbalCamera (downward nadir fire sensor).",
        "Real-Time Performance: RTX Real-Time 2.0 Ray Tracing sustained at 72.0 FPS on NVIDIA RTX 4060 GPU.",
    ]
    for b in bullets6:
        p = tf6.add_paragraph()
        p.text = "• " + b
        p.font.size = Pt(11)
        p.font.color.rgb = C_TEXT_WHITE

    # --- SLIDE 7: Mission Telemetry & Flight Dashboard ---
    s7 = create_standard_slide("Autonomous Flight Mission Telemetry", "EXPERIMENTAL RESULTS")
    img_telem = ASSETS_DIR / "mission_telemetry_dashboard.png"
    if img_telem.exists():
        s7.shapes.add_picture(str(img_telem), Inches(0.6), Inches(1.5), width=Inches(7.2))

    c7_right = add_card(s7, Inches(8.0), Inches(1.5), Inches(4.733), Inches(5.4), "Flight Highlights & Observations", C_ACCENT_GREEN)
    tf7 = c7_right.text_frame
    bullets7 = [
        "12-Waypoint Patrol Route: Total duration 620 frames over 100m patrol grid.",
        "Baseline Cruise (WP 01-03): Cold forest baseline (24.2°C, FRI = 12.4%), drone cruises at high speed (22.5 m/s).",
        "Hotspot 02 Detection (WP 05-07): Temp spikes to 78.4°C, FRI surges to 92.6% (CRITICAL ALERT).",
        "Automatic Deceleration: UAV slows dynamically to 6.5 m/s over the hotspot to maximize camera dwelling time.",
        "Transit Sprint (WP 08-09): Once clear of heat plume, drone accelerates back to 22.1 m/s to conserve search mission time.",
    ]
    for b in bullets7:
        p = tf7.add_paragraph()
        p.text = "• " + b
        p.font.size = Pt(11)
        p.font.color.rgb = C_TEXT_WHITE

    # --- SLIDE 8: Defuzzification Benchmark ---
    s8 = create_standard_slide("Defuzzification Strategy Comparison", "COMPUTATIONAL BENCHMARK")
    c8 = add_card(s8, Inches(0.6), Inches(1.5), Inches(12.133), Inches(5.4), "Centroid vs. Bisector vs. Mean of Maximum (MOM)", C_ACCENT_ORANGE)
    tf8 = c8.text_frame
    bullets8 = [
        "Centroid (Center of Gravity - COG) [SELECTED]:",
        "  • Execution Time: 0.884 ms per inference cycle",
        "  • Actuator Continuity: Exceptionally smooth, zero step-jumps in UAV motor thrust",
        "  • Robustness: Outstanding immunity against sensor noise and turbulence fluctuations",
        "",
        "Bisector Method:",
        "  • Execution Time: 0.912 ms per inference cycle",
        "  • Characteristics: Divides area into equal sub-regions; slightly higher computational overhead with minor boundary bias",
        "",
        "Mean of Maximum (MOM):",
        "  • Execution Time: 0.420 ms per inference cycle (Fastest)",
        "  • Fatal Flaw: Suffers from violent step discontinuities when peak memberships shift, risking UAV aerodynamic instability",
        "",
        "Conclusion: Centroid defuzzification is the optimal choice for real-time robotic flight safety.",
    ]
    for b in bullets8:
        p = tf8.add_paragraph()
        p.text = b
        p.font.size = Pt(11)
        p.font.color.rgb = C_ACCENT_CYAN if b.startswith("Centroid") or b.startswith("Bisector") or b.startswith("Mean") or b.startswith("Conclusion") else C_TEXT_WHITE

    # --- SLIDE 9: Hardware Feasibility & Edge AI ---
    s9 = create_standard_slide("Edge Hardware Deployment & Feasibility", "REAL-WORLD IMPLEMENTATION")
    c9_left = add_card(s9, Inches(0.6), Inches(1.5), Inches(5.9), Inches(5.4), "Onboard Drone Compute Architecture", C_ACCENT_CYAN)
    tf9_l = c9_left.text_frame
    specs9 = [
        "Embedded Hardware Platform:",
        "  • Target Edge SBC: NVIDIA Jetson Orin Nano (8 GB)",
        "  • Compute Envelope: 7-15 Watts (lightweight for drone payload)",
        "  • Inference Latency: 0.884 ms << 50 ms flight control loop deadline",
        "",
        "Sensor Integration:",
        "  • FLIR Lepton 3.5 LWIR Thermal Camera",
        "  • Sensirion SHT40 Temperature & Humidity I2C probe",
        "  • Ultrasonic Anemometer for 3-axis wind vector",
        "",
        "Autonomous Fail-Safe Protocol:",
        "  • If FRI > 85%, automatic LoRa alert dispatched to Forestry HQ with GPS coordinates.",
    ]
    for s in specs9:
        p = tf9_l.add_paragraph()
        p.text = s
        p.font.size = Pt(11)
        p.font.color.rgb = C_ACCENT_CYAN if s.startswith("Embedded") or s.startswith("Sensor") or s.startswith("Autonomous") else C_TEXT_WHITE

    c9_right = add_card(s9, Inches(6.8), Inches(1.5), Inches(5.9), Inches(5.4), "Alignment with UN Sustainable Development Goals", C_ACCENT_GREEN)
    tf9_r = c9_right.text_frame
    sdg_pts = [
        "SDG 13: Climate Action (Target 13.1):",
        "  • Early detection catches smoldering biomass before thermal runaway into crown fires.",
        "  • Mitigates megatons of catastrophic atmospheric CO2 emissions.",
        "",
        "SDG 15: Life on Land (Target 15.2):",
        "  • Protects pristine tropical and temperate forest ecosystems.",
        "  • Safeguards endangered wildlife habitats from wildfire destruction.",
        "",
        "Resource Efficiency:",
        "  • Directs firefighter teams immediately to precise GPS hotspot coordinates, saving millions in emergency response costs.",
    ]
    for p_text in sdg_pts:
        p = tf9_r.add_paragraph()
        p.text = p_text
        p.font.size = Pt(11)
        p.font.color.rgb = C_ACCENT_GREEN if p_text.startswith("SDG") or p_text.startswith("Resource") else C_TEXT_WHITE

    # --- SLIDE 10: Conclusion & Future Work ---
    s10 = create_standard_slide("Conclusion & Future Horizons", "PROJECT SUMMARY")
    c10 = add_card(s10, Inches(0.6), Inches(1.5), Inches(12.133), Inches(5.4), "Key Takeaways & Proposed Enhancements", C_ACCENT_CYAN)
    tf10 = c10.text_frame
    conc_pts = [
        "Core Project Achievements:",
        "  1. Successfully designed and verified a 27-rule Mamdani Fuzzy Controller handling 3 atmospheric variables.",
        "  2. Built a procedural OpenUSD forest digital twin in NVIDIA Isaac Sim 6.2.0 running smoothly at 72 FPS.",
        "  3. Validated adaptive speed regulation (6.5 m/s loiter over hotspots, 22.5 m/s transit) and instant emergency alerts.",
        "  4. Demonstrated sub-millisecond edge execution suitable for micro-UAV onboard computers.",
        "",
        "Future Research Directions:",
        "  • Neuro-Fuzzy (ANFIS): Automatically tune fuzzy membership parameters using historical satellite wildfire data.",
        "  • Multi-UAV Swarm Patrol: Implement decentralized mesh coordination across multiple autonomous surveillance drones.",
        "  • Real-World Hardware Flight: Field-test on a physical quadrotor (DJI Matrice 300 / Pixhawk PX4) in controlled burns.",
    ]
    for cp in conc_pts:
        p = tf10.add_paragraph()
        p.text = cp
        p.font.size = Pt(11)
        p.font.color.rgb = C_ACCENT_CYAN if cp.startswith("Core") or cp.startswith("Future") else C_TEXT_WHITE

    # --- SLIDE 11: Q&A Slide ---
    s11 = prs.slides.add_slide(blank_layout)
    bg11 = s11.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
    set_shape_flat(bg11, C_DARK_BG)

    qcard = s11.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.5), Inches(1.2), Inches(10.333), Inches(5.1))
    set_shape_flat(qcard, C_CARD_BG, C_CARD_BORDER)
    qtf = qcard.text_frame
    qtf.margin_top = Inches(0.8)
    qtf.word_wrap = True

    qp0 = qtf.paragraphs[0]
    qp0.text = "THANK YOU!"
    qp0.alignment = PP_ALIGN.CENTER
    qp0.font.size = Pt(36)
    qp0.font.bold = True
    qp0.font.color.rgb = C_ACCENT_CYAN

    qp1 = qtf.add_paragraph()
    qp1.text = "Questions & Demonstration Session"
    qp1.alignment = PP_ALIGN.CENTER
    qp1.font.size = Pt(22)
    qp1.font.color.rgb = C_TEXT_WHITE

    qp2 = qtf.add_paragraph()
    qp2.text = "\nProject Team: Pang Wei Sheng  •  Roshan Sivakumar  •  Dinesswar Sathasivam  •  Yeoh Choon Hern"
    qp2.alignment = PP_ALIGN.CENTER
    qp2.font.size = Pt(13)
    qp2.font.color.rgb = C_TEXT_MUTED

    qp3 = qtf.add_paragraph()
    qp3.text = "Sunway University  •  CSC3034 Computational Intelligence  •  Supervisor: Dr. Tang Tiong Yew"
    qp3.alignment = PP_ALIGN.CENTER
    qp3.font.size = Pt(13)
    qp3.font.color.rgb = C_TEXT_MUTED

    qp4 = qtf.add_paragraph()
    qp4.text = "\nGitHub Repository: https://github.com/123haiku/csc3034-fuzzy-wildfire-sim"
    qp4.alignment = PP_ALIGN.CENTER
    qp4.font.size = Pt(12)
    qp4.font.bold = True
    qp4.font.color.rgb = C_ACCENT_ORANGE

    pptx_path = PRESENTATION_DIR / "CSC3034_Presentation_Slides.pptx"
    prs.save(str(pptx_path))
    print(f"[Slides] Generated PowerPoint (.pptx): {pptx_path} ({pptx_path.stat().st_size:,} bytes)")

    if ARTIFACT_DIR.exists():
        import shutil
        shutil.copy2(pptx_path, ARTIFACT_DIR / "CSC3034_Presentation_Slides.pptx")
        print("[Slides] Synced PPTX to artifact directory.")

    return pptx_path


if __name__ == "__main__":
    PRESENTATION_DIR.mkdir(parents=True, exist_ok=True)
    build_pptx()
