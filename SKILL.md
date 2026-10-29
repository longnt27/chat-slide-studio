---
name: chat-slide-studio
description: A GitHub-hosted instruction set and CI-powered PowerPoint builder used from ordinary ChatGPT conversations. Read this repository when a user shares its GitHub URL and asks to create, revise, or polish complete slide decks, including content, researched images, speaker notes, semantic On Click animations, selective Morph, visual QA, and verified PPTX artifacts. It works through the GitHub connector and GitHub Actions; no ChatGPT Work mode or installed custom skill is required.
---

# Chat Slide Studio: production contract

This file is **repository guidance** for ChatGPT to read via GitHub. It does not become an automatically installed ChatGPT skill merely because a repo link exists. The user gives a link + topic, and ChatGPT should deliberately read `AGENTS.md` and this file before changing code.

## Workflow

1. Read `AGENTS.md`, then `references/chat-github.md`, `schemas/deck.schema.json`, `decks/demo/deck.json` and the focused references.
2. Build a coherent narrative, verifying factual statements and locating properly attributed source imagery. **Honor the requested slide count literally**: if the user requests 15 slides, set `requested_slide_count: 15`, write exactly 15 slides, and verify 15 actual pages in PPTX/PDF. Never treat a shorter demo as an end-to-end acceptance test. Default 12–16 only when no count is given.
3. Commit `decks/<slug>/deck.json` and `decks/<slug>/sources.json` (and any local images) to a new feature branch. Do not rewrite the shared engine unless a genuine bug is found.
4. Let GitHub Actions perform asset download, PptxGenJS build, grouped auto-Fade and On Click entrance, selective native Morph, PDF rendering, and QA. Inspect actual CI run/logs and download final artifact.
5. Examine the rendered montage **and important slides at full resolution**. Fix ugly crops, awkward alignments, inconsistent spacing and unexplained motion in the source. Repeat the CI loop until acceptable.
6. Deliver an editable `.pptx`, PDF, preview, credits, and CI run link. Do not claim PowerPoint animation playback was tested unless it really was.

## Unbreakable rules

- **Preserve full subjects in images**: never crop through a face/head, the distinctive roof of a building, an artifact or a diagram. Default image mode `preserve`; allow `cover` only for deliberately decorative, verified compositions.
- **One semantic unit = one animation group**: background/card border, icon/photo, title and body appear simultaneously, with the same Fade and duration. A peer list obeys one consistent policy. First card may auto-appear; card 2 waits for click 1; card 3 for click 2. The speaker, not a timer, controls the pace.
- **Morph only on meaningful continuity** across adjacent slides, with the same image and `morph_id`. Never morph slide numbers into list numbers or fly decorative frames around the screen.
- **True centering and pixel QA**: check object geometry plus text alignment, equal card width/gaps, balanced outer margins, readable font, suitable line height, no orphan words and no overlaps.
- **Concise, natural captions**: identify the item or date. No insulting disclaimers obvious to the audience. Notes should contain provenance and relevant qualifications.
- **Speaker notes and citations on every slide**. The deck must remain useful to a presenter, not just a poster.
- **Actual GitHub CI green + artifact + visual review** are required to call a deck production-ready. Static PDF render is not a playback test.

## Reusable scripts

`python scripts/run_pipeline.py --deck SLUG` performs all checks, downloads validated images, builds, animates and renders. `python scripts/run_pipeline.py --all` builds all decks.

To audit or adapt, see `references/design-qa.md`, `references/image-sourcing.md`, `references/animation-direction.md`, `references/story-design.md`, `references/chat-github.md`.
