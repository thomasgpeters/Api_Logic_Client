# Development Log

What was done and what was learned, newest first. Commits are on
`claude/dazzling-darwin-awec2o` (Api_Logic_Client unless marked *TXV* = Test_Xib_View).
For the plan see `ROADMAP.md`; for open items `BACKLOG.md`.

---

## 2026-11-23 — LogicBank for FutureBasic: engine core

- `Logic Rules.incl` (LogicFormula / LogicConstraint / LogicActivate: name checks,
  dependency order, cycles), `Logic Row.incl` (LogicValue / LogicDouble / LogicOldValue /
  LogicChanged …), `Logic Engine.incl` (LogicInsert / LogicUpdate / LogicDelete: formulas
  with pruning, constraints with `{Attr}` messages, one transaction, rollback).
- Rules are called by address with a `cln` cast to a C function pointer — FB's `@fn` gives
  "the address of a callback function"; `def fn … using` needs a global pointer per call
  site (unsafe when saves chain) and has no examples in FB's 578. `@fn` takes the bare
  name only (no quoted form).
- Generated apps: Logic files in the runtime, starting template `Rules.incl` (Rules group),
  `.main` calls DeclareRules + LogicActivate after DataOpen.
- Tests: `tools/logic_reference.py` (Python, follows the FB code; 17 scenarios on Northwind,
  all pass) and `tools/make_logic_test.py` (the same scenarios as an FB project for the Mac).
- fblint: `for x in (Type)fn …` is now reported too.

---
