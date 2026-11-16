# Development Log

What was done and what was learned, newest first. Commits are on
`claude/dazzling-darwin-awec2o` (Api_Logic_Client unless marked *TXV* = Test_Xib_View).
For the plan see `ROADMAP.md`; for open items `BACKLOG.md`.

---

## 2026-11-16 — Responsive generator window; Hello menu removed (`6632828`)

- Window: minimum content size 1000 × 620. Entity list from the top edge to the +/−
  buttons, height follows the window. Heading moved right of the list and stretches.
- Every page view is sized to the area beside the list (`FitPageView`, after the toolbar
  is set — the toolbar changes the content area) and resizes in both directions; the
  page XIBs' autoresizing masks pin and stretch their controls.
- Removed the Hello demo menu (`SayHello`, `_textLabel`, `_pushBtn`); Model is menu 2,
  Help menu 3.
- See `features/RESPONSIVE_LAYOUT_FEATURE.md`.

---
