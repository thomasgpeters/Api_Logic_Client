# Development Log

What was done and what was learned, newest first. Commits are on
`claude/dazzling-darwin-awec2o` (Api_Logic_Client unless marked *TXV* = Test_Xib_View).
For the plan see `ROADMAP.md`; for open items `BACKLOG.md`.

---

## 2026-11-24 — XIB reference; architecture diagram

- `docs/reference/XIB Reference.md`: XIB vs nib, the object graph (placeholders, top-level
  objects, ids, tags, cells, catalog colours), geometry and springs-and-struts, FB's `nib…`
  statements (`nibview` loads into another view with `superviewTag`, picks a view by
  `identifier`), checking with `ibtool`, and the rules we learned writing XIBs. Apple has no
  published XIB schema; Apple's nib guide read in full; the ibtool man page and Chromium's
  notes are blocked from this environment (flags from search results, to confirm with
  `xcrun ibtool --help`).
- `docs/design/architecture.svg` (light and dark), drawn by `tools/make_architecture_svg.py`;
  shown at the top of the README.

---
