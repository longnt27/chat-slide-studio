# Narrative and visual storyboard conventions

Create **factual, subject-specific slide headlines**, not marketing hooks. A title tells the audience what that slide actually proves. A subtitle adds context, number, causal relation or evidence; it does not restate the title in emotional language.

## No filler slogans

- Never invent motivational taglines, fake quotations, symbolic metaphors or generic statements for visual decoration. Do not write "Lịch sử là mạch nối", "Hành trình còn tiếp", "The journey begins" or similar content-free lines just because there is empty space.
- **Thanks page:** plain `CẢM ƠN` / `XIN CẢM ƠN` / `Thank you`, optionally `Mời thầy cô và các bạn đặt câu hỏi` or a contact address. No sentimental subtitle unless the user explicitly requested and approved a creative closing in the storyboard.
- Keep educational/history/technical wording neutral and clear. Use provenance in notes, not patronizing negative disclaimers on the canvas. Do not invent dates, metrics, publications or source claims.
- One key idea per slide. Mix evidence formats: portraits, maps, photographs, diagrams, equations, timelines, before/after comparisons only where relevant. Keep sentences concise and put the actual explanation in Speaker Notes.

## Choose semantic relationships before layout

For every conceptual diagram, identify whether concepts are equal peers, parent and children, or two sides influencing each other. A row of three equal items may be ideal, while a left-right exchange with three factors grouped opposite another concept can be more truthful for reciprocal influence. These are examples, not hardcoded rules. Never guess causation from the number of boxes or from a single keyword. Avoid decorative divider lines unless they carry structural information. See `references/semantic-layout.md`.

## Storyboard before production (internal only)

Do not pause to ask the user to approve this planning artifact. Build the actual PPTX/PDF and let the user comment on slide previews.

Create the *entire requested number* of internal layouts before authoring `deck.json`. Every entry declares slide title, one-sentence takeaway, layout kind, composition details, selected visual, count of information units, reveal order and any Morph intent. **Do not show the wireframe for user sign-off or pause before building.** Present the rendered PPTX slides for user review. Keep the selected `design.style` and `design.primary_color` in the internal plan and implement them in slide composition.

## Choose the right amount of production

Basic decks have no animation. Studio decks get grouped click reveals only where speaking needs pauses. Pro offers advanced data charts and photo TOC Morph, not a mandatory special effect on every page. Plan tier, color and style internally before building. When a TOC is revisited, each appearance is a physical slide but not an additional unique idea.

`chart` needs traceable numerical data and source, not fabricated example metrics disguised as real results. See `references/tiers-and-navigation.md`.

## Animation planning

Example for a three-card slide: heading remains visible; first card fades in at entry; click 1 shows the entire second card; click 2 shows the entire third. If a specific card image must Morph into the next slide, keep that image static and avoid an entrance animation on the Morph target. Layout/card structure and click rhythm are part of the internal storyboard and must remain consistent with the deck unless authorized revisions change them.

For historical topics distinguish contemporaneous source images, later photos of historical sites and modern illustration. An appropriate, natural caption identifies the artifact and timeframe. Detailed caveats and credits go into notes.
