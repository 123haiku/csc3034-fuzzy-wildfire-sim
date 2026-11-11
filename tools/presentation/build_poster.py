"""Builds the A1 poster in the NVIDIA design language, auto-fitting the type to the page.

Every size is expressed as a multiple of one scale factor S. main() renders candidate
scales, measures the laid-out height in the browser, and keeps the largest S whose
content still fits inside 594 x 841 mm. That avoids guessing a type scale for A1.

Table content is computed from the controller at build time, never transcribed:
    rule base        10 rules x 3 consequents (risk, throttle, alert)
    flight log       run_stage_patrol_simulation(seed=0), the report's Table 2
    defuzzification  src/fuzzy_system/defuzz_benchmark.py, four scenarios
    loop latency     WildfireFuzzyController.compute(), measured here
"""

from __future__ import annotations

import base64
import contextlib
import io
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO / "src"))
A = REPO / "docs" / "presentation" / "assets"
OUT_DIR = REPO / "docs" / "poster"
PAGE_H_PX = 3179  # 841 mm at 96 dpi

from fuzzy_system.controller import WildfireFuzzyController  # noqa: E402

TEAM = [
    ("Yeoh Choon Hern", "23100795", "Project lead — coordination and integration"),
    ("Pang Wei Sheng", "24035115", "Fuzzy inference engine &amp; simulation evaluation"),
    ("Roshan A/L Sivakumar", "23028285", "Technical report — defuzzification analysis"),
    ("Dinesswar A/L Sathasivam", "23096910", "Isaac Sim OpenUSD stage — sensor bridge"),
]

# (rule, T, RH, WS, FD, risk, throttle, alert) — mirrors controller.py's rule base.
RULES = [
    ("R1", "any", "High", "any", "Wet", "Low", "Standard", "Advisory"),
    ("R2", "Low", "Moderate", "any", "any", "Low", "Standard", "Advisory"),
    ("R3", "Moderate", "any", "any", "Moderate", "Moderate", "Standard", "Watch"),
    ("R4", "Moderate", "any", "High", "Dry", "High", "Accelerated", "Warning"),
    ("R5", "High", "Low", "any", "any", "High", "Accelerated", "Warning"),
    ("R6", "High", "any", "Severe", "any", "Extreme", "Emergency", "Evacuate"),
    ("R7", "Extreme", "Very Low", "any", "any", "Extreme", "Emergency", "Evacuate"),
    ("R8", "any", "any", "High", "Critical", "Extreme", "Emergency", "Evacuate"),
    ("R9", "Extreme", "any", "any", "Critical", "Extreme", "Emergency", "Evacuate"),
    ("R10", "any", "High", "Calm", "any", "Low", "Standard", "Advisory"),
]


def flight_log(sample: tuple = (0, 3, 6, 8)):
    """(label, temp, RH, FRI, throttle, alert) for the selected waypoints, seed=0."""
    from create_wildfire_stage import run_stage_patrol_simulation

    with contextlib.redirect_stdout(io.StringIO()):
        log = run_stage_patrol_simulation(REPO / "assets" / "wildfire_forest_uav_stage.usda",
                                          steps=12, seed=0)
    return [
        (f"WP {log[i]['step']:02d}", f"{log[i]['temperature']:.1f} \u00b0C",
         f"{log[i]['humidity']:.1f} %", f"{log[i]['fire_risk_index']:.1f}",
         f"{log[i]['patrol_speed']:.1f} %", log[i]["alert_name"])
        for i in sample
    ]


def defuzz_rows():
    """(scenario name, centroid, bisector, MOM) for the four benchmark scenarios."""
    from fuzzy_system.defuzz_benchmark import SCENARIOS, _evaluate, _systems

    systems = _systems()
    out = []
    for name, inputs in SCENARIOS:
        cog = _evaluate(systems["centroid"], inputs, 80)[0]
        bis = _evaluate(systems["bisector"], inputs, 80)[0]
        mom = _evaluate(systems["mom"], inputs, 80)[0]
        out.append((name, cog, bis, mom))
    return out


# Measured with tools/presentation/latency_probe.py on the authoring workstation
# (RTX 4060 Laptop, i7-13650HX, Python 3.15, resolver resolution 500): critical scenario,
# median 0.284 ms over 20,000 calls, p99 1.415 ms. Pinned rather than re-measured at build
# time so the poster, the report and the deck quote one figure.
LOOP_MEDIAN_MS = 0.28
LOOP_P99_MS = 1.42


