"""Exports the CSC3034 final report markdown to a professional Microsoft Word (.docx) document."""

from __future__ import annotations

import re
from pathlib import Path
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT

REPO_ROOT = Path(__file__).resolve().parent.parent
REPORT_MD = REPO_ROOT / "docs" / "report" / "REPORT_TEMPLATE.md"
DOCX_OUT = REPO_ROOT / "docs" / "report" / "CSC3034_Final_Report.docx"
PLOTS_DIR = REPO_ROOT / "plots"

# Word cannot render LaTeX, so the note-style maths in the markdown is flattened to
# plain text on export. Each entry is (pattern, literal replacement): replacements are
# literals, never back-references, so a lambda applies them safely below.
LATEX_SUBS = [
    (r"\\text\{s\}", "s"),
    (r"\\text\{([^{}]*)\}", None),
    (r"\\mathrm\{([^{}]*)\}", None),
    (r"\\Big", ""),
    (r"\\big", ""),
    (r"\\left", ""),
    (r"\\right", ""),
    (r"\\mu_\{([^{}]*)\}", "mu_"),
    (r"\\alpha_\{k\}", "alpha_k"),
    (r"\\mu", "\u00b5"),
    (r"\\alpha", "alpha"),
    (r"\\Delta", "\u0394"),
    (r"\\min", "min"),
    (r"\\max", "max"),
    (r"\\in", "in"),
    (r"\\times", "x"),
    (r"\\cdot", "."),
    (r"\\circ", "\u00b0"),
    (r"\\,", " "),
    (r"\\%", "%"),
    (r"\\$", ""),
    (r"\\ ", " "),
    (r"\^", ""),
    (r"\\", ""),
    (r"\$", ""),
    (r"[{}]", ""),
]

# Entries whose replacement is None keep capture group 1 instead of a literal.
GROUP_PASSTHROUGH = {r"\\text\{([^{}]*)\}", r"\\mathrm\{([^{}]*)\}"}


def flatten_math(text: str) -> str:
    """Converts the report's inline LaTeX into plain text for Word."""
    for pattern, repl in LATEX_SUBS:
        if pattern in GROUP_PASSTHROUGH:
            text = re.sub(pattern, lambda m: m.group(1), text)
        else:
            text = re.sub(pattern, lambda _m, literal=repl: literal, text)
    # Tidy the whitespace the substitutions can leave behind.
    text = re.sub(r"\(\s+", "(", text)
    text = re.sub(r"\s+\)", ")", text)
    text = re.sub(r"\s{2,}", " ", text)
    return text


