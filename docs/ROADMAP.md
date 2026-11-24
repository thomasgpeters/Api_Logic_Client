# Roadmap

Where Api_Logic_Client is going. Details per item in `BACKLOG.md`; history in
`DEVELOPMENT_LOG.md`; designs in `design/`.

## Phase 1 — Lite edition: generate a SQLite app (current)

The generated app talks directly to a SQLite database.

| Step | Status |
|---|---|
| 1. Model from SQLite (tables, keys, keyKind, relationships) | done — awaiting first Mac build |
| ↳ Entity definitions: recommendations + designer adjustments (`Design.json`) | done — awaiting build |
| 2. Form and List XIB parts per entity | done — awaiting build |
| ↳ Separate Generate XIBs / XIB / Binding Code / App; generated binding code | done — awaiting build |
| ↳ Generated app is an FB project (groups, `.main`) with starting templates: EventHandlers, Menus, Windows | done — awaiting build |
| 3. App shell: entity navigator + List + Form, SQLite data layer (query builder packaged), per-entity event handlers (FB event model) | in progress — shell, pages and branding done (`features/APP_SHELL_FEATURE.md`); awaiting build |
| 4. Crumb trail and page stack | |
| 5. Related lists in tabs (master-detail), drill-in (`_tableViewDoubleAction`) | |
| 6. Hook files for hand-written code (created only if missing) | |
| 7. `admin.yaml` hints (titles, `user_key`, relationship names) | |

## Phase 2 — Look and feel

- Theme files: CSS-like named styles (light, dark, colorful, base) applied to parts.
- Controls catalog in generated apps: toast, image / PDF viewers, thumbnails,
  token fields, carousel (prototype first) — offered as Form Control choices.

## Phase 3 — Generator app

- Workspace in Application Support — done. Product name; Settings window (Application Support + Keychain).
- Git (init/commit on generation, status, push/pull) and GitHub (create repo, PRs).
- Settings for ALS/APIs, AI/LLM providers, SMTP notifications.

## Phase 4 — API middleware edition

- ALS JSON:API as a second data source behind the same data interface (the
  existing ALS client as its starting point); login, paging, relationships.

## Phase 5 — Rules

Design: `design/Logic Engine Design.md`. Needs the Phase 1 shell's data layer first.

| Step | Status |
|---|---|
| Study LogicBank (Python): rule types, per-row sequence, delta adjustment, chaining, dependencies | done (design doc) |
| Licensing: current is Apache 2.0 + Commons Clause (2026-05-29); build clean-room; proposal to Val (percentage + name) | open — author |
| 0. Data runtime (SQLite records, transactions) the engine sits on — `features/DATA_RUNTIME_FEATURE.md` | done — awaiting build |
| 1. Logic Engine core (`Logic Rules` / `Logic Row` / `Logic Engine.incl`): rule set, LogicRow, formulas + constraints, transaction/rollback | done — Python reference passes; FB awaiting build |
| 2. Aggregates: sum/count with where, delta adjustment, re-parenting, chaining; parent references | done — Python reference 36/36; FB awaiting build |
| 3. Copy, parent check, cascade, delete actions, events | done — Python reference 70/70, 20 rules proven; FB awaiting build |
| 4. Imagery Logic Studio in the generator: Rules page, `Rules.json`, generated `<Entity> Rules.incl`, validation, Explain | |
| 5. Import ALS `declare_logic.py`; test bench; allocate / copy-children | |
