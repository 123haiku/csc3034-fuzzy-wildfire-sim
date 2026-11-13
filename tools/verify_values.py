"""Checks that every deliverable quotes the values measured into docs/measurements.json.

    python tools/verify_values.py

Three checks run against the built artefacts:

1. required   every measured figure that the document claims to report is present
2. stale      no superseded figure survives anywhere in the document
3. tables     the report's mission and defuzzification tables match the measurement row
              by row, not just as substrings

Exit code 1 when any check fails, so it can gate a build.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import docx
from docx.table import Table
from pptx import Presentation

REPO = Path(__file__).resolve().parent.parent
MEASUREMENTS = REPO / "docs" / "measurements.json"
REPORT = REPO / "docs" / "report" / "CSC3034_Final_Report.docx"
DECK = REPO / "docs" / "presentation" / "CSC3034_Presentation_Slides.pptx"
POSTER_HTML = REPO / "docs" / "poster" / "CSC3034_A1_Poster.html"

failures: list[str] = []
checks = 0


def check(condition: bool, label: str, detail: str = "") -> None:
    global checks
    checks += 1
    if condition:
        print(f"  [ok]   {label}")
    else:
        print(f"  [FAIL] {label} {detail}")
        failures.append(label)


def docx_text(path: Path) -> str:
    document = docx.Document(str(path))
    parts = [p.text for p in document.paragraphs]
    for table in document.tables:
        for row in table.rows:
            for cell in row.cells:
                parts.append(cell.text)
    return "\n".join(parts)


def pptx_text(path: Path) -> str:
    prs = Presentation(str(path))
    parts = []
    for slide in prs.slides:
        for shape in slide.shapes:
            if shape.has_text_frame:
                parts.append(shape.text_frame.text)
        if slide.has_notes_slide:
            parts.append(slide.notes_slide.notes_text_frame.text)
    return "\n".join(parts)


def poster_text(path: Path) -> str:
    """Visible poster text, with the embedded base64 images removed.

    The HTML inlines four PNGs as data URIs, and a base64 blob will contain almost any
    short digit string by chance, which would make a substring check meaningless.
    """
    html = path.read_text(encoding="utf-8")
    return re.sub(r'data:image/[a-z]+;base64,[A-Za-z0-9+/=]+', '', html)


def main() -> int:
    data = json.loads(MEASUREMENTS.read_text(encoding="utf-8"))
    engine = data["engine"]
    latency = data["latency"]
    mission = data["mission"]
    tests = data["tests"]["passed"]

    med = max(v for k, v in latency.items() if k.endswith("_median_ms"))
    p99 = max(v for k, v in latency.items() if k.endswith("_p99_ms"))

    documents = {
        "report": docx_text(REPORT),
        "deck": pptx_text(DECK),
        "poster": poster_text(POSTER_HTML),
    }

    print("\n=== 1. figures that must be present ===")
    required = {
        "report": [f"{med:.2f}", f"{latency['benign_p99_ms']:.3f}",
                   f"{latency['critical_p99_ms']:.3f}", str(tests), "0.069"],
        "deck": [f"{med:.2f}", f"{p99:.2f}", str(engine["trees_in_asset"])],
        "poster": [f"{med:.2f}", f"{p99:.2f}", str(engine["trees_in_asset"]), str(tests)],
    }
    for name, needles in required.items():
        body = documents[name]
        for needle in needles:
            check(needle in body, f"{name}: contains {needle!r}")

    print("\n=== 2. superseded figures that must not survive ===")
    stale = {
        "report": ["0.077", "0.284", "1.415", "0.182 ms", "67.3", "72.1", "24,800", "48 procedurally"],
        "deck": ["0.28 ms", "1.42 ms", "0.078", "0.36 ms", "60 Hz", "67-72"],
        "poster": ["0.28", "1.42", "67", "48 procedural", "15\u201330"],
    }
    for name, needles in stale.items():
        body = documents[name]
        for needle in needles:
            check(needle not in body, f"{name}: no {needle!r}")

    print("\n=== 3. tables match the measurement ===")
    document = docx.Document(str(REPORT))
    mission_table = None
    defuzz_table = None
    for table in document.tables:
        header = [c.text.strip() for c in table.rows[0].cells]
        if header and header[0] == "WP":
            mission_table = table
        if header and header[0].startswith("Environmental"):
            defuzz_table = table

    check(mission_table is not None, "report: mission table present")
    if mission_table is not None:
        rows_ok = 0
        for row, expected in zip(mission_table.rows[1:], mission):
            cells = [c.text.strip() for c in row.cells]
            want = [
                f"{expected['temperature']:.1f}",
                f"{expected['humidity']:.1f}",
                f"{expected['wind_speed']:.1f}",
                f"{expected['vegetation_dryness']:.1f}",
                f"{expected['fire_risk_index']:.1f}",
                f"{expected['patrol_urgency']:.1f}",
                f"{expected['suppression_alert']:.3f}",
            ]
            got = cells[2:9]
            if got == want:
                rows_ok += 1
            else:
                print(f"       WP {expected['step']:02d} expected {want} got {got}")
        check(rows_ok == len(mission), f"report: mission table rows match ({rows_ok}/{len(mission)})")

    check(defuzz_table is not None, "report: defuzzification table present")
    if defuzz_table is not None:
        rows_ok = 0
        for row, expected in zip(defuzz_table.rows[1:], data["defuzz"]):
            cells = [c.text.strip() for c in row.cells]
            if cells[1:] == [f"{expected['centroid']:.1f}", f"{expected['bisector']:.1f}",
                             f"{expected['mom']:.1f}"]:
                rows_ok += 1
        check(rows_ok == len(data["defuzz"]),
              f"report: defuzzification rows match ({rows_ok}/{len(data['defuzz'])})")

    print(f"\nRESULT: {checks - len(failures)} passed, {len(failures)} failed")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
