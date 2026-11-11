"""Builds the CSC3034 defence deck from scratch on an NVIDIA palette.

Design rules enforced here:
  * Palette is black / white / grey / #76B900 only. No cyan, no orange, no per-card hues.
  * Text never sits inside a shape. Every autoshape is a 1-3 pt rule, so nothing can be
    vertically centred in a box with dead space around it.
  * One grid: 0.75 in margins, content from y=1.75, footer at y=7.13.
  * Figures are the NVIDIA-palette rebuilds from scratch/nvidia_plots.py.

Slide-7 numbers come from an actual run of create_wildfire_stage.run_stage_patrol_simulation
(12 waypoints), not from hand-typed values.
"""

from __future__ import annotations

from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.oxml.ns import qn
from pptx.util import Inches, Pt

REPO = Path(__file__).resolve().parent.parent.parent
PRES = REPO / "docs" / "presentation"
ASSETS = PRES / "assets"
DST = PRES / "CSC3034_Presentation_Slides.pptx"   # canonical deliverable; v4 is the current generation

from deck_notes import NOTES  # same directory as this script

# ---------------------------------------------------------------- NVIDIA palette
BG = RGBColor(0x0A, 0x0A, 0x0A)       # canvas
INK = RGBColor(0xFF, 0xFF, 0xFF)      # primary text
DIM = RGBColor(0x8C, 0x8C, 0x8C)      # secondary text
RULE = RGBColor(0x1F, 0x1F, 0x1F)     # hairlines
GREEN = RGBColor(0x76, 0xB9, 0x00)    # NVIDIA green - the only accent
LIME = RGBColor(0xC6, 0xF2, 0x6A)     # rare emphasis highlight
FONT = "Arial"

L = 0.75                  # left margin
W = 11.833                # content width
CW = 5.62                 # one column
RX = 6.96                 # right column x
TOP = 1.75                # content top
FOOT = 7.13

prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)
BLANK = prs.slide_layouts[6]


# ------------------------------------------------------------------- primitives
def frame(slide) -> None:
    bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
    bg.fill.solid()
    bg.fill.fore_color.rgb = BG
    bg.line.fill.background()


def rule_h(slide, x, y, w, color=RULE, pt=0.9) -> None:
    sh = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(x), Inches(y), Inches(w), Pt(pt))
    sh.fill.solid()
    sh.fill.fore_color.rgb = color
    sh.line.fill.background()


def rule_v(slide, x, y, h, color=RULE, pt=0.9) -> None:
    sh = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(x), Inches(y), Pt(pt), Inches(h))
    sh.fill.solid()
    sh.fill.fore_color.rgb = color
    sh.line.fill.background()


def text(slide, x, y, w, h, paras, anchor=MSO_ANCHOR.TOP, align=PP_ALIGN.LEFT):
    """paras: list of (string, size, color, bold) or (string, size, color, bold, space_before)"""
    box = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = box.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = anchor
    tf.margin_left = 0
    tf.margin_right = 0
    tf.margin_top = 0
    tf.margin_bottom = 0
    for i, spec in enumerate(paras):
        s, size, color, bold = spec[0], spec[1], spec[2], spec[3]
        before = spec[4] if len(spec) > 4 else 0
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        if before:
            p.space_before = Pt(before)
        r = p.add_run()
        r.text = s
        r.font.name = FONT
        r.font.size = Pt(size)
        r.font.bold = bold
        r.font.color.rgb = color
    return box


def head(slide, eyebrow: str, title: str, page: int | None) -> None:
    text(slide, L, 0.52, W, 0.26, [(eyebrow.upper(), 9.5, GREEN, True)])
    text(slide, L, 0.80, W, 0.55, [(title, 26, INK, True)])
    rule_h(slide, L, 1.42, 0.85, GREEN, 3.0)
    if page is not None:
        text(slide, L, FOOT, 8.0, 0.22,
             [("CSC3034  ·  Computational Intelligence  ·  Autonomous UAV wildfire surveillance", 8.5, DIM, False)])
        text(slide, 11.6, FOOT, 0.98, 0.22, [(f"{page:02d}", 8.5, DIM, False)], align=PP_ALIGN.RIGHT)


