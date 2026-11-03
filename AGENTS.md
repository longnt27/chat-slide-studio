# Chat Slide Studio: GitHub-connected slide production agent

Read this file whenever a user requests a deck through this repository. This is
GitHub-hosted operating guidance for a normal ChatGPT conversation, not an
installed Skill or a requirement to use Work.

## Production workflow: build first, review actual slides

**DO NOT ask the user to approve wireframes or a storyboard before the first
PPTX build.** The storyboard is now an INTERNAL intermediate representation.
The user reviews actual rendered slides, not wireframe sketches.

1. Read \`SKILL.md\`, \`references/tiers-and-navigation.md\`,
   \`references/semantic-layout.md\`, \`references/animation-direction.md\`,
   \`references/image-sourcing.md\`, and \`references/design-qa.md\`.
2. Interpret the brief and choose \`content\` (static), \`presenter\` (grouped
   Auto/On Click with optional purposeful Morph), or \`studio\` (optional
   sourced data charts and photo TOC navigation). Never force effects or charts.
3. Create a feature branch for the deck. Write a complete internal
   \`decks/<slug>/storyboard.json\` with exactly the requested number of
   **logical** slides, meaningful headings, content relationships, composition,
   sourced visuals, click order and justified Morph pairs. No TODOs.
4. Validate with \`python scripts/check_storyboard.py decks/<slug> --proposals-only\`.
   Wireframe rendering is available as an INTERNAL diagnostic; it is **not**
   an approval checkpoint or a user deliverable.
5. Generate an editable \`deck.json\` from this plan using
   \`python scripts/new_deck.py <slug> --from-internal-plan\`, replace all
   placeholders with researched real content, source citations and speaker
   notes, and populate \`sources.json\`.
6. Run CI to build actual PPTX/PDF and PNG slide previews; inspect the montage
   AND individual full-size slides. Fix errors in source and rebuild.
   **Send the user slide previews and actual artifacts in this same production
   workflow, without waiting for storyboard sign-off.**
7. User feedback applies to the ACTUAL SLIDES. Support both whole-deck comments
   and logical-slide-specific edits. After each edit run revision acceptance
   tests, regular PowerPoint QA and visual regression. Present before/after
   evidence for review. Never mark a user's feedback as accepted on their behalf.
8. Deliver final PPTX/PDF, speaker notes, asset credits, QA report and CI link.
   Do not merge a deck branch to main unless the user authorized it.

## Slide revision contract (required)

For an already-built deck, preserve the previous \`deck.json\` commit SHA as
\`baseline_commit\` in \`decks/<slug>/revision_requests.json\`.
Use **logical** slide numbers even when the Studio tier duplicates a TOC in
the physical PPTX/PDF. Structure:

\`\`\`json
{
  "version": 1,
  "baseline_commit": "FULL_40_CHARACTER_SHA_OF_PRE_EDIT_COMMIT",
  "requests": [
    {
      "id": "CR-001",
      "scope": "slide",
      "slides": [5],
      "feedback": "Remove the obsolete point from slide 5; keep the remaining animation.",
      "checks": [
        {"kind": "text_removed", "slide": 5, "text": "Obsolete point"},
        {"kind": "animation_preserved", "slide": 5}
      ]
    }
  ]
}
\`\`\`

For deck-wide feedback use \`scope: "deck"\` and explicit checks on the slide
numbers being modified. Available assertion kinds:
\`slide_changed\`, \`text_removed\`, \`text_added\`, \`text_replaced\` (old/new),
\`title_equals\` (text), \`layout_is\` (value), \`image_changed\`, and
\`animation_preserved\`.

One or more checks MUST match the user's actual wording where measurable.
\`slide_changed\` alone proves only that files differ, NOT that the change is
semantically correct. Preserve the original comment in \`feedback\`. The
revision checker compares with the pinned Git baseline, rejects no-op changes
and rejects edits outside an explicit slide scope. Changing a layout or number
of items is allowed ONLY when the revision record authorizes that slide.
Unchanged slides remain bound to the original internal plan.

Run:
\`\`\`bash
python scripts/revision_qa.py decks/<slug> --report decks/<slug>/dist/revision-qa.json
python scripts/run_pipeline.py --deck <slug>
\`\`\`

The pipeline also attempts a **before/after visual comparison** by rendering
the Git-pinned baseline with the current engine. If historical assets or
rendering tools are missing, \`revision-visual.json\` must say \`NOT_RUN\`;
do NOT imply the visual check passed. The script detects unexpected visual
changes outside the authorized logical-slide scope and generates paired images
for revised slides when it can render both versions.

Always distinguish: **structural/machine pass**, **semantic/visual review**,
and **user acceptance**. Human confirmation is still needed to determine
whether subjective intent was met. Do not promise fully automatic semantic QA.

## Core composition rules

- One factual, meaningful message per slide, not a made-up slogan. Thanks/Q&A
  pages must be plain unless the user explicitly asks for a creative ending.
- Geometry follows relationships: \`peers\`, \`hierarchy\`, \`reciprocal\`,
  chronology or comparison. Center incomplete rows. Avoid decorative rules.
- Use original verified, credited images; do not crop a face or meaningful
  historical object. Natural captions, no condescending disclaimers.
- For enabled animation, the whole semantic content group enters together;
  each needed pause uses a real On Click trigger. Title/first idea may be Auto.
- Morph is optional. Match an actual subject and identical verified image bytes
  between adjacent physical slides with meaningful position/scale changes.
- Count 20 unique logical slides + 3 TOC returns as **23 physical pages**, not 20.
- Check notes, sources, images, chart editability, overflow, spacing, click cues,
  Morph pairs, preview renders and PDF slide count.
- Static PDF/PNG and OOXML validation do NOT prove that a PowerPoint Slide Show
  plays animations correctly. State this limitation.

## Legacy approvals

Older decks may contain \`approval.json\`. Verify its real recorded user approval
and plan hash; do not fabricate one. **New decks must not require it.**
The legacy \`--from-approved-plan\` command remains for backward compatibility.
See \`references/hitl-approval.md\` for migration details.

## Repository entry points

- Internal planning: \`scripts/new_deck.py\`, \`scripts/check_storyboard.py\`,
  \`scripts/render_storyboard.py\`.
- PowerPoint: \`scripts/check_spec.py\`, \`scripts/run_pipeline.py\`,
  \`scripts/build_deck.cjs\`, \`scripts/patch_animations.py\`.
- Revision: \`scripts/revision_qa.py\`, \`scripts/visual_revision.py\`.
- QA: \`scripts/qa_pptx.py\`, \`scripts/render_deck.py\`, \`tests/\`.
- Specs: \`schemas/storyboard.schema.json\`, \`schemas/deck.schema.json\`.
- CI: \`.github/workflows/build-slides.yml\`.

Use actual GitHub Actions results, not guessed sandbox paths. Do not modify the
demo deck to satisfy a user's unrelated brief.
