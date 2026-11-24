# Development Log

What was done and what was learned, newest first. Commits are on
`claude/dazzling-darwin-awec2o` (Api_Logic_Client unless marked *TXV* = Test_Xib_View).
For the plan see `ROADMAP.md`; for open items `BACKLOG.md`.

---

## 2026-11-24 — LogicBank for FutureBasic: sums, counts, chaining (`8d99a8f`)

- `LogicSum` / `LogicCount` (with a where function), declared on the parent and filed
  under the child at activation (child list → child entity + foreign key).
- Child saves adjust parents by the difference they make (insert, delete, change, where
  starting/stopping, re-parenting: both parents); one write per parent row, through
  `LogicUpdateRow`, so parents run their own logic (chaining to `Customer.Balance` and the
  credit check). Chains deeper than 20 are refused.
- Parent references in formulas: `LogicParentValue` / `LogicParentDouble`, `Role.Attr` in
  dependsOn (checked at activation; pruned unless the row moves to another parent).
- FB: the update ↔ adjust-parents recursion needs a `def fn` prototype; fblint's build-order
  check now counts prototypes as definitions.
- Tests: 36 scenarios in `tools/logic_reference.py` (19 new, the canonical check-credit
  logic on Northwind) — all pass; the FB test project (`make_logic_test.py`) has the same 36.

---
