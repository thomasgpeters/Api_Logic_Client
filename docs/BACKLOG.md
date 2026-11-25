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

## Form designer (author, 2026-11-24; split into three features)

- [x] 1. Form layout 1 / 2 / 3 columns per entity; Hidden fields; read-only text, the default for a key the database generates (`features/XIB_PARTS_FEATURE.md`)
- [ ] Verify on a Mac: the Form layout popup in the entity view; a 3-column Form; a Hidden field; the read-only key on New / Save
- [x] 2. Date and time widgets: Time picker, Date and time picker; the Control popup in the entity view (choose from a list; Recommended clears it)
- [ ] Verify on a Mac: the Control popup follows the selected attribute; a TIME and a DATETIME column round-trip through Save
- [x] 3. Choices: Radio buttons, Dropdown (a value list in the Values column, or a foreign key's lookup table: the parent's key stored, a display column shown), Checkbox; `AppDataLookup`
- [ ] Verify on a Mac: a foreign key's Dropdown lists the parent's rows and Save stores the key; a value list Dropdown; Radio buttons (one at a time); the Form layout popup keeps its choice (log lines "Form layout popup: item …")
- [ ] Choose the lookup's display column (or several: "givenName surname"); show the display value in the List instead of the key
- [ ] Studio review (author, 2026-11-24) - `STUDIO_REVIEW.md`: step 1 done (menus regrouped, toolbar rethought and wired, commands enabled by project / entity / attribute, New / Close Project, the ALS form's Cancel); step 2 context menus; step 3 small fixes (+ / − under Objects)
- [ ] Generated app toolbar (author): New, Save, Delete, Refresh, Search, Theme, Log In - proposal in `STUDIO_REVIEW.md` 2.6
- [ ] Users and roles in generated apps (author, 2026-11-24): sign-in, users, roles (e.g. Admin, Editor, Viewer) deciding who may see, edit or delete each entity; Lite: users in the app's SQLite database; Enterprise: the API Logic Server's. Then an audit trail (who changed which record, when)
- [ ] Generated app window layouts, a project setting (`design/App Shell Design.md`, Window layouts): Single window (built); Multiple windows - a window per entity, Window menu with Stack and Tile; Tabs - one tab per entity (future)

## SQL Generator (module, shared on the FB list - `features/SQL_GENERATOR_FEATURE.md`)

- [x] Example project `src/SQLGeneratorExample` (MIT): ten examples, Help window, About box, README, announcement draft
- [x] INSERT of an array of dictionaries (author); joins fixed (associations array)
- [ ] Verify on a Mac (see the feature's checklist), then post to the FB list
- [ ] ORDER BY in the builder (`AddOrderToQuery`); `IN` with one `?` per value
- [ ] The Help window could show the object model (the SVG as a PNG in the text)

## App shell — lite edition (see `design/App Shell Design.md`)

- [x] App icon (picture or SF Symbol) and an icon per entity, chosen in the Studio; the app name large, centred on the icon
- [ ] Finder icon for the generated app: the icon picture as `AppIcon.icns` plus `#plist CFBundleIconFile @"AppIcon"` (FB help, Build System)
- [ ] Verify on a Mac: the Icon popup and preview, the app symbol popup in Project Settings, the Dock icon from a picture

- [ ] Navigation bar: scroll when there are more entities than fit (removed for now: the flipped scroll view left the items at the bottom)

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

## Installing the Studio

- [x] Runtime and templates in the workspace (`workspace/Runtime`, `workspace/Templates`), copied from
      the repository folder on first launch; *Generate > Update Runtime and Templates* (`Studio Library.incl`)
- [ ] Installer for a release: the Studio app plus the runtime and templates, put into
      `~/Library/Application Support/Imagery LogicBank Studio for FutureBasic/workspace/` (a `.pkg` with a per-user
      postinstall, or a first-launch copy from the installer's disk image), so users need no repository
- [ ] Preferences (⌘,): the repository / library folder, the workspace location

## Enterprise edition — started 2026-11-25 (author: "we must not fall behind" on multi-user, three tiers)

Code in this repository for now (`src/Enterprise`, behind `Edition.incl`), moved to a private repository when sold (author).
- [x] The ALS contract measured against a running server and written up: `design/ALS Contract.md`, `tools/als_contract.py` (18 checks)
- [x] `ALS Client.incl` follows it: error messages (title first, `msg`, bare strings), 401 / 422 = sign in again, paging by offset to `meta.total`, `ALSGet` to re-read the checksum
- [x] The SQL Generator's JSON:API side (author's design): `src/Enterprise/DataObject_JSONAPI.incl`, the model from `app_model.yaml` / `admin.yaml` (`ALS Model.incl`); `AddOrderToQuery` on both sides (`features/ENTERPRISE_DATA_FEATURE.md`)
- [x] Open ALS Project (`features/ALS_PROJECT_FEATURE.md`): the ALS project's folder, model file or public GitHub repository (raw.githubusercontent.com, main / master, the three model paths in order); typed, Folder…, Model File… or dropped (a subclassed view); a copy kept in `<project>/ALS Model/`; `alsSource` and `edition` in Project.json
- [ ] *Model > Refresh Model from API Logic Server*: read `alsSource` again, replace the copy, keep the design
- [ ] Private GitHub repositories: a token in the Keychain; GitHub read without blocking the window (URLSession)
- [x] The ALS model from `database/models.py`, parsed as text (never run): `ALSModelFromModelsPy` in `src/Generator/ALS Model.incl` (moved from src/Enterprise), reference and test `tools/models_py_reference.py` (against SQLAlchemy, Northwind and CRM)
- [x] The Studio points at the ALS project the app is built from (author: the model is ALS's, not FB's): `database/models.py` first, `admin.yaml` for the display column (Open ALS Project)
- [ ] `App Data Enterprise.incl`: the App Data interface over ALS (list with paging, lookups, save with `S_CheckSum` + re-read, remove, login), answers on the main thread
- [ ] Connection: the server's address, API and login paths in the Studio (Project Settings) and a Server window in the app; Log In in the header; the token for the session, the password in the Keychain
- [ ] Multi-user: a stale checksum explained to the user (reload the record, re-apply the change); Refresh reads the server
- [ ] Generate App (Enterprise): `declare_logic.py` from the project's rules (the rules bridge in FB)
- [ ] `Edition.incl` offers Enterprise (licensing still parked)
- [ ] Kafka (author, 2026-11-25; already used behind ALS in the author's other applications): first through ALS's own Kafka integration (the app keeps talking JSON:API, the server publishes and consumes); then a plain-HTTP messaging module in FB for Kafka's REST Proxy, and Redis through an HTTP gateway (Webdis, Upstash) - publish / poll, set / get over URLSession

## Parked: Enterprise edition — revisit after the Lite release (author, 2026-11-24)

Everything needed to pick this up again is in `design/Editions and Licensing.md` (the editions,
the code split, what the License Server issues today, the licence options, the roadmap).
Done already: the data interface `App Data` with its Lite implementation, and the edition hook
`src/Generator/Edition.incl` (Lite only).

When resuming, in this order:

1. [ ] Choose the licence option — author: **A** portable checksum (SHA-256 on the License Server),
       **B** signed licence file (the server signs, the Studio verifies with `SecKeyVerifySignature`),
       or **C** online activation (breaks the no-dependency rule). Already decided: offline, Studio only.
2. [ ] Create the private repository (e.g. `Api_Logic_Client_Enterprise`) and attach it to a session;
       move `src/Runtime/ALS Client.incl`, `ALS Binding.incl`, `ALS App.incl` there.
3. [ ] Its `Edition.incl` (replaces this repo's): `EditionEnterpriseAvailable` from the licence;
       Enterprise runtime files, start-up (`gALSHost`, login paths), `EditionRulesInApp` = NO.
4. [ ] `App Data Enterprise.incl`: list / save / remove / login over JSON:API; a request context per
       call (URLSession `userData`); answers on the main thread (`dispatchmain`); records keep the
       JSON:API id for Save and Delete.
5. [ ] Sign-in window for the header's Log In; token for the session; Keychain for a remembered password.
6. [ ] Generate App (Enterprise): export `Rules.json` to `declare_logic.py` for the server.
7. [ ] Studio: an edition choice in Project Settings and a "Licence…" entry (Preferences).
8. [ ] License Server (its own repository): product `imagery_logicbank_studio_fb`, bit 0 `enterprise`,
       and the licence format chosen in step 1.
9. [ ] The paid build: project file, release, distribution from the License Server.

## Tools in FutureBasic (author, 2026-11-24)

- [x] No Python in the Studio's bundle (author, 2026-11-24): Rules Bridge.incl says "coming" for
      Import / Export and writes an empty `Studio Rules.incl` until the port below
- [ ] **Next:** port `tools/rules_bridge.py` into the generator in FB: `Rules.json` check and `Studio Rules.incl`
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
- [x] Application Support folder renamed to `Imagery LogicBank Studio for FutureBasic` (2026-11-24); an old `Api_Logic_Client` folder is moved over on first launch, its stored paths fixed (`Studio Library.incl`)
- [ ] Rename the rest to the product name (author, later): the FB project and its `.main` (`Api Logic Client.fbeproj` → the built app's name in the Dock and menu bar), the bundle id. The repository and folder names may stay.
- [x] Workspace in `~/Library/Application Support/Imagery LogicBank Studio for FutureBasic/workspace/<project>/`; *Show Workspace in Finder*
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
- [x] ~~Move to FB's newer type names~~ — reversed 2026-11-24: FutureBasic 7.0.38 does not know `StringRef`, `URLRef`, …; everything uses the CF names (fblint enforces it)

## Modern look - the UI transformation (author, 2026-11-25)

A modern Mac look for the Studio and for the apps it generates, and the native controls a
generated app's Form can use. Each control: a choice in the Studio's Control popup (Type Mapping),
the XIB part (XIB Generator), its show / take in the binding (Binding Generator, Binding Support),
both editions. The author adds to this list.

- [x] Pill buttons (`features/PILL_BUTTONS_FEATURE.md`): `Pill Buttons.incl` (the Studio and the runtime,
  identical copies); macOS 26: AppKit's capsule (`ButtonSetBorderShape`), macOS 15: the same shape
  drawn by the layer; the Studio's push buttons; the generated app's footer (Save accent, Delete red)
  and Log In; `gThemePillButtons` in Theme.incl
- [ ] Verify on a Mac (26 and 15): the Studio's pages and a generated app's footer; light and dark; the
  Return button; Delete in red; disabled buttons
- [ ] Toggle switch (`NSSwitch`): a Control choice for BOOLEAN / yes-no columns, beside Checkbox
- [ ] Combo box (`NSComboBox`): a value list the user can also type into (Dropdown only picks)
- [ ] Date, time and date-and-time display: read-only, formatted (short / medium / long, relative "Yesterday")
  for keys, audit columns and Lists
- [ ] Calendar date picker: `NSDatePicker`'s graphical (calendar) style, in a popover from the date field
- [ ] Colour picker (`NSColorWell`): for colour columns, stored as hex text (#RRGGBB)
- [ ] More controls and looks (author to add): e.g. steppers and sliders for numbers, a search field over
  the List, a segmented control for short value lists, glass / rounded panels in the shell

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
