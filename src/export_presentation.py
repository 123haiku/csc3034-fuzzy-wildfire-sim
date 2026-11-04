"""Generates clean, spacious, uncluttered 16:9 PowerPoint (.pptx) slides for CSC3034."""

from __future__ import annotations

from pathlib import Path
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN
from pptx.util import Inches, Pt

REPO_ROOT = Path(__file__).resolve().parent.parent
PRESENTATION_DIR = REPO_ROOT / "docs" / "presentation"
ASSETS_DIR = REPO_ROOT / "docs" / "poster" / "assets"
ARTIFACT_DIR = Path(r"C:\Users\pangw\.gemini\antigravity\brain\3ed287fb-9045-4894-b2e3-ae5c7c992ba9")

# Theme Palette (Consistent with Poster & Report)
C_DARK_BG = RGBColor(15, 23, 42)       # Canvas: #0F172A (Deep Slate Navy)
C_CARD_BG = RGBColor(30, 41, 59)       # Cards:  #1E293B (Card Dark Slate)
C_CARD_BORDER = RGBColor(51, 65, 85)   # Border: #334155 (Subtle Slate Border)
C_TEXT_WHITE = RGBColor(255, 255, 255) # Primary text: #FFFFFF
C_TEXT_MUTED = RGBColor(148, 163, 184) # Secondary: #94A3B8 (Light Slate)
C_ACCENT_CYAN = RGBColor(56, 189, 248) # Cyan Accent: #38BDF8
C_ACCENT_ORANGE = RGBColor(255, 87, 34)# Orange Accent: #FF5722
C_ACCENT_GREEN = RGBColor(34, 197, 94) # Green Accent: #22C55E


def set_shape_flat(shape, fill_color, border_color=None, border_width=1.5):
    shape.fill.solid()
    shape.fill.fore_color.rgb = fill_color
    if border_color:
        shape.line.color.rgb = border_color
        shape.line.width = Pt(border_width)
    else:
        shape.line.fill.background()


def add_header(slide, prs, title_text: str, category_text: str = "CSC3034 DEFENSE"):
    header_box = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(0.4), Inches(11.733), Inches(0.85))
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
    p1.font.size = Pt(21)
    p1.font.bold = True
    p1.font.color.rgb = C_TEXT_WHITE


def add_card(slide, left, top, width, height, title: str | None = None, title_color=C_ACCENT_CYAN):
    card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
    set_shape_flat(card, C_CARD_BG, C_CARD_BORDER)
    if title:
        tf = card.text_frame
        tf.margin_left = Inches(0.25)
        tf.margin_top = Inches(0.22)
        p = tf.paragraphs[0]
        p.text = title
        p.font.size = Pt(15)
        p.font.bold = True
        p.font.color.rgb = title_color
    return card