def pairs(slide, x, y, w, items, lead_sz=12.5, body_sz=10.8, gap=0.30, lead_color=INK, fill_to=None):
    """Lead-in + body block, separated by a hairline. Returns bottom y.

    fill_to: extra air is distributed between the blocks so a short column still reaches
    the same baseline as the column beside it.
    """
    n = len(items)
    item_h, post = 0.89, 0.12
    if fill_to and n > 1:
        gap = max(0.22, (fill_to - y - n * (item_h + post)) / (n - 1))
    cy = y
    for i, (lead, body) in enumerate(items):
        text(slide, x, cy, w, 0.26, [(lead, lead_sz, lead_color, True)])
        text(slide, x, cy + 0.27, w, 0.62, [(body, body_sz, DIM, False)])
        cy += item_h
        rule_h(slide, x, cy + 0.02, w)
        cy += post + (gap if i < n - 1 else 0.0)
    return cy


def stats(slide, y, items, num_sz=30, label_sz=9.5):
    """Big number + small caption, separated by vertical hairlines. No boxes."""
    n = len(items)
    cell = (W - (n - 1) * 0.55) / n
    for i, (num, label) in enumerate(items):
        x = L + i * (cell + 0.55)
        text(slide, x, y, cell, 0.52, [(num, num_sz, GREEN, True)])
        text(slide, x, y + 0.54, cell, 0.5, [(label, label_sz, DIM, False)])
        if i:
            rule_v(slide, x - 0.28, y + 0.04, 1.12)


def pic(slide, path, x, y, w, caption=None, cap_sz=9.5, h=None):
    if h is not None:
        p = slide.shapes.add_picture(str(path), Inches(x), Inches(y), height=Inches(h))
    else:
        p = slide.shapes.add_picture(str(path), Inches(x), Inches(y), width=Inches(w))
    h = p.height / 914400
    w = p.width / 914400
    if caption:
        text(slide, x, y + h + 0.12, w, 0.28, [(caption, cap_sz, DIM, False)])
    return h


# ------------------------------------------------------------------------ 01
s = prs.slides.add_slide(BLANK)
frame(s)
rule_h(s, L, 1.38, 1.25, GREEN, 3.0)
text(s, L, 1.62, W, 0.26,
     [("SUNWAY UNIVERSITY  ·  SCHOOL OF MATHEMATICAL SCIENCES & COMPUTING", 9.5, GREEN, True)])
text(s, L, 1.96, 11.2, 1.55,
     [("Autonomous Wildfire Risk", 40, INK, True),
      ("Assessment & UAV Surveillance", 40, INK, True)])
text(s, L, 3.42, 10.6, 0.9,
     [("Mamdani fuzzy inference driving a four-probe UAV inside an NVIDIA Isaac Sim digital twin",
       15.5, DIM, False)])
text(s, L, 4.02, 10.6, 0.3,
     [("CSC3034 Computational Intelligence      Supervisor: Dr. Tang Tiong Yew", 10.5, DIM, False)])
rule_h(s, L, 4.55, W)

col_name, col_id, col_role = L, 3.85, 5.62
text(s, col_name, 4.70, 3.0, 0.24, [("NAME", 8.5, GREEN, True)])
text(s, col_id, 4.70, 1.6, 0.24, [("STUDENT ID", 8.5, GREEN, True)])
text(s, col_role, 4.70, 6.4, 0.24, [("ROLE", 8.5, GREEN, True)])

