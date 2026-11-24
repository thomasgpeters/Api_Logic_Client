# Backlog

Open items and ideas, grouped by area. The phase plan is in `ROADMAP.md`;
what was done and learned is in `DEVELOPMENT_LOG.md`.

## Verify on a Mac (first build of recent work)

- [x] Generator builds and runs (2026-11-16)
- [ ] ⌘D opens `nw/database/db.sqlite`; entity summaries and definitions show
- [ ] Editing Title / widths in the definitions table (`_tableViewCellTextDidEndEditing`); `Design.json` written and re-applied
- [ ] Regex Title split (`StringByReplacingOccurrencesOfStringWithOptions`, `$1 $2`)
- [ ] `SQLite Access.incl` `cln` declarations compile and link (`-lsqlite3`)
- [ ] Generate XIBs / XIB / Binding Code / App write the expected files; generated XIBs open in Xcode
- [ ] New Project view: Choose… shows the tables; Create opens the definitions
- [ ] Resizing: window minimum 1000 × 620; entity list follows the height; pages fill and stretch — `features/RESPONSIVE_LAYOUT_FEATURE.md`
- [ ] Project Settings (⌘;): counter, 250 limit, Done saves; generated app's About box shows `Credits.rtf`
- [ ] Welcome view: Open Project… button and Recent Projects table; double-click opens (see `features/PROJECTS_FEATURE.md`)
- [ ] FBE bundles the `../Runtime` and `../Templates` folders as resources of the generator
- [ ] Generated `<project>.fbeproj` opens in FB with its groups and builds; `nibview` in `Windows.incl` places each Form part

## App shell — lite edition (see `design/App Shell Design.md`)

- [x] List XIB part per entity
- [x] Entity definitions with recommendations; designer adjustments in `Design.json`
- [x] Separate commands: Generate XIBs / XIB / Binding Code / App
- [x] Generated `<Entity> Binding.incl`
- [x] Shell: entity navigator + List + Form, wired to SQLite — `features/APP_SHELL_FEATURE.md`
- [x] Studio: branding form in Project Settings (logo well, tag-line, copyright)
- [x] Generated code readable for FB developers: file headers, developer notes, `README.md` tour
- [ ] Verify on a Mac: the shell (`features/APP_SHELL_FEATURE.md` → Verify)
- [ ] Enterprise edition (roadmap, after Lite ships): `design/Editions and Licensing.md` → Roadmap
- [x] Save / New / Delete / Refresh on a page, through the data interface (`App Data Lite.incl`) and the rules
- [ ] Lite release: first Mac build of a generated app; fix what the Build Log shows; tag a release
- [ ] Per-entity event handlers routed from one `on dialog` handler by tag range
- [ ] Crumb trail and page stack (drill-in replaces the page; back via crumbs)
- [ ] Related-list tabs (master-detail) and drill-in
- [x] App starting templates, created only if missing: `EventHandlers.incl`, `Menus.incl`, `Windows.incl`
- [ ] Per-entity hook files, created only if missing
- [ ] Optional: open related records in a modal dialog instead of replacing the page
- [ ] Form controls for assigned keys: editable on New, read-only after; identity keys read-only
- [ ] `guid` key kind: generate with `UUIDString( UUIDInit )`, stored lower-case `TEXT`

## Model diagram (`features/MODEL_DIAGRAM_FEATURE.md`)

