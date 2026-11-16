# Development Log

What was done and what was learned, newest first. Commits are on
`claude/dazzling-darwin-awec2o` (Api_Logic_Client unless marked *TXV* = Test_Xib_View).
For the plan see `ROADMAP.md`; for open items `BACKLOG.md`.

---

## 2026-11-16 — About box text; Project Settings view

- Generated apps show the designer's About text (≤ 250 characters) in the standard
  macOS About box: FB's About menu item opens it, and it shows the bundle's
  `Credits.rtf` — written by Generate App with `AttributedStringRTFFromRange`, listed
  in `data.fbproj`, removed when there is no text. Also `"about"` in `Model.json`.
- Generator: new Project Settings view (`ProjectSettingsView.xib`, *Model → Project
  Settings…* ⌘;) with the About text, a live `n / 250` counter and Done; saved as
  `"about"` in `Project.json`.

---
