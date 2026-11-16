# Development Log

What was done and what was learned, newest first. Commits are on
`claude/dazzling-darwin-awec2o` (Api_Logic_Client unless marked *TXV* = Test_Xib_View).
For the plan see `ROADMAP.md`; for open items `BACKLOG.md`.

---

## 2026-11-16 — First clean build and run of the generator; warnings cleaned up

- The generator translates, compiles, links and runs. Remaining clang warnings:
  - `-lsqlite3: 'linker' input unused` on every file — FB passes Compiler Options to each
    compile step. Added `-Wno-unused-command-line-argument` to the generator's
    `Settings2.plist` (the template for generated apps already had it).
  - `SQLite Model.incl`: `CFMutableArrayRef` variables assigned from
    `DictionaryObjectForKey` ("discards qualifiers") — cast; unused `pkIndex` removed.
- Both rules added to `FB Coding Rules.md`.

---
