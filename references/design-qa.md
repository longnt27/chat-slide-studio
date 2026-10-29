# Design standards, failure patterns and release QA

## Layout system

- Default canvas 16:9. Choose an intentional grid, outer margins and type scale. Use shared tokens for text sizes, gaps, typography, border radius, and colors. Never vary spacing among peer cards accidentally.
- **True centering**: the text paragraph must be centered **and** the text box's center x must match the center of its parent/background or diagram axis. A box aligned on the wrong x cannot be fixed solely by `textAlign=center`. "LỤC BỘ" and its caption in a government diagram must match the centerline of the Lục bộ grid, not the center of the whole slide or left position of an oversized text frame.
- For N equal cards: widths equal, inner padding consistent, gaps equal, outer margins balanced within reasonable tolerance. Place card image/text in a common grid. Test coordinates, then visually inspect.
- Avoid one orphan word alone on a line, titles glued to body copy, inconsistent line heights, tiny source captions, title/body overlap, and text boxes extending into image regions. A single word forced onto a second line should be edited, not left as a design "feature".
- Decorative shapes should support visual hierarchy, not add noise. Simpler is often better. A slide may have substantial empty space if deliberate but not because content is missing.

## Machine + visual QA: both required

1. Inspect PPTX internals: number of slides, notes, valid archive, no out-of-bounds shapes, explicit center alignment where required, card margin/gap symmetry, animation targets and order, Morph pairs, image audit metadata, source and credits.
2. Render to PDF and slide PNGs using `scripts/render_deck.py`. Make montage and open **every slide full size**, particularly image-heavy slides, slide 2 (timeline), diagrams, and closing slide. PDF does not show entrance animations; don't judge click behavior by PDF image alone.
3. Compare before/after renders on edits; preserve intentional content, source notes, and animations. Do not treat generic overlap diagnostics as final truth: text over an intentional image overlay can be valid, while a caption separated by only two pixels from a card edge can look wrong despite passing geometry tests.
4. Fix defects in source and rerun build. A one-off manual PPTX patch is not a durable fix if the next CI build regenerates the problem.
5. Include a QA report with tests run, issue fixes, known limitations and a link to the verified artifact. Report CI status only after inspecting actual run and artifact.

## A release must fail if

- Severe text/text overlap or text/image obstruction; text or images outside slide canvas; inconsistent peer card widths or margins; incorrectly centered title/caption.
- Wrong or missing photo, off-topic source image, unacceptable crop, uncredited image used as factual evidence.
- Card border appears after text; a partial semantic group is static/animated separately; click order does not match Speaker Notes.
- Morph joins page numbers to unrelated data or appears on nearly every transition without an explanatory reason.
- CI green but visual render shows an obviously damaged subject or layout. CI must complement, not replace, human vision.

## Suggested report fields

`slide_count`, `notes_count`, `slides_with_images`, `image_manifest_verified`, `auto_fade_groups`, `click_steps`, `morph_steps`, `text_collisions`, `center_alignment_checks`, `card_spacing_checks`, `out_of_bounds`, `pdf_render_pages`, `visual_reviewed`, `powerpoint_playback_tested` (true/false), `ci_run_url`, `artifact_url`.
