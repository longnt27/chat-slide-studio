---
name: chat-slide-studio
description: GitHub-hosted instructions for generating and revising source-driven PowerPoint presentations. Plan slide structure internally, produce actual editable PPTX/PDF, then accept slide-level or deck-wide feedback with baseline-pinned revision QA and visual comparisons. No user wireframe approval required.
---

# Chat Slide Studio: create first, review real slides

This repository is operating guidance read through the GitHub connector in a
normal ChatGPT chat. It is not an installed Skill and does not need Work.

## Single-pass initial production

1. Read \`AGENTS.md\` and the relevant \`references/\` design/QA guides.
2. Select Content, Presenter or Studio by actual presentation needs.
3. Create a private-to-production **internal storyboard** in
   \`decks/<slug>/storyboard.json\`; never ask the user to approve or review its
   wireframe before creating slides. Verify the exact requested logical count.
4. Validate the internal plan, then generate and author a full \`deck.json\`:
   \`python scripts/new_deck.py <slug> --from-internal-plan\`.
5. Build native PPTX, animation, PDF and full-resolution slide previews via CI.
   Audit and revise the result. Give users actual slides to review, not layout
   sketches. Retain the storyboard as an internal structural contract.

## Revision workflow

Slide-specific and global comments both work AFTER the deck is built.
Pin the previous deck specification with a real Git commit SHA and record
feedback with explicit acceptance checks in \`revision_requests.json\`.
\`scripts/revision_qa.py\` verifies a measurable before/after change, that
requested text was truly removed/replaced, that animation was preserved when
requested, and that unaffected slides did not change. Rebuild with
\`scripts/run_pipeline.py\`; \`scripts/visual_revision.py\` attempts paired
render comparisons and reports when visual regression could not run.

Subjective design quality requires visual/semantic review and user acceptance;
an automatic machine pass is NOT a declaration that user intent was met.
Revisions may legitimately change the layout or content-unit count of an
explicitly targeted slide without mutating the original storyboard. Other
slides must still follow the internal plan.

## Non-negotiable standards

- No invented factual claims, slogans or arbitrary metaphors in titles.
- Geometry must represent peers, hierarchy, reciprocity, timeline or comparison.
- Speaker notes, image/source credits and edited PowerPoint chart objects
  should survive final export. Preserve complete photo subjects.
- Animation, when enabled, operates on meaningful groups, with real
  PowerPoint On Click triggers. Morph needs an actually shared subject with
  meaningful geometry change and adjacent physical slides.
- Preserve logical vs physical slide count, especially on Studio TOC returns.
- Run structural checks AND inspect rendered PPTX/PDF. PDF does not prove
  PowerPoint playback; never claim it does.
- Do not merge unrelated deck branches into main without authorization.

## Commands

\`\`\`bash
python scripts/new_deck.py my-topic --title "Presentation title" --slides 15 --tier presenter
# Fill the INTERNAL storyboard.json with final plans, no TODO.
python scripts/check_storyboard.py decks/my-topic --proposals-only
python scripts/new_deck.py my-topic --from-internal-plan
# Fill deck.json, sources.json and notes with final content.
python scripts/run_pipeline.py --deck my-topic

# AFTER user feedback: create revision_requests.json pinned to the prior commit,
# implement the specific edits, then run full revision + PPTX QA:
python scripts/revision_qa.py decks/my-topic
python scripts/run_pipeline.py --deck my-topic
\`\`\`

Legacy \`approval.json\` and \`--from-approved-plan\` continue to work for
previously authored decks, but are NOT prerequisites for new decks.
