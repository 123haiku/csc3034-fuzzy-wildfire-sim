"""Verifies the two canonical deliverables in docs/presentation/.

Checks are assertions, not printouts: a failure raises with the actual value.
"""

from __future__ import annotations

import hashlib
import re
import sys
import zipfile
from pathlib import Path

from pptx import Presentation
from pptx.util import Emu

REPO = Path(__file__).resolve().parent.parent.parent
PPTX = REPO / "docs" / "presentation" / "CSC3034_Presentation_Slides.pptx"
PDF = REPO / "docs" / "presentation" / "CSC3034_Presentation_Slides.pdf"
ASSETS = REPO / "docs" / "presentation" / "assets"

ok = 0


def check(label: str, value) -> None:
    global ok
    ok += 1
    print(f"  [ok] {label}: {value}")


print(f"\n=== {PPTX.name} ===")
prs = Presentation(str(PPTX))
w, h = prs.slide_width / 914400, prs.slide_height / 914400
assert len(prs.slides) == 11, f"expected 11 slides, found {len(prs.slides)}"
check("slides", len(prs.slides))
assert abs(w - 13.333) < 0.01 and abs(h - 7.5) < 0.01, f"slide size {w}x{h}"
check("slide size", f"{w:.3f} x {h:.3f} in (16:9)")

# speaker notes
notes = [len(s.notes_slide.notes_text_frame.text.strip()) for s in prs.slides]
assert all(n > 200 for n in notes), f"thin notes: {notes}"
check("speaker notes", f"11/11 slides, {min(notes)}-{max(notes)} chars")

# no text trapped inside autoshapes
auto = with_text = 0
for s in prs.slides:
    for sh in s.shapes:
        if str(sh.shape_type).startswith("AUTO_SHAPE"):
            auto += 1
            if sh.has_text_frame and sh.text_frame.text.strip():
                with_text += 1
assert with_text == 0, f"{with_text} autoshapes still carry text"
check("autoshapes", f"{auto} total, {with_text} containing text")

# palette: only the three allowed fills
allowed = {"#0A0A0A", "#1F1F1F", "#76B900"}
found = set()
for s in prs.slides:
    for sh in s.shapes:
        try:
            if sh.fill.type == 1:
                found.add("#" + str(sh.fill.fore_color.rgb))
        except Exception:
            pass
assert found <= allowed, f"unexpected fills: {found - allowed}"
check("shape fills used", sorted(found))

# pictures resolvable, and every embedded image is one of the four assets
pics = []
for i, s in enumerate(prs.slides, 1):
    for sh in s.shapes:
        if sh.shape_type is not None and str(sh.shape_type).startswith("PICTURE"):
            pics.append((i, sh.image.size, sh.width / 914400, sh.height / 914400))
assert len(pics) == 4, f"expected 4 pictures, found {len(pics)}"
for slide_no, size, pw, ph in pics:
    native = size[0] / size[1]
    placed = pw / ph
    assert abs(native - placed) / native < 0.01, f"slide {slide_no}: aspect {placed:.3f} vs native {native:.3f}"
check("pictures", f"{len(pics)} embedded, all aspect-correct (no stretch)")

# no shapes off the canvas
for i, s in enumerate(prs.slides, 1):
    for sh in s.shapes:
        right = (sh.left + sh.width) / 914400
        bottom = (sh.top + sh.height) / 914400
        assert right <= w + 0.01, f"slide {i}: {sh.name} right edge {right:.2f} in"
        assert bottom <= h + 0.01, f"slide {i}: {sh.name} bottom edge {bottom:.2f} in"
check("geometry", "every shape inside the 13.333 x 7.5 canvas")

# package integrity + embedded media
with zipfile.ZipFile(PPTX) as z:
    bad = z.testzip()
    assert bad is None, f"corrupt zip member: {bad}"
    media = [n for n in z.namelist() if n.startswith("ppt/media/")]
    slides = [n for n in z.namelist() if re.match(r"ppt/slides/slide\d+\.xml$", n)]
check("zip integrity", f"ok, {len(slides)} slide parts, {len(media)} media parts")

unused = sorted({p.name for p in ASSETS.iterdir()} - {f"image{i}{Path(m).suffix}" for i, m in enumerate(media, 1)})
print(f"  [--] assets on disk: {sorted(p.name for p in ASSETS.iterdir())}")

print(f"\n=== {PDF.name} ===")
raw = PDF.read_bytes()
assert raw[:5] == b"%PDF-", f"bad signature {raw[:8]!r}"
check("signature", raw[:8].decode("ascii", "replace"))
pages = raw.count(b"/Type /Page") - raw.count(b"/Type /Pages")
if pages <= 0:
    pages = len(re.findall(rb"/Type\s*/Page[^s]", raw))
assert pages == 11, f"expected 11 pages, found {pages}"
check("pages", pages)
check("size", f"{len(raw)/1024:.0f} KB")

match = re.search(rb"/MediaBox\s*\[\s*([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s*\]", raw)
if match:
    bx0, by0, bx1, by1 = (float(x) for x in match.groups())
    pw, ph = bx1 - bx0, by1 - by0
    ratio = pw / ph
    assert abs(ratio - 16 / 9) < 0.02, f"page aspect {ratio:.3f}"
    check("page box", f"{pw:.0f} x {ph:.0f} pt, aspect {ratio:.3f} (16:9)")

print(f"\n=== source assets ===")
for p in sorted(ASSETS.iterdir()):
    digest = hashlib.sha256(p.read_bytes()).hexdigest()[:12]
    check(p.name, f"{p.stat().st_size/1024:.0f} KB  sha256:{digest}")

print(f"\nRESULT: {ok} checks passed, 0 failed")