roster = [
    ("Yeoh Choon Hern", "23100795", "Project lead — coordination and integration"),
    ("Pang Wei Sheng", "24035115", "Fuzzy inference engine & simulation evaluation"),
    ("Roshan A/L Sivakumar", "23028285", "Technical report — defuzzification analysis"),
    ("Dinesswar A/L Sathasivam", "23096910", "Isaac Sim OpenUSD stage — sensor bridge"),
]
for i, (name, sid, role) in enumerate(roster):
    y = 5.03 + i * 0.50
    text(s, col_name, y, 3.0, 0.26, [(name, 12, INK, True)])
    text(s, col_id, y + 0.02, 1.6, 0.26, [(sid, 11, GREEN, False)])
    text(s, col_role, y + 0.02, 6.4, 0.26, [(role, 10.5, DIM, False)])
    rule_h(s, L, y + 0.40, W)

# ------------------------------------------------------------------------ 02
s = prs.slides.add_slide(BLANK)
frame(s)
head(s, "Background", "Why a threshold is the wrong tool", 2)
rule_v(s, 6.66, TOP, 5.15)
text(s, L, TOP, CW, 0.24, [("THE PROBLEM", 9.5, GREEN, True)])
text(s, RX, TOP, CW, 0.24, [("THE APPROACH", 9.5, GREEN, True)])

left = [
    ("A single threshold cannot see interaction.",
     "A 40 °C cut-off cannot separate 38 °C at 15 % humidity and 70 km/h wind from 42 °C in saturated still air. The first case is the dangerous one."),
    ("Spread is non-linear.",
     "Dry wind at moderate temperature ignites faster than a hot, humid afternoon, so a temperature-only trigger fires late."),
    ("The telemetry is noisy.",
     "Rotor vibration and turbulence corrupt raw readings, so a hard edge flickers between alarm states."),
]
right = [
    ("Continuous membership.",
     "Four overlapping sets per variable replace the cliff edge, so the output moves smoothly with the input."),
    ("Four-probe fusion.",
     "Temperature, relative humidity, wind speed and fuel dryness combine into one fire risk index."),
    ("The output flies the aircraft.",
     "Throttle scales from 20 % patrol to 90 % emergency, so the UAV closes its own loop above a hotspot."),
]
pairs(s, L, TOP + 0.36, CW, left, fill_to=6.02)
pairs(s, RX, TOP + 0.36, CW, right, fill_to=6.02)

# ------------------------------------------------------------------------ 03
s = prs.slides.add_slide(BLANK)
frame(s)
head(s, "System pipeline", "Sensing to actuation in five stages", 3)
stages = [
    ("01", "Synthetic sensing", "Four probes on the OpenUSD stage, sampled at 60 Hz."),
    ("02", "Fuzzification", "16 input sets, four per variable, triangular and trapezoidal."),
    ("03", "Fuzzy inference", "10 expert rules; min for AND, max for aggregation."),
    ("04", "Defuzzification", "Centroid of area; continuous output, 0.28 ms median per loop."),
    ("05", "Actuation and alert", "Throttle 20-90 %; alert 0-3 as a third fuzzy output."),
]
cell = (W - 4 * 0.36) / 5
for i, (num, title, body) in enumerate(stages):
    x = L + i * (cell + 0.36)
    text(s, x, TOP + 0.05, cell, 0.5, [(num, 24, GREEN, True)])
    text(s, x, TOP + 0.62, cell, 0.3, [(title, 13, INK, True)])
    text(s, x, TOP + 0.95, cell, 1.5, [(body, 10.5, DIM, False)])
    if i:
        rule_v(s, x - 0.18, TOP + 0.05, 2.6)
rule_h(s, L, 4.92, W)
stats(s, 5.12, [
    ("60 Hz", "sensor tick from the Isaac Sim stage"),
    ("0.28 ms", "median per loop, p99 1.42 ms"),
    ("0.6 %", "of the 50 ms control budget"),
])

