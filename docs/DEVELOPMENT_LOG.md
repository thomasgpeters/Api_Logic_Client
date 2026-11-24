# Development Log

What was done and what was learned, newest first. Commits are on
`claude/dazzling-darwin-awec2o` (Api_Logic_Client unless marked *TXV* = Test_Xib_View).
For the plan see `ROADMAP.md`; for open items `BACKLOG.md`.

---

## 2026-11-24 — Studio's test concept; LogicBank audit mapped; every rule proven (`132d5f3`)

- Imagery LogicBank Studio attached read-only. Its rule lifecycle: a test case per operation
  (insert, update, delete, upsert), each run as given rows → change → accepted with the
  expected state or rejected with the expected message → clean up; a rule passes when all four
  pass (`TestRunner.h`, `GOVERNANCE.md`).
- The converse, now in `tools/logic_reference.py --prove`: leave each rule out, a scenario must
  fail. All 10 rules proven. The reference's data layer now returns failure on a database
  error (as `DataInsert` does) instead of raising — found by leaving the Quantity rule out.
- Studio's `docs/upstream/` audit of LogicBank 1.34.3 (44 findings) mapped against our engine
  in `design/Logic Engine Design.md` §4a; open for us: LB-41 (derived columns writable by
  clients), LB-40 (rounding), LB-42 (cycles through aggregates), LB-27/30 (step 3).

---
