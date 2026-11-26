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
| 3. App shell: entity navigator + List + Form, SQLite data layer (query builder packaged), per-entity event handlers (FB event model) | in progress — shell, pages, branding, New / Save / Delete / Refresh through the rules done (`features/APP_SHELL_FEATURE.md`); awaiting build |
| 4. Crumb trail and page stack | |
| 5. Related lists in tabs (master-detail), drill-in (`_tableViewDoubleAction`) | |
| 6. Hook files for hand-written code (created only if missing) | |
| 7. `admin.yaml` hints (titles, `user_key`, relationship names) | `user_key` done (the lookups' display column, ALS projects); titles open |

## Phase 2 — Look and feel: the Modern look (author, 2026-11-25)

| Step | Status |
|---|---|
| Pill buttons in the Studio and generated apps (`features/PILL_BUTTONS_FEATURE.md`) | done — awaiting build |
| Form controls: toggle switch, combo box, date / time display, calendar picker, colour picker | next (`BACKLOG.md` → Modern look) |
| Map view: any result set with latitude / longitude on a map, an entity first; geocoding fills the columns (`design/Map View Design.md`) | designed |
| Image / PDF viewers, thumbnails, token fields, toast, carousel | |
| Theme files: CSS-like named styles (light, dark, colourful, base) applied to parts | |

## Phase 3 — Generator app

- Workspace in Application Support — done. Product name; Settings window (Application Support + Keychain).
- Git (init/commit on generation, status, push/pull) and GitHub (create repo, PRs).
- Settings for ALS/APIs, AI/LLM providers, SMTP notifications.

## Phase 4 — Professional edition (paid) — started 2026-11-25 (author); licensing parked until the Lite release

Design: `design/Editions and Licensing.md`. A three-tier app over API Logic Server behind the same
data interface as Lite (`App Data`); private repository; licence checked offline by the Studio only.

| Step | Status |
|---|---|
| Data interface `App Data` with the Lite implementation; edition hook `Edition.incl` | done — awaiting build |
| The ALS contract, measured (`design/ALS Contract.md`); `ALS Client.incl` follows it | done |
| The SQL Generator's JSON:API side (`features/PROFESSIONAL_DATA_FEATURE.md`) | done — awaiting build |
| The ALS model from `database/models.py`, as text; the API Logic Server Project page (folder, file, GitHub, drop) (`features/ALS_PROJECT_FEATURE.md`) | done — awaiting build |
| `App Data Professional.incl`, connection and sign-in | next |
| Licence option (portable checksum / signed file / online) | open — author (parked) |
| Private repository; `App Data Professional.incl`, sign-in, `declare_logic.py` export | |
| License Server: FB Studio product and licence format | |

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