# ------------------------------------------------------------------------ 04
s = prs.slides.add_slide(BLANK)
frame(s)
head(s, "Fuzzy engine", "Linguistic variables and membership functions", 4)
text(s, L, TOP, 5.0, 0.24, [("INPUTS", 9.5, GREEN, True)])
specs = [
    ("Temperature (T)", "0 - 50 °C   low · moderate · high · extreme"),
    ("Relative humidity (RH)", "0 - 100 %   very low · low · moderate · high"),
    ("Wind speed (WS)", "0 - 100 km/h   calm · moderate · high · severe"),
    ("Fuel dryness (FD)", "0 - 100 %   wet · moderate · dry · critical"),
]
y = TOP + 0.30
for name, detail in specs:
    text(s, L, y, 5.0, 0.24, [(name, 12, INK, True)])
    text(s, L, y + 0.24, 5.0, 0.24, [(detail, 10.5, DIM, False)])
    y += 0.52
    rule_h(s, L, y - 0.08, 5.0)
y += 0.14
text(s, L, y, 5.0, 0.24, [("OUTPUTS", 9.5, GREEN, True)])
y += 0.30
for name, detail in [
    ("Fire risk index (FRI)", "0 - 100   low · moderate · high · extreme"),
    ("Throttle urgency", "0 - 100 %   standard · accelerated · emergency"),
    ("Suppression alert", "0 - 3   advisory · watch · warning · evacuate"),
]:
    text(s, L, y, 5.0, 0.24, [(name, 12, INK, True)])
    text(s, L, y + 0.24, 5.0, 0.24, [(detail, 10.5, DIM, False)])
    y += 0.52
    rule_h(s, L, y - 0.08, 5.0)
text(s, L, y + 0.08, 5.0, 0.6,
     [("Trapezoids close the outermost sets, so readings past the sensor range saturate instead of running off the universe. Each rule fires one term in all three universes.", 10, DIM, False)])
pic(s, ASSETS / "membership_nvidia.png", 6.55, TOP + 0.02, 6.0, h=4.68,
    caption="Temperature and fuel dryness shown; humidity and wind use the same four-set template. "
            "Output 3 adds the alert consequent.")

# ------------------------------------------------------------------------ 05
s = prs.slides.add_slide(BLANK)
frame(s)
head(s, "Knowledge base", "Ten curated rules out of 256 combinations", 5)

hdr_y = TOP + 0.04
text(s, L, hdr_y, 1.5, 0.24, [("RULE", 8.5, GREEN, True)])
text(s, 2.10, hdr_y, 4.85, 0.24, [("ANTECEDENT", 8.5, GREEN, True)])
text(s, 6.95, hdr_y, 1.35, 0.24, [("FIRE RISK", 8.5, GREEN, True)], align=PP_ALIGN.RIGHT)
text(s, 8.45, hdr_y, 1.55, 0.24, [("THROTTLE", 8.5, GREEN, True)], align=PP_ALIGN.RIGHT)
text(s, 10.10, hdr_y, 2.45, 0.24, [("ALERT (0-3)", 8.5, GREEN, True)], align=PP_ALIGN.RIGHT)
rule_h(s, L, hdr_y + 0.28, W, RULE, 1.0)

rules = [
    ("R09 · R07", "Temperature extreme AND (fuel critical OR humidity very low)", "92", "90 %", "2.87"),
    ("R04", "Temperature moderate AND wind high AND fuel dry", "71", "60 %", "2.00"),
    ("R03", "Temperature moderate AND fuel moderate", "45", "20 %", "1.00"),
    ("R01 · R10", "Humidity high AND (fuel wet OR wind calm)", "20", "20 %", "1.00"),
]
y = hdr_y + 0.46
for tag, ante, fri, thr, alt in rules:
    text(s, L, y + 0.10, 1.5, 0.26, [(tag, 11, GREEN, True)])
    text(s, 2.10, y + 0.08, 4.85, 0.5, [(ante, 12, INK, False)])
    text(s, 6.95, y + 0.04, 1.35, 0.4, [(fri, 18, INK, True)], align=PP_ALIGN.RIGHT)
    text(s, 8.45, y + 0.08, 1.55, 0.4, [(thr, 16, DIM, True)], align=PP_ALIGN.RIGHT)
    text(s, 10.10, y + 0.08, 2.45, 0.4, [(alt, 16, GREEN, True)], align=PP_ALIGN.RIGHT)
    y += 0.78
    rule_h(s, L, y - 0.10, W)

