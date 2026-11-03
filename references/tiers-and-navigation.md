# Presentation service tiers and chapter-hub navigation

Chat Slide Studio is a **chat-first presentation production service**. Choose the smallest tier that solves the user's task. All tiers must satisfy factual accuracy, legible typography, source credits (where relevant), meaningful layout and structural QA. Tiers affect workload and available motion, **not minimum quality**.

## Tier choice (confirmed in the HITL storyboard)

| Tier | Expected output | Native animation | Charts | Morph & chapter hub |
| --- | --- | --- | --- | --- |
| `content` | Clean, editable, information-first deck; minimum overhead | **None**. No On Click, Fade, or slide transitions | Optional, sourced, fully editable | Not available with `animation_mode=none` |
| `presenter` | Teaching and speaking deck with narrative pacing | Auto/On Click for meaningful content units; groups enter together | Optional, sourced | Optional, when explicitly planned/approved |
| `studio` | Showcase or complex-data presentation with purposeful composition | Same presenter effects, with selectively richer transitions | Optional bar, line, pie. Never invent data | Optional photo TOC → chapter → TOC → next chapter |

**Tier is a preset, not a quota:** `studio` does not require charts or Morph on every page. `presenter` is allowed to have 0 Morph. Charts are available even in a static content deck when numerical evidence benefits understanding.

- New-deck default: `content`, `animation_mode=none`.
- Legacy decks missing a tier retain `presenter` behavior to avoid breaking existing authored animation.
- `animation_mode` can be `none` or `presenter`; for example `studio` + `none` allows detailed data charts without animation. A `navigation` loop requires `presenter`.
- Ask the user to choose a tier in Stage 1 only if their intent isn't clear. Don't sell them unnecessary animation as a universal prerequisite.
- A tier and its animation mode belong in both `storyboard.json` and `deck.json`, locked to the approved plan.

## Two different slide counts

The **logical count** is the number of unique *content* slides specified by the user, including cover, TOC and thanks. Repeated appearances of the exact same TOC are not counted as new ideas.

The **physical count** is the number of actual pages in the PPTX and exported PDF, which must include every replay of the TOC to make the slideshow follow the expected path.

Example for a 20-slide request:

- `requested_slide_count: 20` and `slides.length: 20` in both approved storyboard and authored deck.
- `navigation: { "mode": "hub_return", "hub_slide": 2, "return_after": [5, 9, 14], "morph": true }`.
- There are 3 extra TOC visits, therefore **20 logical slides / 23 physical PowerPoint and PDF pages**.
- `slide-route.json` lists which physical position maps to which logical content slide, with role `primary` or `hub_return`.
- CI rejects a mismatch in either count. Reports must **show both**. Never tell the user that the PPTX contains exactly 20 physical pages when it actually contains 23.
- The storyboard preview displays 20 unique cards; include a routing summary that explains the 3 returns. Ask whether the user needs exactly 20 physical pages instead: in that case omit hub returns or use navigation hyperlinks without physical duplication (not implemented yet).

A TOC return is not "duplicate content" in the sense of authoring 3 redundant new ideas. It is a **new view of one logical navigation hub** in the physical slideshow.

## Photo TOC: Morph has an actual subject and route

1. Author a logical `contents` slide (for example #2) with `toc_entries` in the approved storyboard and `entries` in the authored deck. Each entry has `title`, `image` asset ID, `morph_id`, and `target_slide` (logical number).
2. For chapter content referenced by the TOC, place the **same verified image asset** with the same `morph_id` in that slide. The image's frame may resize, but the original media bytes stay identical.
3. Use `morph_subject` on the storyboard's content slide so the user is approving the identity of that connection. Example: `historical_gate` in the TOC entry and in the corresponding content slide.
4. Set `navigation.mode=hub_return`, `hub_slide`, and `return_after`. A return after logical slide #5 places a new physical copy of the TOC *after* that slide. The next original logical slide continues after that return.
5. `navigation.morph=true` asks the route compiler to Morph only **adjacent** physical visits that share an approved photo and subject: TOC → content, content → TOC, TOC → next content. It rejects routes missing a pairing; it does not Morph irrelevant page numbers or text.
6. The photo TOC thumbnails remain visible without independent entrance animations. They do not fly around as unrelated decorative objects.
7. Content layout can remain in the approved type `split` or `section`; a TOC can have 2–6 entries. If the last slide of a section doesn't show the shared photo, don't request a return Morph from that slide; choose another return point or an ordinary Fade.
8. More than 30% Morph transitions may be meaningful in this **navigation-specific** structure. The normal 30% limit remains for linear decks; hub Morph is exempt from the *quota*, not from subject, geometry or source verification.

The route is **linear in actual slideshow order** and respects presenter Next/Previous. It is not a random-access clickable menu, and no unsupported click-to-jump promises should be made.

## Data charts

- The `chart` layout uses `chart_data.kind` (`bar`, `line`, `pie`), `labels`, numeric `series`, and a mandatory `source`. Chart visuals are editable PowerPoint chart objects.
- `chart_kind` is locked in the approved storyboard; data values can be refined from the verified source without changing chart type or story structure, unless the change is material.
- Use a chart only when it actually helps explain numbers. Never invent an economic or historical timeseries because the user chose `studio`.
- Same chart is valid in `content` with no animations.

## Delivery and QA

- **Content**: zero `p:timing`, `p:transition` or Morph; still verify layout, sources, static notes, PDF and image composition.
- **Presenter**: validate real On Click / With Previous groups and only selected Morph.
- **Studio with navigation**: additionally verify `slide-route.json`, every logical slide once, number of physical returns, photo identity across each Morph boundary, and that PDF page count equals physical count.
- Never claim Microsoft PowerPoint playback is verified merely because native OOXML is well formed or LibreOffice exported a PDF.
- HITL approval covers tier, counts, TOC target cards, navigation returns and Morph relationships. No silent tier upgrade or extra pages after approval.

## Example prompt

> Repo: https://github.com/longnt27/chat-slide-studio. Make a **20-logical-slide Studio** presentation on [topic]. First propose the 20 unique layouts and a photo table-of-contents at slide 2 that returns after chapters 5, 9 and 14. Explain physical page count, image identity for each Morph, charts and On Click groups in the storyboard. **Do not build** until I approve.

A minimalist alternative:

> Same repo. **Content tier**, 12 slides on [topic]. Clean, static, editable PPTX without animation. Propose storyboard first.