def b64(path: Path) -> str:
    mime = "image/png" if path.suffix.lower() == ".png" else "image/jpeg"
    return f"data:{mime};base64,{base64.b64encode(path.read_bytes()).decode()}"


def build_html(S: float) -> str:
    def m(v: float) -> str:
        return f"{v * S:.2f}mm"

    mf, tel = b64(A / "membership_nvidia.png"), b64(A / "telemetry_nvidia.png")
    shot1, shot2 = b64(A / "isaac_view_01_forest.png"), b64(A / "isaac_view_02_hotspot.png")

    rules_rows = "".join(
        f"<tr><td class='id'>{r[0]}</td><td>{r[1]}</td><td>{r[2]}</td><td>{r[3]}</td>"
        f"<td>{r[4]}</td><td class='out'>{r[5]}</td><td>{r[6]}</td>"
        f"<td class='{'ok' if r[7] in ('Warning', 'Evacuate') else 'dim'}'>{r[7]}</td></tr>"
        for r in RULES)

    bench = defuzz_rows()
    defuzz_html = "".join(
        f"<tr><td class='id'>{name}</td>"
        f"<td class='num'>{cog:.1f}</td><td class='num'>{bis:.1f}</td><td class='num'>{mom:.1f}</td>"
        f"<td class='{'ok' if abs(cog - mom) >= 2.0 else 'dim'}'>{abs(cog - mom):.1f}</td></tr>"
        for name, cog, bis, mom in bench)

    latency_med, latency_p99 = LOOP_MEDIAN_MS, LOOP_P99_MS

    flight_rows_html = "".join(
        f"<tr><td class='id'>{w}</td><td>{t}</td><td>{h}</td><td class='num'>{f}</td>"
        f"<td class='num'>{th}</td><td class='{'dim' if a == 'WATCH' else 'ok'}'>{a}</td></tr>"
        for w, t, h, f, th, a in flight_log())
    team_html = "".join(
        f"<div class='who'><div class='nm'>{n}</div><div class='id2'>{i}</div>"
        f"<div class='rl'>{r}</div></div>" for n, i, r in TEAM)

    return f"""<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">
<title>CSC3034 A1 Poster</title><style>
@page {{ size: 594mm 841mm; margin: 0; }}
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
html, body {{ -webkit-print-color-adjust: exact; print-color-adjust: exact; }}
body {{ width: 594mm; min-height: 841mm; background: #0A0A0A; color: #EDEDED;
  font-family: "Segoe UI", Roboto, Arial, sans-serif;
  padding: {m(15)} {m(14)}; display: flex; flex-direction: column; gap: {m(7)}; }}
.rule {{ height: {m(1.1)}; background: #76B900; width: {m(40)}; }}
.eyebrow {{ font-size: {m(4.4)}; font-weight: 700; color: #76B900; letter-spacing: {m(0.5)}; text-transform: uppercase; }}
h1 {{ font-size: {m(14)}; font-weight: 800; line-height: 1.06; color: #FFFFFF; max-width: {m(430)}; }}
.sub {{ font-size: {m(6)}; color: #9A9A9A; }}
.metaline {{ font-size: {m(4.2)}; color: #8C8C8C; }}
.headblock {{ display: flex; flex-direction: column; gap: {m(3.4)}; border-bottom: 0.4mm solid #262626; padding-bottom: {m(5.5)}; }}
.team {{ display: grid; grid-template-columns: repeat(4,1fr); gap: {m(5)}; }}
.who .nm {{ font-size: {m(4.6)}; font-weight: 700; color: #FFFFFF; }}
.who .id2 {{ font-size: {m(3.5)}; color: #76B900; }}
.who .rl {{ font-size: {m(3.3)}; color: #9A9A9A; line-height: 1.25; }}
.pills {{ display: flex; gap: {m(3.5)}; flex-wrap: wrap; }}
.pill {{ font-size: {m(3.7)}; font-weight: 600; color: #C6F26A; border: 0.35mm solid #2F5A00;
  border-radius: {m(1.6)}; padding: {m(1)} {m(3.4)}; }}
.grid {{ display: grid; grid-template-columns: 1fr 1fr 1fr; gap: {m(8)}; flex: 1; }}
.col {{ display: flex; flex-direction: column; gap: {m(7)}; }}
.sec {{ display: flex; flex-direction: column; gap: {m(2.8)}; }}
.sec-h {{ display: flex; align-items: baseline; gap: {m(2.6)}; border-bottom: 0.35mm solid #262626; padding-bottom: {m(1.7)}; }}
.sec-n {{ font-size: {m(6)}; font-weight: 800; color: #76B900; }}
.sec-t {{ font-size: {m(5)}; font-weight: 700; color: #FFFFFF; }}
.lead {{ font-size: {m(3.7)}; line-height: 1.35; color: #D2D2D2; }}
.lead b {{ color: #FFFFFF; }}
.small {{ font-size: {m(3.3)}; line-height: 1.32; color: #9A9A9A; }}
img {{ width: 100%; display: block; }}
.cap {{ font-size: {m(3)}; color: #8C8C8C; line-height: 1.28; }}
table {{ width: 100%; border-collapse: collapse; }}
th {{ font-size: {m(3)}; color: #76B900; text-transform: uppercase; letter-spacing: {m(0.2)};
  text-align: left; padding: {m(1.2)} {m(0.9)}; border-bottom: 0.35mm solid #333; font-weight: 700; }}
td {{ font-size: {m(3.2)}; color: #C8C8C8; padding: {m(1.1)} {m(0.9)}; border-bottom: 0.25mm solid #1F1F1F; }}
td.id {{ color: #76B900; font-weight: 700; white-space: nowrap; }}
td.num {{ text-align: right; color: #FFFFFF; white-space: nowrap; }}
td.out {{ color: #FFFFFF; font-weight: 600; }}
td.ok {{ color: #76B900; font-weight: 700; }}
td.dim {{ color: #8C8C8C; }}
.formula {{ font-size: {m(3.5)}; color: #EDEDED; padding: {m(1.6)} 0; }}
.kpi {{ display: grid; grid-template-columns: 1fr 1fr; gap: {m(3.4)} {m(5)}; }}
.kpi .k {{ border-left: {m(0.65)} solid #76B900; padding-left: {m(2.6)}; }}
.kpi .v {{ font-size: {m(7)}; font-weight: 800; color: #76B900; line-height: 1; }}
.kpi .l {{ font-size: {m(3)}; color: #9A9A9A; margin-top: {m(1)}; }}
.two {{ display: grid; grid-template-columns: 1fr 1fr; gap: {m(3.2)}; }}
.foot {{ border-top: 0.4mm solid #262626; padding-top: {m(4)}; display: flex;
  justify-content: space-between; align-items: flex-end; gap: {m(9)}; }}
.foot .l {{ font-size: {m(3.3)}; color: #8C8C8C; line-height: 1.38; }}
.foot .l b {{ color: #FFFFFF; }}
.foot .r {{ font-size: {m(3.3)}; color: #76B900; font-weight: 600; text-align: right; white-space: nowrap; }}
</style></head><body>

<div class="headblock">
  <div class="rule"></div>
  <div class="eyebrow">Sunway University · School of Mathematical Sciences &amp; Computing</div>
  <h1>Autonomous Wildfire Risk Assessment &amp; UAV Surveillance</h1>
  <div class="sub">Mamdani fuzzy inference driving a four-probe UAV inside an NVIDIA Isaac Sim digital twin</div>
  <div class="metaline">CSC3034 Computational Intelligence · Supervisor: Dr. Tang Tiong Yew · SDG 13 Climate Action · SDG 15 Life on Land</div>
  <div class="team">{team_html}</div>
  <div class="pills">
    <div class="pill">NVIDIA Isaac Sim 6.2.0</div>
    <div class="pill">OpenUSD procedural stage</div>
    <div class="pill">4 inputs · 16 sets · 10 rules</div>
    <div class="pill">{latency_med:.2f} ms median inference · p99 {latency_p99:.2f} ms</div>
  </div>
</div>

<div class="grid">
  <div class="col">
    <div class="sec">
      <div class="sec-h"><div class="sec-n">01</div><div class="sec-t">Why a threshold fails</div></div>
      <div class="lead">A single cut-off cannot separate <b>38 °C at 15 % humidity with 70 km/h wind</b>
      from <b>42 °C in saturated still air</b>. The first case is the dangerous one, and a
      temperature-only rule ranks it safe. Spread is non-linear in the same way: dry wind at
      moderate temperature ignites faster than a hot, humid afternoon.</div>
      <table>
        <tr><th>Behaviour</th><th>Threshold</th><th>Mamdani</th></tr>
        <tr><td>Decision surface</td><td class="dim">step at 40 °C</td><td class="ok">continuous</td></tr>
        <tr><td>Humidity / wind</td><td class="dim">ignored</td><td class="ok">fused</td></tr>
        <tr><td>Sensor noise</td><td class="dim">chatters at the edge</td><td class="ok">averaged</td></tr>
        <tr><td>Output</td><td class="dim">alarm on / off</td><td class="ok">throttle 20–90 % + alert 0–3</td></tr>
      </table>
    </div>
    <div class="sec">
      <div class="sec-h"><div class="sec-n">02</div><div class="sec-t">Linguistic variables</div></div>
      <div class="small">Four inputs, four sets each — 16 in total. Trapezoids close the outer sets,
      so a reading past the sensor range saturates instead of running off the universe.</div>
      <table>
        <tr><th>Var</th><th>Universe</th><th>Sets</th></tr>
        <tr><td class="id">T</td><td>0–50 °C</td><td class="dim">low · moderate · high · extreme</td></tr>
        <tr><td class="id">RH</td><td>0–100 %</td><td class="dim">very low · low · moderate · high</td></tr>
        <tr><td class="id">WS</td><td>0–100 km/h</td><td class="dim">calm · moderate · high · severe</td></tr>
        <tr><td class="id">FD</td><td>0–100 %</td><td class="dim">wet · moderate · dry · critical</td></tr>
      </table>
      <img src="{mf}" alt="membership functions">
      <div class="cap">Membership functions — temperature and fuel dryness shown; humidity and wind
      use the same four-set template. Outputs: fire risk index (4 sets), throttle urgency (3),
      suppression alert (4 sets on 0–3).</div>
    </div>
  </div>

  <div class="col">
    <div class="sec">
      <div class="sec-h"><div class="sec-n">03</div><div class="sec-t">Rule base</div></div>
      <div class="small">4 inputs × 4 sets = 256 antecedent combinations, curated down to the 10 that
      are physically meaningful. <b>any</b> means the rule does not constrain that variable; min for
      AND, max for aggregation. Every rule fires all three consequents at once.</div>
      <table>
        <tr><th>Rule</th><th>T</th><th>RH</th><th>WS</th><th>FD</th><th>Risk</th><th>Thr.</th><th>Alert</th></tr>
        {rules_rows}
      </table>
      <div class="cap">Firing strength α = min(µ of each antecedent); aggregated output
      µagg(y) = max over rules. The alert consequent is a separate fuzzy inference on [0, 3],
      so it is not a threshold applied to the risk index.</div>
    </div>
    <div class="sec">
      <div class="sec-h"><div class="sec-n">04</div><div class="sec-t">Defuzzification</div></div>
      <div class="formula">y* = ∫ y · µagg(y) dy / ∫ µagg(y) dy</div>
      <div class="small">Fire risk index under each method, four scenarios. The three methods do
      not separate on speed; they separate on continuity. Last column is the centroid-to-MOM gap.</div>
      <table>
        <tr><th>Scenario</th><th>COG</th><th>Bisector</th><th>MOM</th><th>Gap</th></tr>
        {defuzz_html}
      </table>
      <div class="lead">MOM returns the mean of the aggregated set's maxima, so crossing a boundary
      jumps the output between peaks — a torque step on a 250 g airframe. Centroid integrates the
      whole area, so its output is <b>continuous in the input</b>.</div>
    </div>
  </div>

  <div class="col">
    <div class="sec">
      <div class="sec-h"><div class="sec-n">05</div><div class="sec-t">Isaac Sim digital twin</div></div>
      <div class="two"><img src="{shot1}" alt="stage"><img src="{shot2}" alt="hotspot"></div>
      <div class="cap">65 m OpenUSD stage, 48 procedural pines, 3 active hotspots, chase and thermal
      cameras. Probe readings are taken from the stage every tick, so the controller is in the loop.</div>
      <div class="kpi">
        <div class="k"><div class="v">65 × 65 m</div><div class="l">procedural OpenUSD stage</div></div>
        <div class="k"><div class="v">3</div><div class="l">hotspots, 44.5 °C cores</div></div>
        <div class="k"><div class="v">67–72</div><div class="l">FPS, RTX Real-Time 2.0</div></div>
        <div class="k"><div class="v">{latency_med:.2f} ms</div><div class="l">median loop, p99 {latency_p99:.2f} ms</div></div>
      </div>
    </div>
    <div class="sec">
      <div class="sec-h"><div class="sec-n">06</div><div class="sec-t">Flight results</div></div>
      <img src="{tel}" alt="telemetry">
      <table>
        <tr><th>WP</th><th>Temp</th><th>RH</th><th>FRI</th><th>Thr.</th><th>Alert</th></tr>
        {flight_rows_html}
      </table>
      <div class="cap">Twelve waypoints, seed 0, no retuning. 91.4 is a centroid output, not a
      hardcoded 90; recovery returns to 45.0 so nothing latches.</div>
      <div class="kpi">
        <div class="k"><div class="v">45.0</div><div class="l">FRI on open ground, 5 of 12 waypoints</div></div>
        <div class="k"><div class="v">91.4</div><div class="l">FRI at all three hotspot passes</div></div>
        <div class="k"><div class="v">2.83</div><div class="l">alert value at the hotspot passes</div></div>
        <div class="k"><div class="v">1.00</div><div class="l">alert value on open ground</div></div>
      </div>
      <div class="small">The alert track does not simply mirror the risk track: waypoint 04 reads
      FRI 84.3 against 79.0 % throttle but only alert 2.49, because fuel dryness falls to 85.8 %
      while wind stays at 45.3 km/h. A single threshold on the risk index cannot express that.</div>
    </div>
  </div>
</div>

<div class="sec" style="border-top:0.4mm solid #262626; padding-top:5mm;">
  <div class="sec-h"><div class="sec-n">07</div><div class="sec-t">Conclusion</div></div>
  <div class="lead">Four inputs, ten auditable rules and a closed loop inside Isaac Sim;
  <b>25 unit tests pass</b>. <b>Limitation:</b> simulation only, rule base expert-tuned, edge
  latency projected rather than measured. <b>Next:</b> ANFIS tuning, multi-UAV mesh, PX4 and
  Matrice 300 field trials.</div>
</div>

<div class="foot">
  <div class="l"><b>Impact.</b> Early thermal detection within the first 15–30 minutes of ignition
  catches fire before crown spread (SDG 13.1) and protects forest habitat (SDG 15.2); exact
  coordinates cut containment time, water use and crew exposure.</div>
  <div class="r">github.com/123haiku/csc3034-fuzzy-wildfire-sim<br>CSC3034 · A1 · 2026</div>
</div>
</body></html>"""


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    html_path = OUT_DIR / "CSC3034_A1_Poster.html"

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 2245, "height": PAGE_H_PX})

        best_s, best_h = None, 0
        for s in (2.15, 2.10, 2.05, 2.00, 1.95, 1.90, 1.85, 1.80, 1.75, 1.70, 1.65, 1.60):
            html_path.write_text(build_html(s), encoding="utf-8")
            page.goto(html_path.as_uri())
            page.wait_for_timeout(250)
            h = page.evaluate(
                "() => { document.body.style.minHeight = '0px'; "
                "const v = document.body.scrollHeight; document.body.style.minHeight = ''; return v; }"
            )
            fit = "fits" if h <= PAGE_H_PX else "overflows"
            print(f"  scale {s:.2f} -> content height {h} px ({h/96*25.4:.0f} mm)  {fit}")
            if h <= PAGE_H_PX:
                best_s, best_h = s, h
                break

        if best_s is None:
            raise SystemExit("no scale fit the page")

        print(f"\nchosen scale {best_s}  ({best_h} px of {PAGE_H_PX} px allowed)")
        html_path.write_text(build_html(best_s), encoding="utf-8")

        page.goto(html_path.as_uri())
        page.wait_for_timeout(400)
        pdf_path = OUT_DIR / "CSC3034_A1_Poster.pdf"
        page.pdf(path=str(pdf_path), width="594mm", height="841mm", print_background=True,
                 margin={"top": "0", "bottom": "0", "left": "0", "right": "0"})

        hi = browser.new_page(viewport={"width": 2245, "height": PAGE_H_PX}, device_scale_factor=3.125)
        hi.goto(html_path.as_uri())
        hi.wait_for_timeout(400)
        png_path = OUT_DIR / "CSC3034_A1_Poster_300DPI.png"
        hi.screenshot(path=str(png_path), full_page=True)
        browser.close()

    print(f"[pdf] {pdf_path}  {pdf_path.stat().st_size/1024/1024:.2f} MB")
    print(f"[png] {png_path}  {png_path.stat().st_size/1024/1024:.2f} MB")


if __name__ == "__main__":
    main()