text(s, L, y + 0.22, W, 0.9,
     [("4 inputs × 4 sets = 256 antecedent combinations, curated down to the 10 that are physically meaningful. ", 11, DIM, False),
      ("Mamdani: min for AND, max for aggregation, centroid for defuzzification.", 11, INK, False),
      ("Cost: 0.28 ms per loop on the workstation; each rule fires all three consequents.", 11, DIM, False)])

# ------------------------------------------------------------------------ 06
s = prs.slides.add_slide(BLANK)
frame(s)
head(s, "3D digital twin", "NVIDIA Isaac Sim 6.2.0 — procedural forest stage", 6)
h1 = pic(s, ASSETS / "isaac_view_01_forest.png", L, TOP + 0.05, 5.70,
         "65 m procedural forest: 48 pines, hotspot plumes, chase camera")
pic(s, ASSETS / "isaac_view_02_hotspot.png", 6.88, TOP + 0.05, 5.70,
    "UAV prim over hotspot 01 — probe readings feed the next inference tick")
rule_h(s, L, 5.42, W)
stats(s, 5.62, [
    ("65 × 65 m", "OpenUSD stage, procedurally generated"),
    ("3", "active hotspots, up to 44.5 °C core plumes"),
    ("2", "cameras: chase view and thermal gimbal"),
    ("67-72", "FPS in RTX Real-Time 2.0 at 1280 × 720"),
], num_sz=26)

# ------------------------------------------------------------------------ 07
s = prs.slides.add_slide(BLANK)
frame(s)
head(s, "Flight results", "Twelve waypoints, closed loop, no retuning", 7)
pic(s, ASSETS / "telemetry_nvidia.png", L, TOP + 0.10, 7.00)
text(s, 8.30, TOP, 4.28, 0.24, [("WHAT THE RUN SHOWS", 9.5, GREEN, True)])
obs = [
    ("Baseline, WP 00-01", "29.1 °C, RH 49.0 %. FRI 45.0 holds at WATCH, throttle 20.1 %, alert 1.000."),
    ("Hotspot entry, WP 03", "42.8 °C, RH 18.9 %, fuel 86.8 %. FRI 91.4, throttle 89.5 %, alert 2.826."),
    ("Second plume, WP 08", "42.9 °C, RH 18.7 %. FRI 91.4, alert 2.829 — same response, no retuning."),
    ("Recovery, WP 06", "28.2 °C, RH 46.4 %. FRI returns to 45.0, throttle 19.9 %, alert 1.000."),
]
y = TOP + 0.36
for lead, body in obs:
    text(s, 8.30, y, 4.28, 0.24, [(lead, 11.5, INK, True)])
    text(s, 8.30, y + 0.26, 4.28, 0.75, [(body, 10.2, DIM, False)])
    y += 1.14
text(s, 8.30, y - 0.06, 4.28, 0.5,
     [("Numbers are the printed output of run_stage_patrol_simulation(seed=0), reproducible from the repository.", 9, DIM, False)])

# ------------------------------------------------------------------------ 08
s = prs.slides.add_slide(BLANK)
frame(s)
head(s, "Design decision", "Why centroid, when all three are this cheap", 8)

