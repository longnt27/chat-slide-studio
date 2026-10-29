# Semantic geometry, restraint and diagram review

**Think about the relationship before drawing any boxes.** This is a design principle, not a screenshot-specific layout rule.

## Translate meaning into spatial relationships

Ask what the viewer should infer from the placement:

| Meaning | Typical composition | Misleading alternative |
|---|---|---|
| Equal peers / categories | Balanced row(s) with equal sizes, incomplete rows centered | Two items on top and one stranded in a bottom-left cell |
| Parent → children | Deliberate top-down tree / hierarchy | A ring suggesting equal influence |
| Reciprocal influence | Left ↔ right, two-direction connection; associated peer concepts grouped on one side | Stack that incorrectly implies one-way causation |
| Ordered events / workflow | Directed timeline / sequence with a visible order | Symmetric tiles that erase chronology |
| Comparison | Aligned side-by-side columns | Arbitrary stack hiding the comparison |
| Hub-and-spoke | Center with appropriately connected participants | Disconnected cards implying no relationship |

These are *preferred starting points*, not mandatory shapes. In a dense diagram, readability and semantic correctness outweigh a simplistic "three items always equals three columns" rule. If items cannot fit legibly, split the explanation, abbreviate labels, or propose another diagram during HITL.

The reusable `diagram` renderer supports **`diagram_relationship`**:
- `peers` (backwards-compatible default): items have equal status; their rows share a common center axis.
- `hierarchy`: a parent/root is positioned above equally ranked child items.
- `reciprocal`: the root is to the left, a balanced group of interacting concepts to the right, and the connecting symbol is bidirectional. Never suggest this means every right-hand item is subordinate to the left.

For an approved storyboard, set `diagram_relationship` explicitly on the diagram slide. Copy that exact value into `deck.json`; changing it means a structural change and requires approval again. Do not infer reciprocal influence from a keyword or Vietnamese phrase alone: validate the actual intended relationship.

## Divider restraint

The preferred number of decorative horizontal rules is **zero**. Use typography, white space, layout alignment, background panels and grouping first. Keep a horizontal line only if it **encodes something** (such as the axis of a timeline or a real boundary between sections). Default renderer permits **at most one meaningful long horizontal rule per slide**, and QA counts visible line shapes to catch accidental accumulation. This is a baseline, not a global mandate: exceptionally complex diagrams may justify extra real connectors when explained in the approved storyboard, but decorative header/footer rules do not qualify.

Avoid a top stripe + a caption line + a footer line in the same frame. Borders on a card are not automatically dividers; add them only when they improve visual separation.

## Anti-overfitting checklist

Review the rule against varied topics (history, science, economics), item counts (2, 3, 5, 7), and layouts (comparison, timeline, reciprocal system). If the rule would make a different diagram misleading, refine the rule instead of adding hardcoded phrase/slide-number detection.

Before approving the wireframe, assess:
1. What *relationship* is being conveyed? Is any implied direction false?
2. Are equal-level items genuinely equal in scale and grouping?
3. Is the incomplete row centered, and is the overall visual mass balanced?
4. Does each line, arrow or decorative border earn its space?
5. Would showing fewer ideas or making two slides help more than cramming cards?

## Motion, including Morph

Motion follows the approved story. Do not create a Morph merely because two adjacent slides happen to contain some of the same slide furniture. The plan must name the continuous subject, describe old/new framing, and explain why the viewer benefits. The PPTX QA validates expected destination slides and produces **Morph geometry evidence** (travel, scale, matching subject), but a true playback pass must happen in Microsoft PowerPoint. If that cannot be done, report that native playback remains unverified.

A deck with **zero Morph** is entirely valid when its concepts do not invite an honest continuity transition. Fade is fine.
