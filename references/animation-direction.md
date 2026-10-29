# Animation & Morph: meaningful narration-controlled motion

## First diagnose the previous failure

The old animation patch emitted `presetID=9` for Fade and marked all peers `nodeType=withEffect`. That was **not** the PowerPoint-authored Fade-on-click tree. The correct model is based on a real PowerPoint 16.0 file: a complete step (`p:par`) with delay `indefinite` holds one first effect marked `clickEffect`, followed by `withEffect` siblings; Fade has `presetID=10`, a `p:set` to `style.visibility=visible`, and `p:animEffect filter=fade`. Use `p:bldLst/p:bldP` only for text-bearing shapes. Source comparison: [PowerPoint-authored animation oracle](https://github.com/shbernal/pptx-ts/blob/main/test/read/fixtures/slide-animation-basic.oracle.json).

## Presenter timeline rules

- Background, shared footer and chrome are static from slide entry. A title + first content unit may use `auto` (immediate 350–550ms Fade).
- Card 2 and card 3 **wait for separate user clicks**. Never rely on automatic delays for ideas that need verbal explanation.
- A semantic unit is all its component shapes: panel, icon, photo, badge, text, divider. Every unit enters as one PowerPoint timing step, each of its component effects begins simultaneously at the same duration. Never show card content before its container or vice versa.
- Equivalent peer units use equivalent effects and duration. All six peer ministry tiles can share one click, not six aimless clicks.
- Speaker Notes list every click cue in exact order. Animation steps and cues must match, and `qa_pptx.py` validates event kinds, numbers, target IDs and build-list semantics.
- A slide may intentionally remain static if its visual is meant to be studied immediately; repeated cards/timeline entries need presenter pacing unless the approved storyboard explicitly explains why all must remain visible.

## Morph: content continuity, not a transition quota

**Zero Morph is valid.** If the user specifically requests Morph, the storyboard must propose a justified object pair or explicitly explain why no reliable pair exists, rather than silently claiming to have included an effect. Every planned Morph must show a concrete before/after subject in the storyboard and a meaningful change in framing. CI now checks that the requested destination slide is present and records per-object geometry evidence; actual motion playback still requires Microsoft PowerPoint. A reciprocal relationship within one slide is a diagram, not an excuse for a Morph between unrelated slides.

1. Include Morph only when the *same evidence / diagram / person / object* appears on both neighboring slides, and there is a meaningful change in focus, scale or framing. Describe the audience benefit in the **approved storyboard**, including where the object begins and ends.
2. Name the matched pictures `!!subject_key` on both slides, uniquely. Keep all unrelated title/slide-number/card decorations outside Morph. Avoid crossing the whole canvas or shrinking subjects to a point.
3. Use the **identical original image bytes** for the pair, not separately reprocessed images at two sizes. This lets PowerPoint interpolate one photo's placement/scale instead of awkwardly cross-fading two precomposed mattes. Keep unpaired decorative shapes static or fade; do not animate the Morph image again with an entrance.
4. Emit Office-compatible inline XML namespaces on the Morph transition: `mc:Choice` declares `p159`, and the nested `p:transition` declares `p14` with `p14:dur` (not an auto-generated `ns1:dur`). Validate serialization against PowerPoint-authored OOXML examples.
5. Limit Morph to selected overview→detail, location→zoom or before→after comparisons with actual evidence. Fade is the default slide transition. Target transition duration about 1.45 seconds; peer Fade about 480ms.
6. Machine QA rejects unchanged framing, extreme travel, excessive scale, mismatched subject IDs and different original image bytes.

## Playback truth

A PDF, static montage and an OOXML inspection cannot prove that Microsoft PowerPoint plays effects. CI builds structurally compatible native OOXML and checks against an authored oracle, but **a final presentation that matters must be played in Microsoft PowerPoint Slide Show** (Animations Pane/Preview) before claiming actual playback was verified. Other viewers (Google Slides, LibreOffice, Keynote, embedded web viewer) may ignore or reinterpret Morph and object animations. Disclose when the available environment cannot run desktop PowerPoint.