cols = [2.50, 1.60, 2.95, 1.45, 2.55]
rows = [
    ("Method", "Critical FRI", "Actuator smoothness", "Noise", "Flight suitability"),
    ("Centroid (COG)", "92.2", "continuous", "high", "selected"),
    ("Bisector", "92.5", "good", "moderate", "viable"),
    ("Mean of max (MOM)", "95.1", "step jumps", "low", "unsafe"),
]
tbl_y = TOP + 0.10
shape = s.shapes.add_table(len(rows), 5, Inches(L), Inches(tbl_y), Inches(sum(cols)), Inches(0.52 * len(rows)))
table = shape.table
tblPr = table._tbl.tblPr
for el in tblPr.findall(qn("a:tableStyleId")):
    tblPr.remove(el)
sid = tblPr.makeelement(qn("a:tableStyleId"), {})
sid.text = "{2D5ABB26-0587-4C30-8999-92F81FD0307C}"
tblPr.append(sid)
table.first_row = True
table.horz_banding = False
for i, cw in enumerate(cols):
    table.columns[i].width = Inches(cw)
for r in table.rows:
    r.height = Inches(0.52)
for ri, row in enumerate(rows):
    for ci, val in enumerate(row):
        c = table.cell(ri, ci)
        c.fill.solid()
        c.fill.fore_color.rgb = BG
        c.margin_left = Inches(0.02)
        c.margin_right = Inches(0.06)
        c.margin_top = 0
        c.margin_bottom = 0
        c.vertical_anchor = MSO_ANCHOR.MIDDLE
        p = c.text_frame.paragraphs[0]
        p.alignment = PP_ALIGN.LEFT
        r_ = p.add_run()
        r_.text = val
        r_.font.name = FONT
        if ri == 0:
            r_.font.size = Pt(9)
            r_.font.bold = True
            r_.font.color.rgb = GREEN
        else:
            r_.font.size = Pt(11)
            r_.font.bold = ci == 0
            r_.font.color.rgb = INK if ci == 0 else DIM
            if ri == 1 and ci == 4:
                r_.font.color.rgb = GREEN
                r_.font.bold = True
for i in range(len(rows) + 1):
    rule_h(s, L, tbl_y + 0.52 * i, W, RULE, 1.0)

pairs(s, L, 4.62, 5.55, fill_to=6.40, items=[
    ("Continuity, not speed.",
     "Centroid integrates the whole aggregated area, so a small input change produces a small output change. On a 250 g airframe that is the difference between smooth thrust and torque steps."),
    ("All three are cheap.",
     "A full evaluation loop is 0.28 ms, so none of the methods is the bottleneck. They differ only in the 2.9-point gap MOM shows at the critical scenario."),
])
pairs(s, RX, 4.62, 5.55, fill_to=6.40, items=[
    ("MOM jumps between peaks.",
     "Mean of maxima returns the average of the aggregated set's maxima, so as the input crosses a boundary the output leaps to the next peak: 95.1 against 92.2."),
    ("Bisector is the compromise.",
     "Smooth and within 0.3 points of centroid on every scenario, but no better on the flight logs, so the simpler method wins."),
])

# ------------------------------------------------------------------------ 09
s = prs.slides.add_slide(BLANK)
frame(s)
head(s, "Feasibility", "It fits on the aircraft", 9)
rule_v(s, 6.66, TOP, 5.0)
text(s, L, TOP, CW, 0.24, [("EDGE STACK", 9.5, GREEN, True)])
text(s, RX, TOP, CW, 0.24, [("WHY IT MATTERS", 9.5, GREEN, True)])
pairs(s, L, TOP + 0.36, CW, [
    ("Jetson Orin Nano, 8 GB.", "7-15 W envelope, inside a micro-UAV battery budget."),
    ("0.28 ms inference.", "median per loop; 0.6 % of the 50 ms budget."),
    ("Sensors already proven.", "FLIR Lepton 3.5 LWIR for the plume, Sensirion SHT40 for temperature and humidity."),
    ("LoRa backhaul.", "Carries the GPS fix of a confirmed hotspot to the ground crew."),
], lead_sz=12, body_sz=10.5, fill_to=6.55)
pairs(s, RX, TOP + 0.36, CW, [
    ("SDG 13.1, climate action.", "Early thermal detection catches a fire before crown spread, which is where the emission saving is."),
    ("SDG 15.2, life on land.", "Protects forest reserves and the habitat inside them."),
    ("Operational value.", "Exact coordinates cut containment time, water use and crew exposure."),
    ("Offline by design.", "The decision survives link loss, which is exactly when the fire matters most."),
], lead_sz=12, body_sz=10.5, fill_to=6.55)

