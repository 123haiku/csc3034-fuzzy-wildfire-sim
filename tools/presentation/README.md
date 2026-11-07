# Presentation pipeline

Everything in `docs/presentation/` is generated. Do not edit the `.pptx` by hand — a rebuild
overwrites it.

## Deliverables

| File | What it is |
|---|---|
| `docs/presentation/CSC3034_Presentation_Slides.pptx` | the deck, 11 slides, 16:9, speaker notes on all 11 |
| `docs/presentation/CSC3034_Presentation_Slides.pdf` | the same deck, 11 pages, for submission and email |
| `docs/presentation/assets/` | figures the deck embeds |
| `docs/presentation/_archive/` | superseded generations + the v2/v3 repair scripts, gitignored |

## Rebuild

```powershell
# 1. figures (needs the interpreter that has matplotlib: C:\Python315\python.exe)
$env:MPLBACKEND="Agg"
C:\Python315\python.exe tools\presentation\nvidia_plots.py

# 2. deck  (python-pptx is in the DSH runtime)
& "$env:USERPROFILE\.dsh\dsh-runtimes\dsh-primary-runtime\dependencies\python\python.exe" tools\presentation\build_deck_v4.py

# 3. pdf   (LibreOffice Kit CLI)
& "C:\Users\pangw\AppData\Local\Programs\DeepSeek Harness\resources\runtime\primary-runtime\dependencies\node\bin\node.exe" `
  "C:\Users\pangw\AppData\Local\Programs\DeepSeek Harness\resources\app\dsh\node_modules\@deepseek-ai\libreoffice-kit\lib\cli.js" `
  convert --input docs\presentation\CSC3034_Presentation_Slides.pptx --output docs\presentation\CSC3034_Presentation_Slides.pdf
```

## Scripts

| Script | Role |
|---|---|
| `nvidia_plots.py` | rebuilds `membership_nvidia.png` and `telemetry_nvidia.png` in the black/#76B900 palette, drawn at their final physical size so label sizes are literal. Prints the 12-waypoint telemetry table it uses. |
| `crop_viewport.py` | cuts the Isaac Sim window chrome off the raw 1024x611 captures; asserts the source size and that the crop is a bright 3D scene, not a dark panel. |
| `build_deck_v4.py` | builds all 11 slides. Layout rules live in `frame`/`rule_h`/`rule_v`/`text`/`pairs`/`stats` at the top. |
| `deck_notes.py` | speaker notes per slide, separate so the build file stays readable. |

## Conventions the build enforces

- Palette is four values only: `#0A0A0A` canvas, `#1F1F1F` hairline, `#FFFFFF`/`#8C8C8C` text, `#76B900` accent.
- **No text inside shapes.** Autoshapes are 1-3 pt rules only; every string is a textbox on the 0.75 in grid.
- Grid: margins 0.75 in, content from y=1.75, footer at y=7.13, slide 13.333 x 7.5 in.
- Slide-7 numbers come from `run_stage_patrol_simulation`, not from hand-typed values. If the controller
  changes, re-run `nvidia_plots.py` and update the four observation blocks to match its printed output.
