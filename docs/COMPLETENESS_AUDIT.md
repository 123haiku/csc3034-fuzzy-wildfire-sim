# Repository Completeness Audit

Audit date: 2026-11-14, second pass 2026-11-15. Repository:
`123haiku/csc3034-fuzzy-wildfire-sim`. Branch `main`, remote `origin` in sync.

## Verdict

Ready to submit against the Assignment 1 brief. The three deliverables exist, are generated from
the code rather than transcribed, and every gate in `docs/SUBMISSION.md` returns the count it
claims. The formatting pass on 15 November brought the report inside the 10-page cap and matched
its section structure to the brief.

## Assignment 1 brief compliance

| Brief requirement | Where it is met | Evidence |
|---|---|---|
| Functional fuzzy system | `src/fuzzy_system/controller.py` (Mamdani, 4 inputs, 3 consequents), `isaac_sim_bridge.py`, `create_wildfire_stage.py` | `pytest -q` -> 25 passed; the extracted `CSC3034_Fuzzy_System.zip` runs the same 25 tests |
| Software must use NVIDIA Isaac Sim | OpenUSD stage `assets/wildfire_forest_uav_stage.usda` (65 x 65 m, 47 trees, 3 hotspots, 14 UAV keyframes) driven by the Isaac Sim bridge | Poster badge "NVIDIA Isaac Sim 6.2.0"; report Section 2.6 |
| A1-sized infographic poster | `docs/poster/CSC3034_A1_Poster.pdf` | 1 page, 1684 x 2385 pt = 594 x 841 mm, 300 DPI PNG alongside |
| Report: max 10 pages excluding cover and references | 10 pages total: page 1 is the cover, body runs pages 2-10 with the reference list closing page 10 | `pypdf` page count 10; body without cover and references is 8 full pages plus the head of page 10 |
| Cover page with group information | Page 1: title, course line, institution, supervisor, four students with IDs and roles | Rendered page 1; no running footer on the cover |
| Body font 11 pt or above | Body 11 pt Times New Roman, line spacing 1.12 | DOCX style inspection; table body and captions are 9.5 pt |
| 1. Introduction: problem definition and motivation (SDGs) | Section 1.1, with SDG 13 Target 13.1 and SDG 15 Target 15.2 named | Heading scan |
| 1. Introduction: existing solutions | Section 1.2, three families: deterministic indices, learning-based perception, simulation-only studies | Heading scan; citations [1]-[5] |
| 2. System design | Sections 2.1 architecture, 2.2 inputs, 2.3 outputs, 2.4 rule base, 2.5 defuzzification, 2.6 Isaac Sim stage and UAV | Heading scan; Figure 1, Table 1 |
| 3. Evaluation: case study | Section 3.1, 12-waypoint seed-0 mission with the full telemetry log and mission replay | Table 2 (12/12 rows match the measurement), Figure 3 |
| 3. Evaluation: discussion of output and impact | Section 3.4: output behaviour, auditability, noise robustness, SDG impact, limitations | Section 3.4 text; `tools/report/rule_trace.py` reproduces the trace quoted there |
| 4. Conclusion | Section 4, plus the future-work paragraph | Heading scan |
| Poster summarises the report | Sections 01-07 mirror the report's motivation, rule base, defuzzification, stage, flight results and conclusion | Rendered poster; every figure on it comes from `docs/measurements.json` |

## Checks run and returned

| # | Check | Command | Result |
|---|---|---|---|
| 1 | Unit tests | `python -m pytest -q` | `25 passed` |
| 2 | Engine vs scikit-fuzzy | `python -m src.fuzzy_system.reference_engine --tolerance 0.5` | 9/9 scenarios within tolerance, worst deviation 0.069 |
| 3 | Figure consistency | `python tools/verify_values.py` | `36 passed, 0 failed` (required figures present, superseded figures absent, both tables row-exact) |
| 4 | Report layout | `python tools/report/audit_report_docx.py` | 0 rendering defects; 6 Heading 1, 13 Heading 2, 5 tables, 3 figures, 2861 words |
| 5 | Citation wiring | `python tools/report/check_citations.py` | 6 reference entries, 6 cited, no dangling citation |
| 6 | Structure and links | `python tools/audit_repo.py` | 12 Markdown files, 58 referenced paths, 0 missing, 0 tracked-but-absent, 0 failures |
| 7 | Deck | `python tools/presentation/verify_deck.py` | `16 checks passed` (11 slides, 16:9, notes 11/11, 4 pictures, zip intact) |
| 8 | Encoding | `python tools/report/fix_encoding.py` | every source `clean`, 0 residual mojibake markers |
| 9 | Deliverable geometry | `pypdf` | report 10 pages A4 595 x 842 pt; poster 1 page 1684 x 2385 pt = 594 x 841 mm; deck 11 pages 960 x 540 pt |

