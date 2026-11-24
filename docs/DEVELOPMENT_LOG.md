# Development Log

What was done and what was learned, newest first. Commits are on
`claude/dazzling-darwin-awec2o` (Api_Logic_Client unless marked *TXV* = Test_Xib_View).
For the plan see `ROADMAP.md`; for open items `BACKLOG.md`.

---

## 2026-11-24 — Step 3 in the Python reference (FB next)

- Reference engine: copy (on insert and when the row moves to another parent; no parent: keep),
  parent check (empty foreign key allowed), parent changes cascading to children whose formulas
  read them (after the parent is written), delete actions per child list (prevent / cascade /
  nullify), row events (also on delete, LB-12; a row event that changes the row fails the save,
  LB-11), commit events (after the outermost commit, once per row with its last state, a delete
  winning; none on rollback).
- Found by the scenarios: a cascade delete adjusted the customer twice — the order's delete
  used its totals from before its details were deleted. The row is now read again after the
  delete actions. The FB engine must do the same.
- 70 scenarios (24 new), all pass; `--prove`: 20 rules, all proven (a scenario that crashes
  without a rule counts as proof).
- Next: the same in FB (`Logic Rules` / `Logic Row` / `Logic Engine.incl`) and the 24 new
  scenarios in `make_logic_test.py`.

---
