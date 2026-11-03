# Ordo Studio: using a normal ChatGPT conversation

Repository: https://github.com/longnt27/chat-slide-studio

Default user journey: **Prompt → Generate PPTX/PDF → QA → Review actual slides
→ Revise → Deliver**. Storyboards and wireframes are internal.

## 1. Choose the new tier

- **Basic**: static, fully editable slides (no Auto/Fade/On Click/Morph).
- **Studio**: speaker-controlled grouping, On Click and optional Morph.
- **Pro**: advanced layouts, verified charts, optional photo TOC/returns.

Charts are based on real data even for Basic. Pro does not force Morph.

## 2. Give each deck a unique Git branch + deck slug

Example:
- Git branch: `decks/data-infra-onboarding`
- Deck slug: `data-infra-onboarding`
- Source directory: `decks/data-infra-onboarding/`

Use a **new pair for each concurrent project**. Creating separate branches
while writing two different presentations to the same deck slug is still
unsafe after merging or when downloading artifacts. The branch name is
explicit in the prompt. Do not modify a different deck or branch.

## 3. Choose primary color and visual style

Use `#RRGGBB` such as `#2563EB` for a brand hue. Give a visual direction,
e.g. `Swiss minimalist`, `editorial`, `corporate`, `academic` or a
specific reference. The agent saves both in `design` in the internal
storyboard and authored `deck.json`, then incorporates them into real
layout, typography, charts and accent color. Contrast adjustments prevent
invisible color combinations.

## 4. Generate and QA in one request

Ask ChatGPT to read `AGENTS.md`, create EXACTLY the named branch from
`main`, and create the deck in its own slug directory. The internal plan
does not need human sign-off. Generate editable PPTX/PDF, run GitHub Actions
and visual QA, then return slides and artifact links. The workflow supports
1 or 3–80 logical slides.

The CI workflow is triggered by changes to decks/scripts/tests/schemas on
each branch, with branch-specific concurrency. Filter GitHub Actions by
the **exact branch** to download the correct deck artifacts.

## 5. Request changes on the SAME branch

For slide 5 feedback, reference the original branch and slug. Record
`revision_requests.json` pinned to the prior deck commit. Revision QA
checks measurable changes, their scope, before/after images and unintended
regressions. For a new global color/style, use a **deck-wide** request.
Never assume automatic QA equals user acceptance.

## 6. Local example

```bash
# First checkout a dedicated Git branch matching the deck.
python scripts/new_deck.py data-infra-onboarding \
  --title "Data infrastructure" --slides 15 --tier studio \
  --branch decks/data-infra-onboarding \
  --primary-color '#2563EB' --style 'Swiss minimalist'
# Complete storyboard.json internally.
python scripts/check_storyboard.py decks/data-infra-onboarding --proposals-only
python scripts/new_deck.py data-infra-onboarding --from-internal-plan
# Complete the authored deck, source credits and notes.
python scripts/run_pipeline.py --deck data-infra-onboarding
```

## More

[Copyable prompts](../CHAT_PROMPT.md), [revision QA](revision-workflow.md),
[tiers/navigation](tiers-and-navigation.md), [design QA](design-qa.md),
[animation](animation-direction.md), [source images](image-sourcing.md).