Deliverables:

| Deliverable | File | Verified property |
|---|---|---|
| A1 poster | `docs/poster/CSC3034_A1_Poster.pdf` | 1 page, 594 x 841 mm, `%PDF` signature, footer carries the repository URL only |
| Poster raster | `docs/poster/CSC3034_A1_Poster_300DPI.png` | 3.8 MB, tracked |
| Report | `docs/report/CSC3034_Final_Report.docx` | OOXML zip intact, 10 pages when exported |
| Report PDF | `docs/report/CSC3034_Final_Report.pdf` | 10 pages, A4, text extractable, 0 mojibake |
| Deck | `docs/presentation/CSC3034_Presentation_Slides.pptx` / `.pdf` | 11 slides, 13.333 x 7.5 in, 11 PDF pages |
| Proposal | `docs/proposal/CSC3034_Group_Proposal_Form.docx` / `.md` | zip intact, Markdown source present |
| Stage asset | `assets/wildfire_forest_uav_stage.usda` | 75 KB OpenUSD layer, referenced by the stage builder |

## Defects found and fixed

1. **Reference list with no in-text citations.** `check_citations.py` reported entries 1, 2, 4, 5 and
   6 never cited; the only bracketed numbers in the body were input-universe bounds such as
   `[0, 50]`. `[1]`-`[6]` are now wired into Sections 1.1, 1.2, 2.4 and 3.4.
2. **Mojibake in the shipped report.** Eight sequences of a UTF-8 em dash decoded as cp1252 sat in
   five paragraphs and were visible in the rendered PDF. `tools/report/fix_encoding.py` repairs the
   source; the layout audit now flags mojibake instead of reporting zero defects.
3. **Raw Markdown in the document body.** A `# Title` line and a trailing `---` shipped on page 1
   because the template began with a UTF-8 BOM and because the paragraph continuation rule did not
   break on a horizontal rule. The builder reads `utf-8-sig` and breaks on `---`.
4. **Report was 13 pages and structured against the wrong brief.** The content was restructured to
   the Assignment 1 sections (Introduction with existing solutions, System Design, Evaluation with
   case study and discussion, Conclusion), the duplicated output-universe figure was dropped, the
   coordinate column left Table 2, and the page count fell to 11 including cover and references.
5. **Layout defects.** US Letter page size, a cover that shared page 1 with the abstract and carried
   a footer, an uncaptioned rule table, and a defuzzification table split across pages. Now A4 with a
   standalone cover and no first-page footer, Table 1 captioned, `cantSplit` on every table row.
6. **Report figures diverged from the deck and poster.** Figures used the matplotlib default palette
   and were drawn on 13-16 in canvases shrunk into 6 in frames. `src/fuzzy_system/palette.py` now
   supplies the NVIDIA ramp to all three figure scripts, and each figure is drawn at print size.
7. **Environment and gates.** `requirements.txt` floors, no CI, and no structural check were the
   standing risks; `tools/audit_repo.py`, `check_citations.py` and `fix_encoding.py` close the check
   gap, and the verify block in `docs/SUBMISSION.md` lists all of them.

## Still open, none blocking submission

- **No LICENSE file.** Add one only if the code should be reusable outside the submission.
- **Requirements are floors, not pins.** The measured figures were produced on Python 3.15.1, which
  `docs/measurements.json` records; pinning would make the build reproducible elsewhere.
- **No CI.** The eight verify commands are run by hand.
- **`docs/_legacy/` carries a generator that writes to an absolute path on the original authoring
  machine.** Documented in `docs/_legacy/README.md`; deleting the directory before archival submission
  removes the trap.
- **Table body and captions are 9.5 pt** while body text is 11 pt. Raising every table to 11 pt would
  add roughly a page and breach the 10-page cap.
- **Deadline.** 15 November 2026, 23:59.

## Reproduce this audit

```bash
python -m pytest -q
python -m src.fuzzy_system.reference_engine --tolerance 0.5
python tools/verify_values.py
python tools/report/audit_report_docx.py
python tools/report/check_citations.py
python tools/report/fix_encoding.py
python tools/audit_repo.py
python tools/presentation/verify_deck.py
```

Expected: `25 passed`; `9/9 scenarios within tolerance` with worst deviation `0.0690`;
`RESULT: 36 passed, 0 failed`; `total: 0` rendering defects; `reference entries never cited in
body: []`; every source `clean`; `RESULT: 0 failures, 0 notes`; `RESULT: 16 checks passed,
0 failed`.
