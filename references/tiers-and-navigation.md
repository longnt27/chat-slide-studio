# Ordo Studio tiers, design inputs and advanced navigation

Quality checks, factual accuracy, editability, source credits and legibility
apply to every tier. The tiers describe available production complexity,
**not whether QA is optional**.

| Tier | Purpose | Animation | Extra capability |
| --- | --- | --- | --- |
| **Basic** (`basic`) | Clear, editable, static slide deck | `none` by default. No entrance/transition effects | Source-backed chart when useful |
| **Studio** (`studio`) | Speaker-led presentation | `presenter`: grouped Auto/On Click and selective Morph | Richer pacing, layout and notes |
| **Pro** (`pro`) | Premium storytelling and complex data visuals | `presenter`, or `none` by request | Purposeful chapter/photo TOC, advanced composition, verified charts |

The names replace the former Content → Basic, Presenter → Studio and
Studio → Pro. The internal motion enum remains `none` / `presenter`.
Previously authored deck fixtures with no explicit `tier` remain animated
as Studio. If migrating an old explicit `tier: "studio"` deck that used
the *old* top-tier semantics, change it to `pro` and review its saved
storyboard. Do not silently reinterpret an ambiguous old Studio label.

## Branch and deck isolation

A new presentation must have a unique **branch** and **deck slug**, for
example `decks/robotics-roadmap` and `robotics-roadmap`.
`decks/robotics-roadmap/{storyboard.json,deck.json,sources.json}` is the
project's source. Other decks belong on their own branch and slug.
The selected branch is recorded in both storyboard and deck metadata.
The agent must create it from main, must not reuse an unrelated branch,
and should commit only that deck's changes. For revisions, reuse the
original branch and slug; the Git baseline is always for that deck.
Different branches have separate GitHub Actions concurrency groups.
Do not merge a deck into main without permission.

## Design preferences

Include the same `design` in the internal storyboard and `deck.json`:

```json
{
  "branch": "decks/robotics-roadmap",
  "tier": "studio",
  "animation_mode": "presenter",
  "design": {
    "primary_color": "#2563EB",
    "style": "Swiss minimalist with generous whitespace"
  }
}
```

- `design.primary_color`: exact six-digit HEX, with leading `#`.
  The renderer applies it to visible accents and charts and adjusts shade
  if needed for sufficient contrast against the slide background.
  The palette's `theme.primary` means **primary text**, not brand color.
- `design.style`: freeform natural-language style, not merely a theme
  filename. The agent must reflect it in storyboard composition, typography,
  whitespace, image treatment, hierarchy and final renders. The renderer
  selects a base serif/editorial, scientific or modern theme from style
  keywords, and additional explicit `theme` properties remain supported.
- For a whole-deck redesign, record a **deck-wide revision** and update
  design settings. Don't modify the original storyboard merely to satisfy
  a slide-edit comment.

## Two slide counts

`requested_slide_count` and `slides.length` count **unique logical slides**,
including cover, TOC and ending. A chapter TOC reused in the actual slideshow
appears as extra **physical pages**. E.g. 20 logical slides and 3 returns
after logical slides 5, 9 and 14 produce **23 PPTX/PDF physical pages**.
`slide-route.json` records each physical → logical mapping.

## Photo TOC and Morph (typically Pro)

For `navigation.mode=hub_return`, provide `hub_slide`, a sorted unique
`return_after` list, and optional `morph`. The hub must be a contents
slide with real entries. Each chapter uses the SAME verified image asset
and semantic `morph_id` as the hub card. The route compiler only Morphs
when those matching subjects are on adjacent **physical** pages and geometry
meaningfully changes. Otherwise use normal Fade or skip the Morph.

Navigation requires `animation_mode=presenter`; a Pro deck can also omit
navigation or use `animation_mode=none` for advanced static layouts.
Do not invent charts or require a photo TOC merely to justify Pro pricing.

## QA

Basic: assert zero p:timing, transitions and Morph. Studio: verify real
On Click / With Previous semantic groups. Pro with TOC: additionally
verify the expanded physical route, image identity, Morph boundaries and
PDF page count. All: visually inspect individual slides and speaker notes.
OOXML validation / LibreOffice render do not prove PowerPoint Slide Show,
Keynote or Google Slides playback compatibility.
