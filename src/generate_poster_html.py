"""Generates a publication-grade A1 academic infographic poster in HTML, PDF, and high-res PNG."""

from __future__ import annotations

import base64
import os
from pathlib import Path
from playwright.sync_api import sync_playwright

REPO_ROOT = Path(__file__).resolve().parent.parent
POSTER_DIR = REPO_ROOT / "docs" / "poster"
ASSETS_DIR = POSTER_DIR / "assets"


def to_base64_data_uri(path: Path) -> str:
    """Encodes an image to a self-contained base64 data URI."""
    if not path.exists():
        return ""
    mime_type = "image/png" if path.suffix.lower() == ".png" else "image/jpeg"
    encoded = base64.b64encode(path.read_bytes()).decode("utf-8")
    return f"data:{mime_type};base64,{encoded}"


def generate_poster():
    print("[Poster] Loading assets and converting to base64 ...")
    img_forest = to_base64_data_uri(ASSETS_DIR / "isaac_sim_forest_scene.png")
    img_drone = to_base64_data_uri(ASSETS_DIR / "isaac_sim_drone_closeup.png")
    img_mf = to_base64_data_uri(ASSETS_DIR / "membership_functions.png")
    img_telemetry = to_base64_data_uri(ASSETS_DIR / "mission_telemetry_dashboard.png")

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CSC3034 A1 Infographic Poster — Autonomous Wildfire Fuzzy Surveillance</title>
    <style>
        @page {{
            size: 594mm 841mm;
            margin: 0;
        }}
        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            background-color: #0F172A;
            color: #1E293B;
            width: 594mm;
            min-height: 841mm;
            margin: 0 auto;
            padding: 16mm;
            display: flex;
            flex-direction: column;
            gap: 12mm;
            -webkit-print-color-adjust: exact;
            print-color-adjust: exact;
        }}
        
        /* Glass / Card styling */
        .card {{
            background: #FFFFFF;
            border-radius: 8mm;
            padding: 8mm;
            box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.2), 0 8px 10px -6px rgba(0, 0, 0, 0.1);
            border: 1px solid #E2E8F0;
            display: flex;
            flex-direction: column;
        }}

        /* Header Banner */
        .header-card {{
            background: linear-gradient(135deg, #1E293B 0%, #0F172A 50%, #1E1B4B 100%);
            border: 2px solid #334155;
            color: #FFFFFF;
            padding: 10mm 12mm;
            border-radius: 8mm;
            display: flex;
            flex-direction: column;
            gap: 6mm;
            box-shadow: 0 20px 30px -10px rgba(0, 0, 0, 0.5);
        }}
        .header-top {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 2px solid rgba(255, 255, 255, 0.15);
            padding-bottom: 4mm;
        }}
        .inst-title {{
            font-size: 8mm;
            font-weight: 800;
            letter-spacing: 0.5mm;
            color: #38BDF8;
            text-transform: uppercase;
        }}
        .course-badge {{
            background: #FF5722;
            color: #FFFFFF;
            padding: 2mm 6mm;
            border-radius: 4mm;
            font-size: 5.5mm;
            font-weight: 700;
            letter-spacing: 0.3mm;
        }}
        .main-title {{
            font-size: 13mm;
            font-weight: 900;
            line-height: 1.15;
            color: #FFFFFF;
            text-shadow: 0 4px 12px rgba(0,0,0,0.4);
        }}
        .main-title span {{
            color: #FB923C;
        }}
        .authors-row {{
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 4mm;
            background: rgba(255, 255, 255, 0.06);
            padding: 4mm 6mm;
            border-radius: 4mm;
            border: 1px solid rgba(255, 255, 255, 0.1);
        }}
        .author-box {{
            display: flex;
            flex-direction: column;
            gap: 1mm;
        }}
        .author-name {{
            font-size: 4.8mm;
            font-weight: 700;
            color: #F8FAFC;
        }}
        .author-meta {{
            font-size: 3.5mm;
            color: #94A3B8;
        }}
        .author-role {{
            font-size: 3.2mm;
            color: #38BDF8;
            font-weight: 600;
        }}
        .badge-bar {{
            display: flex;
            gap: 4mm;
            align-items: center;
        }}
        .sdg-badge {{
            padding: 1.5mm 5mm;
            border-radius: 3mm;
            font-size: 4mm;
            font-weight: 800;
            color: #FFFFFF;
            display: inline-flex;
            align-items: center;
            gap: 2mm;
        }}
        .sdg-13 {{ background: #4C9F38; }}
        .sdg-15 {{ background: #56C02B; }}
        .tech-pill {{
            background: rgba(255, 255, 255, 0.12);
            padding: 1.5mm 4mm;
            border-radius: 3mm;
            font-size: 3.8mm;
            font-weight: 600;
            color: #E2E8F0;
            border: 1px solid rgba(255, 255, 255, 0.2);
        }}

        /* 2-Column Grid Layout */
        .content-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 10mm;
            flex: 1;
        }}
        .col {{
            display: flex;
            flex-direction: column;
            gap: 8mm;
        }}

        /* Section Headings */
        .sec-header {{
            display: flex;
            align-items: center;
            gap: 3mm;
            margin-bottom: 4mm;
            border-bottom: 2px solid #E2E8F0;
            padding-bottom: 2.5mm;
        }}
        .sec-num {{
            background: #EA580C;
            color: #FFFFFF;
            font-size: 4.5mm;
            font-weight: 800;
            width: 8mm;
            height: 8mm;
            display: flex;
            align-items: center;
            justify-content: center;
            border-radius: 2mm;
        }}
        .sec-title {{
            font-size: 6.5mm;
            font-weight: 800;
            color: #0F172A;
            text-transform: uppercase;
            letter-spacing: 0.3mm;
        }}

        /* Typography & Paragraphs */
        p, li {{
            font-size: 4mm;
            line-height: 1.45;
            color: #334155;
        }}
        strong {{
            color: #0F172A;
        }}

        /* Highlight Boxes */
        .highlight-box {{
            background: #FFF7ED;
            border-left: 1.5mm solid #F97316;
            padding: 3mm 4mm;
            border-radius: 2mm;
            margin: 2mm 0;
            font-size: 3.8mm;
        }}
        .success-box {{
            background: #F0FDF4;
            border-left: 1.5mm solid #22C55E;
            padding: 3mm 4mm;
            border-radius: 2mm;
            margin: 2mm 0;
            font-size: 3.8mm;
        }}

        /* Tables */
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 3mm 0;
            font-size: 3.4mm;
        }}
        th, td {{
            padding: 2mm 2.5mm;
            text-align: left;
            border-bottom: 1px solid #E2E8F0;
        }}
        th {{
            background: #F1F5F9;
            font-weight: 700;
            color: #0F172A;
            text-transform: uppercase;
            font-size: 3.2mm;
        }}
        tr:nth-child(even) {{
            background: #F8FAFC;
        }}
        .status-pill {{
            padding: 0.8mm 2.5mm;
            border-radius: 2mm;
            font-weight: 800;
            font-size: 3mm;
            display: inline-block;
        }}
        .status-watch {{ background: #FEF3C7; color: #B45309; }}
        .status-warning {{ background: #FFEDD5; color: #C2410C; }}
        .status-critical {{ background: #FEE2E2; color: #B91C1C; }}

        /* Media / Image containers */
        .img-container {{
            width: 100%;
            background: #F8FAFC;
            border: 1px solid #E2E8F0;
            border-radius: 4mm;
            overflow: hidden;
            margin: 3mm 0;
            display: flex;
            flex-direction: column;
        }}
        .img-container img {{
            width: 100%;
            height: auto;
            display: block;
            object-fit: cover;
        }}
        .img-caption {{
            font-size: 3.2mm;
            color: #64748B;
            padding: 2mm 3mm;
            background: #F1F5F9;
            border-top: 1px solid #E2E8F0;
            font-weight: 500;
        }}

        /* Mathematical equation display */
        .equation-box {{
            background: #F8FAFC;
            border: 1px solid #CBD5E1;
            border-radius: 3mm;
            padding: 3mm 4mm;
            text-align: center;
            font-family: "Cambria Math", "Times New Roman", serif;
            font-size: 4.2mm;
            margin: 2mm 0;
            color: #0F172A;
        }}

        /* Key Metrics Grid */
        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 3mm;
            margin: 3mm 0;
        }}
        .metric-card {{
            background: #F8FAFC;
            border: 1px solid #E2E8F0;
            padding: 3mm;
            border-radius: 3mm;
            text-align: center;
        }}
        .metric-value {{
            font-size: 6.5mm;
            font-weight: 900;
            color: #EA580C;
        }}
        .metric-label {{
            font-size: 3.2mm;
            color: #64748B;
            font-weight: 600;
            text-transform: uppercase;
        }}
        
        /* Dual Image Grid */
        .dual-img-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 3mm;
        }}

        /* Footer */
        .footer-banner {{
            background: #1E293B;
            border-radius: 6mm;
            padding: 4mm 8mm;
            color: #94A3B8;
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 3.5mm;
        }}
    </style>
</head>
<body>

    <!-- ZONE 1: HEADER & TITLE -->
    <div class="header-card">
        <div class="header-top">
            <div class="inst-title">Sunway University &bull; School of Mathematical Sciences &amp; Computing</div>
            <div class="course-badge">CSC3034 Computational Intelligence &bull; Final Project</div>
        </div>
        
        <h1 class="main-title">
            Autonomous Wildfire Risk Assessment &amp; UAV Surveillance Dispatch<br>
            Using <span>Mamdani Fuzzy Logic</span> in <span>NVIDIA Isaac Sim</span>
        </h1>

        <div class="authors-row">
            <div class="author-box">
                <span class="author-name">Pang Wei Sheng</span>
                <span class="author-meta">ID: 24035115 &bull; Lead Author</span>
                <span class="author-role">Fuzzy Architecture &amp; Isaac Sim Bridge</span>
            </div>
            <div class="author-box">
                <span class="author-name">Roshan A/L Sivakumar</span>
                <span class="author-meta">ID: 23028285</span>
                <span class="author-role">Report Writing &amp; Defuzzification</span>
            </div>
            <div class="author-box">
                <span class="author-name">Dinesswar A/L Sathasivam</span>
                <span class="author-meta">ID: 23096910</span>
                <span class="author-role">OpenUSD Scene &amp; Sensors</span>
            </div>
            <div class="author-box">
                <span class="author-name">Yeoh Choon Hern</span>
                <span class="author-meta">ID: 23100795</span>
                <span class="author-role">Simulation &amp; Infographic Design</span>
            </div>
        </div>

        <div class="badge-bar">
            <span class="sdg-badge sdg-13">&#x1F30D; SDG 13: Climate Action (Target 13.1)</span>
            <span class="sdg-badge sdg-15">&#x1F333; SDG 15: Life on Land (Target 15.2)</span>
            <span class="tech-pill">&#x2699; NVIDIA Isaac Sim 6.2 (OpenUSD)</span>
            <span class="tech-pill">&#x1F3A8; RTX Real-Time Ray Tracing (RTX 4060)</span>
            <span class="tech-pill">&#x1F9E0; Scikit-Fuzzy Engine</span>
            <span class="tech-pill">&#x1F393; Supervisor: Dr. Tang Tiong Yew</span>
        </div>
    </div>

    <!-- 2-COLUMN MAIN CONTENT GRID -->
    <div class="content-grid">

        <!-- LEFT COLUMN -->
        <div class="col">

            <!-- ZONE 2: PROBLEM & SDG ALIGNMENT -->
            <div class="card">
                <div class="sec-header">
                    <div class="sec-num">1</div>
                    <div class="sec-title">Problem Statement &amp; Climate Action (UN SDGs)</div>
                </div>
                <p>
                    Wildfires inflict catastrophic ecological degradation and greenhouse emissions. Environmental interactions among 
                    ambient heat, air moisture, localized wind shear, and fuel desiccation are <strong>inherently continuous, non-linear, and uncertain</strong>.
                </p>

                <div class="highlight-box">
                    <strong>Critical Flaw of Traditional Systems:</strong> Static binary threshold triggers (e.g., alert if <em>Temp &gt; 40&deg;C</em>) 
                    suffer from severe false-alarm rates during benign humid days and dangerous response delays when moderate heat is amplified by 
                    parched undergrowth and high winds.
                </div>

                <table>
                    <thead>
                        <tr>
                            <th>Parameter</th>
                            <th>Traditional Binary Threshold</th>
                            <th>Proposed Mamdani Fuzzy System</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td><strong>Input Processing</strong></td>
                            <td>Rigid Step Functions (0 or 1)</td>
                            <td>Smooth Continuous Membership Degrees (&mu; &isin; [0, 1])</td>
                        </tr>
                        <tr>
                            <td><strong>Sensor Noise</strong></td>
                            <td>High Chatter &amp; False Alarms</td>
                            <td>Inherently Resilient via Overlapping Partitions</td>
                        </tr>
                        <tr>
                            <td><strong>Drone Actuation</strong></td>
                            <td>Abrupt On/Off Dispatches</td>
                            <td>Smooth Velocity Throttling (20% &rarr; 90% Urgency)</td>
                        </tr>
                        <tr>
                            <td><strong>Explainability</strong></td>
                            <td>None / Opaque Thresholds</td>
                            <td>100% Transparent Rule Base Traceability</td>
                        </tr>
                    </tbody>
                </table>

                <div class="success-box">
                    <strong>UN SDG Alignment:</strong> Early aerial detection within the initial 15 minutes of ignition suppresses wildfires before 
                    megaton-scale carbon release (<strong>SDG 13.1</strong>) while safeguarding biodiversity in endangered forest ecosystems (<strong>SDG 15.2</strong>).
                </div>
            </div>

            <!-- ZONE 3: FUZZY SYSTEM ARCHITECTURE -->
            <div class="card">
                <div class="sec-header">
                    <div class="sec-num">2</div>
                    <div class="sec-title">Mamdani Fuzzy Inference Formulation</div>
                </div>
                <p>
                    The controller ingests <strong>4 meteorological inputs</strong> across continuous universes of discourse and computes 
                    <strong>2 actuation outputs</strong> via Mamdani min-max inference:
                </p>

                <table>
                    <thead>
                        <tr>
                            <th>Linguistic Variable</th>
                            <th>Universe of Discourse</th>
                            <th>Fuzzy Subsets (Partitions)</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td><strong>Ambient Temperature (T)</strong></td>
                            <td>[0, 50] &deg;C</td>
                            <td>Low, Moderate, High, Extreme</td>
                        </tr>
                        <tr>
                            <td><strong>Relative Humidity (RH)</strong></td>
                            <td>[0, 100] %</td>
                            <td>High, Moderate, Low, Very Low</td>
                        </tr>
                        <tr>
                            <td><strong>Wind Velocity (W)</strong></td>
                            <td>[0, 100] km/h</td>
                            <td>Calm, Moderate, High, Severe</td>
                        </tr>
                        <tr>
                            <td><strong>Vegetation Dryness (F)</strong></td>
                            <td>[0, 100] %</td>
                            <td>Wet, Moderate, Dry, Critically Dry</td>
                        </tr>
                        <tr>
                            <td><strong>Fire Risk Index (FRI) [Out]</strong></td>
                            <td>[0, 100]</td>
                            <td>Low, Moderate, High, Extreme</td>
                        </tr>
                        <tr>
                            <td><strong>Drone Patrol Urgency [Out]</strong></td>
                            <td>[0, 100] %</td>
                            <td>Standard Patrol, Accelerated, Emergency Dispatch</td>
                        </tr>
                    </tbody>
                </table>

                <div class="equation-box">
                    <strong>Center of Gravity (Centroid / COG) Defuzzification:</strong><br>
                    y* = &int; y &bull; &mu;<sub>agg</sub>(y) dy &nbsp;/&nbsp; &int; &mu;<sub>agg</sub>(y) dy
                </div>

                <div class="img-container">
                    <img src="{img_mf}" alt="Fuzzy Linguistic Membership Functions">
                    <div class="img-caption">Figure 1: Full 6-variable linguistic fuzzy membership curves (4 meteorological inputs + 2 actuation outputs).</div>
                </div>
            </div>

        </div>

        <!-- RIGHT COLUMN -->
        <div class="col">

            <!-- ZONE 4: NVIDIA ISAAC SIM 3D ENVIRONMENT -->
            <div class="card">
                <div class="sec-header">
                    <div class="sec-num">3</div>
                    <div class="sec-title">NVIDIA Isaac Sim 3D Digital Twin</div>
                </div>
                <p>
                    A photorealistic, physics-accurate digital twin was procedurally generated using <strong>Pixar OpenUSD</strong> in 
                    <strong>NVIDIA Isaac Sim 6.2.0</strong>, powered by RTX Real-Time Ray Tracing on an RTX 4060 GPU:
                </p>

                <div class="dual-img-grid">
                    <div class="img-container">
                        <img src="{img_forest}" alt="Isaac Sim Forest Stage">
                        <div class="img-caption">Figure 2: 65m&times;65m forest terrain with 48 procedural trees &amp; 3 thermal ignition hotspots.</div>
                    </div>
                    <div class="img-container">
                        <img src="{img_drone}" alt="Autonomous Surveillance Drone">
                        <div class="img-caption">Figure 3: Kinematic 4-rotor quadcopter UAV hovering over canopy with thermal camera pod.</div>
                    </div>
                </div>

                <div class="metrics-grid">
                    <div class="metric-card">
                        <div class="metric-value">65 &times; 65 m</div>
                        <div class="metric-label">Forest Terrain</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">48 Trees</div>
                        <div class="metric-label">Moisture Shaders</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">3 Hotspots</div>
                        <div class="metric-label">Thermal Radiators</div>
                    </div>
                </div>

                <p style="font-size: 3.6mm; margin-top: 1mm;">
                    <strong>Real-Time USD Telemetry Sync:</strong> The UAV prim updates custom USD attributes in real time 
                    (<code>fuzzy:fire_risk_index</code>, <code>fuzzy:patrol_urgency_speed</code>, <code>fuzzy:alert_status</code>). Dual onboard cameras 
                    (<code>ChaseCamera</code> and <code>ThermalGimbalCamera</code>) provide third-person tracking and first-person inspection.
                </p>
            </div>

            <!-- ZONE 5: RESULTS & EVALUATION -->
            <div class="card">
                <div class="sec-header">
                    <div class="sec-num">4</div>
                    <div class="sec-title">Autonomous Mission Telemetry &amp; Evaluation</div>
                </div>

                <div class="img-container">
                    <img src="{img_telemetry}" alt="Mission Telemetry Dashboard">
                    <div class="img-caption">Figure 4: 3D UAV reconnaissance flight path heatmap &amp; 4-panel multi-variable atmospheric/actuation timeline.</div>
                </div>

                <table>
                    <thead>
                        <tr>
                            <th>Waypoint</th>
                            <th>Coord (X, Y, Z)</th>
                            <th>Temp</th>
                            <th>RH</th>
                            <th>Wind</th>
                            <th>Dryness</th>
                            <th>Fuzzy FRI</th>
                            <th>Throttle</th>
                            <th>System Status</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td><strong>WP 00 (Base)</strong></td>
                            <td>(0.0, 0.0, 5.0m)</td>
                            <td>28.8 &deg;C</td>
                            <td>47.8%</td>
                            <td>23 km/h</td>
                            <td>40.2%</td>
                            <td><strong>45.0</strong></td>
                            <td>20.0%</td>
                            <td><span class="status-pill status-watch">WATCH</span></td>
                        </tr>
                        <tr>
                            <td><strong>WP 03 (Hotspot 1)</strong></td>
                            <td>(13.5, 15.5, 5.0m)</td>
                            <td>42.4 &deg;C</td>
                            <td>19.4%</td>
                            <td>45 km/h</td>
                            <td>86.8%</td>
                            <td><strong>91.2</strong></td>
                            <td>89.2%</td>
                            <td><span class="status-pill status-critical">CRITICAL DISPATCH</span></td>
                        </tr>
                        <tr>
                            <td><strong>WP 06 (Buffer)</strong></td>
                            <td>(0.0, 15.0, 7.0m)</td>
                            <td>28.3 &deg;C</td>
                            <td>47.4%</td>
                            <td>24 km/h</td>
                            <td>39.8%</td>
                            <td><strong>45.0</strong></td>
                            <td>20.1%</td>
                            <td><span class="status-pill status-watch">WATCH</span></td>
                        </tr>
                        <tr>
                            <td><strong>WP 08 (Hotspot 2)</strong></td>
                            <td>(-17.5, 9.8, 4.5m)</td>
                            <td>44.5 &deg;C</td>
                            <td>17.9%</td>
                            <td>47 km/h</td>
                            <td>87.3%</td>
                            <td><strong>91.7</strong></td>
                            <td>90.0%</td>
                            <td><span class="status-pill status-critical">CRITICAL DISPATCH</span></td>
                        </tr>
                        <tr>
                            <td><strong>WP 11 (Hotspot 3)</strong></td>
                            <td>(7.8, -19.5, 5.0m)</td>
                            <td>43.0 &deg;C</td>
                            <td>17.6%</td>
                            <td>48 km/h</td>
                            <td>88.9%</td>
                            <td><strong>91.5</strong></td>
                            <td>89.6%</td>
                            <td><span class="status-pill status-critical">CRITICAL DISPATCH</span></td>
                        </tr>
                    </tbody>
                </table>

                <div class="metrics-grid">
                    <div class="metric-card">
                        <div class="metric-value">0.15 ms</div>
                        <div class="metric-label">Inference Latency</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">100%</div>
                        <div class="metric-label">Pytest Unit Pass Rate</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">72.1 FPS</div>
                        <div class="metric-label">Isaac Sim Ray Tracing</div>
                    </div>
                </div>

                <p style="font-size: 3.5mm;">
                    <strong>Defuzzification Analysis:</strong> Centroid (COG) provides smooth, vibration-free motor throttle curves (142&mu;s), 
                    avoiding the step discontinuities observed in Mean of Maximum (MOM) defuzzification.
                </p>
            </div>

            <!-- ZONE 6: CONCLUSION & HORIZON -->
            <div class="card" style="margin-top: auto;">
                <div class="sec-header">
                    <div class="sec-num">5</div>
                    <div class="sec-title">Key Conclusions &amp; Impact</div>
                </div>
                <ul style="padding-left: 5mm; display: flex; flex-direction: column; gap: 1.5mm;">
                    <li><strong>Rigorous Explainability:</strong> Unlike black-box neural networks, all dispatch actions are 100% traceable to domain rules.</li>
                    <li><strong>Edge Deployment Ready:</strong> At 0.15 ms execution time, the pipeline runs easily on embedded flight computers (NVIDIA Jetson).</li>
                    <li><strong>Future Horizon:</strong> Decentralized multi-UAV swarm surveillance and reinforcement learning reward shaping via Isaac Lab.</li>
                </ul>
            </div>

        </div>

    </div>

    <!-- FOOTER BANNER -->
    <div class="footer-banner">
        <span>Sunway University &bull; School of Mathematical Sciences &amp; Computing &bull; CSC3034 Computational Intelligence</span>
        <span>Repository: github.com/123haiku/csc3034-fuzzy-wildfire-sim &bull; November 2026</span>
    </div>

</body>
</html>"""

    html_file = POSTER_DIR / "CSC3034_A1_Poster.html"
    html_file.write_text(html_content, encoding="utf-8")
    print(f"[Poster] Wrote self-contained A1 Poster HTML ({html_file.stat().st_size:,} bytes) to: {html_file}")

    # Copy to Antigravity artifact directory for chat inline preview
    conv_artifact_dir = Path(r"C:\Users\pangw\.gemini\antigravity\brain\3ed287fb-9045-4894-b2e3-ae5c7c992ba9")
    if conv_artifact_dir.exists():
        (conv_artifact_dir / "CSC3034_A1_Poster.html").write_text(html_content, encoding="utf-8")
        print(f"[Poster] Copied artifact to: {conv_artifact_dir / 'CSC3034_A1_Poster.html'}")

    # Render to PDF and PNG using Playwright
    pdf_file = POSTER_DIR / "CSC3034_A1_Poster.pdf"
    png_file = POSTER_DIR / "CSC3034_A1_Poster.png"
    print("[Poster] Rendering A1 vector PDF and high-res PNG via Playwright Chromium ...")

    with sync_playwright() as p:
        browser = p.chromium.launch()
        # A1 pixel dimensions for crisp rendering
        page = browser.new_page(viewport={"width": 2245, "height": 3175}, device_scale_factor=1.5)
        page.goto(f"file:///{html_file.as_posix()}", wait_until="networkidle")

        # Export high-res PNG
        page.screenshot(path=str(png_file), full_page=True)
        print(f"[Poster] Exported high-res PNG ({png_file.stat().st_size:,} bytes) to: {png_file}")

        # Export exact A1 vector PDF
        page.pdf(
            path=str(pdf_file),
            width="594mm",
            height="841mm",
            print_background=True,
            margin={"top": "0mm", "bottom": "0mm", "left": "0mm", "right": "0mm"},
        )
        print(f"[Poster] Exported print-ready A1 PDF ({pdf_file.stat().st_size:,} bytes) to: {pdf_file}")

        browser.close()

    print("[Poster] All poster formats generated successfully!")


if __name__ == "__main__":
    generate_poster()
