"""Exports REPORT_TEMPLATE.md to a formatted Word document.

    python src/export_report_docx.py

The Markdown is parsed into blocks (fenced code, display maths, tables, headings,
lists, paragraphs) and each block is emitted with the Word construct it needs. A
line-by-line emitter was the previous design and it produced four visible defects:
the ASCII architecture diagram was torn apart as a Markdown table, multi-line
paragraphs were split into one paragraph per source line, backticks reached the
page, and the display equations came out as unreadable run-together text.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import List, Optional, Tuple

import docx
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor

REPO_ROOT = Path(__file__).resolve().parent.parent
REPORT_MD = REPO_ROOT / "docs" / "report" / "REPORT_TEMPLATE.md"
DOCX_OUT = REPO_ROOT / "docs" / "report" / "CSC3034_Final_Report.docx"
PLOTS_DIR = REPO_ROOT / "plots"
MEASUREMENTS = REPO_ROOT / "docs" / "measurements.json"

INK = RGBColor(0x0F, 0x17, 0x2A)
BODY_INK = RGBColor(0x1E, 0x29, 0x3B)
MUTED = RGBColor(0x64, 0x74, 0x8B)
ACCENT = RGBColor(0xEA, 0x58, 0x0C)

# ---------------------------------------------------------------------------
# LaTeX -> linear plain text
# ---------------------------------------------------------------------------

GREEK = {
    "alpha": "\u03b1", "beta": "\u03b2", "gamma": "\u03b3", "delta": "\u03b4",
    "epsilon": "\u03b5", "lambda": "\u03bb", "mu": "\u03bc", "nu": "\u03bd",
    "pi": "\u03c0", "rho": "\u03c1", "sigma": "\u03c3", "tau": "\u03c4",
    "theta": "\u03b8", "phi": "\u03c6", "psi": "\u03c8", "omega": "\u03c9",
    "Delta": "\u0394", "Sigma": "\u03a3", "Omega": "\u03a9", "Phi": "\u03a6",
}

SYMBOLS = {
    "in": "\u2208", "notin": "\u2209", "times": "\u00d7", "cdot": "\u00b7",
    "pm": "\u00b1", "le": "\u2264", "leq": "\u2264", "ge": "\u2265",
    "geq": "\u2265", "neq": "\u2260", "approx": "\u2248", "to": "\u2192",
    "rightarrow": "\u2192", "leftarrow": "\u2190", "infty": "\u221e",
    "partial": "\u2202", "int": "\u222b", "sum": "\u03a3", "prod": "\u03a0",
    "circ": "\u00b0", "degree": "\u00b0", "equiv": "\u2261",
}

WORD_FUNCS = {"min", "max", "exp", "log", "ln", "round", "arctan2", "arctan", "mod"}

# Commands that take exactly one braced argument and keep only its content.
PASSTHROUGH_ONE_ARG = {"text", "mathrm", "mathbf", "mathit", "operatorname", "mathcal"}

# Commands that carry no typographic content once flattened.
DROP = {
    "Big", "big", "bigg", "Bigg", "left", "right", "displaystyle", "textstyle",
    "limits", "nolimits", "quad", "qquad", "!", ",", ";", ":", " ", "thinspace",
}


class _LatexToText:
    """Brace-aware converter for the small LaTeX subset used in the report."""

    def __init__(self, source: str) -> None:
        self.s = source
        self.i = 0

    def convert(self) -> str:
        out = self._parse(None)
        return _tidy(out)

    # -- internals ---------------------------------------------------------
    def _parse(self, stop: Optional[str]) -> str:
        parts: List[str] = []
        while self.i < len(self.s):
            ch = self.s[self.i]
            if stop is not None and ch == stop:
                break
            if ch == "\\":
                parts.append(self._command())
            elif ch in "{}":
                self.i += 1
            elif ch in "^_":
                self.i += 1
                body = self._script_body()
                if ch == "^" and body.strip() == "*":
                    # y^* / A^*: the star is part of the symbol, not an emphasis marker,
                    # so it is written as the asterisk operator and left alone downstream.
                    parts.append("\u2217")
                else:
                    parts.append((" " if ch == "^" else "_") + body)
            elif ch == "&":
                self.i += 1
            else:
                parts.append(ch)
                self.i += 1
        return "".join(parts)

    def _script_body(self) -> str:
        if self.i < len(self.s) and self.s[self.i] == "{":
            return "(" + self._group() + ")"
        if self.i < len(self.s):
            ch = self.s[self.i]
            self.i += 1
            return ch
        return ""

    def _group(self) -> str:
        while self.i < len(self.s) and self.s[self.i].isspace():
            self.i += 1
        if self.i < len(self.s) and self.s[self.i] == "{":
            self.i += 1
            body = self._parse("}")
            self.i += 1
            return body
        if self.i < len(self.s):
            ch = self.s[self.i]
            self.i += 1
            return ch
        return ""

    def _command(self) -> str:
        self.i += 1  # backslash
        if self.i >= len(self.s):
            return ""
        if not self.s[self.i].isalpha():
            ch = self.s[self.i]
            self.i += 1
            return SYMBOLS.get(ch, ch)
        start = self.i
        while self.i < len(self.s) and self.s[self.i].isalpha():
            self.i += 1
        name = self.s[start:self.i]

        if name == "frac":
            num = self._group_maybe_braced()
            den = self._group_maybe_braced()
            return f"({num}) / ({den})"
        if name == "sqrt":
            return "\u221a(" + self._group_maybe_braced() + ")"
        if name in PASSTHROUGH_ONE_ARG:
            return self._group_maybe_braced()
        if name in DROP:
            return ""
        if name in GREEK:
            return GREEK[name]
        if name in SYMBOLS:
            return SYMBOLS[name]
        if name in WORD_FUNCS:
            return name
        return name

    def _group_maybe_braced(self) -> str:
        while self.i < len(self.s) and self.s[self.i].isspace():
            self.i += 1
        if self.i < len(self.s) and self.s[self.i] == "{":
            return self._group()
        if self.i < len(self.s):
            ch = self.s[self.i]
            self.i += 1
            return ch
        return ""


def _tidy(text: str) -> str:
    text = text.replace("\u00b5", "\u03bc")
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"\(\s+", "(", text)
    text = re.sub(r"\s+\)", ")", text)
    text = re.sub(r"\s+([,.;:])", r"\1", text)
    text = re.sub(r"\s*/\s*", " / ", text)
    text = re.sub(r"(?<=[A-Za-z])\s*_\s*(?=[A-Za-z])", "_", text)
    return text.strip()


def math_to_text(source: str) -> str:
    """Flattens one LaTeX expression into linear plain text."""
    # ^\circ and ^{\circ} are a degree sign, not a superscripted command name.
    source = source.replace("^{\\circ}", "\\degree").replace("^\\circ", "\\degree")
    return _LatexToText(source).convert()


INLINE_MATH = re.compile(r"\$([^$]+)\$")


def flatten_inline(text: str) -> str:
    """Replaces every $...$ span with its flattened text, leaving prose alone."""
    return INLINE_MATH.sub(lambda m: math_to_text(m.group(1)), text)


# ---------------------------------------------------------------------------
# Measured values
# ---------------------------------------------------------------------------

def load_measurements() -> dict:
    """Reads docs/measurements.json, which tools/presentation/measure.py writes."""
    if not MEASUREMENTS.exists():
        raise SystemExit(
            f"[Report] missing {MEASUREMENTS}; run: python tools/presentation/measure.py"
        )
    return json.loads(MEASUREMENTS.read_text(encoding="utf-8"))


MEASURED = load_measurements()

VALUE_TOKEN = re.compile(r"\{\{\s*([A-Za-z0-9_.]+)\s*\}\}")


def _format_value(key: str, value) -> str:
    if isinstance(value, float):
        if key.endswith("_ms"):
            return f"{value:.3f}"
        if key.endswith("deviation"):
            return f"{value:.3f}"
        if value.is_integer():
            return str(int(value))
        return f"{value:g}"
    return str(value)


def resolve(path: str):
    node = MEASURED
    for part in path.split("."):
        if isinstance(node, list):
            node = node[int(part)]
        else:
            node = node[part]
    return node


def substitute(text: str) -> str:
    """Replaces {{a.b.c}} with the value measured into measurements.json."""
    def repl(match: re.Match) -> str:
        path = match.group(1)
        try:
            return _format_value(path, resolve(path))
        except (KeyError, IndexError, ValueError) as exc:
            raise SystemExit(f"[Report] unknown measurement token {{{{{path}}}}}: {exc}")

    return VALUE_TOKEN.sub(repl, text)


def mission_table() -> List[List[str]]:
    rows = [["WP", "Position (X, Y, Z)", "T (\u00b0C)", "RH (%)", "W (km/h)",
             "F (%)", "FRI", "Urgency (%)", "Alert", "Status"]]
    for m in MEASURED["mission"]:
        rows.append([
            f"{m['step']:02d}",
            f"({m['x']:.1f}, {m['y']:.1f}, {m['z']:.1f})",
            f"{m['temperature']:.1f}",
            f"{m['humidity']:.1f}",
            f"{m['wind_speed']:.1f}",
            f"{m['vegetation_dryness']:.1f}",
            f"{m['fire_risk_index']:.1f}",
            f"{m['patrol_urgency']:.1f}",
            f"{m['suppression_alert']:.3f}",
            m["alert_name"],
        ])
    return rows


def defuzz_table() -> List[List[str]]:
    rows = [["Environmental scenario", "Centroid (COG)", "Bisector", "Mean of Maximum (MOM)"]]
    for r in MEASURED["defuzz"]:
        t, rh, w, f = r["inputs"]
        label = f"{r['scenario']} (T = {t:g}, RH = {rh:g}, W = {w:g}, F = {f:g})"
        rows.append([label, f"{r['centroid']:.1f}", f"{r['bisector']:.1f}", f"{r['mom']:.1f}"])
    return rows


GENERATED_TABLES = {
    "{{TABLE_MISSION}}": (mission_table, 10),
    "{{TABLE_DEFUZZ}}": (defuzz_table, 4),
}


# ---------------------------------------------------------------------------
# Markdown block parsing
# ---------------------------------------------------------------------------

Block = Tuple[str, object]


def parse_blocks(markdown: str) -> List[Block]:
    lines = markdown.splitlines()
    blocks: List[Block] = []
    i = 0
    while i < len(lines):
        raw = lines[i]
        s = raw.strip()
        if not s:
            i += 1
            continue

        # A list item wrapped onto an indented continuation line stays one item. Without
        # this the continuation became a full-width paragraph under a half-finished bullet.
        if (
            blocks
            and blocks[-1][0] in ("bullet", "number")
            and raw[:1] in (" ", "\t")
            and not re.match(r"^(?:[*+-]|\d+\.)\s+", s)
        ):
            if blocks[-1][0] == "bullet":
                blocks[-1] = ("bullet", str(blocks[-1][1]) + " " + s)
            else:
                number, text = blocks[-1][1]  # type: ignore[misc]
                blocks[-1] = ("number", (number, text + " " + s))
            i += 1
            continue

        if s.startswith("```"):
            i += 1
            buf: List[str] = []
            while i < len(lines) and not lines[i].strip().startswith("```"):
                buf.append(lines[i].rstrip())
                i += 1
            i += 1
            blocks.append(("code", "\n".join(buf)))
            continue

        if s.startswith("$$"):
            if s.endswith("$$") and len(s) > 4:
                blocks.append(("math", s[2:-2].strip()))
                i += 1
                continue
            i += 1
            buf = []
            while i < len(lines) and "$$" not in lines[i]:
                buf.append(lines[i].strip())
                i += 1
            i += 1
            blocks.append(("math", " ".join(buf)))
            continue

        m = re.match(r"^(#{1,4})\s+(.*)$", s)
        if m:
            blocks.append(("heading", (len(m.group(1)), m.group(2).strip())))
            i += 1
            continue

        if s == "---":
            i += 1
            continue

        if s.startswith("|"):
            buf = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                buf.append(lines[i].strip())
                i += 1
            blocks.append(("table", buf))
            continue

        if re.match(r"^[*+-]\s+", s):
            blocks.append(("bullet", re.sub(r"^[*+-]\s+", "", s)))
            i += 1
            continue

        m = re.match(r"^(\d+)\.\s+(.*)$", s)
        if m:
            blocks.append(("number", (m.group(1), m.group(2))))
            i += 1
            continue

        buf = [s]
        i += 1
        while i < len(lines):
            t = lines[i].strip()
            if (
                not t
                or t.startswith("|")
                or t.startswith("```")
                or t.startswith("#")
                or t.startswith("$$")
                or re.match(r"^[*+-]\s+", t)
                or re.match(r"^\d+\.\s+", t)
            ):
                break
            buf.append(t)
            i += 1
        blocks.append(("para", " ".join(buf)))

    return blocks


# ---------------------------------------------------------------------------
# Rich-text runs
# ---------------------------------------------------------------------------

TOKEN = re.compile(r"(\*\*[^*]+\*\*|\*[^*]+\*|`[^`]+`)")


def add_runs(paragraph, text: str, size: Optional[float] = None,
             bold: bool = False, italic: bool = False,
             color: Optional[RGBColor] = None) -> None:
    """Adds text to a paragraph, honouring **bold**, *italic* and `code` spans."""
    flat = flatten_inline(text)
    for token in TOKEN.split(flat):
        if not token:
            continue
        if token.startswith("**") and token.endswith("**") and len(token) > 4:
            run = paragraph.add_run(token[2:-2])
            run.font.bold = True
        elif token.startswith("`") and token.endswith("`") and len(token) > 2:
            run = paragraph.add_run(token[1:-1])
            run.font.name = "Consolas"
            run.font.bold = bold
        elif token.startswith("*") and token.endswith("*") and len(token) > 2:
            run = paragraph.add_run(token[1:-1])
            run.font.italic = True
        else:
            run = paragraph.add_run(token)
            if bold:
                run.font.bold = True
        if italic:
            run.font.italic = True
        if size is not None:
            run.font.size = Pt(size)
        if color is not None:
            run.font.color.rgb = color


# ---------------------------------------------------------------------------
# Document furniture
# ---------------------------------------------------------------------------


def add_field(paragraph, instruction: str) -> None:
    run = paragraph.add_run()
    begin = OxmlElement("w:fldChar")
    begin.set(qn("w:fldCharType"), "begin")
    instr = OxmlElement("w:instrText")
    instr.set(qn("xml:space"), "preserve")
    instr.text = instruction
    end = OxmlElement("w:fldChar")
    end.set(qn("w:fldCharType"), "end")
    run._r.append(begin)
    run._r.append(instr)
    run._r.append(end)


def configure_page(section) -> None:
    section.top_margin = Inches(1.0)
    section.bottom_margin = Inches(0.9)
    section.left_margin = Inches(0.95)
    section.right_margin = Inches(0.95)

    footer = section.footer.paragraphs[0]
    footer.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = footer.add_run("CSC3034 Final Report  \u00b7  ")
    run.font.size = Pt(8.5)
    run.font.color.rgb = MUTED
    add_field(footer, "PAGE")
    for r in footer.runs:
        r.font.size = Pt(8.5)
        r.font.color.rgb = MUTED


def set_repeat_header(row) -> None:
    tr_pr = row._tr.get_or_add_trPr()
    header = OxmlElement("w:tblHeader")
    header.set(qn("w:val"), "true")
    tr_pr.append(header)
    cant_split = OxmlElement("w:cantSplit")
    tr_pr.append(cant_split)


def style_table(table, body_size: float) -> None:
    table.style = "Table Grid"
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = True
    for r_idx, row in enumerate(table.rows):
        if r_idx == 0:
            set_repeat_header(row)
        for cell in row.cells:
            for paragraph in cell.paragraphs:
                paragraph.paragraph_format.space_before = Pt(1)
                paragraph.paragraph_format.space_after = Pt(1)
                for run in paragraph.runs:
                    run.font.size = Pt(body_size)
                    if r_idx == 0:
                        run.font.bold = True


# ---------------------------------------------------------------------------
# Build
# ---------------------------------------------------------------------------

FIGURE_ANCHORS = {
    "*(Figure 1 below is generated": [
        ("architecture_diagram.png", 6.2,
         "Figure 1: The three-module control loop. Synthetic telemetry crosses from the "
         "OpenUSD stage into the Mamdani engine, and the defuzzified consequents are written "
         "back onto the same stage."),
    ],
    "*(Figure 2 plots all seven": [
        ("membership_functions.png", 6.3,
         "Figure 2: The seven linguistic variables of the controller. The first four panels "
         "are the inputs (temperature, humidity, wind, fuel dryness); the remaining panels are "
         "the three defuzzified outputs."),
        ("output_membership_functions.png", 5.6,
         "Figure 3: The three output universes drawn separately, including the "
         "suppression-alert consequent whose tiers are inferred by the rule base."),
    ],
    "*(Figure 4 replays": [
        ("mission_telemetry_dashboard.png", 6.3,
         "Figure 4: Mission replay for seed = 0. Top left, the 3D flight path coloured by "
         "fire risk index over the three hotspots; the remaining panels are the four sensor "
         "series and the two actuation outputs across the 12 waypoints."),
    ],
}

SKIP_PARAGRAPH_PREFIXES = (
    "**Course**", "**Institution**", "**Supervisor", "**Authors**", "**Submission Date",
)


def add_figure(doc, filename: str, width_in: float, caption: str) -> None:
    path = PLOTS_DIR / filename
    if not path.exists():
        print(f"[Report] WARNING missing figure, skipped: {path}")
        return
    picture_p = doc.add_paragraph()
    picture_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    picture_p.paragraph_format.space_before = Pt(6)
    picture_p.paragraph_format.space_after = Pt(2)
    picture_p.add_run().add_picture(str(path), width=Inches(width_in))

    caption_p = doc.add_paragraph()
    caption_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    caption_p.paragraph_format.space_after = Pt(10)
    run = caption_p.add_run(caption)
    run.font.size = Pt(9)
    run.font.italic = True
    run.font.color.rgb = MUTED


def create_report_docx() -> Path:
    doc = docx.Document()
    for section in doc.sections:
        configure_page(section)

    normal = doc.styles["Normal"]
    normal.font.name = "Times New Roman"
    normal.font.size = Pt(11)
    normal.font.color.rgb = BODY_INK
    normal.paragraph_format.space_after = Pt(6)
    normal.paragraph_format.line_spacing = 1.12

    # ---- Title block -----------------------------------------------------
    title_p = doc.add_paragraph()
    title_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    title_p.paragraph_format.space_after = Pt(8)
    title_run = title_p.add_run(
        "Intelligent Forest Fire Risk Assessment and UAV Dispatch\n"
        "Using Mamdani Fuzzy Logic in NVIDIA Isaac Sim"
    )
    title_run.font.size = Pt(18)
    title_run.font.bold = True
    title_run.font.color.rgb = INK

    sub_p = doc.add_paragraph()
    sub_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    sub_p.paragraph_format.space_after = Pt(4)
    sub_run = sub_p.add_run(
        "CSC3034 Computational Intelligence \u2014 Final Technical Project Report"
    )
    sub_run.font.size = Pt(12)
    sub_run.font.bold = True
    sub_run.font.color.rgb = ACCENT

    inst_p = doc.add_paragraph()
    inst_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    inst_p.paragraph_format.space_after = Pt(12)
    inst_run = inst_p.add_run(
        "Sunway University \u00b7 School of Mathematical Sciences & Computing\n"
        "Supervisor: Dr. Tang Tiong Yew \u00b7 November 2026"
    )
    inst_run.font.size = Pt(10.5)
    inst_run.font.color.rgb = MUTED

    table_auth = doc.add_table(rows=1, cols=4)
    table_auth.style = "Table Grid"
    table_auth.alignment = WD_TABLE_ALIGNMENT.CENTER
    authors = [
        ("Yeoh Choon Hern", "23100795", "Project Lead"),
        ("Pang Wei Sheng", "24035115", "Fuzzy Engine & Simulation"),
        ("Roshan A/L Sivakumar", "23028285", "Technical Report"),
        ("Dinesswar A/L Sathasivam", "23096910", "OpenUSD Scene"),
    ]
    for i, (name, sid, role) in enumerate(authors):
        p = table_auth.rows[0].cells[i].paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r1 = p.add_run(name + "\n")
        r1.font.bold = True
        r1.font.size = Pt(9.5)
        r2 = p.add_run(f"ID: {sid}\n({role})")
        r2.font.size = Pt(8.5)
        r2.font.color.rgb = MUTED

    doc.add_paragraph()

    # ---- Body ------------------------------------------------------------
    blocks = parse_blocks(REPORT_MD.read_text(encoding="utf-8"))
    pending_caption: Optional[str] = None
    first_heading_seen = False

    for kind, payload in blocks:
        if kind == "heading":
            level, text = payload  # type: ignore[misc]
            if level == 1 and not first_heading_seen:
                first_heading_seen = True
                continue  # document title already emitted above
            first_heading_seen = True
            style = {2: 1, 3: 2, 4: 3}.get(level, 3)
            h = doc.add_heading(level=style)
            h.paragraph_format.space_before = Pt(15 if level == 2 else 10)
            h.paragraph_format.space_after = Pt(4)
            h.paragraph_format.keep_with_next = True
            size = 13.5 if level == 2 else (12 if level == 3 else 11)
            run = h.add_run(substitute(flatten_inline(text)))
            run.font.name = "Times New Roman"
            run.font.size = Pt(size)
            run.font.bold = True
            run.font.color.rgb = INK if level == 2 else BODY_INK
            continue

        if kind == "code":
            code = str(payload)
            para = doc.add_paragraph()
            para.paragraph_format.space_before = Pt(6)
            para.paragraph_format.space_after = Pt(6)
            para.paragraph_format.line_spacing = 1.0
            para.paragraph_format.left_indent = Inches(0.0)
            run = para.add_run(code)
            run.font.name = "Consolas"
            run.font.size = Pt(7.5)
            run.font.color.rgb = BODY_INK
            continue

        if kind == "math":
            expr = math_to_text(str(payload))
            para = doc.add_paragraph()
            para.alignment = WD_ALIGN_PARAGRAPH.CENTER
            para.paragraph_format.space_before = Pt(6)
            para.paragraph_format.space_after = Pt(6)
            run = para.add_run(expr)
            run.font.name = "Cambria Math"
            run.font.size = Pt(11)
            continue

        if kind == "bullet":
            para = doc.add_paragraph(style="List Bullet")
            para.paragraph_format.space_after = Pt(3)
            para.paragraph_format.left_indent = Inches(0.3)
            add_runs(para, substitute(str(payload)))
            continue

        if kind == "number":
            number, text = payload  # type: ignore[misc]
            para = doc.add_paragraph()
            para.paragraph_format.space_after = Pt(4)
            para.paragraph_format.left_indent = Inches(0.32)
            para.paragraph_format.first_line_indent = Inches(-0.32)
            add_runs(para, substitute(f"{number}.\u2002{text}"))
            continue

        if kind == "table":
            rows = [r for r in payload if not re.fullmatch(r"[\|\-:\s]+", r)]  # type: ignore[union-attr]
            cells = [[c.strip() for c in row.strip("|").split("|")] for row in rows]
            n_cols = max(len(r) for r in cells)
            if pending_caption:
                caption_p = doc.add_paragraph()
                caption_p.paragraph_format.space_before = Pt(6)
                caption_p.paragraph_format.space_after = Pt(3)
                caption_p.paragraph_format.keep_with_next = True
                run = caption_p.add_run(pending_caption)
                run.font.size = Pt(8.5)
                run.font.italic = True
                run.font.color.rgb = MUTED
                pending_caption = None
            table = doc.add_table(rows=len(cells), cols=n_cols)
            for r_idx, row in enumerate(cells):
                for c_idx in range(n_cols):
                    value = row[c_idx] if c_idx < len(row) else ""
                    cell = table.rows[r_idx].cells[c_idx]
                    para = cell.paragraphs[0]
                    para.paragraph_format.space_before = Pt(1)
                    para.paragraph_format.space_after = Pt(1)
                    if c_idx > 0:
                        para.alignment = WD_ALIGN_PARAGRAPH.CENTER
                    add_runs(para, value)
            style_table(table, 7.5 if n_cols >= 9 else 8.5)
            doc.add_paragraph()
            continue

        # paragraph
        text = str(payload)
        if text.startswith(SKIP_PARAGRAPH_PREFIXES):
            continue

        if text.strip() in GENERATED_TABLES:
            builder, n_cols = GENERATED_TABLES[text.strip()]
            if pending_caption:
                caption_p = doc.add_paragraph()
                caption_p.paragraph_format.space_before = Pt(6)
                caption_p.paragraph_format.space_after = Pt(3)
                caption_p.paragraph_format.keep_with_next = True
                run = caption_p.add_run(pending_caption)
                run.font.size = Pt(8.5)
                run.font.italic = True
                run.font.color.rgb = MUTED
                pending_caption = None
            cells = builder()
            table = doc.add_table(rows=len(cells), cols=n_cols)
            for r_idx, row in enumerate(cells):
                for c_idx in range(n_cols):
                    cell = table.rows[r_idx].cells[c_idx]
                    para = cell.paragraphs[0]
                    para.paragraph_format.space_before = Pt(1)
                    para.paragraph_format.space_after = Pt(1)
                    if c_idx > 0:
                        para.alignment = WD_ALIGN_PARAGRAPH.CENTER
                    add_runs(para, row[c_idx] if c_idx < len(row) else "")
            style_table(table, 7.5 if n_cols >= 9 else 8.5)
            doc.add_paragraph()
            continue

        anchor = next((k for k in FIGURE_ANCHORS if text.startswith(k)), None)
        if anchor is not None:
            for filename, width, caption in FIGURE_ANCHORS[anchor]:
                add_figure(doc, filename, width, caption)
            continue

        if text.startswith("**Table") and text.endswith("**"):
            pending_caption = text.strip("*").strip()
            continue

        para = doc.add_paragraph()
        para.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        para.paragraph_format.space_after = Pt(6)
        body = substitute(text)
        if body.startswith("**Keywords**"):
            add_runs(para, body, size=10)
        else:
            add_runs(para, body)

    doc.save(str(DOCX_OUT))
    size = DOCX_OUT.stat().st_size
    print(f"[Report] Generated Word document (.docx): {DOCX_OUT} ({size:,} bytes)")
    return DOCX_OUT


if __name__ == "__main__":
    try:
        create_report_docx()
    except Exception as exc:  # noqa: BLE001 - surface the failure with a non-zero exit
        print(f"[Report] FAILED: {exc}", file=sys.stderr)
        raise