def create_report_docx():
    doc = docx.Document()

    # Page Margins: 1 inch (25.4 mm)
    for section in doc.sections:
        section.top_margin = Inches(1.0)
        section.bottom_margin = Inches(1.0)
        section.left_margin = Inches(1.0)
        section.right_margin = Inches(1.0)

    # Style: Normal
    style = doc.styles['Normal']
    font = style.font
    font.name = 'Times New Roman'
    font.size = Pt(11)
    font.color.rgb = RGBColor(0x1E, 0x29, 0x3B)

    # Title
    title_p = doc.add_paragraph()
    title_p.paragraph_format.space_before = Pt(0)
    title_p.paragraph_format.space_after = Pt(8)
    title_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    title_run = title_p.add_run("Intelligent Forest Fire Risk Assessment and UAV Dispatch\nUsing Mamdani Fuzzy Logic in NVIDIA Isaac Sim")
    title_run.font.size = Pt(18)
    title_run.font.bold = True
    title_run.font.color.rgb = RGBColor(0x0F, 0x17, 0x2A)

    # Subtitle / Course
    sub_p = doc.add_paragraph()
    sub_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    sub_p.paragraph_format.space_after = Pt(14)
    sub_run = sub_p.add_run("CSC3034 Computational Intelligence — Final Technical Project Report\nSunway University | School of Mathematical Sciences & Computing")
    sub_run.font.size = Pt(12)
    sub_run.font.bold = True
    sub_run.font.color.rgb = RGBColor(0xEA, 0x58, 0x0C)

    # Authors Table
    table_auth = doc.add_table(rows=1, cols=4)
    table_auth.alignment = WD_TABLE_ALIGNMENT.CENTER
    authors = [
        ("Yeoh Choon Hern", "23100795", "Project Lead"),
        ("Pang Wei Sheng", "24035115", "Fuzzy Engine & Simulation"),
        ("Roshan A/L Sivakumar", "23028285", "Technical Report"),
        ("Dinesswar A/L Sathasivam", "23096910", "OpenUSD Scene"),
    ]
    hdr_cells = table_auth.rows[0].cells
    for i, (name, sid, role) in enumerate(authors):
        p = hdr_cells[i].paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r1 = p.add_run(f"{name}\n")
        r1.font.bold = True
        r1.font.size = Pt(9.5)
        r2 = p.add_run(f"ID: {sid}\n({role})")
        r2.font.size = Pt(8.5)
        r2.font.color.rgb = RGBColor(0x64, 0x74, 0x8B)

    doc.add_paragraph()  # spacer

    # Read markdown content
    content = REPORT_MD.read_text(encoding="utf-8")
    lines = content.splitlines()

    in_abstract = False
    in_table = False
    table_rows = []

    for line in lines:
        stripped = line.strip()

        # Skip main header lines already formatted
        if stripped.startswith("# Intelligent Forest") or stripped.startswith("**Course**:") or stripped.startswith("**Authors**:") or stripped.startswith("**Institution**:") or stripped.startswith("**Supervisor") or stripped.startswith("**Submission Date"):
            continue

        if stripped == "---":
            continue

        if stripped.startswith("## Abstract"):
            in_abstract = True
            h = doc.add_heading(level=1)
            r = h.add_run("Abstract")
            r.font.size = Pt(14)
            r.font.bold = True
            r.font.color.rgb = RGBColor(0x0F, 0x17, 0x2A)
            continue

        if in_abstract and stripped.startswith("## 1. Introduction"):
            in_abstract = False

        # Display equations ($$...$$) get their own centred monospace paragraph.
        if stripped.startswith("$$") and stripped.endswith("$$") and len(stripped) > 4:
            eq = flatten_math(stripped[2:-2].strip())
            eq_p = doc.add_paragraph()
            eq_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            eq_p.paragraph_format.space_before = Pt(4)
            eq_p.paragraph_format.space_after = Pt(4)
            eq_run = eq_p.add_run(eq)
            eq_run.font.name = "Cambria Math"
            eq_run.font.size = Pt(10)
            eq_run.font.italic = False
            continue

        # Headings
        if stripped.startswith("## "):
            h_text = flatten_math(stripped.replace("## ", "").strip())
            h = doc.add_heading(level=1)
            h.paragraph_format.space_before = Pt(14)
            h.paragraph_format.space_after = Pt(4)
            r = h.add_run(h_text)
            r.font.size = Pt(13)
            r.font.bold = True
            r.font.color.rgb = RGBColor(0x0F, 0x17, 0x2A)
            continue

        if stripped.startswith("### "):
            h_text = flatten_math(stripped.replace("### ", "").strip())
            h = doc.add_heading(level=2)
            h.paragraph_format.space_before = Pt(10)
            h.paragraph_format.space_after = Pt(3)
            r = h.add_run(h_text)
            r.font.size = Pt(11.5)
            r.font.bold = True
            r.font.color.rgb = RGBColor(0x1E, 0x29, 0x3B)
            continue

        if stripped.startswith("#### "):
            h_text = flatten_math(stripped.replace("#### ", "").strip())
            h = doc.add_heading(level=3)
            r = h.add_run(h_text)
            r.font.size = Pt(11)
            r.font.bold = True
            continue

        # Bullet points
        if stripped.startswith("* ") or stripped.startswith("- "):
            p = doc.add_paragraph(style='List Bullet')
            p.paragraph_format.space_after = Pt(2)
            clean_text = flatten_math(stripped[2:].strip())
            # Clean basic markdown bold
            parts = re.split(r'(\*\*[^*]+\*\*)', clean_text)
            for pt in parts:
                if pt.startswith("**") and pt.endswith("**"):
                    r = p.add_run(pt[2:-2])
                    r.font.bold = True
                else:
                    p.add_run(pt)
            continue

        # Tables in markdown
        if stripped.startswith("|") and stripped.endswith("|"):
            cells = [c.strip() for c in stripped.split("|")[1:-1]]
            if all(set(c).issubset({'-', ':', ' '}) for c in cells):
                continue  # header divider
            table_rows.append(cells)
            in_table = True
            continue
        elif in_table and table_rows:
            # Commit table
            num_cols = len(table_rows[0])
            doc_table = doc.add_table(rows=len(table_rows), cols=num_cols)
            doc_table.alignment = WD_TABLE_ALIGNMENT.CENTER
            for r_idx, r_data in enumerate(table_rows):
                row = doc_table.rows[r_idx]
                for c_idx, cell_value in enumerate(r_data[:num_cols]):
                    c = row.cells[c_idx]
                    cp = c.paragraphs[0]
                    cp.paragraph_format.space_after = Pt(1)
                    cp.paragraph_format.space_before = Pt(1)
                    clean_cell = flatten_math(cell_value.replace("**", "").replace("`", ""))
                    cr = cp.add_run(clean_cell)
                    cr.font.size = Pt(9)
                    if r_idx == 0:
                        cr.font.bold = True
            doc.add_paragraph()  # spacer
            table_rows = []
            in_table = False

        # Regular paragraphs
        if stripped:
            p = doc.add_paragraph()
            p.paragraph_format.space_after = Pt(5)
            p.paragraph_format.line_spacing = 1.15
            parts = re.split(r'(\*\*[^*]+\*\*)', flatten_math(stripped))
            for pt in parts:
                if pt.startswith("**") and pt.endswith("**"):
                    r = p.add_run(pt[2:-2])
                    r.font.bold = True
                else:
                    p.add_run(pt)

    # Insert images if referenced
    if (PLOTS_DIR / "membership_functions.png").exists():
        doc.add_page_break()
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.add_run().font.bold = True
        doc.add_picture(str(PLOTS_DIR / "membership_functions.png"), width=Inches(6.2))
        cp = doc.add_paragraph()
        cp.alignment = WD_ALIGN_PARAGRAPH.CENTER
        cr = cp.add_run("Figure 1: Full 7-Variable Linguistic Fuzzy Membership Functions "
                        "(4 inputs, 3 outputs).")
        cr.font.size = Pt(9.5)
        cr.font.italic = True

    if (PLOTS_DIR / "mission_telemetry_dashboard.png").exists():
        doc.add_page_break()
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        doc.add_picture(str(PLOTS_DIR / "mission_telemetry_dashboard.png"), width=Inches(6.2))
        cp = doc.add_paragraph()
        cp.alignment = WD_ALIGN_PARAGRAPH.CENTER
        cr = cp.add_run("Figure 2: 3D Autonomous UAV Flight Path & Multi-Variable Telemetry Response Timeline.")
        cr.font.size = Pt(9.5)
        cr.font.italic = True

    if (PLOTS_DIR / "output_membership_functions.png").exists():
        doc.add_page_break()
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        doc.add_picture(str(PLOTS_DIR / "output_membership_functions.png"), width=Inches(5.4))
        cp = doc.add_paragraph()
        cp.alignment = WD_ALIGN_PARAGRAPH.CENTER
        cr = cp.add_run("Figure 3: The Three Output Universes (Fire Risk Index, Patrol Urgency, Suppression Alert).")
        cr.font.size = Pt(9.5)
        cr.font.italic = True

    doc.save(str(DOCX_OUT))
    print(f"[Report] Generated Word document (.docx): {DOCX_OUT} ({DOCX_OUT.stat().st_size:,} bytes)")


if __name__ == "__main__":
    create_report_docx()
