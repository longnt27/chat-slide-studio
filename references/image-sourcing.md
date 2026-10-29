# Real images, copyrights, fallback retrieval and composition

## Source policy

1. Prefer original/authoritative providers, museums, archival libraries, official institutional photographs, Wikimedia Commons with explicit licenses, and original diagrams. Use the historical scene/period's *actual* evidence if claiming it depicts an event; do not decorate a battle slide with an unrelated building photo.
2. For each asset, save: file name, subject, author, license, license URL, original source page, date of retrieval, SHA-256, and role (portrait/document/diagram/decorative). If uncertain, omit it or label it as an illustration, never invent attribution.
3. Put complete credit in Speaker Notes and `credits.csv`; on-canvas caption should identify relevant subject or event, not tell the audience obvious things they already know. Avoid repetitive “không phải...” disclaimers in the slide.
4. Never copy an image discovered through a search snippet without verifying its identity. Search tools/connector results are leads, not permission or final evidence.

## Working around blocked Internet

- Try image search / source lookup, public GitHub connector that can read binary content, direct raw/Commons URLs and compatible file materialization tools; do not assume Python requests is the only path. Do not push user-owned/private files to a public repository.
- If the local container lacks network access, create a **dedicated feature branch** in a permitted GitHub repo, commit an asset manifest and builder, let GitHub Actions fetch with `urllib`/HTTP, install PptxGenJS and embed photos, then upload the PPTX/PDF/credits/QA as an artifact. Inspect workflow logs and downloaded artifact. Never claim it has succeeded before actual verification.
- Do not scatter unlicensed internet images across a repo; check licenses and use a documented download stage. When CI cannot fetch a required image, fail clearly or choose another verified source, never silently substitute the wrong subject.

## Image framing rules

- **Factual photo/portrait/artifact/diagram:** use `contain` or subject-preserving frame. Keep all faces, crowns, hands in meaningful gestures, architectural roofs, artworks and relevant diagram labels. Letterboxing or a quiet blurred, darkened background is preferable to cutting through the subject.
- **Decorative hero background:** `cover` allowed only if focal point survives and source still represents the topic. Position crop manually where necessary, verify actual screenshot, do not let foreground copy obscure the subject.
- Equal cards use consistent photo boxes. If the subject is a portrait, change the layout to a portrait-friendly aspect ratio rather than squeezing a portrait into a wide strip. Never place a landscape monument in a skinny tall column.
- Consider negative space, caption contrast, alignment, composition, visual hierarchy and even source-image quality. Blurred background should be subtle, not a gigantic distracting gradient.
- Inspect the actual rendered PNG of every image-bearing slide at full resolution. Programmatic "no crop" does not prove visual quality; mechanical face detection is not required and can fail.

## Example: a real historical mismatch

Bad: 1858 conflict slide uses a modern photo of Huế and says it is "not a battle photo". Better: use a relevant 1858 engraving if available, caption it by event/document, credit its archival source in notes. Bad: a rectangular card photo frame clips the emperor's head. Better: portrait-size insert with neutral side panels or a redesigned card; no crop through face.

Use `scripts/fetch_assets.py` for provenance and `scripts/fit_image.py` for deterministic subject-preserving composition.
