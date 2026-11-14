"""Ad-hoc repository completeness audit for CSC3034 submission.

Checks:
  1. Every backticked path mentioned in Markdown exists on disk.
  2. Every local Markdown link target exists.
  3. Tracked files match the working tree (no missing-but-tracked files).
  4. Report DOCX: required section headings and structural elements.
  5. PDFs open and report a page count.
"""

from __future__ import annotations

import re
import subprocess
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATH_RE = re.compile(r"`([A-Za-z0-9_./\-]+\.[A-Za-z0-9]{1,5})`")
LINK_RE = re.compile(r"\[[^\]]*\]\((?!https?://|#)([^)]+)\)")

failures: list[str] = []
notes: list[str] = []

# Names that live outside the repository: Isaac Sim ships its own interpreter.
EXTERNAL = {"python.bat", "python.sh"}


def check_paths() -> None:
    md_files = sorted(ROOT.rglob("*.md"))
    seen: set[str] = set()
    for md in md_files:
        if ".git" in md.parts or "_legacy" in md.parts:
            continue
        text = md.read_text(encoding="utf-8", errors="replace")
        rel = md.relative_to(ROOT).as_posix()
        for cand in PATH_RE.findall(text):
            if cand.startswith(("http", "{{", "docs/measurements.json")):
                continue
            if Path(cand).name in EXTERNAL:
                continue
            if re.fullmatch(r"[\d.,]+", cand):
                continue
            seen.add(cand)
            p = ROOT / cand
            if p.exists():
                continue
            # tolerate bare filenames that exist somewhere in the tree
            if any(ROOT.rglob(Path(cand).name)) and "/" not in cand:
                continue
            failures.append(f"missing path in {rel}: {cand}")
        for target in LINK_RE.findall(text):
            target = target.split("#")[0].strip()
            if not target:
                continue
            p = (md.parent / target).resolve()
            if not p.exists():
                failures.append(f"broken link in {rel}: {target}")
    print(f"[1/2] markdown path scan: {len(md_files)} files, {len(seen)} unique referenced paths")


def check_tracked() -> None:
    out = subprocess.run(
        ["git", "ls-files", "-z"], cwd=ROOT, capture_output=True, text=True, check=True
    ).stdout
    tracked = [p for p in out.split("\0") if p]
    missing = [p for p in tracked if not (ROOT / p).exists()]
    print(f"[3] tracked files: {len(tracked)}, missing on disk: {len(missing)}")
    for p in missing:
        failures.append(f"tracked but absent: {p}")


def check_report() -> None:
    try:
        from docx import Document
    except Exception as exc:  # pragma: no cover
        notes.append(f"python-docx unavailable: {exc}")
        return
    path = ROOT / "docs" / "report" / "CSC3034_Final_Report.docx"
    doc = Document(str(path))
    heads = [
        (p.style.name, p.text.strip())
        for p in doc.paragraphs
        if p.style.name.startswith("Heading") and p.text.strip()
    ]
    words = sum(len(p.text.split()) for p in doc.paragraphs)
    print(f"[4] report: {len(heads)} headings, {words} words, {len(doc.tables)} tables, "
          f"{len(doc.inline_shapes)} figures")
    print("    headings:")
    for style, text in heads:
        print(f"      {style:10} {text}")
    required = [
        "abstract", "introduction", "literature", "method", "result",
        "discussion", "conclusion", "reference",
    ]
    blob = " ".join(t.lower() for _, t in heads)
    for want in required:
        if want not in blob:
            failures.append(f"report heading missing keyword: {want}")
    if words < 2500:
        notes.append(f"report body is short: {words} words")


def check_deliverables() -> None:
    for rel in [
        "docs/poster/CSC3034_A1_Poster.pdf",
        "docs/poster/CSC3034_A1_Poster_300DPI.png",
        "docs/poster/CSC3034_A1_Poster.html",
        "docs/report/CSC3034_Final_Report.docx",
        "docs/report/CSC3034_Final_Report.pdf",
        "docs/presentation/CSC3034_Presentation_Slides.pptx",
        "docs/presentation/CSC3034_Presentation_Slides.pdf",
        "docs/proposal/CSC3034_Group_Proposal_Form.docx",
        "assets/wildfire_forest_uav_stage.usda",
    ]:
        p = ROOT / rel
        if not p.exists():
            failures.append(f"deliverable missing: {rel}")
            continue
        tag = ""
        data = p.read_bytes()[:8]
        if p.suffix == ".pdf" and not data.startswith(b"%PDF"):
            failures.append(f"not a PDF: {rel}")
        if p.suffix in {".docx", ".pptx"}:
            try:
                with zipfile.ZipFile(p) as z:
                    bad = z.testzip()
                tag = "zip-ok" if bad is None else f"zip-bad:{bad}"
                if bad is not None:
                    failures.append(f"corrupt OOXML: {rel}")
            except Exception as exc:
                failures.append(f"unreadable OOXML: {rel}: {exc}")
        print(f"    {p.stat().st_size/1024:9.0f} KB  {rel}  {tag}")


def main() -> int:
    check_paths()
    check_tracked()
    print("[5] deliverables:")
    check_deliverables()
    check_report()
    print()
    for n in notes:
        print(f"NOTE  {n}")
    for f in failures:
        print(f"FAIL  {f}")
    print(f"\nRESULT: {len(failures)} failures, {len(notes)} notes")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
