"""Audits the exported report DOCX for format defects and vague statements.

    python tools/report/audit_report_docx.py

Prints four blocks: heading hierarchy, paragraph-shape statistics, rendering defects
found in the shipped file, and a sentence-by-sentence scan for vague wording that
states no quantity, no mechanism and no artefact.
"""

from __future__ import annotations

import re
import statistics
from pathlib import Path

import docx
from docx.enum.text import WD_ALIGN_PARAGRAPH

REPO = Path(__file__).resolve().parent.parent.parent
DOCX = REPO / "docs" / "report" / "CSC3034_Final_Report.docx"

# Phrases that usually signal a claim with no measurable content.
VAGUE = [
    r"\bhighly (?:volatile|non-linear|complex|significant|effective)\b",
    r"\bsignificantly\b",
    r"\bdemonstrated that\b",
    r"\binherently\b",
    r"\brobust\b",
    r"\bseamless(?:ly)?\b",
    r"\bcutting-edge\b",
    r"\bstate-of-the-art\b",
    r"\bpowerful\b",
    r"\bcritically important\b",
    r"\bessential for\b",
    r"\bunderlying\b",
    r"\bvarious\b",
    r"\bnumerous\b",
    r"\bexcellent\b",
    r"\bcomprehensive(?:ly)?\b",
    r"\boptimal(?:ly)?\b",
    r"\bin real-time\b",
    r"\bsmooth(?:ly)?\b",
    r"\bintelligent\b",
    r"\badvanced\b",
    r"\bsuccessfully\b",
]


def iter_block_items(doc):
    """Yield paragraphs and tables in document order."""
    from docx.table import Table
    from docx.text.paragraph import Paragraph

    body = doc.element.body
    for child in body.iterchildren():
        if child.tag.endswith("}p"):
            yield Paragraph(child, doc)
        elif child.tag.endswith("}tbl"):
            yield Table(child, doc)


def main() -> int:
    doc = docx.Document(str(DOCX))

    print("== 1. Paragraph styles / heading hierarchy ==")
    counts = {}
    for p in doc.paragraphs:
        counts[p.style.name] = counts.get(p.style.name, 0) + 1
    for name, n in sorted(counts.items()):
        print(f"{name:<24}{n:>4}")
    print(f"{'TABLES':<24}{len(doc.tables):>4}")
    print(f"{'INLINE SHAPES':<24}{len(doc.inline_shapes):>4}")
    print(f"{'SECTIONS':<24}{len(doc.sections):>4}")

    print("\n== 2. Body paragraph width and alignment ==")
    body_rows = []
    for block in iter_block_items(doc):
        if block.__class__.__name__ != "Paragraph":
            continue
        p = block
        text = p.text.strip()
        if not text or p.style.name.startswith("Heading"):
            continue
        body_rows.append((len(text.split()), p.alignment, text))

    if body_rows:
        words = [w for w, _, _ in body_rows]
        print(f"paragraphs={len(words)} words={sum(words)} "
              f"mean={statistics.mean(words):.1f} median={statistics.median(words):.0f} "
              f"max={max(words)}")
        justified = sum(1 for _, a, _ in body_rows if a == WD_ALIGN_PARAGRAPH.JUSTIFY)
        print(f"justified paragraphs: {justified}/{len(body_rows)}")
        longest = sorted(body_rows, key=lambda r: -r[0])[:3]
        for w, _, t in longest:
            print(f"  LONGEST {w:>3}w  {t[:90]}...")

    print("\n== 3. Rendering defects in the shipped text ==")
    defects = []
    for i, p in enumerate(doc.paragraphs):
        t = p.text
        if "**" in t or "`" in t:
            defects.append(f"markdown residue p{i}: {t[:80]}")
        if re.search(r"\$[^$]*\$", t):
            defects.append(f"unflattened math p{i}: {t[:80]}")
        if re.search(r"\\[a-zA-Z]+", t):
            defects.append(f"latex residue p{i}: {t[:80]}")
        if re.search(r"\(\s+\)|\[\s+\]", t):
            defects.append(f"empty bracket p{i}: {t[:80]}")
        if "  " in t:
            defects.append(f"double space p{i}: {t[:80]}")
        if re.search(r"\b(?:Table|Figure) \d", t) and p.style.name.startswith("Heading"):
            defects.append(f"caption merged into heading p{i}: {t[:80]}")
    for d in defects[:40]:
        print("  " + d)
    print(f"  total: {len(defects)}")

    print("\n== 4. Vague-wording scan (body paragraphs only) ==")
    hits = []
    for i, p in enumerate(doc.paragraphs):
        if p.style.name.startswith("Heading"):
            continue
        t = p.text.strip()
        if len(t) < 40:
            continue
        for pat in VAGUE:
            for m in re.finditer(pat, t, flags=re.IGNORECASE):
                hits.append((m.group(0), i, t))
    per_phrase = {}
    for word, i, t in hits:
        per_phrase.setdefault(word.lower(), []).append(i)
    for word, idxs in sorted(per_phrase.items(), key=lambda kv: -len(kv[1])):
        print(f"  {word:<26} x{len(idxs):<3} paragraphs {idxs[:12]}")
    print(f"  total hits: {len(hits)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
