"""Generates an interactive 16:9 HTML slide deck and exports a publication-grade PDF slide deck."""

from __future__ import annotations

import base64
from pathlib import Path
from playwright.sync_api import sync_playwright

REPO_ROOT = Path(__file__).resolve().parent.parent
PRESENTATION_DIR = REPO_ROOT / "docs" / "presentation"
ASSETS_DIR = REPO_ROOT / "docs" / "poster" / "assets"
ARTIFACT_DIR = Path(r"C:\Users\pangw\.gemini\antigravity\brain\3ed287fb-9045-4894-b2e3-ae5c7c992ba9")


def to_base64_data_uri(path: Path) -> str:
    if not path.exists():
        return ""
    mime = "image/png" if path.suffix.lower() == ".png" else "image/jpeg"
    encoded = base64.b64encode(path.read_bytes()).decode("utf-8")
    return f"data:{mime};base64,{encoded}"


def build_slides_html_and_pdf():
    print("[Slides] Encoding image assets to base64 ...")
    img_forest = to_base64_data_uri(ASSETS_DIR / "isaac_sim_forest_scene.png")
    img_drone = to_base64_data_uri(ASSETS_DIR / "isaac_sim_drone_closeup.png")
    img_mf = to_base64_data_uri(ASSETS_DIR / "membership_functions.png")
    img_telem = to_base64_data_uri(ASSETS_DIR / "mission_telemetry_dashboard.png")

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>CSC3034 Presentation Slides — Autonomous Wildfire Fuzzy Surveillance</title>
<style>
  @page {{
    size: 1920px 1080px;
    margin: 0;
  }}
  * {{
    box-sizing: border-box;
    margin: 0;
    padding: 0;
  }}
  body {{
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
    background-color: #0B0F19;
    color: #F8FAFC;
    margin: 0;
    padding: 0;
    -webkit-print-color-adjust: exact;
    print-color-adjust: exact;
  }}
  .slide {{
    width: 1920px;
    height: 1080px;
    padding: 60px 80px;
    page-break-after: always;
    display: flex;
    flex-direction: column;
    justify-content: flex-start;
    background: radial-gradient(circle at top right, #1E1B4B 0%, #0F172A 40%, #090D16 100%);
    position: relative;
    overflow: hidden;
  }}
  
  /* Header Bar */
  .slide-header {{
    background: #1E293B;
    border: 2px solid #334155;
    border-radius: 16px;
    padding: 18px 30px;
    margin-bottom: 40px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.4);
  }}
  .header-left {{
    display: flex;
    flex-direction: column;
    gap: 4px;
  }}
  .badge-cat {{
    font-size: 14px;
    font-weight: 800;
    letter-spacing: 2px;
    color: #38BDF8;
    text-transform: uppercase;
  }}
  .slide-title {{
    font-size: 32px;
    font-weight: 800;
    color: #FFFFFF;
  }}
  .badge-course {{
    background: #FF5722;
    color: #FFFFFF;
    font-size: 14px;
    font-weight: 700;
    padding: 6px 16px;
    border-radius: 8px;
    letter-spacing: 1px;
  }}

  /* Content Cards */
  .content-grid-2 {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 36px;
    flex: 1;
  }}
  .content-grid-3 {{
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 28px;
    flex: 1;
  }}
  .content-grid-5 {{
    display: grid;
    grid-template-columns: repeat(5, 1fr);
    gap: 20px;
    flex: 1;
  }}
  .card {{
    background: #1E293B;
    border: 1px solid #334155;
    border-radius: 16px;
    padding: 28px 32px;
    display: flex;
    flex-direction: column;
    box-shadow: 0 10px 20px -5px rgba(0, 0, 0, 0.3);
  }}
  .card-title {{
    font-size: 22px;
    font-weight: 700;
    margin-bottom: 20px;
    display: flex;
    align-items: center;
    gap: 10px;
  }}
  .card-title.cyan {{ color: #38BDF8; }}
  .card-title.orange {{ color: #FF5722; }}
  .card-title.green {{ color: #22C55E; }}
  
  ul.styled-list {{
    list-style: none;
    display: flex;
    flex-direction: column;
    gap: 16px;
  }}
  ul.styled-list li {{
    position: relative;
    padding-left: 28px;
    font-size: 18px;
    line-height: 1.5;
    color: #CBD5E1;
  }}
  ul.styled-list li::before {{
    content: "■";
    position: absolute;
    left: 0;
    color: #38BDF8;
    font-size: 14px;
    top: 2px;
  }}
  ul.styled-list li strong {{
    color: #FFFFFF;
  }}

  /* Title Slide Specifics */
  .title-hero {{
    background: linear-gradient(135deg, #1E293B 0%, #0F172A 60%, #1E1B4B 100%);
    border: 2px solid #334155;
    border-radius: 20px;
    padding: 45px 50px;
    box-shadow: 0 20px 40px -10px rgba(0, 0, 0, 0.6);
    margin-bottom: 40px;
  }}
  .inst-header {{
    font-size: 18px;
    font-weight: 800;
    color: #38BDF8;
    letter-spacing: 2px;
    margin-bottom: 12px;
  }}
  .main-h1 {{
    font-size: 46px;
    font-weight: 900;
    color: #FFFFFF;
    line-height: 1.2;
    margin-bottom: 14px;
  }}
  .sub-h2 {{
    font-size: 24px;
    color: #FF5722;
    font-weight: 600;
    margin-bottom: 16px;
  }}
  .meta-p {{
    font-size: 17px;
    color: #94A3B8;
  }}
  .roster-grid {{
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 24px;
  }}
  .member-card {{
    background: #1E293B;
    border: 1px solid #334155;
    border-radius: 16px;
    padding: 24px;
    border-top: 4px solid #38BDF8;
  }}
  .member-name {{
    font-size: 20px;
    font-weight: 700;
    color: #FFFFFF;
    margin-bottom: 6px;
  }}
  .member-id {{
    font-size: 15px;
    font-weight: 700;
    color: #38BDF8;
    margin-bottom: 10px;
  }}
  .member-role {{
    font-size: 14px;
    color: #94A3B8;
    line-height: 1.4;
  }}

  /* Images */
  .slide-img {{
    width: 100%;
    border-radius: 12px;
    border: 1px solid #334155;
    object-fit: cover;
  }}
  .table-clean {{
    width: 100%;
    border-collapse: collapse;
    margin-top: 10px;
  }}
  .table-clean th {{
    background: #0F172A;
    color: #38BDF8;
    font-weight: 700;
    text-align: left;
    padding: 12px 16px;
    font-size: 16px;
    border-bottom: 2px solid #334155;
  }}
  .table-clean td {{
    padding: 12px 16px;
    font-size: 16px;
    color: #E2E8F0;
    border-bottom: 1px solid #334155;
  }}
</style>
</head>
<body>

  <!-- SLIDE 1: Title Slide -->
  <div class="slide">
    <div class="title-hero">
      <div class="inst-header">SUNWAY UNIVERSITY &bull; SCHOOL OF MATHEMATICAL SCIENCES &amp; COMPUTING</div>
      <div class="main-h1">Autonomous Wildfire Risk Assessment &amp; UAV Surveillance Dispatch</div>
      <div class="sub-h2">Mamdani Fuzzy Logic Inference Interfaced with NVIDIA Isaac Sim Digital Twin</div>
      <div class="meta-p">CSC3034 Computational Intelligence &bull; Project Supervisor: <strong>Dr. Tang Tiong Yew</strong></div>
    </div>
    <div class="roster-grid">
      <div class="member-card">
        <div class="member-name">Pang Wei Sheng</div>
        <div class="member-id">ID: 24035115</div>
        <div class="member-role">Project Lead, Fuzzy Engine Architecture &amp; USD Stage Design</div>
      </div>
      <div class="member-card">
        <div class="member-name">Roshan A/L Sivakumar</div>
        <div class="member-id">ID: 23028285</div>
        <div class="member-role">Technical Report Writing &amp; Defuzzification Benchmark Analysis</div>
      </div>
      <div class="member-card">
        <div class="member-name">Dinesswar A/L Sathasivam</div>
        <div class="member-id">ID: 23096910</div>
        <div class="member-role">Isaac Sim 3D Scene Assets &amp; Synthetic Sensor Bridge</div>
      </div>
      <div class="member-card">
        <div class="member-name">Yeoh Choon Hern</div>
        <div class="member-id">ID: 23100795</div>
        <div class="member-role">Simulation Evaluation, Benchmark Scenarios &amp; A1 Poster</div>
      </div>
    </div>
  </div>

  <!-- SLIDE 2: Problem Statement -->
  <div class="slide">
    <div class="slide-header">
      <div class="header-left">
        <span class="badge-cat">BACKGROUND &amp; MOTIVATION</span>
        <span class="slide-title">The Wildfire Challenge &amp; Sensor Noise</span>
      </div>
      <span class="badge-course">CSC3034</span>
    </div>
    <div class="content-grid-2">
      <div class="card">
        <div class="card-title orange">Limitations of Conventional Systems</div>
        <ul class="styled-list">
          <li><strong>Climate Amplification:</strong> Megafires are rising in intensity and speed, demanding autonomous aerial detection (UN SDGs 13 &amp; 15).</li>
          <li><strong>Binary Alarm Failures:</strong> Simple thresholds (e.g. <code>T &gt; 40&deg;C</code>) cause false alarms during humid heat and miss hazards during dry, windy conditions.</li>
          <li><strong>Non-Linear Dynamics:</strong> Fire spread is governed by interconnected atmospheric variables: heat, desiccated fuel, and turbulent wind shear.</li>
          <li><strong>Turbulence &amp; Sensor Noise:</strong> Low-cost drone sensors exhibit drift and electromagnetic jitter in harsh forest terrain.</li>
        </ul>
      </div>
      <div class="card">
        <div class="card-title cyan">Proposed Soft-Computing Solution</div>
        <ul class="styled-list">
          <li><strong>Mamdani Fuzzy Logic:</strong> Implements continuous, robust reasoning under sensor uncertainty with human-interpretable linguistic rules.</li>
          <li><strong>Multi-Sensor Fusion:</strong> Fuses Ambient Temperature, Relative Humidity, and Wind Speed into a normalized <strong>Fire Risk Index (FRI)</strong>.</li>
          <li><strong>Closed-Loop Drone Modulation:</strong> Automatically throttles UAV flight speed (6.5 to 22.5 m/s) to maximize surveillance dwell time over hotspots.</li>
          <li><strong>NVIDIA Isaac Sim Twin:</strong> Physics-accurate OpenUSD simulation enables safe, zero-risk validation before real-world flight.</li>
        </ul>
      </div>
    </div>
  </div>

  <!-- SLIDE 3: System Pipeline -->
  <div class="slide">
    <div class="slide-header">
      <div class="header-left">
        <span class="badge-cat">METHODOLOGY &amp; WORKFLOW</span>
        <span class="slide-title">End-to-End Autonomous Surveillance Pipeline</span>
      </div>
      <span class="badge-course">CSC3034</span>
    </div>
    <div class="content-grid-5">
      <div class="card" style="border-top: 4px solid #38BDF8;">
        <div class="card-title cyan" style="font-size: 18px;">1. Sensing</div>
        <p style="color: #94A3B8; font-size: 15px; line-height: 1.5;">UAV synthetic thermal and atmospheric probes ingest <em>T</em>, <em>RH</em>, and <em>WS</em> at 60 Hz from Isaac Sim.</p>
      </div>
      <div class="card" style="border-top: 4px solid #38BDF8;">
        <div class="card-title cyan" style="font-size: 18px;">2. Fuzzification</div>
        <p style="color: #94A3B8; font-size: 15px; line-height: 1.5;">Converts crisp telemetry into membership degrees across 4 linguistic sets per input.</p>
      </div>
      <div class="card" style="border-top: 4px solid #FF5722;">
        <div class="card-title orange" style="font-size: 18px;">3. Inference</div>
        <p style="color: #94A3B8; font-size: 15px; line-height: 1.5;">27 Mamdani min-max rules compute aggregated fuzzy consequence surfaces.</p>
      </div>
      <div class="card" style="border-top: 4px solid #22C55E;">
        <div class="card-title green" style="font-size: 18px;">4. Defuzzification</div>
        <p style="color: #94A3B8; font-size: 15px; line-height: 1.5;">Centroid calculation produces crisp Fire Risk Index (0-100%) and Patrol Speed (5-25 m/s).</p>
      </div>
      <div class="card" style="border-top: 4px solid #22C55E;">
        <div class="card-title green" style="font-size: 18px;">5. Actuation</div>
        <p style="color: #94A3B8; font-size: 15px; line-height: 1.5;">USD attributes synchronize UAV flight keyframes and dispatch instant ground alerts.</p>
      </div>
    </div>
  </div>

  <!-- SLIDE 4: Fuzzy Membership Functions -->
  <div class="slide">
    <div class="slide-header">
      <div class="header-left">
        <span class="badge-cat">FUZZY ENGINE SPECIFICATION</span>
        <span class="slide-title">Linguistic Variables &amp; Membership Functions</span>
      </div>
      <span class="badge-course">CSC3034</span>
    </div>
    <div class="content-grid-2">
      <div class="card">
        <div class="card-title cyan">Universes of Discourse</div>
        <ul class="styled-list" style="font-size: 16px;">
          <li><strong>Temperature (T):</strong> [0, 50]&deg;C &bull; <em>Low, Moderate, High, Extreme</em></li>
          <li><strong>Relative Humidity (RH):</strong> [0, 100]% &bull; <em>High, Moderate, Low, Very Low</em></li>
          <li><strong>Wind Speed (WS):</strong> [0, 80] km/h &bull; <em>Calm, Moderate, High, Severe</em></li>
          <li><strong>Fire Risk Index (FRI):</strong> [0, 100]% &bull; <em>Safe, Caution, High, Critical</em></li>
          <li><strong>Patrol Urgency Speed:</strong> [5, 25] m/s &bull; <em>Loiter, Nominal, Fast, Sprint</em></li>
        </ul>
        <p style="color: #94A3B8; font-size: 15px; margin-top: 20px;">
          <strong>Design Principle:</strong> Trapezoidal functions for boundary domains (e.g. Extreme heat &gt; 45&deg;C) guarantee full saturation, while triangular functions handle transitional regions.
        </p>
      </div>
      <div>
        <img src="{img_mf}" class="slide-img" style="height: 100%; max-height: 700px; object-fit: contain; background: #0F172A; padding: 10px;">
      </div>
    </div>
  </div>

  <!-- SLIDE 5: 3D Isaac Sim Stage -->
  <div class="slide">
    <div class="slide-header">
      <div class="header-left">
        <span class="badge-cat">3D DIGITAL TWIN</span>
        <span class="slide-title">NVIDIA Isaac Sim 6.2.0 OpenUSD Environment</span>
      </div>
      <span class="badge-course">CSC3034</span>
    </div>
    <div class="content-grid-2">
      <div style="display: flex; flex-direction: column; gap: 20px;">
        <img src="{img_forest}" class="slide-img" style="height: 340px; object-fit: cover;">
        <img src="{img_drone}" class="slide-img" style="height: 340px; object-fit: cover;">
      </div>
      <div class="card">
        <div class="card-title cyan">High-Fidelity Stage Highlights</div>
        <ul class="styled-list">
          <li><strong>Procedural Pine Forest:</strong> 200m &times; 200m terrain populated with 48 pine trees with varied canopies and scales.</li>
          <li><strong>Thermal Hotspots:</strong>
            <ul style="margin-left: 20px; margin-top: 8px; list-style: disc; color: #CBD5E1;">
              <li><em>Hotspot 01:</em> 38&deg;C Smoldering brush fire</li>
              <li><em>Hotspot 02:</em> 78&deg;C Active flaming core plume</li>
              <li><em>Hotspot 03:</em> 54&deg;C Flare-up risk zone</li>
            </ul>
          </li>
          <li><strong>Dual Camera Payloads:</strong>
            <ul style="margin-left: 20px; margin-top: 8px; list-style: disc; color: #CBD5E1;">
              <li><code>ThermalGimbalCamera</code>: Downward nadir inspection</li>
              <li><code>ChaseCamera</code>: Dynamic 3rd-person follow cam for pilot view</li>
            </ul>
          </li>
          <li><strong>RTX Ray Tracing Real-Time 2.0:</strong> Sustained 72 FPS with stable GPU memory footprint on RTX 4060 Laptop GPU.</li>
        </ul>
      </div>
    </div>
  </div>

  <!-- SLIDE 6: Flight Telemetry Results -->
  <div class="slide">
    <div class="slide-header">
      <div class="header-left">
        <span class="badge-cat">SIMULATION EXPERIMENTS</span>
        <span class="slide-title">Autonomous Mission Telemetry &amp; Actuation</span>
      </div>
      <span class="badge-course">CSC3034</span>
    </div>
    <div class="content-grid-2">
      <div>
        <img src="{img_telem}" class="slide-img" style="height: 100%; max-height: 720px; object-fit: contain; background: #0F172A; padding: 10px;">
      </div>
      <div class="card">
        <div class="card-title green">Observed System Behavior</div>
        <ul class="styled-list">
          <li><strong>Baseline Transit (Frames 0-100):</strong> Ambient temp 24&deg;C, FRI = 12.4% (SAFE). Drone sprints at 22.5 m/s to cover search area.</li>
          <li><strong>Hotspot 02 Incursion (Frames 200-340):</strong> Sensor detects sudden thermal spike to 78.4&deg;C. Fuzzy controller escalates FRI to <strong>92.6% (CRITICAL)</strong>.</li>
          <li><strong>Speed Throttling:</strong> Urgency speed automatically drops to <strong>6.5 m/s</strong>, allowing the UAV to loiter and capture high-resolution imagery.</li>
          <li><strong>Hotspot 03 Flare-Up (Frames 450-520):</strong> Moderate risk (FRI = 64.2%), drone decelerates to 12.0 m/s for confirmation.</li>
        </ul>
      </div>
    </div>
  </div>

  <!-- SLIDE 7: Defuzzification Benchmark -->
  <div class="slide">
    <div class="slide-header">
      <div class="header-left">
        <span class="badge-cat">COMPUTATIONAL INTELLIGENCE ANALYSIS</span>
        <span class="slide-title">Defuzzification Comparative Benchmark</span>
      </div>
      <span class="badge-course">CSC3034</span>
    </div>
    <div class="content-grid-2">
      <div class="card">
        <div class="card-title orange">Strategy Comparison</div>
        <table class="table-clean">
          <thead>
            <tr>
              <th>Method</th>
              <th>Avg Latency</th>
              <th>Actuator Smoothness</th>
              <th>Noise Robustness</th>
            </tr>
          </thead>
          <tbody>
            <tr style="background: rgba(56, 189, 248, 0.1);">
              <td><strong style="color: #38BDF8;">Centroid (COG)</strong></td>
              <td>0.884 ms</td>
              <td>Exceptional (Smooth)</td>
              <td>High</td>
            </tr>
            <tr>
              <td><strong>Bisector</strong></td>
              <td>0.912 ms</td>
              <td>Good</td>
              <td>Moderate</td>
            </tr>
            <tr>
              <td><strong>Mean of Max (MOM)</strong></td>
              <td>0.420 ms</td>
              <td>Poor (Step Discontinuities)</td>
              <td>Low</td>
            </tr>
          </tbody>
        </table>
        <p style="color: #94A3B8; font-size: 15px; margin-top: 24px;">
          <strong>Finding:</strong> Although MOM computes faster, it produces sudden step-changes when peak membership shifts, which would cause violent motor torque spikes on a real quadrotor. Centroid was selected for flight safety.
        </p>
      </div>
      <div class="card">
        <div class="card-title cyan">Real-Time Edge Feasibility</div>
        <ul class="styled-list">
          <li><strong>Edge Platform:</strong> Target deployment on NVIDIA Jetson Orin Nano (8 GB, 7-15 W power budget).</li>
          <li><strong>Timing Budget:</strong> Fuzzy inference execution (0.884 ms) consumes only 1.7% of the 50 ms UAV flight control deadline (20 Hz loop).</li>
          <li><strong>Scalability:</strong> Capable of evaluating 1,000+ rule inferences per second without throttling CPU flight controllers.</li>
        </ul>
      </div>
    </div>
  </div>

  <!-- SLIDE 8: Conclusion & Q&A -->
  <div class="slide" style="justify-content: center; align-items: center; text-align: center;">
    <div class="card" style="max-width: 1300px; padding: 60px 80px; align-items: center; border: 2px solid #38BDF8;">
      <div style="font-size: 48px; font-weight: 900; color: #38BDF8; margin-bottom: 16px;">THANK YOU!</div>
      <div style="font-size: 28px; font-weight: 700; color: #FFFFFF; margin-bottom: 24px;">Project Defense &amp; Demonstration Q&amp;A Session</div>
      <p style="font-size: 20px; color: #CBD5E1; max-width: 900px; line-height: 1.6; margin-bottom: 30px;">
        <strong>Autonomous Wildfire Risk Assessment &amp; UAV Surveillance Dispatch</strong><br>
        Mamdani Fuzzy Inference Interfaced with NVIDIA Isaac Sim
      </p>
      <div style="font-size: 18px; color: #94A3B8; margin-bottom: 24px;">
        Pang Wei Sheng &bull; Roshan Sivakumar &bull; Dinesswar Sathasivam &bull; Yeoh Choon Hern<br>
        Sunway University &bull; CSC3034 Computational Intelligence &bull; Supervisor: Dr. Tang Tiong Yew
      </div>
      <div style="background: #0F172A; padding: 12px 30px; border-radius: 10px; border: 1px solid #334155; font-size: 16px; color: #FF5722; font-weight: 700;">
        GitHub: https://github.com/123haiku/csc3034-fuzzy-wildfire-sim
      </div>
    </div>
  </div>

</body>
</html>"""

    html_file = PRESENTATION_DIR / "CSC3034_Presentation_Slides.html"
    html_file.write_text(html, encoding="utf-8")
    print(f"[Slides] Wrote interactive HTML slide deck: {html_file}")

    pdf_file = PRESENTATION_DIR / "CSC3034_Presentation_Slides.pdf"
    print("[Slides] Rendering 16:9 PDF slide deck via Playwright Chromium ...")
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1920, "height": 1080})
        page.goto(f"file:///{html_file.as_posix()}", wait_until="networkidle")
        page.pdf(
            path=str(pdf_file),
            width="1920px",
            height="1080px",
            print_background=True,
            margin={"top": "0px", "bottom": "0px", "left": "0px", "right": "0px"},
        )
        browser.close()
    print(f"[Slides] Exported PDF slides ({pdf_file.stat().st_size:,} bytes) to: {pdf_file}")

    if ARTIFACT_DIR.exists():
        import shutil
        shutil.copy2(html_file, ARTIFACT_DIR / "CSC3034_Presentation_Slides.html")
        shutil.copy2(pdf_file, ARTIFACT_DIR / "CSC3034_Presentation_Slides.pdf")
        print("[Slides] Synced PDF and HTML slides to artifact directory.")

    return pdf_file


if __name__ == "__main__":
    PRESENTATION_DIR.mkdir(parents=True, exist_ok=True)
    build_slides_html_and_pdf()
