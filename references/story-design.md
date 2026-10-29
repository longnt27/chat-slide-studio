# Narrative and visual storyboard conventions

Create **factual, subject-specific slide headlines**, not marketing hooks. A title tells the audience what that slide actually proves. A subtitle adds context, number, causal relation or evidence; it does not restate the title in emotional language.

## No filler slogans

- Never invent motivational taglines, fake quotations, symbolic metaphors or generic statements for visual decoration. Do not write "Lịch sử là mạch nối", "Hành trình còn tiếp", "The journey begins" or similar content-free lines just because there is empty space.
- **Thanks page:** plain `CẢM ƠN` / `XIN CẢM ƠN` / `Thank you`, optionally `Mời thầy cô và các bạn đặt câu hỏi` or a contact address. No sentimental subtitle unless the user explicitly requested and approved a creative closing in the storyboard.
- Keep educational/history/technical wording neutral and clear. Use provenance in notes, not patronizing negative disclaimers on the canvas. Do not invent dates, metrics, publications or source claims.
- One key idea per slide. Mix evidence formats: portraits, maps, photographs, diagrams, equations, timelines, before/after comparisons only where relevant. Keep sentences concise and put the actual explanation in Speaker Notes.

## Storyboard before production (HITL)

Write the *entire requested number* of proposed layouts before authoring `deck.json`. Every entry declares slide title, one-sentence takeaway, layout kind, composition details, selected visual, count of information units, reveal order and any Morph intent. Show the plan and wireframe to the user and STOP until explicit approval. See `references/hitl-approval.md` for required file-level lock and re-approval rules.

## Animation planning

Example for a three-card slide: heading remains visible; first card fades in at entry; click 1 shows the entire second card; click 2 shows the entire third. If a specific card image must Morph into the next slide, keep that image static and avoid an entrance animation on the Morph target. Layout/card structure and click rhythm are part of the approved storyboard, not the author's spontaneous decision after approval.

For historical topics distinguish contemporaneous source images, later photos of historical sites and modern illustration. An appropriate, natural caption identifies the artifact and timeframe. Detailed caveats and credits go into notes.
