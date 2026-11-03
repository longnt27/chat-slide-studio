# Ordo Studio: professional presentation prompts

Paste one prompt into a normal ChatGPT conversation connected to GitHub.
The storyboard is an internal step. Each new project must declare BOTH a
unique Git branch and a unique deck slug so concurrent jobs cannot collide.

Required input fields for every new presentation:
- `[BRANCH_NAME]`: a unique branch such as `decks/team-quarterly-q4`
- `[DECK_SLUG]`: a unique folder name such as `team-quarterly-q4`
- `[PRIMARY_COLOR_HEX]`: brand color such as `#2563EB`
- `[VISUAL_STYLE]`: design direction such as `Swiss minimalist`,
  `editorial`, `premium corporate`, or `academic`

Use a different branch and deck slug for every **independent** presentation.
For revisions, reuse the original pair.

## Basic

```text
Use https://github.com/longnt27/chat-slide-studio.
Read AGENTS.md and the relevant references.
Create the exact new branch [BRANCH_NAME] from main.
Use deck slug [DECK_SLUG] and only edit decks/[DECK_SLUG]/.
Confirm neither the branch nor slug belongs to another presentation.

Create a 12-slide presentation about [TOPIC] for [AUDIENCE],
lasting [DURATION]. Tier: basic; animation_mode: none.
Primary brand color: [PRIMARY_COLOR_HEX].
Visual style: [VISUAL_STYLE].
Use this design consistently in layout, typography and accents.

Build accurate, editable, static PPTX/PDF with sourced imagery,
charts only when supported by verified data, and speaker notes.
Keep the storyboard internal. Run GitHub Actions QA, inspect
all rendered slides, correct defects, and return artifact links
with a concise report. Do not merge into main.
```

## Studio

```text
Use https://github.com/longnt27/chat-slide-studio.
Read AGENTS.md and the relevant references.
Create the exact new branch [BRANCH_NAME] from main.
Use deck slug [DECK_SLUG] and only edit decks/[DECK_SLUG]/.
Confirm neither the branch nor slug belongs to another presentation.

Create a 15-slide presentation about [TOPIC] for [AUDIENCE],
lasting [DURATION]. Tier: studio; animation_mode: presenter.
Primary brand color: [PRIMARY_COLOR_HEX].
Visual style: [VISUAL_STYLE].
Use this design consistently in layout, typography and accents.

Plan native grouped Auto/On Click reveals where useful, with
meaningful Morph only for the same subject across adjacent slides.
Include sourced visuals and speaker notes with click cues.
Keep the storyboard internal. Build PPTX/PDF, inspect each
rendered slide, run QA and present completed slides for review.
Do not merge into main.
```

## Pro

```text
Use https://github.com/longnt27/chat-slide-studio.
Read AGENTS.md and references/tiers-and-navigation.md.
Create the exact new branch [BRANCH_NAME] from main.
Use deck slug [DECK_SLUG] and only edit decks/[DECK_SLUG]/.
Confirm neither the branch nor slug belongs to another presentation.

Create 20 unique logical slides about [TOPIC] for [AUDIENCE],
lasting [DURATION]. Tier: pro; animation_mode: presenter.
Primary brand color: [PRIMARY_COLOR_HEX].
Visual style: [VISUAL_STYLE].
Use this design consistently in layout, typography and accents.

Optionally include a photo table of contents at logical slide 2,
revisiting it after logical slides 5, 9 and 14. If used, report
20 logical slides versus 23 physical PPTX/PDF pages. Use verified
images and charts only when there is real numerical evidence.
Morph only matching visual subjects across physical neighbors.
Include detailed speaker notes and appropriately timed On Click cues.

Keep the storyboard internal. Build PPTX/PDF, run QA, inspect
every slide, resolve defects and show the actual slides for review.
Do not merge into main.
```

## Revise selected slides (same branch and slug)

```text
Use https://github.com/longnt27/chat-slide-studio.
Continue the existing presentation on [BRANCH_NAME] in
decks/[DECK_SLUG]/. Do not switch to main or another deck.

On logical slide 5, remove [EXACT CONTENT].
On logical slide 8, replace [OLD TEXT] with [NEW TEXT].
Preserve all unrelated content and existing animation groups.

Pin the previous deck commit in revision_requests.json, record
the exact original comments and measurable acceptance checks,
rebuild the PPTX/PDF, and run structural and visual regression QA.
Show before/after previews and do not assume my acceptance.
```

## Global redesign (same branch and slug)

```text
Use https://github.com/longnt27/chat-slide-studio.
Continue on branch [BRANCH_NAME], decks/[DECK_SLUG]/.
Change the design to primary color [PRIMARY_COLOR_HEX] and
visual style [VISUAL_STYLE] throughout the existing presentation.
Preserve factual content, references, slide count and speaker notes
unless the request explicitly requires other changes.

Record a deck-wide revision against the previous Git commit.
Update design.primary_color and design.style, run full slide
and visual regression QA, and provide before/after evidence.
Do not merge into main or mark the revision accepted for me.
```

## Final QA audit

```text
Audit [BRANCH_NAME], decks/[DECK_SLUG]/, slide by slide.
Inspect layout, readability, image crop, sources, speaker notes,
editable charts, native On Click and Morph structure, slide count,
brand color and design style consistency. Rebuild and fix defects.
Provide the exact CI run, generated artifacts and unresolved
compatibility limitations. Do not merge without approval.
```
