# Contributor notes

Change deck data under `decks/<slug>/` for new presentations. Do not copy an old subject/theme without checking relevance. Engine changes require a sample build, unit tests, machine QA and visual rendering of the demo. Use a feature branch; don't bypass the GitHub Actions check, and don't auto-merge.

Read `AGENTS.md` before making a deck on a user's behalf.

New product tiers: `basic` (static), `studio` (presenter click pacing), `pro` (advanced visuals/navigation). Record a dedicated branch and unique deck slug for every independent project, plus `design.primary_color` (`#RRGGBB`) and `design.style` in both specs. In revisions, stay on the original deck branch.
