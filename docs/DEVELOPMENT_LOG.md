# Development Log

What was done and what was learned, newest first. Commits are on
`claude/dazzling-darwin-awec2o` (Api_Logic_Client unless marked *TXV* = Test_Xib_View).
For the plan see `ROADMAP.md`; for open items `BACKLOG.md`.

---

## 2026-11-24 — Imagery LogicBank Studio for FutureBasic: name and logo

- The product name is shown in the window title, the Welcome view (title and tagline), the
  server form and the generator's own About box (`Credits.rtf`); the Welcome copyright line
  is corrected ("Imagery Business Systems").
- The canonical Imagery logos (byte-identical to Imagery LogicBank Studio's, checksums
  0554a91d… and 8b4dcd39…) replace the "cloud" symbol. `Branding.incl`: `ImageryLogo`, one
  image that draws the colour or the white logo for the current appearance, so it follows
  light and dark mode by itself.
- Author's decision: display name only for now; the project file, app bundle, bundle id and
  Application Support folder are renamed later (backlog).

---
