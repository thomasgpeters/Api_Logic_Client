# Development Log

What was done and what was learned, newest first. Commits are on
`claude/dazzling-darwin-awec2o` (Api_Logic_Client unless marked *TXV* = Test_Xib_View).
For the plan see `ROADMAP.md`; for open items `BACKLOG.md`.

---

## 2026-11-16 — New Project from a SQLite database (`72d9bfe`)

- *Create Project* now opens a New Project view (`NewProjectView.xib`, `New Project.incl`):
  name, *Choose…* a SQLite database, a summary of its tables and views, *Create*. The ALS
  server form stays one button away (*API Logic Server instead…*).
- Create clears the connection and About fields, then uses the shared
  `LoadSQLiteModel` path (Project.json, Design.json, Recent Projects); an existing name
  offers *Open It*.
- XIB: key equivalents for Return/Escape are stored base64 (`DQ`, `Gw`) — `&#13;`/`&#27;`
  are not valid XML.
- fblint: build-order check — a `local fn` used before its definition in `data.fbproj`
  order (it caught `ShowdProjectCreateView`, defined in the later `EventHandlers.incl`).

---
