# Using Chat Slide Studio in a regular ChatGPT conversation

Repository: https://github.com/longnt27/chat-slide-studio

The default experience is now **Prompt → Generate PPTX/PDF → QA → Review Slides
→ Revise → Deliver**. Wireframes are internal engineering artifacts and are
not presented as a separate sign-off milestone.

## 1. Connect GitHub

Connect GitHub in ChatGPT with access to read/write branches, see GitHub Actions
and inspect the resulting artifacts. Work mode and installed Skill ZIPs are not
required. At the beginning of each presentation request, provide the repo URL
and instruct ChatGPT to read `AGENTS.md`.

## 2. Select tier

- **Content:** fully static, editable slides; no Fade, On Click or Morph.
- **Presenter:** native grouped On Click reveals; meaningful Morph is optional.
- **Studio:** data-heavy layouts and optional photo TOC with chapter returns.

No tier forces charts or animation. In a 20-logical-slide Studio deck with three
TOC revisits, the PPTX/PDF has 23 physical pages. Report both counts.

## 3. Generate in a single user request

Tell ChatGPT the topic, exact slide count (1 or 3–80), audience, duration,
sources and tier. It must internally plan all slides in `storyboard.json`, validate
that plan, author `deck.json` plus sources and notes, build the actual PowerPoint,
render each slide, run CI, fix defects and return preview/artifact links.

The user should NOT be asked to inspect wireframe thumbnails or approve the
storyboard before generation. An internal storyboard can still be rendered
by the QA tool, but it is not the presentation review surface.

## 4. Review and revise actual slides

After reading the previews, comment on any logical slide number or issue a
whole-deck request. For specific slides, quote the content to remove/replace
and say what should remain unchanged when useful. The agent:
1. Pins the Git commit that contains the previous deck specification.
2. Records every comment and deterministic acceptance checks in
   `revision_requests.json`.
3. Updates the PPTX source, then runs `revision_qa.py` against that baseline.
4. Builds the complete PPTX and reruns structural and animation QA.
5. Attempts before/after visual rendering and regression checks on untouched
   slides. If a previous asset is missing, reports `NOT_RUN` rather than PASS.
6. Shows revised slides and QA evidence for the user to approve or comment again.

The original storyboard is an internal baseline. User-authorized changes to
layout, title or content-unit count on a targeted slide can depart from it;
other slides remain protected by the plan and the pinned revision baseline.
No need for a second wireframe approval.

## 5. Receive the files

Find the GitHub Actions run `Build and QA PowerPoint decks` on the relevant
branch, inspect the **Success** status, then download the artifacts: editable
PPTX, PDF, montage and per-slide PNG, image credits and machine QA report.
For a revised deck, expect `revision-qa.json` and `revision-visual.json`.
The latter explicitly reports whether the before/after render comparison ran.

Static render and OOXML checks do not prove native PowerPoint On Click/Morph
playback. Verify those effects in Microsoft PowerPoint when possible.

## 6. Local commands

```bash
npm install
python -m pip install python-pptx lxml Pillow PyMuPDF jsonschema

python scripts/new_deck.py my-deck --title "Presentation title" --slides 20
# Complete internal storyboard.json, no TODOs.
python scripts/check_storyboard.py decks/my-deck --proposals-only
python scripts/new_deck.py my-deck --from-internal-plan
# Complete deck.json and sources.json.
python scripts/run_pipeline.py --deck my-deck

# For an existing deck: pin its prior Git SHA in revision_requests.json
python scripts/revision_qa.py decks/my-deck
python scripts/run_pipeline.py --deck my-deck
```

Further information: [revision checks](revision-workflow.md),
[design QA](design-qa.md), [animation](animation-direction.md),
[semantic layout](semantic-layout.md), [CI troubleshooting](ci-troubleshooting.md).
