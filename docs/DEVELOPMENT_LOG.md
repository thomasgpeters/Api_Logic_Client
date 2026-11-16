# Development Log

What was done and what was learned, newest first. Commits are on
`claude/dazzling-darwin-awec2o` (Api_Logic_Client unless marked *TXV* = Test_Xib_View).
For the plan see `ROADMAP.md`; for open items `BACKLOG.md`.

---

## 2026-11-16 — Generated apps are FB projects with starting templates (`86d59b6`)

- **Project, not a single file.** `<project>.fbeproj` with a generated `data.fbproj`
  (groups Runtime, Model, Bindings, Resources, Controller, View, Main — the
  Test_Xib_View layout) and `Settings2.plist` from `src/Templates/Project`.
- **`.main` stays short:** connection globals, `on …` registration, then
  `ALSAppStart` → `BuildMenus` → `BuildWindows` → `ALSAppReady`.
- **Starting templates** (written only when missing, then the developer's):
  `EventHandlers.incl`, `Menus.incl` (from `src/Templates/App`) and `Windows.incl`
  (generated: a `nibview` per entity Form part). Menus moved out of `ALS App.incl`;
  the runtime still loads any part `Windows.incl` doesn't (`ALSEnsureResourceViews`).
- **Templates are a folder resource** (`resources "../Templates"`), like Runtime.
- fblint: declarations with initializers containing commas were split wrongly
  (`"fn" is an FB keyword`); now split at the top level.

---
