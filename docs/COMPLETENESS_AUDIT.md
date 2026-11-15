# Repository Completeness Audit

Audit date: 2026-11-14. Repository: `123haiku/csc3034-fuzzy-wildfire-sim`.
Commit at the start of the audit: `6206f16` ("feat(values): route every quoted figure through one
measurement file"), working tree clean, `main` level with `origin/main`.

## Verdict

Submission-complete after the repairs listed under "Defects found and fixed". The three deliverables
are present, internally consistent with the code, and every build/verify command in
`docs/SUBMISSION.md` returns the count it claims. Before this pass the report shipped with an
uncited reference list, no literature review, and eight mojibake sequences in the body text.

## Checks run and returned

| # | Check | Command | Result |
|---|---|---|---|
| 1 | Remote state | `git fetch origin --prune; git status -sb` | `## main...origin/main`, no local divergence, no dirty files before the audit |
| 2 | Inventory | `git ls-files`, `git status --ignored` | 55 tracked files; no `__pycache__` or `.pytest_cache` entry tracked; ignored trees only (`plots/`, caches) |
| 3 | Unit tests | `python -m pytest -q` | `25 passed` in 1.93 s |
| 4 | Engine vs scikit-fuzzy | `python -m src.fuzzy_system.reference_engine --tolerance 0.5` | 9/9 scenarios within tolerance, worst absolute deviation 0.069 |
| 5 | Figure consistency | `python tools/verify_values.py` | `35 passed, 0 failed` (required figures present, superseded figures absent, both tables row-exact) |
| 6 | Deck | `python tools/presentation/verify_deck.py` | `16 checks passed, 0 failed` (11 slides, 16:9, notes 11/11, 4 embedded pictures, zip intact) |
| 7 | Report layout | `python tools/report/audit_report_docx.py` | 0 rendering defects, 4 tables, 4 inline figures, 1 section, 114 paragraphs / 3566 body words |
| 8 | Path and link integrity | `python tools/audit_repo.py` | 8 Markdown files, 38 referenced paths, 0 missing, 0 tracked-but-absent |
| 9 | Citation wiring | `python tools/report/check_citations.py` | 6 reference entries, 6 cited, no dangling citation |
| 10 | Measurement reproducibility | `python tools/presentation/measure.py` then `git diff docs/measurements.json` | Every deterministic field reproduced byte-identically; only the four latency numbers moved (machine timing): benign median 0.069 -> 0.064 ms, benign p99 0.228 -> 0.335 ms, critical median 0.071 -> 0.068 ms, critical p99 0.186 -> 0.304 ms. Committed measurement restored afterwards. |

Deliverables inspected:

| Deliverable | File | Verified property |
|---|---|---|
| A1 poster | `docs/poster/CSC3034_A1_Poster.pdf` | 1 page, 1684 x 2385 pt = 594 x 841 mm, `%PDF` signature |
| Poster raster | `docs/poster/CSC3034_A1_Poster_300DPI.png` | 3.9 MB, tracked |
| Report | `docs/report/CSC3034_Final_Report.docx` | 2.7 MB, OOXML zip intact, 13 pages when exported |
| Report PDF | `docs/report/CSC3034_Final_Report.pdf` | 13 pages, A4 (595 x 842 pt), text extractable, 0 mojibake |
| Deck | `docs/presentation/CSC3034_Presentation_Slides.pptx` / `.pdf` | 11 slides, 13.333 x 7.5 in, 11 PDF pages |
| Proposal | `docs/proposal/CSC3034_Group_Proposal_Form.docx` / `.md` | zip intact, Markdown source present |
| Stage asset | `assets/wildfire_forest_uav_stage.usda` | 75 KB OpenUSD layer, referenced by the stage builder |

## Defects found and fixed

1. **No literature review.** The report went from Section 1 Introduction straight to Section 2 System
   Design; no related-work content existed. Fixed by adding Section 2 Literature Review with five
   subsections (fire danger indices, Mamdani inference and defuzzification, UAV monitoring,
   simulation substrate, positioning against learned controllers) and renumbering the remaining
   sections: System Design is now 3, Isaac Sim 4, Results 5, Discussion 6, Conclusion 7. The stale
   cross-reference in `docs/SUBMISSION.md` ("Section 5.1") now reads "Section 6.1".
2. **Reference list with no in-text citations.** `check_citations.py` reported entries 1, 2, 4, 5 and
   6 never cited, and the only bracketed numbers in the body were input-universe bounds such as
   `[0, 50]`. Fixed by wiring `[1]`-`[6]` into Section 1.1, Section 1.2, Sections 2.1-2.5 and
   Section 6.1. Re-run reports `reference entries never cited in body: []`.
3. **Mojibake in the shipped report.** Eight `a-euro"` sequences (UTF-8 em dash decoded as cp1252)
   sat in five paragraphs: the abstract, Section 1.1, the rule-matrix discussion, Section 5.2 and
   the new Section 2.3, and were visible in the rendered PDF. Source repaired with
   `tools/report/fix_encoding.py`; report DOCX rebuilt and PDF re-exported from Word. The PDF now
   carries 9 correct em dashes and 0 mojibake sequences.
4. **The layout audit could not see defect 3.** `audit_report_docx.py` printed "total: 0" while the
   mojibake was shipping. A `MOJIBAKE` pattern was added to the defect scan; run against the stale
   DOCX it flags 5 paragraphs, against the rebuilt DOCX it reports 0.
5. **No structural or citation gate.** Added `tools/audit_repo.py` (referenced paths, broken local
   links, tracked-but-absent files, deliverable signatures, OOXML zip integrity, report section
   keywords), `tools/report/check_citations.py` and `tools/report/fix_encoding.py`. All three are
   listed in the README tree and in the verify block of `docs/SUBMISSION.md`.
6. **DOCX and PDF were out of step after the text change.** Rebuilt both from the template so they
   describe the same document: 13 pages each, same section numbering, same table and figure order.

## Typography pass (second pass, same day)

| Defect | Evidence | Fix |
|---|---|---|
| Raw Markdown heading shipped in the body: a line reading `# Intelligent Forest Fire Risk Assessment ...` sat between the cover and the abstract | rendered page 1, and paragraph 4 of the DOCX | The template began with a UTF-8 BOM, so the `#` line missed the heading pattern and fell through as prose. Builder now reads `utf-8-sig` and the BOM was stripped from the file |
| Trailing `---` welded onto the keywords paragraph | rendered page 1: "Sustainable Development Goals. ---" | The block parser's continuation rule did not break on a horizontal rule; `t == "---"` added to the break list |
| Page size was US Letter | DOCX geometry: 8.50 x 11.00 in | Set to A4 8.27 x 11.69 in, margins 1.0 / 0.9 / 0.9 / 0.9; content width 6.47 in still clears the 6.3 in figures |
| Cover shared page 1 with the abstract, and carried the running footer | rendered page 1 | Page break after the team table, `different_first_page_header_footer` with an empty first-page footer, title block given 110 pt of space above |
| Rule-base table had no caption, so Table 2 and Table 3 had no Table 1 | caption scan found Figure 1-4, Table 2, Table 3 only | `**Table 1: The ten Mamdani rules ...**` added ahead of the table; the builder renders it in the same italic caption style |
| Defuzzification table split across pages | rendered page 10: one row on page 10, three on page 11 | `cantSplit` on every body row, `keep_with_next` on figure paragraphs; Table 3 now sits whole on page 11 |
| Mission-log column widths forced every coordinate onto three lines and pushed row 11 onto the next page | DOCX table geometry: 0.65 in for every column | Fixed widths for the 10-column table (position 1.10 in), rows drop to two lines |
| Template line endings were doubled to blank lines between table rows by a text-mode rewrite | parser produced 12 single-row "tables" instead of one 12-row table | Template restored from git, rewritten as bytes with LF only, and the parse re-checked |
| Report figures used the matplotlib default palette (blue / orange / green / red) while the deck and poster used NVIDIA black and green | rendered pages 6 and 11 | `src/fuzzy_system/palette.py` defines the NVIDIA ramp, and the three figure scripts draw from it; membership legends moved below each axes because every curve spans the full x range |
| Report figures were drawn on 13-16 in canvases and shrunk into 6 in frames, halving every label | figure pixel sizes 3900 x 3600 and 4800 x 3000 against a 6.3 in placement | Redrawn at print size: 1980 x 2700, 1860 x 2520 and 2100 x 1620, with 6.5 pt ticks and 8 pt axis titles |

Verification after the pass: `pytest` 25 passed, `verify_values.py` 35 passed, `audit_report_docx.py`
0 rendering defects, `check_citations.py` no uncited entry, `audit_repo.py` 0 failures,
`verify_deck.py` 16 passed. Report is 13 pages A4, cover on page 1, references end on page 13.

## Still open, none blocking submission

- **No LICENSE file.** The repository declares no licence. Add one only if the course or the team
  wants the code reusable outside the submission.
- **Requirements are floors, not pins.** `requirements.txt` reads `numpy>=1.23.0`, `scipy>=1.9.0`,
  `scikit-fuzzy>=0.4.2`, `matplotlib>=3.6.0`, `pytest>=7.0.0`. The measured figures were produced on
  Python 3.15.1 (recorded in `docs/measurements.json`); pinning would make the build reproducible on
  other machines. Note the deprecation warning from `skfuzzy` (990 warnings) comes from that floor
  version and does not fail a test.
- **No CI.** Every check above is manual. A single workflow running the eight commands in
  `docs/SUBMISSION.md` would gate the deliverables on push.
- **`docs/_legacy/` carries a generator that writes to an absolute path on the original authoring
  machine.** It is documented in `docs/_legacy/README.md` and excluded by the audit, but deleting the
  directory before archival submission removes the trap.
- **Report figures now use the NVIDIA palette.** `src/fuzzy_system/palette.py` holds the ramp
  (lime to olive to black, severity by luminance) shared by `visualize_membership.py`,
  `visualize_mission_telemetry.py` and `visualize_architecture.py`, so the report, the deck and the
  poster no longer disagree on colour.
- **Deadline.** README states 15 November 2026, 23:59, which is the day after this audit.

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

Expected console results: `25 passed`; `9/9 scenarios within tolerance` with worst deviation
`0.0690`; `RESULT: 35 passed, 0 failed`; `total: 0` rendering defects; `reference entries never
cited in body: []`; every source `clean`; `RESULT: 0 failures, 0 notes`; `RESULT: 16 checks passed,
0 failed`.
