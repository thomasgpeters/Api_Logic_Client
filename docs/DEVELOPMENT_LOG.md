# Development Log

What was done and what was learned, newest first. Commits are on
`claude/dazzling-darwin-awec2o` (Api_Logic_Client unless marked *TXV* = Test_Xib_View).
For the plan see `ROADMAP.md`; for open items `BACKLOG.md`.

---

## 2026-11-16 — Open Project and Recent Projects (`c54948a`)

- *Model → Open Project…* (⇧⌘O) opens a project's `Project.json` and reopens its
  model from `source`; if the file moved, *Locate…* saves the new path.
- Recent Projects (`Recent Projects.json` in Application Support, newest first, max 10)
  on the Welcome view: double-click opens; *Model → Recent Projects* goes back to it;
  *Clear Recent Projects*. The row dictionaries use the column identifiers as keys.
- Model loading refactored: `LoadSQLiteModel` / `LoadMetadataModel` / `LoadModelFile`
  share `ProjectModelLoaded` (settings, design, save, recent list) — the menu commands and
  Open Project use the same path.
- FB: `alert` as a function returns `NSAlertFirstButtonReturn`… (no `sheetFlag`);
  `_tableViewDoubleAction` + `TableViewClickedRow` need no setup.
- Merged `origin/main` (PR #5) into the branch.

---
