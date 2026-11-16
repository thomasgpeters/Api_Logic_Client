# Development Log

What was done and what was learned, newest first. Commits are on
`claude/dazzling-darwin-awec2o` (Api_Logic_Client unless marked *TXV* = Test_Xib_View).
For the plan see `ROADMAP.md`; for open items `BACKLOG.md`.

---

## 2026-11-16 — Each project keeps its own copy of the database

- The SQLite database is copied into `workspace/<project>/Database/` (plus `-wal`/`-shm`)
  before the model is read; `Project.json`'s `source` is the copy. Done in
  `LoadSQLiteModel` → `ProjectLocalDatabase`, so New Project, *Open SQLite Database…* and
  Open Project (older projects) all do it. Existing copy: Keep / Replace / Cancel.
- Why: a self-contained project folder, for the planned backup and restore.
- `ProjectFolderURLNamed( name )` names the folder from a typed name (`<name> Project`).

---
