# Legacy HITL approvals and the internal-storyboard migration

**Current workflow:** Users review generated slides, not preliminary wireframes.
The storyboard remains an internal structural plan. No explicit approval,
\`approval.json\` file or extra chat turn is needed for the first PPTX build.

## Backward compatibility

Older projects may already have an \`approval.json\` recording an authentic user
decision and a hash of a specific storyboard. The engine continues to validate
these files when they exist. Never forge a user quote or mark an internal plan as
human-approved. \`--from-approved-plan\` is a legacy CLI command only.

New projects should use:

\`\`\`bash
python scripts/new_deck.py <slug> --title "Title" --slides 15
# Complete storyboard.json internally
python scripts/check_storyboard.py decks/<slug> --proposals-only
python scripts/new_deck.py <slug> --from-internal-plan
# Author completed deck.json, notes and sources, then build and QA
python scripts/run_pipeline.py --deck <slug>
\`\`\`

## Revision acceptance replaces the extra review stage

Once users review the actual rendered slides, each comment becomes a
\`revision_requests.json\` change request scoped to specific logical slides
or to the whole deck. The request includes baseline Git commit, original
feedback text and testable acceptance checks. The engine checks targeted edits,
rejects unexpected changes to other slides, renders before/after comparisons
where possible, and generates machine-readable reports.

**Machine QA cannot independently guarantee subjective intent.** Show the
user the revised slide and obtain their acceptance. See
\`references/revision-workflow.md\` and \`AGENTS.md\` for the current contract.