- [x] ERD page: entities, keys, relationships (crow's foot, optional), rule symbols; drag, open / close, select, find, themes, Export SVG
- [x] *Model → Show Model Diagram* (`ERD Generator.incl`, FB)
- [ ] Verify on a Mac (feature page → Verify)
- [ ] Show the diagram inside the Studio (a WKWebView window) instead of the browser
- [ ] Click a rule symbol to open it on the Rules page (once the Rules page exists)
- [ ] ALS projects: relationships from the metadata (ALS `/metadata` lists them per resource)

## Editions and licensing (`design/Editions and Licensing.md`)

- [x] Data interface `App Data` (Lite: SQLite + rules); edition hook `src/Generator/Edition.incl` (Lite only)
- [ ] Licence option: portable checksum, signed licence file, or online activation — author
- [ ] Private Enterprise repository; move `ALS Client / Binding / App.incl` there
- [ ] License Server: product `imagery_logicbank_studio_fb` and the licence format (its own repository)

## Tools in FutureBasic (author, 2026-11-24)

- [ ] Port `tools/rules_bridge.py` into the generator in FB: `Rules.json` check and `Studio Rules.incl`
      generation first (plain FB), then `declare_logic.py` import / export (needs a small parser
      for LogicBank's `Rule.*(...)` calls and their lambdas, written in FB)

## Data layer

- [x] Data runtime: SQLite records layer in `src/Runtime` (the shell and the rules engine sit on it) — `features/DATA_RUNTIME_FEATURE.md`
- [ ] Verify on a Mac: generated app opens its database; Test_Xib_View still works with the updated builder

- [ ] UPSERT in the query builder (`ON CONFLICT ( key ) DO UPDATE SET … = excluded.…`; SQLite 3.24+)
- [x] Quote every identifier in generated SQL (`"Order"`, `"Union"` are reserved words) — query builder `QuoteSQLName`
- [ ] INSERT omits identity keys and returns `last_insert_rowid()`; omit empty columns so defaults apply
- [ ] Generator offers `build_db.py`-style database creation for generated apps
- [ ] Computed columns (`Customer.Balance`, `OrderCount`) are not maintained in the lite edition — see Rules

## Generator app (see `design/Generator App Design.md`)

- [x] Add an Edit menu (`editmenu`) to the generator: Cut / Copy / Paste in its text fields
- [x] Generate XIBs uses ⌘X, which is Cut on the Mac: moved to ⇧⌘X (author to confirm)
- [ ] Preferences… (⌘,) does nothing yet
- [x] Rules bridge in the generator: Import / Export Rules (declare_logic.py), Studio Rules.incl on Generate App — `features/RULES_BRIDGE_FEATURE.md`
- [ ] The Rules page: list, editor (model-driven pop-ups), check — on `Rules.json`

- [x] Model from a SQLite database — `SQLite Model.incl`
- [x] New Project view: a project starts from a SQLite database — `features/NEW_PROJECT_FEATURE.md`
- [x] Product name: **Imagery LogicBank Studio for FutureBasic** — shown in the window title, Welcome view, server form and About box; Imagery logo (2026-11-24)
- [ ] Rename the rest to the product name (author, later): the FB project and its `.main` (`Api Logic Client.fbeproj` → the built app's name in the Dock and menu bar), the bundle id, and the Application Support folder (`Api_Logic_Client` → new name, moving an existing workspace and Recent Projects over at first launch). The repository and folder names may stay.
- [x] Workspace in `~/Library/Application Support/Api_Logic_Client/workspace/<project>/`; *Show Workspace in Finder*
- [x] Project settings in `<project>/Project.json`; generated app in `<project>/FBapp/`
- [x] Project Settings view; About text (≤ 250 chars) deployed as `Credits.rtf` — `features/ABOUT_BOX_FEATURE.md`
- [ ] More project settings: version, copyright, bundle id, app icon, theme
- [x] Each project keeps its own copy of the database in `<project>/Database/`
- [ ] Project backup and restore (zip the project folder; restore into the workspace)
- [ ] Generated app uses the project's database copy (lite data source, step 3)
- [x] Open Project (⇧⌘O) and Recent Projects on the Welcome view — `features/PROJECTS_FEATURE.md`
- [ ] `.alcproj` document type: double-click a project in Finder; Open Recent via NSDocumentController
- [ ] Settings window; `Settings.plist` in Application Support; secrets in the Keychain
- [ ] Git via `/usr/bin/git` (NSTask): init/commit on generation, status, push/pull
- [ ] GitHub REST (create repo, pull requests) and generic Git remotes
- [ ] Settings groups for ALS/APIs, AI/LLM providers, SMTP notifications
- [ ] Optional `admin.yaml` hints (titles, `user_key`, relationship names)
- [ ] Generator's own ALS fetch uses the Create Project form's base URL and credentials (still hard-coded host and `admin`/`p`), and waits for login before fetching
- [ ] Move to FB's current type names (`StringRef`, `DictionaryRef`, …) and Cocoa wrappers everywhere — done in the data runtime and query builder; generator and ALS runtime still use the CF names

## Look and feel

- [ ] Generated apps: resizable shell window; Form fields stretch, List tables fill (same masks as the generator)

- [ ] Theme files: CSS-like named styles (colors with light/dark values, fonts, corner radius, shadows) applied to parts; light, dark, colorful, base
- [ ] `Toast.incl` — in-app toast (visual effect view + fade)
- [ ] Carousel prototype in Test_Xib_View (collection view + Quick Look thumbnails)
- [ ] Form Control choices: Image, PDF, Tokens, Thumbnails (e.g. `Employee.PhotoPath` → Image)

## ALS edition

- [ ] ALS data source behind the shell's data interface (from `src/Runtime/ALS Client.incl`)
- [ ] Paging (today: first `gALSPageLimit` = 100 records)
- [ ] Relationships from ALS (lookups, child tables)

## Tooling

- [ ] `tools/xiblint.py`: unique ids, connections that resolve, tags unique per document, frames inside their superview, base64 key equivalents — run on every generated and hand-written XIB
- [ ] On a Mac: `xcrun ibtool --errors --warnings --notices` on every XIB in `src/Generator` and a generated project (`docs/reference/XIB Reference.md` §5)

- [ ] fblint: check statement syntax (e.g. `tableview`'s `columnWidths`)
- [ ] Python reference for Type Mapping (definitions report) to check the FB rules
- [ ] Retire or make private `futurebasic-apis`: outdated (pre-7.0.35), superseded by FutureBasic_Documentation, and the toolboxes carry no redistribution license

## Test_Xib_View

- [ ] `BuildMenu` is never called — the File menu (Close ⌘W) is not built; add `fn BuildMenu` to the main program
- [ ] Remove or keep `OpenSQLite` / `CloseSQLite` (older database path) and `GetCustomers` / `GetAllCustomers` (hand-written SQL)
- [ ] Wire `InsertPersonRecord` / `UpdatePersonRecord` / `DeletePersonRecord` to the add, save and delete buttons
- [ ] Have the app run `Database/schema.sql` + `seed.sql` instead of its own copy in `CreateEmptySQLDatabase`

## Ideas

### Logic for FutureBasic — engine + Imagery Logic Studio
Rewrite of [LogicBank](https://github.com/valhuber/LogicBank) (Val Huber) for FutureBasic:
**FB code is the rules**, a runtime **Logic Engine** enforces them on every save, and an
**Imagery Logic Studio** built into Api Logic Client authors them. Full design and plan:
`design/Logic Engine Design.md`; phases in `ROADMAP.md` → Phase 5.

- [x] Study the Python edition (rule types, per-row sequence, delta adjustment, chaining, formula dependencies)
- [x] Confirm FB can call rules by address (`@fn` + `def fn … using`)
- [x] License check: current is Apache 2.0 + Commons Clause (since 2026-05-29, `a475a9c`); BSD in setup.py/pyproject is stale
- [ ] Proposal to Val Huber: percentage offer + use of the name "LogicBank for FutureBasic" (author) — clean-room until then
- [x] Engine core: formulas (order, pruning), constraints, transactions — `features/LOGIC_ENGINE_FEATURE.md`
- [ ] Run `tools/make_logic_test.py` on a Mac: the 70 FB scenarios pass
- [x] Aggregates (sum/count with where, delta, re-parenting, chaining), parent references
- [x] Copy, parent check, cascade of parent changes to children, delete cascade/nullify/prevent, events
- [ ] Recompute command: rebuild stored sums/counts from the data (adjustment assumes they start right)
- [x] LB-41: protect derived sum/count columns from client writes; aggregates start at 0 on insert
- [ ] LB-42: detect dependency cycles through aggregates at activation (today: depth limit at run time)
- [ ] LB-40: round sums to the column's scale (decide)
- [x] Upsert (Studio's fourth operation): `LogicUpsert` — update when the row exists, else insert
- [ ] Scenarios per rule and operation (insert / update / delete / upsert), as Studio tests rules; keep `--prove` at 0 unproven
- [ ] Studio: Rules page, `Rules.json`, generated rule files, validation, Explain
- [ ] Import ALS `logic/declare_logic.py`
