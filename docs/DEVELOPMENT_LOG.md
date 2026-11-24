# Development Log

What was done and what was learned, newest first. Commits are on
`claude/dazzling-darwin-awec2o` (Api_Logic_Client unless marked *TXV* = Test_Xib_View).
For the plan see `ROADMAP.md`; for open items `BACKLOG.md`.

---

## 2026-11-24 — LogicBank for FutureBasic: step 3 in FB

- `Logic Rules.incl`: LogicCopy, LogicParentCheck, LogicDeleteAction, LogicRowEvent,
  LogicCommitEvent; activation checks their relationships and builds cascades from
  formulas' `Role.Attr` dependencies.
- `Logic Engine.incl`: copy → parent check → formulas → adjust → constraints → row events →
  write → cascade; delete actions (prevent / cascade / nullify) with the row read again
  before its parents are adjusted (the double adjustment the reference scenarios found);
  `LogicDeleteRow` prototyped; `LogicFinish` runs commit events once per row after the
  outermost commit. Early exits now end through `LogicFinish` too (and `finish` in the
  reference), so a rolled-back save never leaves commit events behind.
- `ObjectRef` arguments cast everywhere in the runtime and tests; fblint now reports uncast
  ones (parameter types from the headers).
- FB test project: the 24 step 3 scenarios (70 in all, as in the reference).

---
