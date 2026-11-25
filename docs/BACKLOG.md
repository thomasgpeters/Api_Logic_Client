# Backlog

Open items and ideas, grouped by area, with a proposed order at the top. The phase plan is in
`ROADMAP.md`; what was done and learned is in `DEVELOPMENT_LOG.md`; each feature's page is in
`features/`. Reviewed in full on 2026-11-25.

## Priorities (proposal, 2026-11-25 - the author decides)

1. **A green Mac build.** Everything since the last build (2026-11-24) is lint-clean and tested
   here but not compiled: the Studio's menus, toolbar and crumb trail, the Form designer's three
   features, the API Logic Server Project page, pill buttons, and a generated app. One build of
   the Studio and one generated app, then the Build Log and the checklist below.
2. **The open bug:** the Form layout popup "pops back to automatic" (needs the log lines below).
3. **Modern look controls** for generated Forms (the author's current interest): toggle switch,
   combo box, date / time display, calendar picker, colour picker. Each follows the Form
   designer's pattern (Control popup -> XIB part -> binding), so they are small and independent.
4. **Lite release:** a generated app builds and runs on a Mac; tag it. Then post the SQL Generator
   to the FB list.
5. **Enterprise data:** `App Data Enterprise.incl` and the connection / sign-in, so an ALS project
   generates a working three-tier app.
6. **Rules in FB:** the port of `rules_bridge.py` (Rules.json check, Studio Rules.incl), then the
   Rules page.
7. Then the Studio review (context menus), the generated app's toolbar, window layouts, users and
   roles.

## Waiting on the author

- [ ] **Bug:** Form layout popup - choosing "3 columns" pops back to "automatic". Diagnostics are in
  (`DesignFormColumnsChosen`): the NSLog lines "Form layout popup: item …" and "Form layout of …"
- [ ] A crash seen in the Studio (2026-11-24): the author is trying to reproduce it
- [ ] Studio review: agree the generated app's toolbar (`STUDIO_REVIEW.md` 2.6)
- [ ] The Modern look: more controls and looks to add to the list
- [ ] Enterprise licensing option (A / B / C, see Parked)
- [ ] Proposal to Val Huber: percentage offer + the name "LogicBank for FutureBasic"
- [ ] Rename the FB project and its `.main` to the product name (later)

## Verify on a Mac - everything built since the last Mac build

The Studio
- [x] Generator builds and runs (2026-11-16); runs again after the 2026-11-24 fixes
- [ ] Menus regrouped, commands enabled by project / entity / attribute, keyboard shortcuts (`USER_GUIDE.md` §16)
- [ ] Toolbar: Projects, Entities, Diagram, Generate, Settings; the crumb trail's buttons go back
- [ ] New Project: Choose… shows the tables; Create opens the definitions
- [ ] API Logic Server Project (⇧⌘N): drop an ALS project folder; paste `https://github.com/ApiLogicServer/basic_demo` + Read; Create; Employee's two Department keys are Dropdowns; reopen from Recent Projects (`features/ALS_PROJECT_FEATURE.md` → Verify)
- [ ] Pill buttons on every page, light and dark, Return presses Create; on macOS 15 too if possible (`features/PILL_BUTTONS_FEATURE.md`)
- [ ] Definitions: editing Title / widths writes `Design.json` and it is re-applied; the regex Title split
- [ ] Form designer: the Form layout popup; a 3-column Form; a Hidden field; the read-only key on New / Save
- [ ] Form designer: the Control popup follows the selected attribute; TIME and DATETIME round-trip through Save
- [ ] Form designer: a foreign key's Dropdown lists the parent's rows and stores the key; a value-list Dropdown; Radio buttons
- [ ] Icons: the entity Icon popup and preview, the app symbol in Project Settings, the Dock icon from a picture
- [ ] Project Settings (⌘;): counter, 250 limit, Done saves
- [ ] Welcome view: Open Project… and Recent Projects (double-click opens)
- [ ] Resizing: window minimum 1000 × 620; pages fill and stretch (`features/RESPONSIVE_LAYOUT_FEATURE.md`)
- [ ] Model diagram (⇧⌘D) - also for an ALS project (its relationships now come from models.py)
- [ ] `SQLite Access.incl` `cln` declarations compile and link (`-lsqlite3`)

A generated app
- [ ] Generate XIBs / XIB / Binding Code / App write the expected files; the XIBs open in Xcode
- [ ] `<project>.fbeproj` opens in FB with its groups and builds; `nibview` in `Windows.incl` places each part
- [ ] The shell (`features/APP_SHELL_FEATURE.md` → Verify): navigation at the top, Business Objects heading, header, footer pill buttons (Save accent, Delete red), theme menu
- [ ] Opens its database copy; New / Save / Delete / Refresh through the rules; the About box shows `Credits.rtf`
- [ ] Run `tools/make_logic_test.py` on a Mac: the 70 FB logic scenarios pass

Shared modules
- [ ] The SQL Generator example project (`features/SQL_GENERATOR_FEATURE.md` checklist); Test_Xib_View still works with the updated builder

## Modern look - the UI transformation (author, 2026-11-25)

A modern Mac look for the Studio and for the apps it generates, and the native controls a
generated app's Form can use. Each control: a choice in the Studio's Control popup (Type Mapping),
the XIB part (XIB Generator), its show / take in the binding (Binding Generator, Binding Support),
both editions. The author adds to this list.

- [x] Pill buttons (`features/PILL_BUTTONS_FEATURE.md`): `Pill Buttons.incl` (the Studio and the runtime,
  identical copies); macOS 26: AppKit's capsule (`ButtonSetBorderShape`), macOS 15: the same shape
  drawn by the layer; the Studio's push buttons; the generated app's footer and Log In; `gThemePillButtons`
- [ ] Toggle switch (`NSSwitch`): a Control choice for BOOLEAN / yes-no columns, beside Checkbox
- [ ] Combo box (`NSComboBox`): a value list the user can also type into (Dropdown only picks)
- [ ] Date, time and date-and-time display: read-only, formatted (short / medium / long, relative
  "Yesterday") for keys, audit columns and Lists
- [ ] Calendar date picker: `NSDatePicker`'s graphical (calendar) style, in a popover from the date field
- [ ] Colour picker (`NSColorWell`): for colour columns, stored as hex text (#RRGGBB)
- [ ] Form Control choices: Image, PDF, Tokens, Thumbnails (e.g. `Employee.PhotoPath` → Image)
- [ ] More controls and looks (author to add): e.g. steppers and sliders for numbers, a search field over
  the List, a segmented control for short value lists, glass / rounded panels in the shell
- [ ] Theme files: CSS-like named styles (colours with light / dark values, fonts, corner radius,
  shadows) applied to parts; light, dark, colourful, base
- [ ] `Toast.incl` - an in-app toast (visual effect view + fade) for Saved / refused
- [ ] Carousel prototype in Test_Xib_View (collection view + Quick Look thumbnails)

## Form designer and the generated app (Lite)

Done: Form layout 1 / 2 / 3 columns, Hidden, read-only keys (`features/XIB_PARTS_FEATURE.md`); Time
and Date-and-time pickers, the Control popup; Radio buttons, Dropdown (value list or lookup),
Checkbox; app and entity icons; the shell with New / Save / Delete / Refresh through the rules
(`features/APP_SHELL_FEATURE.md`); starting templates; a developer README.

- [ ] Choose the lookup's display column (or several: "givenName surname"); show the display value in the List instead of the key
- [ ] Generated app toolbar (author): New, Save, Delete, Refresh, Search, Theme, Log In - proposal in `STUDIO_REVIEW.md` 2.6
- [ ] Window layouts, a project setting (`design/App Shell Design.md`): Single window (built); Multiple windows - a window per entity, Window menu with Stack and Tile; Tabs - one per entity (future)
- [ ] Users and roles (author, 2026-11-24): sign-in, users, roles (Admin, Editor, Viewer) deciding who may see, edit or delete each entity; Lite: users in the app's SQLite database; Enterprise: the server's. Then an audit trail (who changed which record, when)
- [ ] Finder icon: the icon picture as `AppIcon.icns` plus `#plist CFBundleIconFile @"AppIcon"` (FB help, Build System)
- [ ] Navigation bar: scroll when there are more entities than fit (the flipped scroll view left the items at the bottom; removed for now)
- [ ] Form fields stretch and List tables fill when the window grows (the same masks as the Studio)
- [ ] Crumb trail and page stack (drill-in replaces the page; back via crumbs)
- [ ] Related-list tabs (master-detail) and drill-in; optionally a modal dialog instead of replacing the page
- [ ] Per-entity event handlers routed from one `on dialog` handler by tag range; per-entity hook files, created only if missing
- [ ] Assigned keys: editable on New, read-only after (identity keys are read-only already)
- [ ] `guid` key kind: generated with `UUIDString( UUIDInit )`, stored lower-case `TEXT`
- [ ] Lite release: the first Mac build of a generated app; fix what the Build Log shows; tag a release

## Enterprise edition - started 2026-11-25 (author: "we must not fall behind" on multi-user, three tiers)

Code in this repository for now (`src/Enterprise`, behind `Edition.incl`), moved to a private
repository when sold (author). The model is API Logic Server's: Lite points at the SQLite file,
Enterprise at the ALS project.

- [x] The ALS contract measured against a running server: `design/ALS Contract.md`, `tools/als_contract.py` (25 checks); `ALS Client.incl` follows it
- [x] The SQL Generator's JSON:API side (`src/Enterprise/DataObject_JSONAPI.incl`, `features/ENTERPRISE_DATA_FEATURE.md`); `AddOrderToQuery` on both sides
- [x] The ALS model from `database/models.py`, parsed as text (never run): `ALSModelFromModelsPy` (`src/Generator/ALS Model.incl`), tested against SQLAlchemy on Northwind and CRM; older `class X(SAFRSBaseX, Base)` too
- [x] API Logic Server Project page (`features/ALS_PROJECT_FEATURE.md`): folder, model file or public GitHub repository; typed, chosen or dropped; a copy in `<project>/ALS Model/`; lookups from the relationships, display columns from `admin.yaml`
- [ ] **Next:** `App Data Enterprise.incl`: the App Data interface over ALS (list with paging, lookups, save with `S_CheckSum` + re-read, remove, login), answers on the main thread; records keep the JSON:API id
- [ ] Connection: the server's address (the page's API Server, `baseURL`), login paths; a sign-in window for the header's Log In; the token for the session, a remembered password in the Keychain
- [ ] Multi-user: a stale checksum explained to the user (reload the record, re-apply the change); Refresh reads the server
- [ ] *Model > Refresh Model from API Logic Server*: read `alsSource` again, replace the copy, keep the design
- [ ] Private GitHub repositories: a token in the Keychain; GitHub read without blocking the window (URLSession)
- [ ] `admin.yaml` titles as the attributes' Titles (its `user_key` is used already)
- [ ] Generate App (Enterprise): `declare_logic.py` from the project's rules (the rules bridge in FB)
- [ ] `Edition.incl` offers Enterprise (licensing parked)
- [ ] The Studio's own ALS fetch (the running-server form) uses the form's base URL and credentials (still a hard-coded host and `admin` / `p`), and waits for login before fetching
- [ ] Kafka (author, 2026-11-25; already used behind ALS in the author's other applications): first through ALS's own Kafka integration (the app keeps talking JSON:API); then a plain-HTTP messaging module in FB for Kafka's REST Proxy, and Redis through an HTTP gateway (Webdis, Upstash) - publish / poll, set / get over URLSession

## Rules - Logic for FutureBasic (`design/Logic Engine Design.md`, ROADMAP Phase 5)

Done: the engine (formulas, constraints, sums / counts with delta and re-parenting, parent
references, copy, parent check, cascade, delete actions, events, upsert; LB-41) - 70 scenarios and
20 rules proven in the Python reference; the rules bridge in Python (`features/RULES_BRIDGE_FEATURE.md`).

- [ ] **Next:** port `tools/rules_bridge.py` into the Studio in FB: `Rules.json` check and `Studio Rules.incl` first (plain FB), then `declare_logic.py` import / export (a small parser for LogicBank's `Rule.*(...)` calls and their lambdas)
- [ ] The Rules page: list, editor (model-driven pop-ups), check, Explain - on `Rules.json`
- [ ] Recompute command: rebuild stored sums / counts from the data (adjustment assumes they start right)
- [ ] LB-42: detect dependency cycles through aggregates at activation (today: a depth limit at run time)
- [ ] LB-40: round sums to the column's scale (decide)
- [ ] Scenarios per rule and operation (insert / update / delete / upsert), as the Studio tests rules; keep `--prove` at 0 unproven
- [ ] Computed columns (`Customer.Balance`, `OrderCount`) need the rules: without them the Lite app does not maintain them

## SQL Generator (module, shared on the FB list - `features/SQL_GENERATOR_FEATURE.md`)

Done: the example project (ten examples, Help window, About box, README, announcement draft);
INSERT of an array of dictionaries; joins fixed; ORDER BY (`AddOrderToQuery`); names quoted.

- [ ] Verify on a Mac (above), then post to the FB list (`ANNOUNCEMENT.md`: your name, the link)
- [ ] `IN` / `NOT IN` with one `?` per value (today one `?` for the whole list)
- [ ] UPSERT (`ON CONFLICT ( key ) DO UPDATE SET … = excluded.…`; SQLite 3.24+)
- [ ] INSERT omits identity keys and returns `last_insert_rowid()`; omits empty columns so defaults apply
- [ ] The Help window could show the object model (the SVG as a PNG in the text)

## Model diagram (`features/MODEL_DIAGRAM_FEATURE.md`)

- [ ] Show the diagram inside the Studio (a WKWebView window) instead of the browser
- [ ] Click a rule symbol to open it on the Rules page (once the Rules page exists)

## The Studio

Done: menus, toolbar, crumb trail, shortcuts (`STUDIO_REVIEW.md` step 1); Edit menu; product name
and Application Support folder; workspace, `Project.json`, the project's database copy; Project
Settings and branding; Open Project (⌘O) and Recent Projects; New Project from SQLite; API Logic
Server Project; runtime and templates in the workspace.

- [ ] Studio review step 2: context menus on the entity list and the attribute table (`STUDIO_REVIEW.md`)
- [ ] Studio review step 3: small fixes (the + / − under Objects)
- [ ] Preferences… (⌘,): the repository / library folder, the workspace location; a Settings window, `Settings.plist` in Application Support, secrets in the Keychain
- [ ] More project settings: version, bundle id, theme
- [ ] Project backup and restore (zip the project folder; restore into the workspace)
- [ ] `.alcproj` document type: double-click a project in Finder; Open Recent via NSDocumentController
- [ ] Git via `/usr/bin/git` (NSTask): init / commit on generation, status, push / pull; GitHub REST (create repo, pull requests)
- [ ] Settings groups for ALS / APIs, AI / LLM providers, SMTP notifications
- [ ] Generator offers `build_db.py`-style database creation for generated apps
- [ ] Rename the rest to the product name (author, later): the FB project and its `.main`, the bundle id

## Installing the Studio

- [ ] Installer for a release: the Studio app plus the runtime and templates, put into
  `~/Library/Application Support/Imagery LogicBank Studio for FutureBasic/workspace/` (a `.pkg` with a
  per-user postinstall, or a first-launch copy from the disk image), so users need no repository

## Tooling

- [ ] `tools/xiblint.py`: unique ids, connections that resolve, tags unique per document, frames inside their superview, base64 key equivalents - on every generated and hand-written XIB
- [ ] On a Mac: `xcrun ibtool --errors --warnings --notices` on every XIB (`docs/reference/XIB Reference.md` §5)
- [ ] fblint: check statement syntax (e.g. `tableview`'s `columnWidths`)
- [ ] A Python reference for Type Mapping (the definitions report) to check the FB rules
- [ ] Retire or make private `futurebasic-apis`: outdated (pre-7.0.35), and the toolboxes carry no redistribution licence

## Test_Xib_View

- [ ] `BuildMenu` is never called - the File menu (Close ⌘W) is not built; add `fn BuildMenu` to the main program
- [ ] Remove or keep `OpenSQLite` / `CloseSQLite` (older database path) and `GetCustomers` / `GetAllCustomers` (hand-written SQL)
- [ ] Wire `InsertPersonRecord` / `UpdatePersonRecord` / `DeletePersonRecord` to the add, save and delete buttons
- [ ] Have the app run `Database/schema.sql` + `seed.sql` instead of its own copy in `CreateEmptySQLDatabase`

## Parked: licensing and the paid build - revisit after the Lite release (author, 2026-11-24)

Everything needed is in `design/Editions and Licensing.md`. In this order:

1. [ ] Choose the licence option - author: **A** portable checksum (SHA-256 on the License Server),
       **B** signed licence file (`SecKeyVerifySignature`), or **C** online activation (breaks the
       no-dependency rule). Already decided: offline, Studio only.
2. [ ] Create the private repository (e.g. `Api_Logic_Client_Enterprise`); move `src/Enterprise` and
       `src/Runtime/ALS Client.incl`, `ALS Binding.incl`, `ALS App.incl` there.
3. [ ] Its `Edition.incl` (replaces this repo's): `EditionEnterpriseAvailable` from the licence;
       Enterprise runtime files, start-up (`gALSHost`, login paths), `EditionRulesInApp` = NO.
4. [ ] Studio: an edition choice in Project Settings and a "Licence…" entry (Preferences).
5. [ ] License Server (its own repository): product `imagery_logicbank_studio_fb`, bit 0 `enterprise`.
6. [ ] The paid build: project file, release, distribution from the License Server.

## Ideas

- LogicBank for FutureBasic: offer it back to Val Huber's project (above, waiting on the author).
- The ALS model's relationships make a Lite app possible from an ALS project too: its
  `database/db.sqlite` (SQLite projects) with the ALS model's names.
