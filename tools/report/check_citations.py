"""Inspect report references block and in-text citations."""
import re
import sys
from pathlib import Path

from docx import Document

root = Path(__file__).resolve().parents[2]
doc = Document(str(root / "docs" / "report" / "CSC3034_Final_Report.docx"))
paras = [p.text.strip() for p in doc.paragraphs]
idx = next(k for k, t in enumerate(paras) if t.lower() == "references")
print("=== references block ===")
entries = [t for t in paras[idx + 1:] if t]
for t in entries:
    print(f"  {t[:200]}")
print(f"entries: {len(entries)}")

body = " ".join(paras[:idx])
markers = re.findall(r"\[\d+(?:\s*[-,]\s*\d+)*\]", body)
nums = set()
for m in markers:
    for part in re.findall(r"\d+", m):
        nums.add(int(part))
print(f"in-text markers: {len(markers)}, distinct numbers: {sorted(nums)}")
print(f"body words: {len(body.split())}")
missing = sorted(n for n in range(1, len(entries) + 1) if n not in nums)
print(f"reference entries never cited in body: {missing}")
uncited = sorted(n for n in nums if n > len(entries))
print(f"citations with no reference entry: {uncited}")
sys.exit(0)
