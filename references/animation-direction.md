# Animation direction: semantic reveals, not moving furniture

## Entrance policy

- No animation means visible **at slide entry**. This includes fixed background, navigation, and shared chrome; do not accidentally expose the card's text without its frame.
- Optional `AUTO_G0_*`: heading + subtitle + first unit of content can Fade on slide entry, simultaneously. It should finish quickly (suggest 350–550 ms).
- `CLICK_G1_*`, `CLICK_G2_*`, etc.: one step per **meaningful narration chunk**. One card's background, image, icon, year, title, body and divider must share exactly one timing step and visual effect. Use distinct clicks for card 2 and card 3 when the speaker needs to explain each.
- Six peer ministries may enter simultaneously under one click, not in six needless clicks. A group of equal options/list items should use the same effect and duration; differences in start times are allowed only for genuinely sequential speech cues.
- Speaker Notes must contain a click cue for each group in order. Don't make the slide advance automatically before the user finishes speaking.

## Morph policy

A Morph candidate **must** satisfy all four tests:

1. The subject or concept is identical in adjacent slides; same person, diagram, geographic entity, or photo detail. A page number, footer, separator, generic card border or progress dot does not qualify.
2. Morph teaches a relationship (overview → detailed explanation; zoom into a particular photo; same object across phases), not merely creates a moving ornament.
3. The object moves/scales only as much as the explanation needs; avoid long cross-screen flights and unintended collisions. Remove gratuitous movement.
4. One transition has at most a few paired objects and has a fallback Fade. Every paired shape is clearly named the same `!!semantic_subject`; verify the match and don't create non-adjacent pairs by accident.

When Morph changes the same subject across slides, leave that subject visible on entry to the destination slide (do not add a conflicting entrance effect). Use Fade for all other transitions. Never add a Morph to every slide just because PowerPoint supports it.

## OOXML caveat and test strategy

`patch_animations.py` operates on OOXML and uses `AUTO_G0_` / `CLICK_G#_` naming. Test both sequence/group structure and the actual resulting slide package. PowerPoint's Morph extension and click timeline have product-specific behavior; a successful XML check and LibreOffice PDF render are **not** equivalent to native animation playback in desktop PowerPoint. When native playback is unavailable, report it as an unverified limit, not as a passed test.

## Example timeline

Slide 2 three cards: title + subtitle visible, first card Fade on entry (or static for Morph continuity), Click 1 = *complete second card*, Click 2 = *complete third card*, optional Click 3 = synthesis line. A next click after all content advances the slide. Card text must never materialize before its border, photo or backdrop.
