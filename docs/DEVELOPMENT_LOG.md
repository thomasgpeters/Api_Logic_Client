# Development Log

What was done and what was learned, newest first. Commits are on
`claude/dazzling-darwin-awec2o` (Api_Logic_Client unless marked *TXV* = Test_Xib_View).
For the plan see `ROADMAP.md`; for open items `BACKLOG.md`.

---

## 2026-11-16 — Logic for FutureBasic: design (engine + Imagery Logic Studio)

- Studied LogicBank's Python source (`logic_row.py`, `aggregate.py`, `rule_bank_setup.py`,
  `formula.py`): before_flush hook; per-row sequence (early events, defaults, parents,
  copy, formulas in dependency order with pruning, parent aggregates, constraints,
  cascade, events); sums/counts **adjusted by delta**, never re-queried; one parent write
  per role; chaining through parents; dependencies scanned from `row.X` in rule text.
- FB can be the rule language: rule functions registered with `@fn`, called through
  `def fn … using <address>`; `def fn` prototypes allow forward references.
- Design: `design/Logic Engine Design.md` — `Logic Engine.incl` runtime, rules as
  generated/hand-editable `<Entity> Rules.incl` with explicit dependencies (found by the
  Studio at generation time), Imagery Logic Studio as a Rules page with `Rules.json`.
- Licensing: LogicBank's LICENSE is Apache 2.0 + Commons Clause (no selling), its
  setup.py says BSD. Clean-room from behaviour; recommended asking Val Huber.

---
