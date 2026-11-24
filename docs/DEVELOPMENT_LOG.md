# Development Log

What was done and what was learned, newest first. Commits are on
`claude/dazzling-darwin-awec2o` (Api_Logic_Client unless marked *TXV* = Test_Xib_View).
For the plan see `ROADMAP.md`; for open items `BACKLOG.md`.

---

## 2026-11-24 — LB-41 fix (derived totals belong to the rules); LogicUpsert (`71e4707`)

- `LogicProtectDerived`: on insert, sums and counts start at 0; on a save from the app, their
  stored values are kept (logged); only chained parent saves change them. Closes LogicBank
  audit LB-41 for our engine.
- `LogicUpsert( entity, record )`: update when a row with the record's key exists, else
  insert — Studio's fourth test operation.
- 10 new scenarios (46 in all, Python and FB); `--prove`: 10 rules, all proven, with more
  scenarios per rule. Scenarios that depend on a failed step now fail instead of crashing
  under `--prove`.

---
