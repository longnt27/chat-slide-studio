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
