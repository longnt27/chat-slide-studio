# Revising a generated deck: verified slide-level and global feedback

Wireframes/storyboards are internal. Users comment on actual PowerPoint slide
previews. Do not patch the pre-production storyboard after a user revision;
record the authorized difference against the original internal plan.

## Step 1: capture the baseline and user feedback

The baseline is the **Git commit containing the previous deck.json**, not the
current commit with partially edited slides. Use the full 40-character SHA.
Create \`decks/<slug>/revision_requests.json\`:

\`\`\`json
{
  "version": 1,
  "baseline_commit": "REPLACE_WITH_PRE_EDIT_40_CHAR_COMMIT_SHA",
  "requests": [
    {
      "id": "CR-001",
      "scope": "slide",
      "slides": [5],
      "feedback": "Remove the obsolete point from slide 5; keep the other animations.",
      "checks": [
        {"kind": "text_removed", "slide": 5, "text": "Obsolete point"},
        {"kind": "animation_preserved", "slide": 5}
      ]
    }
  ]
}
\`\`\`

Always use logical slide numbers, never physical position when a Studio TOC
appears more than once. For an overall redesign, use \`scope: "deck"\`; put
specific logical slide numbers on each acceptance check. \`feedback\` should
preserve the user's request faithfully, not invent a stronger claim.

Supported machine assertions:
- \`text_removed\`, \`text_added\`: \`slide\` and \`text\`.
- \`text_replaced\`: \`slide\`, \`old\` and \`new\`.
- \`title_equals\`: \`slide\` and \`text\`.
- \`layout_is\`: \`slide\` and new \`value\` (layout must actually change).
- \`image_changed\`: \`slide\`; checks asset identifiers, not visual framing.
- \`animation_preserved\`: \`slide\`; compares animation mode and surviving
  content groups' reveal triggers, but does not certify desktop playback.
- \`slide_changed\`: \`slide\`; verifies a nontrivial source change only.
  **It does not prove that subjective intent was satisfied.**

Multiple requests can target different slides within the same revision.
Changes outside the union of authorized slides are blocked. One or more
machine assertions must pass for each revision request, and a no-op edit fails.

## Step 2: run checks and build

\`\`\`bash
python scripts/revision_qa.py decks/<slug> --report decks/<slug>/dist/revision-qa.json
python scripts/run_pipeline.py --deck <slug>
\`\`\`

\`check_spec.py\` reads the revision record before allowing structural
deviations from the original internal storyboard. Unchanged slides still
have to match that plan. The usual PowerPoint QA still runs in full.

The pipeline attempts to re-render the pinned original deck and compares each
physical slide with its revised counterpart. If successful, the output includes
\`revision-visual.json\` and \`dist/revision-comparison/*before-after.png\`.
It checks whether unrequested slides suffered visual regressions. If old
images/assets are not available, it records \`NOT_RUN\`, NOT a false PASS.

## Step 3: user acceptance

Machine check = required conditions observed in source/PPTX. Visual inspection
= typography/crop/composition. Semantic review = interpreted user intent.
Human acceptance = user confirms the result is right. Keep these distinct.
Neither a green CI run nor a model's self-evaluation is user acceptance.

Legacy \`approval.json\` belongs only to projects that genuinely received
storyboard approval under the older process; do not manufacture it for new decks.
