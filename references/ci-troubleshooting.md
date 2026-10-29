# CI troubleshooting for chat-driven builds

- **GitHub Actions not triggered**: branch push and changed path must match `.github/workflows/build-slides.yml`. Check whether Actions are enabled. Never report success merely because the workflow YAML exists.
- **`npm install` failure**: check Node 22 and npm registry availability; check package names/versions. Do not quietly ignore install failure.
- **Image download/metadata 404**: verify exact Wikimedia Commons file page, author and license. Fix `sources.json` or choose a different approved image; never silently substitute unrelated visuals. CI should fail loudly rather than output an incomplete deck.
- **`image_mode: cover` rejected**: keep full photo (`preserve`), redesign a frame, or explicitly authorize a decorative crop after visual inspection.
- **`Morph subject mismatch`**: destination slide number in `morph_to_slides` must refer to adjacent slides with exactly the same `image` ID and `morph_id`. Do not Morph between dissimilar concepts.
- **`wrong_auto_vs_click_start`**: adjust card-level `reveal`, not random shape-level animation. Every component of a card inherits the group's reveal.
- **`not_really_centered`**: correct both the text alignment and shape center axis. Do not just increase the textbox width.
- **`unequal_card_gaps`**: use the shared grid component instead of manually placing cards.
- **PDF previews show all card contents**: expected; they are static renderings. On Click trigger validation uses PPTX structure; real playback requires PowerPoint.
- **A blank or ugly slide despite green CI**: open `decks/<slug>/dist/preview/slides/slide-NN.png` from the artifact, fix input layout/source, and rerun. The visual audit is mandatory.

- **CI created only a storyboard preview:** This is the expected HITL Stage 1. The user has not approved and `deck.json` must not exist yet. Show the wireframe artifact and wait.
- **HITL approval missing or stale:** Never bypass `check_storyboard.py`. Re-present the current final storyboard, receive real user approval, then record the quote and digest. A changed plan requires new approval.
- **On Click seems absent in PDF/Google Slides/Keynote:** Those viewers do not prove PowerPoint animations. Inspect the native Microsoft PowerPoint slideshow; machine QA must verify Fade preset 10 and clickEffect/withEffect group triggers. Do not claim playback verified in CI.
- **Morph rough or still:** Check the matched `!!` pair uses identical original picture bytes and visibly different framing. Don't use separately padded JPEG outputs, don't morph decoration, and don't force wildly distant targets.
- **CI passes but thank-you has a slogan:** Inspect `thanks.subtitle`, remove unsolicited tagline, rerun `check_spec.py`; the standard closing should be simple Q&A text.
