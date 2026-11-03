# GitHub CI and artifact lifecycle (for ordinary ChatGPT chats)

This repository **already contains a full, runnable GitHub Actions workflow** at `.github/workflows/build-slides.yml`. Do not copy scripts into a temporary `.slide-skill/` path or invent another pipeline for a new presentation.

1. Read `AGENTS.md` and `references/chat-github.md`. Confirm GitHub connector permission to create the exact user-specified dedicated branch from main, with a unique deck slug, and commit `storyboard.json`, `deck.json` and `sources.json`.
2. `decks/**` pushes trigger `Build and QA PowerPoint decks` on feature branches. The workflow installs Node 22, Python 3.12, LibreOffice, fonts, and packages, runs unit tests, builds **changed deck(s) only** with `scripts/run_pipeline.py --changed`, renders slides and performs structural QA.
3. The artifact name is `chat-slide-review-or-pptx-<run number>`. It preserves each deck's relative output path `decks/<slug>/dist/` and includes `.pptx`, `.pdf`, PNG preview/montage, `credits.csv`, and the QA report.
4. Confirm that the workflow run is `completed` + `success`, and get the artifact for **that run and exact head_sha**. Download it through the GitHub connector, not an old file with a similar name.
5. Inspect the rendered montage and larger screenshots. Fix visible defects in `deck.json`, `sources.json` or only when needed in the reusable engine; rerun CI. QA green is necessary but not sufficient for visual production quality.
6. No auto-merge to main, no website deploy, no external asset without author and license, no false claim that Morph playback was tested.

Local reproduction: `npm install && python -m pip install python-pptx lxml Pillow PyMuPDF jsonschema && python scripts/run_pipeline.py --deck demo` (LibreOffice required for PDF). For a new deck, replace `demo` with the folder/ID.

Use `design.primary_color` and `design.style` in both specs. Branch and deck ID must remain stable across revision rounds. GitHub Actions concurrency is already per branch; use distinct slugs too, so exported filenames cannot collide.
