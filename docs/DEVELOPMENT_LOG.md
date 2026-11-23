# Development Log

What was done and what was learned, newest first. Commits are on
`claude/dazzling-darwin-awec2o` (Api_Logic_Client unless marked *TXV* = Test_Xib_View).
For the plan see `ROADMAP.md`; for open items `BACKLOG.md`.

---

## 2026-11-23 — Data runtime: SQLite records for the shell and the rules engine (`5e2f173`)

- New runtime layer, copied into every generated app first: `Data SQLite.incl` (our own
  SQLite declarations; opens read-write and never creates a file; nested transactions),
  the author's DataObject query builder, `Data Model.incl` (Model.json), `Data Records.incl`
  (fetch, parent, children, insert, update, delete). See `features/DATA_RUNTIME_FEATURE.md`.
- Query builder (both repos): names quoted (`"Order"`), an over-release of `myOperator`
  in `GenerateSelectSQL` removed, CF calls → Cocoa wrappers and current type names, typed
  filter values, `QueryParameterValues`.
- FB headers deprecate the CF *type names* (20 of them, `… // deprecated: 10.0 use:'StringRef'`);
  the CF *functions* are not marked but have Cocoa wrappers — new code uses those.
- `Tlbx SQLite3.incl` (FB community) carries no license; only SQLite's public-domain
  blessing in the expanded original. Not shipped in generated apps.
- Generator: one runtime list (`AppRuntimeFiles`), `NSLog.incl` in generated projects,
  `"database"` in Model.json, `.main` sets `isLoggingOn` and calls `DataOpen` for SQLite projects.
- Verified the generated SQL against Northwind (parent/children, writes on `"Order"`, rollback).

---
