# How a ChatGPT conversation uses this repository

This is the cross-chat protocol. The user only needs a GitHub URL and a topic/brief; the assistant uses the GitHub connector to read/write repository files and inspect workflow runs.

## First turn: link + user brief

- Fetch `AGENTS.md`, `SKILL.md` and source JSON schema using the GitHub connector. Do not rely on approximate memories of a previous deck.
- Parse the requested count (e.g. **15**). Set `requested_slide_count` to exactly **15**, then author **15** unique slides with proper narrative and notes. The source JSON count, actual PPTX count and actual PDF page count must agree. If no count is supplied, choose a reasonable one and encode that number explicitly. Do not cite an 8-slide demo as proof of meeting a 15-slide request.
- Read the user's outline or attached content; create a coherent slide arc and speaker notes, not a thin translation or random 15 identical cards.
- Search/reference sources for historical, scientific or product claims. Verify the licensing and exact identity of each image. Prefer Wikimedia Commons `commons_title` when the image is publicly licensed. Use `sources.json` with stable source IDs and explicit attribution.
- Create branch `feat/deck-<slug>` from the repo default branch, using connector actions; write only `decks/<slug>/deck.json`, `sources.json`, and any allowed local source files. A branch push triggers GitHub Actions.

## During build

- Read `.github/workflows/build-slides.yml` to know artifact name and commands. Query real GitHub Actions runs for the new commit SHA/branch. A green commit status alone is not enough if no artifact exists.
- If CI fails, read job steps and logs, fix the source and push again; preserve all contents of the deck during edits.
- Once success, retrieve `powerpoint-decks-<run number>` from that **specific run**. Inspect deck PPTX, report and montage; review individual rendered slide images, especially portraits, diagrams, dense cards and thanks. If layout looks wrong, revise and rerun.
- Distinguish an actual PowerPoint playback test from structural OOXML and PDF render tests. Do not claim animations were seen playing when they were not.
- Do not merge to main or overwrite previous decks unless the user explicitly approves.

## Editing an existing deck

Read current `deck.json`, `sources.json`, notes and QA report. Preserve original content, proven assets, intentional Morph pairs and click pacing. Only change the requested material and any objective defects. Use the same review loop.

## Interface contract (deck.json)

- `requested_slide_count` (required integer): canonical number from the user request, independent of the list length. Build should fail on any mismatch.
- `type`: `cover`, `section`, `cards`, `timeline`, `split`, `diagram`, `comparison`, `quote`, `summary`, `thanks`.
- `notes`: meaningful narration, sources and intended pacing. `source_urls` adds citations to notes.
- `image`: reference ID from `sources.json`. Source images are never guessed by the build engine.
- `reveal`: `static`, `auto`, or `click`. Every `click` creates exactly one semantic step. For an entire multi-component card, use one reveal on the entire card rather than separate reveals on its children.
- `morph_id`: semantic match on a picture across two adjacent slides, with the *same* image asset ID. Add destination slide number (1-based) to `morph_to_slides`.
- `image_mode`: `preserve` by default; only use `cover` with `decorative:true` after visual approval.

## Delivery contract

Send real links to verified PPTX, PDF, preview, image credits and CI run. Keep the final response concise and factual. If connector cannot access or download the artifact, link to the actual Actions run and say why there is no direct sandbox copy.
