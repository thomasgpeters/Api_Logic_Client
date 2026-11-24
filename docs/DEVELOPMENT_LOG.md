# Development Log

What was done and what was learned, newest first. Commits are on
`claude/dazzling-darwin-awec2o` (Api_Logic_Client unless marked *TXV* = Test_Xib_View).
For the plan see `ROADMAP.md`; for open items `BACKLOG.md`.

---

## 2026-11-24 — User guide; rules bridge in the generator

- `docs/USER_GUIDE.md`: the whole app for its users, with the architecture diagram — projects,
  workspace, entity definitions, settings, generation, the generated project, business rules
  (every rule kind, the save sequence), ALS import / export, troubleshooting, shortcuts, what is
  not built yet.
- Writing it showed the generated app did not yet include `Studio Rules.incl`: now
  `Rules Bridge.incl` runs the bundled `tools/rules_bridge.py` (FB's Task toolbox,
  `/usr/bin/python3`): *Model → Import Rules from declare_logic.py… / Export Rules…*, and Generate
  App writes `Studio Rules.incl` (or an empty `DeclareStudioRules`); the generated project has it
  in its Rules group and the main calls `DeclareStudioRules` before `DeclareRules`.
- Found while documenting the menus: the generator has no Edit menu, and Generate XIBs uses ⌘X
  (Cut) — backlog.

---
