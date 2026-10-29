# HITL visual storyboard: the required approval gate

## Why this exists

ChatGPT must not jump from a vague topic into a finished deck with guessed layouts. Every presentation follows a **real two-turn human review**. The user approves not only section headings but also composition, image strategy, reveal order and any Morph.

## Stage A: propose, preview, STOP

1. Infer exact slide count from the prompt; do not shrink a 15-slide request to an 8-slide demo.
2. Create a new feature branch and `decks/<slug>/storyboard.json`, using the schema. Each entry must name:
   - slide number and type (`cards`, `split`, `timeline`, `diagram`, etc.)
   - content-led headline and one audience takeaway
   - **composition**: number of columns, size/position of image or diagram, text hierarchy, gaps; describe what spatial relationships mean
   - **diagram_relationship** for conceptual diagrams: `peers`, `hierarchy` or `reciprocal` (approved before production)
   - **visual**: what image/evidence belongs on that slide, and where
   - `content_units`: exact count of peer cards, events, bullets, diagram items; zero for cover/thanks
   - `reveal_sequence`: `static`, `auto`, `click`, ordered for each content unit, plus a photo step if applicable
   - `morph_from_previous` and a detailed `morph_reason` for true continuity
   - plain thanks/Q&A by default, without an invented inspirational subtitle
3. Keep each proposed layout distinct and legible. Make a readable storyboard **table in the chat** and, if available, show `storyboard-montage.png` from `scripts/render_storyboard.py` (wireframe, not finished slides). A plan of 15 rows is expected when the user requested 15 slides.
4. CI validates proposals and creates wireframe artifacts even with **no approval.json, no deck.json and no PPTX**. If validation fails, fix the plan and show the revised version.
5. **STOP; ask the user to approve or change the storyboard.** Do not produce a final slide deck in this turn. Approval must be an unambiguous user's answer to this specific latest proposal. "OK, duyệt", "chốt bố cục này" qualify; silence and generic compliments do not.

## Stage B: approval lock, then build

Only after an explicit approval turn, write `approval.json` with:

```json
{
  "deck_id": "your-deck-slug",
  "status": "approved",
  "approved_by": "user",
  "approval_channel": "chat",
  "approval_quote": "Duyệt bố cục này",
  "approved_at_utc": "<current UTC timestamp in ISO 8601>",
  "storyboard_sha256": "<sha256 of sorted-key, compact, UTF-8 JSON storyboard>"
}
```

Use the real approval quote, never fabricate a reply or set `approval_channel=demo_fixture` for a production deck. Run `python scripts/check_storyboard.py decks/<slug> --approve-quoted "<exact user words>"` locally when tool access permits; this command records the SHA. Hashing algorithm:

```python
hashlib.sha256(json.dumps(plan, ensure_ascii=False, sort_keys=True,
   separators=(',', ':')).encode('utf-8')).hexdigest()
```

Now `python scripts/new_deck.py <slug> --from-approved-plan` creates a matching `deck.json` skeleton. Fill the content/notes/sources, retaining the **exact approved slide count, titles, layout type, diagram relationship, content unit count, sequence of Auto/On Click triggers and Morph destination slides**. Minor wording refinement inside text bodies and spacing/color fixes that preserve these structural commitments do not require a new review.

**If storyboard, slide structure, presentation timing or Morph changes:** request user reapproval. Existing approval becomes invalid when `storyboard.json` SHA changes; changing deck structure makes `check_storyboard.py`/`check_spec.py` fail. Do not silently change the plan and update its SHA yourself.

## What the machinery can / cannot prove

GitHub CI can prove that an approval record exists, its SHA matches the exact reviewed storyboard file, and the generated deck follows the approved structure. It cannot authenticate who wrote a chat message or whether the user actually agreed. **That human authorization check is the ChatGPT agent's responsibility**. The lone `demo_fixture` approval is for the shipped demo regression test only, never for real presentations.

## Example flow

User: "Tạo 15 slide về lịch sử triều Nguyễn".
Assistant turn 1: Draft a 15-row slide-by-slide composition table, preview, and ask to approve or edit. STOP.
User: "Đổi slide 5 sang sơ đồ. Những cái khác duyệt."
Assistant turn 2: Revise slide 5, regenerate plan and preview. STOP again, because the final version has not yet been explicitly approved.
User: "Duyệt bản mới."
Assistant turn 3: Lock approval, author deck, run GitHub CI, inspect rendered artifact and deliver.
