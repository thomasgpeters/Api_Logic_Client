# Development Log

What was done and what was learned, newest first. Commits are on
`claude/dazzling-darwin-awec2o` (Api_Logic_Client unless marked *TXV* = Test_Xib_View).
For the plan see `ROADMAP.md`; for open items `BACKLOG.md`.

---

## 2026-11-24 — Rules bridge: declare_logic.py import / export, Rules.json, FB generation

- `tools/rules_bridge.py`: `import` reads LogicBank's `declare_logic.py` with Python's `ast`
  and translates `lambda row:` rules into the engine's FB (attributes by model type:
  `LogicDouble` / `LogicString`; `is None` → `LogicIsEmpty`; parent references; `and` / `or` /
  `not`; child lists and parent roles found from the model). Rules it cannot translate
  (Python functions, conditional expressions, events) arrive switched off with their Python
  kept. `export` writes them back (unchanged imports as they came; edits translated from FB);
  `check` validates names and cycles; `generate` writes the app's `Studio Rules.incl`.
- Decision: Python owns import / export / generation — parsing Python is Python's job, and
  every Mac that builds FB has `/usr/bin/python3` (Xcode command-line tools). The generator
  runs it with FB's Task toolbox; the Rules page itself is FB.
- Runtime: `LogicParentString` (text parent references).
- 23 checks, all passing, in `run_tests.sh`.

---
