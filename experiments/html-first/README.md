# HTML-first → editable PowerPoint (isolated experiment)

**Not production-ready.** This experiment lives exclusively on
`spike/html-first-pptx`. The current `scripts/build_deck.cjs` pipeline on
`main` is unchanged.

## Hypothesis

HTML/CSS (including flex/grid, rich typography and declarative animation
classes) can provide a more expressive design authoring surface while still
exporting editable PowerPoint text and simple shapes.

## Fixture

- `demo.html` contains five 16:9 slides with original content only.
- Slide 1: display type and gradient composition
- Slide 2: three cards, shadows and declarative click animation classes
- Slide 3: complex flex/connector pipeline diagram
- Slide 4: illustrative data bars; **not** a native editable chart object
- Slide 5: finish slide with entrance and click animation classes

The PoC tests `dom-to-pptx@2.1.2`, a PptxGenJS-backed DOM converter.
For fair QA it builds the PPTX, captures each HTML slide from Chromium,
renders the resulting PowerPoint through LibreOffice, and produces
side-by-side comparison PNGs and `evaluation.json`.

The test checks **real editable text shapes** on every slide instead of
accepting five full-slide pictures. The visual MAE is a descriptive metric
to be reviewed by a person, not an automatic perfection score.
Native animation OOXML presence is reported, but actual PowerPoint desktop
playback is **NOT verified**. Even if the library supports simple transitions,
arbitrary CSS/GSAP motion cannot be assumed exportable.

## Run (Node 22 and Python 3.12)

```bash
npm install --prefix experiments/html-first --no-audit --no-fund
python -m pip install python-pptx Pillow PyMuPDF
# Requires LibreOffice Impress in PATH and Puppeteer's Chromium.
mkdir -p experiments/html-first/dist
node experiments/html-first/node_modules/dom-to-pptx/bin/cli-exporter.js \
  experiments/html-first/demo.html \
  --output experiments/html-first/dist/html-first.pptx \
  --width 13.333333 --height 7.5 --inject
node experiments/html-first/capture.mjs \
  experiments/html-first/demo.html experiments/html-first/dist/html-preview
python scripts/render_deck.py experiments/html-first/dist/html-first.pptx \
  --out experiments/html-first/dist/pptx-preview --expected 5
python experiments/html-first/evaluate.py \
  --pptx experiments/html-first/dist/html-first.pptx \
  --html-previews experiments/html-first/dist/html-preview \
  --pptx-previews experiments/html-first/dist/pptx-preview/slides \
  --out experiments/html-first/dist/comparison
```

GitHub Actions workflow: `HTML-first PPTX prototype`. Review its artifacts
(PPTX, PDF, screenshots, side-by-side comparisons and metrics) before deciding
whether a production HTML renderer is worth implementing.

## Promotion criteria

1. Every slide must preserve editable text and basic shapes; avoid
   converting an entire page into a single background image.
2. The visual comparison must be visually reviewed at full size,
   not just judged by a single scalar metric.
3. Animation claims need real PPTX timing semantics and eventual desktop
   PowerPoint playback checks.
4. A later experiment must demonstrate true editable PowerPoint chart data,
   sourced images, notes, and stable slide edit/rebuild behavior.
5. The production engine remains in place until these criteria are met.

Experiment dependencies and CI are isolated; no `npm install` at the project
root is required for this proof of concept.
