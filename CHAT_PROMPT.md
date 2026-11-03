# Professional prompts for Chat Slide Studio

The examples below work in a normal ChatGPT conversation with a connected
GitHub repository. The storyboard is internal: do not ask for wireframe approval.
Users review completed slide previews and request changes from those.

## Content tier

```text
Use https://github.com/longnt27/chat-slide-studio.
Read AGENTS.md and all relevant references.
Create a 12-slide PowerPoint on [TOPIC] for [AUDIENCE], lasting [DURATION].
Select tier=content and animation_mode=none.
Prioritize clear composition, verified facts, credited images,
editable chart objects where appropriate, and speaker notes.

Plan internally, then build and QA the actual PPTX/PDF in the same
workflow without requesting wireframe approval. Render slide previews,
correct problems, and provide verified artifact links and QA results.
Do not merge the deck branch without my permission.
```

## Presenter tier

```text
Use https://github.com/longnt27/chat-slide-studio.
Read AGENTS.md and all relevant references.
Create a 15-slide PowerPoint on [TOPIC] for [AUDIENCE], lasting [DURATION].
Select tier=presenter and animation_mode=presenter.
Use grouped On Click reveals when helpful, and selective Morph only when
the same subject continues across adjacent slides. Include click cues
in speaker notes and credit all external images and claims.

Plan the storyboard internally, generate PPTX/PDF and PNG previews,
run GitHub Actions QA, inspect each slide, and present the results
for my feedback. Do not request wireframe approval or merge the branch.
```

## Studio tier

```text
Use https://github.com/longnt27/chat-slide-studio.
Read AGENTS.md and references/tiers-and-navigation.md.
Create 20 unique logical slides about [TOPIC] for [AUDIENCE],
lasting approximately [DURATION]. Select tier=studio and
animation_mode=presenter. Include a photo TOC at logical slide 2,
revisiting it after logical slides 5, 9 and 14. Report the
20 logical / 23 physical page distinction.
Use meaningful shared-subject Morph only when suitable; include
sourced, editable charts where they genuinely improve comprehension.

Plan internally and build the final PPTX/PDF directly, with slides
rendered and QA verified before asking for review. Provide the artifact,
slide previews and QA report. Do not merge without permission.
```

## Revise specific slides

```text
Revise [DECK / BRANCH] according to these comments:
- Logical slide 5: remove [EXACT CONTENT].
- Logical slide 8: replace [OLD TEXT] with [NEW TEXT].
- Preserve the remaining click animations on slide 5.
- Keep all other slides unchanged.

Create revision_requests.json using the previous deck commit as
baseline and the original comments as acceptance criteria.
Build the updated PPTX/PDF, run revision QA and full slide QA,
compare before/after previews, and submit the changed slides for review.
Do not claim the user has accepted the changes.
```

## Revise the whole presentation

```text
Revise the entire [DECK / BRANCH] with [GLOBAL DESIGN REQUEST].
Keep factual claims, references, slide count and speaker notes intact
unless the feedback explicitly requires a change.

Create a deck-wide revision request pinned to the prior Git commit.
Record specific measurable checks where possible. Rebuild all slides,
run QA, inspect every output page and provide before/after examples.
State explicitly which subjective aspects still require my review.
```

## Review the final deck

```text
Audit [DECK / BRANCH] slide by slide at full resolution.
Check content, readability, crop, typography, alignment, image sources,
editability, notes, On Click sequencing, Morph pairs and slide count.
Fix defects, rerun GitHub Actions, and report machine QA separately
from visual review and actual PowerPoint slideshow verification.
```
