# Normal ChatGPT + GitHub connector: two-stage workflow

This is not Work and does not install a native ChatGPT Skill. The user pastes the repo URL and a slide topic; ChatGPT reads `AGENTS.md` from GitHub and follows its **two-turn HITL** protocol.

## 1. Prepare a proposal, then stop

- Read the repo instructions, storyboard schema and current engine. From the user's brief, author a complete per-slide `storyboard.json` with the exact requested count and real slide compositions. Do NOT write `deck.json` yet.
- Create `feat/deck-<slug>` branch via GitHub connector. Commit the proposal only; optionally include factual image sourcing notes. New deck folder contains a storyboard and optional `sources.json`, nothing that produces final slides.
- GitHub CI validates all storyboards and creates `storyboard-preview/storyboard-montage.png`, even though there is no approval file and no build. Grab the branch's *actual run* preview artifact and show the user's slide-by-slide plan and preview. **STOP and await explicit layout approval.** User's next message is a real state transition; do not simulate it.
- If user requests edits to the plan, update the storyboard and show a fresh preview; wait again.

## 2. Once the user explicitly approves

- Record the real approving quote (not invented), lock the reviewed `storyboard.json` SHA-256 in `approval.json`, then write `deck.json` **from that exact final plan**. Keep counts, slide order/layout/headlines, content unit count, reveal plan and Morph destinations unchanged. Code enforces these invariants.
- Source image assets in `sources.json` with clear author, license and source page. Write notes and clear content; never add invented concluding slogans.
- Commit approved deck files to the feature branch. GitHub Actions builds only the changed approved deck(s), not a demo accidentally substituted for the requested work. Inspect the actual run and logs; QA checks PPTX, notes, images and native On Click/Auto/Morph semantics.
- Download that run's PPTX/PDF/preview/credits, inspect montage and any suspect full-sized slide; revise without deviating from the approved plan. If approved layout or animation plan needs to change, STOP and get user reapproval. Deliver final artifact and CI run URL. State whether native PowerPoint playback was actually tested.
- Do not merge to main, deploy a website, or overwrite another deck without explicit permission.

## Stage limits

A GitHub commit, an automatically generated wireframe or a green CI run is **not** approval. `approval.json` hash proves storyboard integrity, not actual human identity; the agent is responsible for recording a real human approval in chat. CI can run tests/proposal preview without making slides.

## Commands for reference

```sh
python scripts/new_deck.py a-new-topic --title "Bài thuyết trình" --slides 15
# Fill decks/a-new-topic/storyboard.json with complete proposed layouts.
python scripts/check_storyboard.py decks/a-new-topic --proposals-only
python scripts/render_storyboard.py decks/a-new-topic
# Stop; show proposal to human in chat.

# In a later turn, AFTER real user approval:
python scripts/check_storyboard.py decks/a-new-topic --approve-quoted "Duyệt bố cục này"
python scripts/new_deck.py a-new-topic --from-approved-plan
# Complete deck.json and sources.json from the plan.
python scripts/run_pipeline.py --deck a-new-topic
```

See `references/animation-direction.md` for native effect rules and `references/ci-troubleshooting.md` for GitHub Actions diagnosis.
