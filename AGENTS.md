# Chat Slide Studio: instructions for ChatGPT with a GitHub connector

**Use from a normal ChatGPT conversation. This repository is NOT an installed Skill and does NOT require Work.** Read this file when the user shares the repo link and asks for slides.

## Mandatory workflow: TWO SEPARATE USER TURNS

### Stage 1: PROPOSE LAYOUTS, DO NOT BUILD A PPTX

1. Read `SKILL.md`, `references/hitl-approval.md`, `references/story-design.md`, `references/semantic-layout.md`, `references/animation-direction.md`, `references/image-sourcing.md`, and the schema `schemas/storyboard.schema.json`.
2. Classify the relationships in each conceptual slide (equal peers, hierarchy, reciprocal exchange, process or comparison) **before** drawing boxes. Then develop an **exact slide-by-slide storyboard**. Use the explicit requested slide count, including opening and thanks. Every slide must state: number, factual headline, audience takeaway, layout type, proposed composition (columns, hierarchy, text/figure positions), visual/asset plan, number of content units, automatic versus On Click reveal order, and any justified Morph relationship.
3. Choose actual, content-led headlines. **No invented aphorisms, marketing slogans or poetic closing lines**. Especially on the thanks slide: use only `Cảm ơn`, `Xin cảm ơn`, `Thank you` or a straightforward Q&A line unless the user explicitly asks for a creative closing and approves it in this storyboard. Never inject "Lịch sử là mạch nối" or similarly generic sentiment just to fill space.
4. Create a feature branch; commit ONLY `decks/<slug>/storyboard.json` and, if helpful, image sourcing notes. Do NOT create `deck.json`, `approval.json`, PPTX, PDF or final artifact in this stage. `python scripts/new_deck.py <slug> --title "..." --slides <N>` generates a proposal skeleton that must be filled with genuine content, not TODO placeholders.
5. Validate with `python scripts/check_storyboard.py decks/<slug> --proposals-only` and generate **wireframe thumbnails**, not final slides, using `python scripts/render_storyboard.py decks/<slug>`. GitHub Actions can publish a storyboard preview artifact even before approval. Show the user the storyboard table and wireframes in chat, and **STOP**. Request approval or changes of the layout plan only. Do NOT continue in the same turn by inventing assent, and do NOT treat silence as approval.

### Stage 2: ONLY AFTER EXPLICIT USER APPROVAL

6. Read the user's approving message. If it contains changes, revise storyboard, regenerate preview and present it again. If it unambiguously approves the specific final storyboard, store a lock `decks/<slug>/approval.json` with `status=approved`, `approved_by=user`, `approval_channel=chat`, the real short verbatim `approval_quote`, timestamp, and SHA-256 digest of the **canonical full storyboard JSON**. Use `scripts/check_storyboard.py ... --approve-quoted "..."` if code execution is available. **Never fabricate user approval.** The digest checks version integrity, not human identity. The demo fixture's special channel may NEVER be used for production decks.
7. Create `deck.json` from the approved plan using `new_deck.py --from-approved-plan <slug>`, then author full slide content and `sources.json`. `check_spec.py` and CI must enforce the approved slide count, slide order, layouts, headlines, content unit counts, animation sequence, and Morph destinations. If any of these change, STOP for reapproval before rebuilding. Minor typo/layout QA adjustments that do not change approved structure are fine.
8. Build via the reusable source and GitHub Actions, on the feature branch. Check run logs, download the actual artifact, visually inspect the montage and slides at full resolution; fix and rerun. **Do not merge to main without permission**. Deliver PPTX, PDF, credits, montage, run URL and any remaining playback limitations.

## Non-negotiable slide rules

- **Semantic geometry:** layout must reflect conceptual meaning, not available grid cells. Use `diagram_relationship: peers | hierarchy | reciprocal` for diagrams in the storyboard and deck. Peers share visual status and incomplete rows are centered; reciprocal exchange is shown as two sides with a bidirectional connection. These are default principles, not an item-count-specific hack. See `references/semantic-layout.md`.
- **Divider restraint:** start with zero decorative rules. Prefer whitespace, alignment and section grouping. A single line encoding chronology or a genuine separation can be worthwhile, but avoid header + card + footer horizontal lines on the same slide. CI enforces a conservative default long-rule budget.

- One slide = one useful message. A title describes content; a subtitle adds evidence/context, not a slogan. Do not create repeated marketing-style hooks or a metaphor on every page. The thanks page is a clean thank-you / Q&A, not an opportunity to fabricate an inspirational quote. Respect requested tone.
- Every image must be genuine and relevant to its claim, traced to author/license/source. Preserve full faces, hats, building roofs and artifacts. `cover` is allowed only on intentionally decorative images marked `decorative: true` after visual checking. Do not write condescending captions such as "không phải ảnh chiến sự".
- For every peer list, title and first content unit may appear automatically. Later content units that need separate narration **must be On Click**, with the frame, photo, icon, title, caption, body and separator entering **together**. Equal peers use the same effect and duration; never animate a card border after its text.
- The native animation writer uses the **PowerPoint-authored Fade preset 10**, `clickEffect` for the first shape of a click and `withEffect` for its peers. CI checks these actual trigger types and build targets, not merely for a `p:timing` tag. Do not claim that PDF render proves PowerPoint slideshow playback.
- Morph ONLY when the same tangible subject bridges adjacent slides and the transition explains its enlarged detail/context. Use the identical original image bytes (no separately precomposed/letterboxed screenshots). Keep the paired `!!subject` unique and avoid Morph on page numbers, list numbers, title chrome or decorative frames. A valid matched asset but no meaningful geometry change is an error; a long cross-screen journey is also an error. Plan Morph **before** approval, not as post-processing decoration.
- Optically align to the parent's true center; inspect both text alignment and coordinates. Equal card widths/gaps, symmetrical margins, no orphan words, no cropped documentary subjects and no unintended overlap.
- Record speaker notes, source URLs, and every presenter click cue on each slide. Deliver the **exact requested slide count**, not a shorter demo.

## Repository source of truth

Read these in order when relevant:
1. `SKILL.md` and `references/hitl-approval.md` (process and lock)
2. `schemas/storyboard.schema.json`, `references/story-design.md` (Stage 1)
3. `schemas/deck.schema.json`, `decks/demo/deck.json` (Stage 2 data contract)
4. `references/animation-direction.md`, `references/design-qa.md`, `references/image-sourcing.md`
5. `references/semantic-layout.md`, `references/chat-github.md`, `.github/workflows/build-slides.yml`, `references/ci-troubleshooting.md`

Scripts: `check_storyboard.py`, `render_storyboard.py`, `new_deck.py`, `check_spec.py`, `fetch_assets.py`, `build_deck.cjs`, `patch_animations.py`, `qa_pptx.py`, `render_deck.py`, `run_pipeline.py`.

The user should be able to paste a repo link and a topic, review one proposed storyboard, and then approve. Do not ask them to copy JSON, run the builder locally, redownload images, or repeatedly re-explain the same slide design standards.