def build_pptx():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    def create_standard_slide(title: str, cat: str = "CSC3034 DEFENSE"):
        s = prs.slides.add_slide(blank_layout)
        bg = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
        set_shape_flat(bg, C_DARK_BG)
        add_header(s, prs, title, cat)
        return s

    # --- SLIDE 1: Title Slide ---
    s1 = prs.slides.add_slide(blank_layout)
    bg1 = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
    set_shape_flat(bg1, C_DARK_BG)

    tcard = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(0.8), Inches(11.733), Inches(3.1))
    set_shape_flat(tcard, C_CARD_BG, C_CARD_BORDER)
    ttf = tcard.text_frame
    ttf.margin_left = Inches(0.4)
    ttf.margin_top = Inches(0.35)

    p0 = ttf.paragraphs[0]
    p0.text = "SUNWAY UNIVERSITY  •  SCHOOL OF MATHEMATICAL SCIENCES & COMPUTING"
    p0.font.size = Pt(11)
    p0.font.bold = True
    p0.font.color.rgb = C_ACCENT_CYAN

    p1 = ttf.add_paragraph()
    p1.text = "Autonomous Wildfire Risk Assessment & UAV Surveillance"
    p1.font.size = Pt(26)
    p1.font.bold = True
    p1.font.color.rgb = C_TEXT_WHITE

    p2 = ttf.add_paragraph()
    p2.text = "Mamdani Fuzzy Logic Inference Interfaced with NVIDIA Isaac Sim 3D Twin"
    p2.font.size = Pt(16)
    p2.font.color.rgb = C_ACCENT_ORANGE

    p3 = ttf.add_paragraph()
    p3.text = "Course: CSC3034 Computational Intelligence  •  Supervisor: Dr. Tang Tiong Yew"
    p3.font.size = Pt(12)
    p3.font.color.rgb = C_TEXT_MUTED

    roster = [
        ("Pang Wei Sheng", "24035115", "Project Lead & Fuzzy Engine"),
        ("Roshan Sivakumar", "23028285", "Technical Report & Defuzzification"),
        ("Dinesswar Sathasivam", "23096910", "Isaac Sim Scene & Sensor Bridge"),
        ("Yeoh Choon Hern", "23100795", "Evaluation & A1 Poster"),
    ]
    for i, (name, sid, role) in enumerate(roster):
        rcard = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8 + i * 2.95), Inches(4.2), Inches(2.8), Inches(2.4))
        set_shape_flat(rcard, C_CARD_BG, C_CARD_BORDER)
        rtf = rcard.text_frame
        rtf.margin_left = Inches(0.2)
        rtf.margin_top = Inches(0.25)

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

    # --- SLIDE 2: Problem Statement (Spacious, 3 punchy points per side) ---
    s2 = create_standard_slide("Problem Statement & Motivation", "BACKGROUND")
    c2_l = add_card(s2, Inches(0.8), Inches(1.5), Inches(5.7), Inches(5.4), "Conventional Limitations", C_ACCENT_ORANGE)
    tf2_l = c2_l.text_frame
    bullets2_l = [
        ("Binary Thresholds Fail:", "Simple rules (T > 40°C) ignore humidity and wind, causing excessive false alarms."),
        ("Non-Linear Dynamics:", "Wildfire spread is stochastic; dry winds can ignite disasters even at moderate temps."),
        ("Noisy Drone Sensors:", "Environmental turbulence and rotor vibration degrade raw telemetry reliability."),
    ]
    for title, desc in bullets2_l:
        p = tf2_l.add_paragraph()
        p.text = f"• {title} "
        p.font.size = Pt(13)
        p.font.bold = True
        p.font.color.rgb = C_TEXT_WHITE
        p_desc = tf2_l.add_paragraph()
        p_desc.text = f"  {desc}\n"
        p_desc.font.size = Pt(12)
        p_desc.font.color.rgb = C_TEXT_MUTED

    c2_r = add_card(s2, Inches(6.8), Inches(1.5), Inches(5.7), Inches(5.4), "Our Soft-Computing Solution", C_ACCENT_CYAN)
    tf2_r = c2_r.text_frame
    bullets2_r = [
        ("Mamdani Fuzzy Inference:", "Continuous soft reasoning provides robust decisions despite sensor noise."),
        ("Multi-Sensor Data Fusion:", "Synthesizes Temperature, Humidity, and Wind into a normalized Fire Risk Index."),
        ("Closed-Loop Modulation:", "UAV automatically decelerates over hotspots to dwell and verify thermal hazards."),
    ]
    for title, desc in bullets2_r:
        p = tf2_r.add_paragraph()
        p.text = f"• {title} "
        p.font.size = Pt(13)
        p.font.bold = True
        p.font.color.rgb = C_TEXT_WHITE
        p_desc = tf2_r.add_paragraph()
        p_desc.text = f"  {desc}\n"
        p_desc.font.size = Pt(12)
        p_desc.font.color.rgb = C_TEXT_MUTED

    # --- SLIDE 3: End-to-End System Architecture (Clean Horizontal Flow) ---
    s3 = create_standard_slide("End-to-End System Architecture Flow", "SYSTEM PIPELINE")
    
    stages = [
        ("01", "Synthetic Sensing", "Temp, Humidity, Wind\nIngested at 60 Hz", C_ACCENT_CYAN),
        ("02", "Fuzzification", "Triangular & Trapezoidal\nLinguistic sets", C_ACCENT_CYAN),
        ("03", "Fuzzy Inference", "27 Mamdani Min-Max\nRule Evaluation", C_ACCENT_ORANGE),
        ("04", "Defuzzification", "Centroid (COG) Method\n0.88 ms latency", C_ACCENT_GREEN),
        ("05", "Actuation & Alert", "Speed: 6.5 - 22.5 m/s\nInstant Ground Alarm", C_ACCENT_GREEN),
    ]
    for i, (num, name, desc, col) in enumerate(stages):
        # Card
        scard = s3.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8 + i * 2.38), Inches(2.0), Inches(2.2), Inches(4.2))
        set_shape_flat(scard, C_CARD_BG, col, border_width=2.0)
        stf = scard.text_frame
        stf.margin_left = Inches(0.18)
        stf.margin_top = Inches(0.3)
        stf.word_wrap = True

        p_num = stf.paragraphs[0]
        p_num.text = num
        p_num.font.size = Pt(28)
        p_num.font.bold = True
        p_num.font.color.rgb = col

        p_title = stf.add_paragraph()
        p_title.text = name + "\n"
        p_title.font.size = Pt(14)
        p_title.font.bold = True
        p_title.font.color.rgb = C_TEXT_WHITE

        p_body = stf.add_paragraph()
        p_body.text = desc
        p_body.font.size = Pt(11)
        p_body.font.color.rgb = C_TEXT_MUTED

    # --- SLIDE 4: Linguistic Membership Functions (Spacious Layout) ---
    s4 = create_standard_slide("Linguistic Variables & Membership Functions", "FUZZY ENGINE")
    c4 = add_card(s4, Inches(0.8), Inches(1.5), Inches(4.2), Inches(5.4), "Universe of Discourse", C_ACCENT_CYAN)
    tf4 = c4.text_frame
    mfs = [
        "Inputs (3 Probes):",
        "• Temp (T): [0, 50] °C",
        "  (Low, Mod, High, Extreme)",
        "• Humidity (RH): [0, 100] %",
        "  (High, Mod, Low, Very Low)",
        "• Wind (WS): [0, 80] km/h",
        "  (Calm, Mod, High, Severe)",
        "",
        "Outputs (2 Controls):",
        "• Fire Risk Index: [0, 100] %",
        "• Patrol Speed: [5, 25] m/s",
    ]
    for m in mfs:
        p = tf4.add_paragraph()
        p.text = m
        p.font.size = Pt(11 if m.startswith(" ") else 12)
        p.font.bold = m.startswith("Inputs") or m.startswith("Outputs")
        p.font.color.rgb = C_ACCENT_CYAN if (m.startswith("Inputs") or m.startswith("Outputs")) else (C_TEXT_WHITE if m.startswith("•") else C_TEXT_MUTED)

    img_mf = ASSETS_DIR / "membership_functions.png"
    if img_mf.exists():
        s4.shapes.add_picture(str(img_mf), Inches(5.2), Inches(1.5), width=Inches(7.3))

    # --- SLIDE 5: Mamdani 27-Rule Matrix (Uncluttered) ---
    s5 = create_standard_slide("27-Rule Mamdani Inference Engine", "KNOWLEDGE BASE")
    math_card = add_card(s5, Inches(0.8), Inches(1.5), Inches(11.733), Inches(1.1))
    mtf = math_card.text_frame
    mtf.margin_left = Inches(0.3)
    mtf.margin_top = Inches(0.18)
    mp0 = mtf.paragraphs[0]
    mp0.text = "Mathematical Formulation:  μ_Rk = min( μ_T, μ_RH, μ_WS )   |   μ_Agg = max_k( μ_Rk ∧ μ_Out )"
    mp0.font.size = Pt(13)
    mp0.font.bold = True
    mp0.font.color.rgb = C_ACCENT_CYAN

    rule_samples = [
        ("CRITICAL HAZARD [R01]", "IF Temp is Extreme AND Humidity is Very Low AND Wind is Severe\n→ Fire Risk: CRITICAL (95%)  |  UAV Speed: LOITER (6 m/s)", C_ACCENT_ORANGE),
        ("HIGH RISK [R02]", "IF Temp is High AND Humidity is Low AND Wind is High\n→ Fire Risk: HIGH (75%)  |  UAV Speed: NOMINAL (12 m/s)", C_ACCENT_ORANGE),
        ("ELEVATED CAUTION [R14]", "IF Temp is Moderate AND Humidity is Low AND Wind is Severe\n→ Fire Risk: HIGH (70%)  |  UAV Speed: NOMINAL (11 m/s)", C_ACCENT_CYAN),
        ("SAFE PATROL [R04]", "IF Temp is Low AND Humidity is High AND Wind is Calm\n→ Fire Risk: SAFE (10%)  |  UAV Speed: SPRINT (24 m/s)", C_ACCENT_GREEN),
    ]
    for i, (title, text, col) in enumerate(rule_samples):
        y_pos = Inches(2.8 + i * 1.0)
        rc = s5.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), y_pos, Inches(11.733), Inches(0.85))
        set_shape_flat(rc, C_CARD_BG, col, border_width=1.5)
        rtf = rc.text_frame
        rtf.margin_left = Inches(0.25)
        rtf.margin_top = Inches(0.12)
        p_t = rtf.paragraphs[0]
        p_t.text = title
        p_t.font.size = Pt(11)
        p_t.font.bold = True
        p_t.font.color.rgb = col
        p_b = rtf.add_paragraph()
        p_b.text = text
        p_b.font.size = Pt(10)
        p_b.font.color.rgb = C_TEXT_WHITE

    # --- SLIDE 6: NVIDIA Isaac Sim 3D Twin ---
    s6 = create_standard_slide("NVIDIA Isaac Sim 6.2.0 OpenUSD Stage", "3D DIGITAL TWIN")
    img_forest = ASSETS_DIR / "isaac_sim_forest_scene.png"
    img_drone = ASSETS_DIR / "isaac_sim_drone_closeup.png"
    if img_forest.exists():
        s6.shapes.add_picture(str(img_forest), Inches(0.8), Inches(1.5), width=Inches(5.7))
    if img_drone.exists():
        s6.shapes.add_picture(str(img_drone), Inches(6.8), Inches(1.5), width=Inches(5.7))

    specs = [
        ("200m x 200m", "48 Procedural Pine Trees"),
        ("3 Hotspots", "38°C, 78°C, 54°C Thermal Plumes"),
        ("Dual Cameras", "Chase Cam + Thermal Gimbal"),
        ("72.0 FPS", "RTX Real-Time 2.0 Ray Tracing"),
    ]
    for i, (title, sub) in enumerate(specs):
        bcard = s6.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8 + i * 2.95), Inches(5.4), Inches(2.8), Inches(1.5))
        set_shape_flat(bcard, C_CARD_BG, C_CARD_BORDER)
        btf = bcard.text_frame
        btf.margin_top = Inches(0.25)
        p1 = btf.paragraphs[0]
        p1.text = title
        p1.font.size = Pt(16)
        p1.font.bold = True
        p1.font.color.rgb = C_ACCENT_CYAN
        p1.alignment = PP_ALIGN.CENTER
        p2 = btf.add_paragraph()
        p2.text = sub
        p2.font.size = Pt(10)
        p2.font.color.rgb = C_TEXT_MUTED
        p2.alignment = PP_ALIGN.CENTER

    # --- SLIDE 7: Mission Telemetry & Flight Results ---
    s7 = create_standard_slide("Autonomous Mission Telemetry & Actuation", "FLIGHT RESULTS")
    img_telem = ASSETS_DIR / "mission_telemetry_dashboard.png"
    if img_telem.exists():
        s7.shapes.add_picture(str(img_telem), Inches(0.8), Inches(1.5), width=Inches(7.2))

    c7 = add_card(s7, Inches(8.2), Inches(1.5), Inches(4.333), Inches(5.4), "Flight Observations", C_ACCENT_GREEN)
    tf7 = c7.text_frame
    obs = [
        ("Transit Sprint (WP 1-3):", "Baseline 24°C, FRI = 12%. Drone flies at 22.5 m/s to cover terrain."),
        ("Hotspot Incursion (WP 5-7):", "Temp spikes to 78.4°C. FRI escalates to 92.6% (CRITICAL ALERT)."),
        ("Adaptive Loiter:", "Speed automatically drops to 6.5 m/s, dwelling over the heat core."),
        ("Post-Detection Sprint:", "Clears thermal plume and returns to 22 m/s patrol speed."),
    ]
    for title, desc in obs:
        p1 = tf7.add_paragraph()
        p1.text = title
        p1.font.size = Pt(12)
        p1.font.bold = True
        p1.font.color.rgb = C_TEXT_WHITE
        p2 = tf7.add_paragraph()
        p2.text = desc + "\n"
        p2.font.size = Pt(11)
        p2.font.color.rgb = C_TEXT_MUTED

    # --- SLIDE 8: Defuzzification Benchmark ---
    s8 = create_standard_slide("Defuzzification Benchmark: Centroid vs. MOM", "ANALYSIS")
    table_card = add_card(s8, Inches(0.8), Inches(1.5), Inches(11.733), Inches(2.4), "Performance Metrics Comparison", C_ACCENT_ORANGE)
    ttf = table_card.text_frame
    table_lines = [
        "Method               Avg Latency    Actuator Smoothness         Noise Robustness     Flight Suitability",
        "Centroid (COG)        0.884 ms      Exceptional (Continuous)     High                 SELECTED (Optimal)",
        "Bisector              0.912 ms      Good                         Moderate             Viable",
        "Mean of Max (MOM)     0.420 ms      Poor (Violent Step Jumps)    Low                  Unsafe for Drone",
    ]
    for i, line in enumerate(table_lines):
        p = ttf.add_paragraph()
        p.text = line
        p.font.size = Pt(11)
        p.font.bold = (i == 0 or i == 1)
        p.font.color.rgb = C_ACCENT_CYAN if i == 0 else (C_ACCENT_GREEN if i == 1 else C_TEXT_WHITE)

    c8_l = add_card(s8, Inches(0.8), Inches(4.2), Inches(5.7), Inches(2.7), "Why Centroid Was Selected", C_ACCENT_CYAN)
    tf8_l = c8_l.text_frame
    bullets8_l = [
        "Continuous Thrust: Produces smooth actuation without motor chatter.",
        "Noise Filtering: Weighted center averages out sensor fluctuations.",
        "Edge Feasible: 0.88 ms is well within the 50 ms UAV control budget.",
    ]
    for b in bullets8_l:
        p = tf8_l.add_paragraph()
        p.text = "• " + b
        p.font.size = Pt(11)
        p.font.color.rgb = C_TEXT_WHITE

    c8_r = add_card(s8, Inches(6.8), Inches(4.2), Inches(5.7), Inches(2.7), "The MOM Flaw in Aerial Robotics", C_ACCENT_ORANGE)
    tf8_r = c8_r.text_frame
    bullets8_r = [
        "Discontinuous Output: Jumping between membership peaks creates sudden velocity steps.",
        "Aerodynamic Instability: Step jumps induce motor torque shocks that destabilize small UAVs.",
    ]
    for b in bullets8_r:
        p = tf8_r.add_paragraph()
        p.text = "• " + b
        p.font.size = Pt(11)
        p.font.color.rgb = C_TEXT_WHITE

    # --- SLIDE 9: Real-World Edge Deployment ---
    s9 = create_standard_slide("Edge Hardware Deployment & UN SDGs", "FEASIBILITY")
    c9_l = add_card(s9, Inches(0.8), Inches(1.5), Inches(5.7), Inches(5.4), "NVIDIA Jetson Edge Architecture", C_ACCENT_CYAN)
    tf9_l = c9_l.text_frame
    specs9 = [
        ("Target Platform:", "NVIDIA Jetson Orin Nano (8 GB)"),
        ("Power Envelope:", "7 - 15 Watts (suitable for micro-UAV batteries)"),
        ("Control Loop Latency:", "0.88 ms inference consumes < 2% of 50 ms budget"),
        ("Sensor Payloads:", "FLIR Lepton 3.5 LWIR + Sensirion SHT40 probe"),
        ("Emergency Dispatch:", "LoRa telemetry transmits GPS hotspot to fire crew"),
    ]
    for title, desc in specs9:
        p1 = tf9_l.add_paragraph()
        p1.text = "• " + title
        p1.font.size = Pt(12)
        p1.font.bold = True
        p1.font.color.rgb = C_TEXT_WHITE
        p2 = tf9_l.add_paragraph()
        p2.text = "  " + desc + "\n"
        p2.font.size = Pt(11)
        p2.font.color.rgb = C_TEXT_MUTED

    c9_r = add_card(s9, Inches(6.8), Inches(1.5), Inches(5.7), Inches(5.4), "Sustainable Development Goals (SDGs)", C_ACCENT_GREEN)
    tf9_r = c9_r.text_frame
    sdg_items = [
        ("SDG 13: Climate Action (Target 13.1)", "Early thermal detection catches fires before runaway crown spread, preventing megatons of CO2 emissions."),
        ("SDG 15: Life on Land (Target 15.2)", "Protects pristine tropical and temperate forest reserves, safeguarding critical wildlife habitats."),
        ("Resource Optimization", "Directs firefighting teams to exact GPS coordinates, minimizing containment costs and water usage."),
    ]
    for title, desc in sdg_items:
        p1 = tf9_r.add_paragraph()
        p1.text = "• " + title
        p1.font.size = Pt(12)
        p1.font.bold = True
        p1.font.color.rgb = C_TEXT_WHITE
        p2 = tf9_r.add_paragraph()
        p2.text = "  " + desc + "\n"
        p2.font.size = Pt(11)
        p2.font.color.rgb = C_TEXT_MUTED

    # --- SLIDE 10: Conclusion & Future Work ---
    s10 = create_standard_slide("Conclusion & Future Horizons", "SUMMARY")
    c10_l = add_card(s10, Inches(0.8), Inches(1.5), Inches(5.7), Inches(5.4), "Key Project Achievements", C_ACCENT_CYAN)
    tf10_l = c10_l.text_frame
    achieve = [
        ("Mamdani Engine:", "Designed & verified 27-rule fuzzy system fusing 3 atmospheric inputs."),
        ("Isaac Sim 3D Twin:", "High-fidelity OpenUSD forest simulation running stably at 72 FPS."),
        ("Autonomous Speed Control:", "Validated dynamic 6.5 - 22.5 m/s speed modulation over hotspots."),
        ("Sub-Millisecond Speed:", "0.88 ms inference verified for micro-UAV edge deployment."),
    ]
    for title, desc in achieve:
        p1 = tf10_l.add_paragraph()
        p1.text = "✔ " + title
        p1.font.size = Pt(12)
        p1.font.bold = True
        p1.font.color.rgb = C_TEXT_WHITE
        p2 = tf10_l.add_paragraph()
        p2.text = "  " + desc + "\n"
        p2.font.size = Pt(11)
        p2.font.color.rgb = C_TEXT_MUTED

    c10_r = add_card(s10, Inches(6.8), Inches(1.5), Inches(5.7), Inches(5.4), "Future Research Horizons", C_ACCENT_ORANGE)
    tf10_r = c10_r.text_frame
    future = [
        ("Neuro-Fuzzy (ANFIS):", "Auto-tune membership functions using historical satellite wildfire burn data."),
        ("Multi-UAV Swarms:", "Deploy decentralized mesh patrol across multiple drones for large-area monitoring."),
        ("Physical Field Tests:", "Deploy algorithms onto DJI Matrice 300 / PX4 drone in controlled burn exercises."),
    ]
    for title, desc in future:
        p1 = tf10_r.add_paragraph()
        p1.text = "➜ " + title
        p1.font.size = Pt(12)
        p1.font.bold = True
        p1.font.color.rgb = C_TEXT_WHITE
        p2 = tf10_r.add_paragraph()
        p2.text = "  " + desc + "\n"
        p2.font.size = Pt(11)
        p2.font.color.rgb = C_TEXT_MUTED

    # --- SLIDE 11: Thank You & Q&A ---
    s11 = prs.slides.add_slide(blank_layout)
    bg11 = s11.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
    set_shape_flat(bg11, C_DARK_BG)

    qcard = s11.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.5), Inches(1.2), Inches(10.333), Inches(5.1))
    set_shape_flat(qcard, C_CARD_BG, C_CARD_BORDER)
    qtf = qcard.text_frame
    qtf.margin_top = Inches(0.8)

    qp0 = qtf.paragraphs[0]
    qp0.text = "THANK YOU!"
    qp0.alignment = PP_ALIGN.CENTER
    qp0.font.size = Pt(36)
    qp0.font.bold = True
    qp0.font.color.rgb = C_ACCENT_CYAN

    qp1 = qtf.add_paragraph()
    qp1.text = "Project Defense & Demonstration Q&A"
    qp1.alignment = PP_ALIGN.CENTER
    qp1.font.size = Pt(22)
    qp1.font.color.rgb = C_TEXT_WHITE

    qp2 = qtf.add_paragraph()
    qp2.text = "\nPang Wei Sheng  •  Roshan Sivakumar  •  Dinesswar Sathasivam  •  Yeoh Choon Hern"
    qp2.alignment = PP_ALIGN.CENTER
    qp2.font.size = Pt(13)
    qp2.font.color.rgb = C_TEXT_MUTED

    qp3 = qtf.add_paragraph()
    qp3.text = "Sunway University  •  CSC3034 Computational Intelligence  •  Dr. Tang Tiong Yew"
    qp3.alignment = PP_ALIGN.CENTER
    qp3.font.size = Pt(13)
    qp3.font.color.rgb = C_TEXT_MUTED

    qp4 = qtf.add_paragraph()
    qp4.text = "\nGitHub: https://github.com/123haiku/csc3034-fuzzy-wildfire-sim"
    qp4.alignment = PP_ALIGN.CENTER
    qp4.font.size = Pt(12)
    qp4.font.bold = True
    qp4.font.color.rgb = C_ACCENT_ORANGE

    pptx_path = PRESENTATION_DIR / "CSC3034_Presentation_Slides.pptx"
    prs.save(str(pptx_path))
    print(f"[Slides] Generated clean, uncluttered PowerPoint (.pptx): {pptx_path}")

    if ARTIFACT_DIR.exists():
        import shutil
        shutil.copy2(pptx_path, ARTIFACT_DIR / "CSC3034_Presentation_Slides.pptx")
        print("[Slides] Synced to artifact directory.")

    return pptx_path


if __name__ == "__main__":
    PRESENTATION_DIR.mkdir(parents=True, exist_ok=True)
    build_pptx()
