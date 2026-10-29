# ChatGPT agent instructions: this GitHub repo is the slide-production system

**This is a chat-first workflow, NOT ChatGPT Work and NOT an installed Skill.** When a user gives the repository link together with slide content/topic, read this file and `SKILL.md`, then act through the connected GitHub tools.

## Goal and default behavior

Turn a user topic/outline/files into a **complete, editable, production-quality PowerPoint deck** by adding `decks/<slug>/deck.json` + `sources.json`, allowing GitHub Actions to build it, and delivering the verified `.pptx`, PDF, montage and source credits. No user copy-pasting code or manually downloading photos.

- Prefer original user content; research and source missing factual information accurately. Keep the user's requested language. A request for "bài thuyết trình/slide deck" implies a complete deck, with cover, content, conclusion and thanks; default to about **12–16 slides**, unless user requests otherwise. A request for exactly one slide means exactly one slide.
- **Do not copy the demo's subject or visual theme automatically**. Choose the design, imagery and narrative for the new topic; write meaningful speaker notes on *every* slide.
- **Never skip the source's QA** just because CI is green. Inspect the rendered montage and every questionable slide at full size. Fix and rerun until it is polished. Motion requires actual PowerPoint playback verification; structural checks are not playback evidence.
- Preserve the entire existing deck when editing, including notes and intentional effects. Do not silently replace a good version with thinner content.

## Must-read files (in order)

1. `SKILL.md`: high-level, non-negotiable quality contract.
2. `references/chat-github.md`: precise GitHub connector → branch → CI → artifact workflow.
3. `references/animation-direction.md`: On Click vs Auto; Morph rules.
4. `references/image-sourcing.md` and `references/design-qa.md`: image QA, optical alignment.
5. `schemas/deck.schema.json` + `decks/demo/deck.json`: the complete data format.
6. `references/story-design.md`: narrative structure and speaker notes.

## What to do from a normal chat

1. Verify GitHub connector access to the specified repository and its default branch. Inspect existing decks, docs, build workflow and demo. If missing rights, clearly explain and stop before claiming action.
2. Extract the **exact requested slide count** from the chat prompt. Set `requested_slide_count` to that number; author exactly that many `slides` entries. Do not replace a 15-slide request with a shorter 8-slide demo or silently change the count. If the user did not specify, choose a reasonable length (12–16). Every slide has one thesis, necessary supporting details, presenter notes, sources, and deliberate reveal stages. Find fitting images with legal provenance and subject-safe composition. Cite assets in `decks/<slug>/sources.json`.
3. Create a **new branch** `feat/deck-<slug>` or a revision branch; commit only `decks/<slug>/**` except when explicitly fixing the reusable engine itself. `deck.id` must equal folder name. For multiple new files use one Git tree/commit when available.
4. Push the commit(s). CI triggers automatically on `decks/**`. If workflow is disabled or event did not trigger, use manual `workflow_dispatch` *if a connector action permits it*. Never claim a workflow was dispatched without the actual result.
5. Inspect the actual GitHub Actions run/status and job logs. Resolve any failure on the branch. Download artifact and review its PPTX, PDF and montage; fix visible issues in source. Continue the verify/fix loop within available tool access.
6. Only call it done when CI is green, artifact exists, and the rendered slides have been visually checked. Send the finished PPTX, PDF/preview, citations/credits, and run URL. If PowerPoint playback was not tested, disclose that limitation.
7. **Never merge to `main`, overwrite another deck or deploy a website** without explicit user authorization. Feature branch builds are sufficient. Do not mistake a branch commit for a validated artifact.

## Authoring contract

- `requested_slide_count` MUST be the explicit integer requested by the user, independently of `len(slides)`. A 15-slide request with 8 actual slide objects is a **hard failure**, not an acceptable proof-of-concept. Validate against both authored JSON and rendered PPTX/PDF page count. Report the actual count in final delivery.
- Write `decks/<slug>/deck.json` according to the JSON schema. The renderer is reusable; **do not rewrite `build_deck.cjs` for every new deck**. New designs must remain within coherent theme tokens.
- Write `sources.json`: real images from Wikimedia Commons (`commons_title`) or verified HTTPS sources with author/license/source page; optionally checked-in original files using `local_path`. Every used `image`/`morph_id` must have a real associated source. Never silently substitute an unrelated image if download fails.
- Use `reveal: auto` for title/first explanation unit; use `reveal: click` for successive ideas that require presenter pacing. **Frame + image + badge + title + body must enter together**. Peer cards must share Fade/duration. In a hierarchy, elements at the same level can enter together, not six pointless separate clicks.
- Use `morph_to_slides` only when the *identical image asset and `morph_id`* appear on adjacent slides and explain true subject continuity. Never morph page numbers, bullets or decorative frames. Keep overall Morph scarce.
- Keep all meaningful portrait heads, architectural roofs, paintings, documents and objects intact. For sourced subjects, use `image_mode: preserve` (default). Only permit `cover` cropping for genuinely decorative images with `decorative: true`, after visual review.
- Center within the **parent/group axis**, not merely within the textbox: both paragraph alignment and textbox center are tested. Make card widths/gaps and outer margins exactly consistent.
- Avoid pointless disclaimers on the canvas (e.g., "ảnh ngày nay, không phải ảnh chiến sự"). Choose the correct source and use concise, positive captions; put detailed provenance in notes.

## Technology/reproducibility

- GitHub Actions: `.github/workflows/build-slides.yml`.
- Build: `python scripts/run_pipeline.py --deck <slug>` or `--all`.
- Node/PptxGenJS: `scripts/build_deck.cjs`; image validation `scripts/fetch_assets.py` and subject-preserving rasterization inside the renderer.
- Animation: `scripts/patch_animations.py` (native OOXML Fade + On Click + limited Morph), with real PowerPoint playback still subject to test.
- QA: `scripts/check_spec.py`, `scripts/qa_pptx.py`, `scripts/render_deck.py`; all failures are blockers until fixed.

When the user supplies a link and a request, **do the work** using the repo workflow. Do not ask them to manually create JSON, install software, download historical photos, or repeatedly restate the same design requirements.
