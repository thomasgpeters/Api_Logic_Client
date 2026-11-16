# Development Log

What was done and what was learned, newest first. Commits are on
`claude/dazzling-darwin-awec2o` (Api_Logic_Client unless marked *TXV* = Test_Xib_View).
For the plan see `ROADMAP.md`; for open items `BACKLOG.md`.

---

## 2026-11-16 — Translator: extra `end if` in XIB Generator.incl

- `XibGenerateProject` closed four `if` blocks where three were open; FB reports a stray
  `end if` as "Unknown variable, command or Toolbox name … 'if'". Removed it.
- fblint now checks block balance per fn (`if`/`select`/`for`/`while`/`do`); it reports
  this line on the old file and nothing else in Api_Logic_Client or Test_Xib_View.

---
