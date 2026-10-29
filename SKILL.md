---
name: chat-slide-studio
description: Repository instructions for creating professional PowerPoint presentations from an ordinary ChatGPT conversation using a GitHub connector and GitHub Actions. Use when the user pastes the chat-slide-studio GitHub repo and asks to prepare slides: first propose a slide-by-slide visual storyboard and stop for explicit human approval (HITL); after approval, generate the exact approved layouts with sourced images, proper native PowerPoint Auto/On Click Fade and selective meaningful Morph, speaker notes, visual QA, and PPTX/PDF CI artifacts. Never invent slogans, especially on the thank-you slide.
---

# Chat Slide Studio, chat-first presentation production

This file is **GitHub-hosted operating guidance**, not an automatically installed ChatGPT Skill. Use the GitHub connector after the user supplies the repo URL.

## Required two-step human workflow

**Turn A = design proposal only.** Read `AGENTS.md` and `references/hitl-approval.md`. Inspect the user brief and identify the exact slide count. Produce `storyboard.json` with **every slide's composition, content thesis, visual choice, click sequence, and optional Morph intent**, alongside a wireframe preview. Present the complete plan to the human and **stop**. Neither deck content nor PPTX nor an approval file may be authored yet. If the plan needs revisions, revise and present it again.

**Turn B = build only if explicitly approved.** Lock the final storyboard with a digest and an authentic approving quote from the user. Author `deck.json` from that approved plan. `scripts/check_spec.py` checks content structure against the lock, including headlines, layouts, content unit count, click order and Morph destinations. Unapproved, stale or modified plans are **hard build failures**. Run GitHub CI, visual QA and deliver actual artifact.

## Content, design and motion standards

- Respect the user's topic and actual evidence. Prefer descriptive headings and short meaningful captions. Ban gratuitous slogans/poetic aphorisms/empty hook sentences, especially on final thank-you page. Default thanks slide: "Cảm ơn" and optional plain Q&A/contact sentence.
- Do not reuse the demo's content or theme. Choose varied but coherent layouts appropriate to the subject.
- Apply **meaning-first geometry**: visually distinguish peer groups, parent-child hierarchy and reciprocal exchange. Specify `diagram_relationship` at HITL approval, and avoid unbalanced incomplete rows. See `references/semantic-layout.md`.
- Default to **no decorative horizontal dividers**. A purposeful line such as a timeline axis may remain, but repeated header/card/footer separators are visual noise, not structure.
- Preserve complete historical/technical/photo subjects. Never crop a face/head or building roof. Image license and credit belong in sources and speaker notes.
- Each presenter's new idea gets its own **On Click** trigger; intro/title/first idea may Fade automatically. A card's panel, image and all text have **the same start and duration**. No arbitrary delayed autoplay. Six peer nodes may enter as one semantic group.
- Native PowerPoint timing must match the PowerPoint-authored Fade oracle (`presetID=10`, `clickEffect` then `withEffect`, proper `bldP` for text). A well-formed XML tag is insufficient; inspect trigger semantics. External viewers may not run PowerPoint animation. Never claim playback verified without testing actual Microsoft PowerPoint Slide Show.
- **Morph is optional, never a quota**. When selected, it must connect the same subject in **adjacent** slides, use the same original image bytes and different purposeful framing, and have a natural geometry path. Reject stationary and excessively distant Morph. Never morph slide numbers or unrelated labels. Limit Morph usage; Fade is the default transition.
- Validate exact requested slide count in JSON/PPTX/PDF; verify alignment, uniform gaps and headings, group entrances, notes, credits, and zero severe overlap. Inspect montage and every suspect full-sized slide.

## Files and commands

- Proposal schema and checks: `schemas/storyboard.schema.json`, `scripts/check_storyboard.py`, `scripts/render_storyboard.py`.
- **Before approval:** `python scripts/new_deck.py <slug> --title "..." --slides 15`; fill proposal, validate and show wireframe. No deck.json.
- **After actual human approval only:** `python scripts/check_storyboard.py decks/<slug> --approve-quoted "<exact approving message>"`; create deck skeleton with `python scripts/new_deck.py <slug> --from-approved-plan`, write content and sources, then `python scripts/run_pipeline.py --deck <slug>`.
- See `references/semantic-layout.md` for meaningful compositions and divider restraint; `references/chat-github.md` for Chat/GitHub action details and CI artifacts.

Do not merge to main or overwrite previous presentation content without authorization. When user asks only to improve this repository engine, regression-test the bundled demo fixture; this is not a request to approve or build a new user's storyboard.