# ------------------------------------------------------------------------ 10
s = prs.slides.add_slide(BLANK)
frame(s)
head(s, "Conclusion", "Delivered, and what is next", 10)
rule_v(s, 6.66, TOP, 5.0)
text(s, L, TOP, CW, 0.24, [("DELIVERED", 9.5, GREEN, True)])
text(s, RX, TOP, CW, 0.24, [("NEXT", 9.5, GREEN, True)])
pairs(s, L, TOP + 0.36, CW, [
    ("Fuzzy engine.", "Four inputs, ten rules, verified against the report's test vectors."),
    ("Digital twin.", "65 m procedural forest holding 67-72 FPS in real-time ray tracing."),
    ("Closed-loop actuation.", "20 % to 90 % throttle demonstrated over a live hotspot."),
    ("Edge speed.", "0.28 ms median per loop, p99 1.42 ms; edge figure projected, not measured."),
], lead_sz=12, body_sz=10.5, fill_to=6.10)
pairs(s, RX, TOP + 0.36, CW, [
    ("ANFIS.", "Replace hand-tuned memberships with functions fitted to satellite burn history."),
    ("Multi-UAV mesh.", "Decentralised coverage for areas a single airframe cannot hold."),
    ("Field trials.", "PX4 and Matrice 300 under a controlled-burn permit."),
], lead_sz=12, body_sz=10.5, fill_to=6.10)
rule_h(s, L, 6.42, W)
text(s, L, 6.58, W, 0.4,
     [("Limitation, stated plainly: every result here is simulation-only, and the rule base is expert-tuned rather than learned.",
       11, DIM, False)])

# ------------------------------------------------------------------------ 11
s = prs.slides.add_slide(BLANK)
frame(s)
rule_h(s, L, 2.10, 1.25, GREEN, 3.0)
text(s, L, 2.36, W, 0.8, [("Thank you", 40, INK, True)])
text(s, L, 3.30, W, 0.4, [("Questions, then the live Isaac Sim run", 16, GREEN, False)])
rule_h(s, L, 3.96, W)
text(s, L, 4.16, W, 0.3,
     [("Pang Wei Sheng   ·   Roshan A/L Sivakumar   ·   Dinesswar A/L Sathasivam   ·   Yeoh Choon Hern", 11.5, INK, False)])
text(s, L, 4.54, W, 0.3,
     [("Sunway University   ·   CSC3034 Computational Intelligence   ·   Dr. Tang Tiong Yew", 10.5, DIM, False)])
text(s, L, 5.10, W, 0.3,
     [("github.com/123haiku/csc3034-fuzzy-wildfire-sim", 11, GREEN, False)])
text(s, L, 6.55, W, 0.3,
     [("Slides, figures and simulation output regenerate from the repository.", 9.5, DIM, False)])

# speaker notes (defence talking points, one block per slide)
for idx, text_ in NOTES.items():
    prs.slides[idx - 1].notes_slide.notes_text_frame.text = text_
print(f"[notes] {len(NOTES)}/11 slides")

prs.save(str(DST))
print(f"[saved] {DST}")
print(f"slides={len(prs.slides)}  size={prs.slide_width/914400:.2f}x{prs.slide_height/914400:.2f} in")
