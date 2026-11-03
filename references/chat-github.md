# Ordo Studio: GitHub-first, parallel-safe presentations

The repository stays named chat-slide-studio; Ordo Studio is the
product/service brand. Connect GitHub in a normal ChatGPT chat.

For every new presentation, collect or choose:
- `BRANCH_NAME`: dedicated branch from `main`, e.g. `decks/history-vietnam`.
- `DECK_SLUG`: unique folder, e.g. `history-vietnam`.
- Tier: `basic`, `studio`, or `pro`.
- `PRIMARY_COLOR_HEX`: a six-digit HEX brand color.
- `VISUAL_STYLE`: concise design description.

Create the branch before writing any file. Refuse to overwrite an
unrelated existing branch or deck folder. Write `storyboard.json`
internally (without user approval), include `branch` and `design`,
then generate `deck.json`, sources, notes and editable PPTX/PDF.
Run CI on the correct branch and inspect full-size slide renders.

For revisions, stay on the same branch and slug. Pin the previous
deck.json Git commit, record the comments and exact measurable checks,
run revision/visual QA and provide before/after slide previews.
Never merge a deck branch into main without the owner's authorization.

Use [prompt examples](../CHAT_PROMPT.md) and
[full guidance](../AGENTS.md). GitHub Actions artifacts are identified
by branch and run; do not invent download URLs or sandbox links.
