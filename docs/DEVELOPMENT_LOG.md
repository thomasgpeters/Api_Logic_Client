# Development Log

What was done and what was learned, newest first. Commits are on
`claude/dazzling-darwin-awec2o` (Api_Logic_Client unless marked *TXV* = Test_Xib_View).
For the plan see `ROADMAP.md`; for open items `BACKLOG.md`.

---

## 2026-11-16 — Project folder holds settings; the app goes in `FBapp/`

- `workspace/<project>/` is the project: `Project.json` (name, model source, base URL,
  user name — never passwords), `Design.json`, later `Database/` and `.git/`.
- The generated FutureBasic app goes in `workspace/<project>/FBapp/`, named after the
  project as typed (without the heading's " Project").
- New `Project Workspace.incl` (one concern: folders + `Project.json`), moved out of
  `Project Actions.incl`. Opening a model reloads saved connection fields that are empty,
  then saves; Generate saves first.

---
