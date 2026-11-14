"""Repair UTF-8-as-cp1252 mojibake in the report source and report on every document."""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PAIRS = {
    "\u00e2\u20ac\u201d": "\u2014",   # em dash
    "\u00e2\u20ac\u201c": "\u201c",   # left double quote
    "\u00e2\u20ac\u009d": "\u201d",   # right double quote
    "\u00e2\u20ac\u2122": "\u2019",   # right single quote
    "\u00e2\u20ac\u02dc": "\u2018",   # left single quote
    "\u00e2\u20ac\u2013": "\u2013",   # en dash
    "\u00c2\u00b0": "\u00b0",         # degree sign
    "\u00c2\u00b5": "\u00b5",         # micro sign
    "\u00c3\u00a9": "\u00e9",
}

SOURCES = [
    ROOT / "docs" / "report" / "REPORT_TEMPLATE.md",
    ROOT / "README.md",
    ROOT / "docs" / "SUBMISSION.md",
    ROOT / "docs" / "poster" / "CSC3034_A1_Poster.html",
]

for path in SOURCES:
    text = path.read_text(encoding="utf-8")
    before = text
    counts = {}
    for bad, good in PAIRS.items():
        n = text.count(bad)
        if n:
            counts[repr(bad)] = n
            text = text.replace(bad, good)
    if text != before:
        path.write_text(text, encoding="utf-8")
        print(f"{path.relative_to(ROOT)}: repaired {counts}")
    else:
        print(f"{path.relative_to(ROOT)}: clean")

# Residual scan: any remaining C1/Latin-1 runs that look like damaged UTF-8.
print("\nresidual mojibake markers:")
pattern = re.compile("[\u00c2\u00c3\u00e2][\u0080-\u00bf\u2018\u2019\u201c\u201d\u2013\u2014\u2020\u2021\u02dc\u2122]")
for path in SOURCES:
    text = path.read_text(encoding="utf-8")
    hits = pattern.findall(text)
    print(f"  {path.relative_to(ROOT)}: {len(hits)}")
