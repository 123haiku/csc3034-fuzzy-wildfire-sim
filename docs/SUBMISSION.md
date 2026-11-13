# Submission Contents

Three deliverables are handed in for CSC3034. Everything else in this repository exists to
regenerate them, verify them, or document how.

## 1. Poster

| Item | Path |
|---|---|
| Print-ready A1 PDF (594 x 841 mm) | `docs/poster/CSC3034_A1_Poster.pdf` |
| 300 DPI raster for print | `docs/poster/CSC3034_A1_Poster_300DPI.png` |
| Generated HTML source | `docs/poster/CSC3034_A1_Poster.html` |

Rebuild:

```bash
python tools/presentation/build_poster.py
```

The builder renders candidate type scales, measures the laid-out height in Chromium, and keeps
the largest scale that still fits the page. Every table cell is computed at build time from the
controller and `run_stage_patrol_simulation(seed=0)`, so the poster cannot drift from the code.

## 2. Report

| Item | Path |
|---|---|
| Word document | `docs/report/CSC3034_Final_Report.docx` |
| PDF export | `docs/report/CSC3034_Final_Report.pdf` |
| Markdown source | `docs/report/REPORT_TEMPLATE.md` |

Rebuild:

```bash
python tools/presentation/measure.py         # docs/measurements.json, the single source
python src/visualize_architecture.py         # Figure 1
python src/visualize_membership.py           # Figure 2 and Figure 3
python src/visualize_mission_telemetry.py    # Figure 4
python src/export_report_docx.py             # DOCX from REPORT_TEMPLATE.md + measurements
```

Then export the PDF from Word (File > Save As > PDF), or with any `docx` to `pdf` converter.

`export_report_docx.py` does three things beyond conversion. It flattens the inline LaTeX
into linear text, because Word does not render it. It substitutes `{{path.to.value}}`
tokens with values from `docs/measurements.json`. And it generates Table 2 and Table 3
from that same file, so neither table is transcribed by hand.

Every number the report, the poster and the deck quote comes from `docs/measurements.json`,
which `tools/presentation/measure.py` writes. Re-run it whenever the controller, the rule
base or the stage model changes; the three deliverables then quote the new figures instead
of drifting apart. `python tools/verify_values.py` fails the build if any shipped document
still carries a superseded figure.

## 3. Code

The inference engine and its surroundings:

| Item | Path |
|---|---|
| Mamdani controller, three defuzzified outputs | `src/fuzzy_system/controller.py` |
| Isaac Sim / Action Graph bridge with a headless mock | `src/fuzzy_system/isaac_sim_bridge.py` |
| scikit-fuzzy cross-check of the hand-written engine | `src/fuzzy_system/reference_engine.py` |
| Defuzzification benchmark (report Table 3) | `src/fuzzy_system/defuzz_benchmark.py` |
| Procedural OpenUSD stage and waypoint patrol | `src/create_wildfire_stage.py` |
| Unit tests | `tests/test_fuzzy_controller.py` |
| Reference tests | `tests/test_reference_engine.py` |

Verify:

```bash
python -m pytest tests -q
python -m src.fuzzy_system.reference_engine --tolerance 0.5
python src/run_demo.py
python -m src.fuzzy_system.isaac_sim_bridge --scenario worsening --steps 10
python tools/report/audit_report_docx.py
python tools/verify_values.py
```

Expected: 25 tests pass, the reference cross-check reports 9/9 scenarios within tolerance
with a worst absolute deviation of 0.069, the report audit reports zero rendering defects,
and the value check passes every required/stale/table assertion.

`tools/report/rule_trace.py --inputs T RH W F` prints the membership degrees and rule
firing strengths behind any single reading, which is how the explainability claims in
Section 5.1 are supported.

## Not needed for submission

`docs/_legacy/` holds two superseded files. See the README in that directory before opening
either of them; one writes to an absolute path on the original authoring machine.

The deck under `docs/presentation/` is supporting material for the defence, not a required
deliverable. It is rebuilt by `python tools/presentation/build_deck_v4.py` and checked by
`python tools/presentation/verify_deck.py`.

## Reproducibility notes

- `run_stage_patrol_simulation(stage, steps=12, seed=0)` is deterministic. Report Table 2 and
  every poster flight row come from that call.
- The production engine does not import scikit-fuzzy. It appears in `requirements.txt` only so
  `reference_engine.py` and `defuzz_benchmark.py` can run.
- All figures under `plots/` are gitignored and rebuilt from source. `docs/poster/assets/` keeps
  the poster-sized copies.
