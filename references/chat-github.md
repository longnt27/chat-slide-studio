# ChatGPT + GitHub: single-request slide generation

Paste the repository URL and an initial brief into a normal ChatGPT
conversation. Connect GitHub with permissions to create branches, inspect files,
see Actions and retrieve artifact links.

## Current workflow

1. Read `AGENTS.md`, choose a suitable tier and create a deck-specific feature
   branch.
2. Prepare `storyboard.json` **internally** with the exact requested number of
   unique logical slides, content relationships and motion plan.
3. Validate the internal plan, then author `deck.json`, notes and `sources.json`
   in the same production cycle, using `--from-internal-plan`.
4. GitHub Actions builds the PPTX/PDF, checks editability/structure, renders
   slide PNGs and publishes artifacts. Inspect individual slides and fix faults.
5. Show the user **actual slides**, not wireframes, for feedback.
6. On any slide or deck-wide comment, create `revision_requests.json` pinned
   to the previous Git commit, with explicit acceptance checks. Run
   `revision_qa.py` and full build/visual QA; show before/after evidence.
7. Do not claim user acceptance until the user confirms the output. Do not
   merge the deck branch into main without permission.

A 20-logical-slide deck with 3 TOC returns has 23 physical pages. Record the
route in `slide-route.json`. Legacy `approval.json` projects remain supported
but no new workflow should create fake user approvals.

## Developer commands

```bash
python scripts/new_deck.py a-new-topic --title "Presentation title" --slides 15
# Fill the internal storyboard with genuine content/layouts
python scripts/check_storyboard.py decks/a-new-topic --proposals-only
python scripts/new_deck.py a-new-topic --from-internal-plan
# Complete deck.json + sources.json
python scripts/run_pipeline.py --deck a-new-topic
# After user feedback, commit a baseline-pinned revision_requests.json:
python scripts/revision_qa.py decks/a-new-topic
python scripts/run_pipeline.py --deck a-new-topic
```

If the GitHub connection cannot download a generated artifact, provide the
actual GitHub Actions run link; never fabricate a sandbox path.
