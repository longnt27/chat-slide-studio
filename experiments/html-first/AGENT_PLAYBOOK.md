# Agent-authored presentations: HTML visual reference → native PPTX

This is a *working experiment*, not a new fixed-layout renderer. The source of
truth for visual composition is the authored HTML and rendered screenshots.
ChatGPT writes presentation-specific PowerPoint source code instead of relying
on a general CSS-to-PPTX conversion engine.

## Contract for an AI authoring agent

1. Read the original HTML/CSS, required content, and browser-rendered screenshots.
   Preserve exact slide count, factual wording, section ordering, charts and
   intended speaker pacing. Decide which items are meaningful grouped objects.
2. Create a new **per-deck** PptxGenJS script. Do not add more template layouts to
   the production build engine. Map CSS layout to native absolute coordinates;
   keep real text as PowerPoint text and ordinary decorations as PowerPoint
   shapes where feasible.
3. Recreate data visualizations from their **underlying values**. For this
   fixture, the original four bar heights encode 24, 42, 58 and 68; they are
   illustrative, not real business results. **Select the target application** before exporting. For PowerPoint, use
   `addChart()` with the real editable workbook data. For cross-app imports
   (Keynote/Google Slides), use native `addShape()` bars plus independent
   `addText()` values/categories; preserve the original numbers in an
   accompanying CSV and notes. Never replace the entire chart with an image.
4. Map presentation *intent*, not literal browser animation syntax:
   - Static objects: `STATIC_<semantic-id>_<part>`.
   - Automatic group entrance: `AUTO_G0_<semantic-id>_<part>`.
   - On Click group: `CLICK_G1_<semantic-id>_<part>`, then G2 and so on.
   - Multiple parts of a single card (background, headline, body, image) share
     one group so they enter together.
   - Use native OOXML Fade/On Click semantics via the existing animation
     serializer; do not try to export arbitrary JavaScript timelines.
   - Only use Morph for an actual subject shared between adjacent slides.
     No relevant adjacent subject exists in the present five-slide fixture.
5. Add speaker notes with actual click cues and source information. Preserve
   any uncertainty about images/data and PowerPoint playback.
6. Build the generated PowerPoint, re-render it to PNG/PDF and compare all
   slides against browser screenshots. Run machine QA for editable text,
   real chart numbers/categories, native click group count, notes, slide
   count and catastrophic layout failures. Inspect the images manually.
7. Fix the **generated deck source**, not the compiled binary, and repeat until
   acceptable. If an unsupported effect must be approximated, disclose it.
8. On later slide edits, use the baseline-pinned `revision_requests.json` and
   existing revision QA in `main` to demonstrate the requested difference.

## Why this is different from the converter path

- **A**: generic DOM/CSS → PowerPoint converter. Broad CSS fidelity, fewer
  decisions about actual slide semantics.
- **B**: ChatGPT-authored native PptxGenJS source. May not reproduce every
  gradient/shadow exactly, but can deliberately preserve chart series, text,
  click groups, notes and PowerPoint editability.

The existing `scripts/patch_animations.py` only serializes native OOXML for
the semantic timing groups declared by the generated per-deck code. It does not
choose layouts, charts, animation groups or visuals. This is a small reusable
technical utility, not a presentation design engine.

## Current test

Run workflow **HTML-first native-vs-converter A/B** on branch
`spike/agent-authored-pptx`, or follow these commands:

```bash
npm install --prefix experiments/html-first
python -m pip install python-pptx lxml Pillow PyMuPDF

mkdir -p experiments/html-first/dist
node experiments/html-first/node_modules/dom-to-pptx/bin/cli-exporter.js \
  experiments/html-first/demo.html \
  --output experiments/html-first/dist/converter.pptx \
  --width 13.333333 --height 7.5 --inject
node experiments/html-first/agent-authored.cjs \
  experiments/html-first/dist/agent-authored.base.pptx
node experiments/html-first/agent-authored.cjs \
  experiments/html-first/dist/agent-portable.base.pptx --portable
python scripts/patch_animations.py \
  experiments/html-first/dist/agent-authored.base.pptx \
  experiments/html-first/dist/agent-native.pptx
python scripts/patch_animations.py \
  experiments/html-first/dist/agent-portable.base.pptx \
  experiments/html-first/dist/agent-portable.pptx

node experiments/html-first/capture.mjs \
  experiments/html-first/demo.html experiments/html-first/dist/html-preview
python scripts/render_deck.py experiments/html-first/dist/converter.pptx \
  --out experiments/html-first/dist/converter-preview --expected 5
python scripts/render_deck.py experiments/html-first/dist/agent-native.pptx \
  --out experiments/html-first/dist/agent-preview --expected 5
python scripts/render_deck.py experiments/html-first/dist/agent-portable.pptx \
  --out experiments/html-first/dist/portable-preview --expected 5
python experiments/html-first/portable_qa.py \
  --pptx experiments/html-first/dist/agent-portable.pptx \
  --slide4-preview experiments/html-first/dist/portable-preview/slides/slide-04.png \
  --slide4-html experiments/html-first/dist/html-preview/slide-04.png \
  --report experiments/html-first/dist/ab-comparison/portable-report.json
python experiments/html-first/ab_compare.py \
  --converter experiments/html-first/dist/converter.pptx \
  --agent experiments/html-first/dist/agent-native.pptx \
  --html-previews experiments/html-first/dist/html-preview \
  --converter-previews experiments/html-first/dist/converter-preview/slides \
  --agent-previews experiments/html-first/dist/agent-preview/slides \
  --out experiments/html-first/dist/ab-comparison
```

Inspect `ab-report.json` and the five side-by-side comparison images; they
must remain reviewable even if some QA assertions fail.

## Compatibility incident: chart missing in Keynote

A reviewer reported that the native Office chart on slide 4 disappeared in
Keynote, while Google Slides imported the chart as a low-quality image.
The previous CI had only checked `shape.has_chart` and LibreOffice rendering.
Those checks did not prove other applications could display it.

The agent-authored source now supports **two explicit export targets**:

- **PowerPoint native** (default): an editable Excel-backed chart for PowerPoint.
  This is the original tested mode, but it is not reliable in all importers.
- **Portable** (`--portable`): four ordinary native PowerPoint rounded shapes,
  four value text boxes and four category labels. There is **no chart part, no
  embedded SVG, and no raster image** in the entire portable PPTX. The 24, 42,
  58, 68 data values are also exported as `chart-data.csv`.
  These shapes and labels are individually editable, but no longer one
  Excel-backed chart object.

`portable_qa.py` is a CI gate that inspects OOXML, bar/label/value text,
geometry, speaker notes, and actual LibreOffice-rendered pixels. This is an
**import-risk reduction**, not a real Keynote or authenticated Google Slides
run. A production release should test the PPTX through both real applications
before calling cross-app compatibility verified.

## What this test cannot prove yet

- That the LLM can reliably translate *arbitrary* HTML by itself on demand.
  This code was authored by ChatGPT specifically for a fixed five-slide deck.
- That CSS keyframes, GSAP timelines or complex physics animations have exact
  native PowerPoint equivalents.
- That PowerPoint Slide Show executes every effect correctly on desktop.
  OOXML structural checks are necessary but not playback verification.
- Full fidelity for images, complex diagrams or native editable chart styles
  across all possible slide designs.

Do not claim the agent-generated approach is superior until both visual
fidelity AND editability/motion QA are reviewed against the converter.
