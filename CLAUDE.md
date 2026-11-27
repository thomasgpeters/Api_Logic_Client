# Api Logic Client — App Builder for FutureBasic

The product's name is **App Builder for FutureBasic** (shown in the app; `Branding.incl`).
The Studio's Application Support folder is `App Builder for FutureBasic` (author, 2026-11-26:
the product is "App Builder for FutureBasic", without "Imagery" - the FB community knows the tool,
not the company; earlier folders, `Imagery LogicBank Studio for FutureBasic` and `Api_Logic_Client`,
are moved over on first launch). Imagery LogicBank Studio is a different product (C++/Wt). The built app
is **Studio for FB** (`src/AppBuilder/Studio for FB.fbeproj`, author 2026-11-26). The repository keeps
the name Api_Logic_Client until the author renames it (backlog).

A **FutureBasic** (FBE, macOS/Cocoa) generator. It reads an API Logic Server
(ALS) project's model (`/metadata?include=attributes`) and generates a complete
FutureBasic app for it: XIB screens, an ALS JSON:API client, and logic binding
the API to the UI. Northwind is only the test model; any ALS project is the target.

The author's general preferences mention C++/Wt and Bootstrap — they do **not**
apply here. What carries over: keep code modular, and keep appearance
theme-able (generated XIBs use macOS system/catalog colors, so light and dark
mode work without extra code).

## Repo layout
- `src/AppBuilder/` — the FB project (`Studio for FB.fbeproj`, which builds Studio for FB.app): open it in the FB
  editor. Its `data.fbproj` (inside the `.fbeproj` bundle) is the build order: an
  `.incl` must come *before* any file that calls it (FB needs definition before use).
  - `Pill Buttons.incl` — Mac-style pill (capsule) push buttons: AppKit's capsule on macOS 26, drawn by the layer on 15; identical to `src/Runtime`'s copy.
  - `Branding.incl` — the product name and the Imagery logo (`ImageryLogo` follows light/dark); `imagery_logo.png` / `imagery_logo_white.png` are the canonical files, never edited.
  - `API Interface.incl` — ALS connectivity for the generator itself (metadata fetch).
  - `SQLite Access.incl` — our own minimal SQLite declarations (open read-only, prepare, step, columns).
  - `SQLite Model.incl` — the model from a SQLite file: columns, keys (`keyKind`), relationships.
  - `Type Mapping.incl` — the rules: control kind, FB type, size, Title, widths, plus the designer's adjustments (`design` per attribute, saved in `Design.json`).
  - `XIB Generator.incl` — Form and List parts per entity; `Model Tags.incl`; model entries.
  - `Binding Generator.incl` — `<Entity> Binding.incl` (record ↔ Form, records → List).
  - `Studio Library.incl` — the runtime and templates in the workspace (`workspace/Runtime`, `workspace/Templates`): installed from the repository folder, updated from the Model menu; also `AppSupportFolderURL`.
  - `Licence.incl` — the licence: ES256, verified offline (Security framework; its calls declared at the top of `Licence.incl` itself, since FB's `Tlbx Security.incl` is newer than the author's FB), kept in the Keychain, `LicenceAllows( feature )`; `Licence Window.incl` — the Licence menu and window, `LicenceGate` on licensed commands (`docs/features/LICENSING_FEATURE.md`). Test keys only here (`tools/licence_test_keys`).
  - `Edition.incl` — which edition the Studio generates: Professional when the licence includes it.
  - `App Generator.incl` — `AppGenerate`: Generate XIBs / XIB / Binding Code / App.
  - `Generate Progress.incl` — Generate App's progress sheet (the steps ticked, a bar, Done when finished).
  - `Project Workspace.incl` — workspace folders (`<project>/`, `<project>/FBapp/`) and `Project.json` (project settings).
  - `New Project.incl` — the New Project view (`NewProjectView.xib`): name + SQLite database → a project (the lite edition's catalyst); the ALS form is one button away.
  - `Project Settings.incl` — the Project Settings view (`ProjectSettingsView.xib`): the About text (≤ 250 chars, the app's `Credits.rtf`) and branding (logo, tag-line, copyright for the app shell).
  - `Rules Bridge.incl` — Import / Export Rules (declare_logic.py) and `Studio Rules.incl` on Generate App; until its port to FB it says "coming" and writes an empty `Studio Rules.incl`.
  - `ERD Generator.incl` — Model > Show Model Diagram: `<project>/Model ERD.html` from the `Templates/ERD` page, the model and `Rules.json`.
  - `Recent Projects.incl` — the Recent Projects list (`Recent Projects.json` in Application Support), shown on the Welcome view.
  - `ALS Model.incl` — an ALS project's model, parsed as text (never run): `database/models.py`, else `app_model.yaml` / `admin.yaml` (attributes, keys, relationships, display column).
  - `ALS Project.incl` — where that model is: an ALS project folder, a model file, or a public GitHub repository (raw.githubusercontent.com); the copy in `<project>/ALS Model/`; the ALS model -> the Studio's.
  - `Open ALS Project.incl` — the API Logic Server Project view (`ALSProjectView.xib`): point at the ALS project (type, Folder…, Model File…, or drop on a subclassed view) → a project (the Professional catalyst).
  - `Project Actions.incl` — Open Project, model loading, entity definitions, design load/save, generate commands.
- `src/CleanApp/` — a project the FB editor created (author, 2026-11-24): the reference for project
  settings (`Settings2.plist`: SDK, architecture, minimum macOS) and the starting point of new example
  projects (its Hello button and menu were removed at the author's request, 2026-11-25). Keep the
  Studio's, the template's and Test_Xib_View's settings in step with it.
- `src/SQLGeneratorExample/` — the SQL Generator shared on its own (MIT): the module, a SQLite runner,
  ten examples on a CRM database, a Help window and About box; README, LICENSE, a draft post for the FB
  list (`docs/features/SQL_GENERATOR_FEATURE.md`). Its module files stay identical to `src/Runtime`'s
  and Test_Xib_View's (`run_tests.sh` checks).
- `src/LogicBankExample/` — LogicBank for FutureBasic shared on its own (MIT): the module (Logic *.incl, Data Model.incl,
  identical to `src/Runtime`'s - `run_tests.sh` checks), `Data Memory.incl` (the data layer in memory), an example on
  Customer / Order / Item with no database, a Help window with the user guide, README, LICENSE
  (`docs/features/LOGICBANK_MODULE_FEATURE.md`; its story is checked by `tools/logicbank_example_reference.py`).
- `src/Shared/` — files shared by the free modules' sample apps, identical in each (`run_tests.sh` checks): `About Imagery.incl`
  + `About Imagery.txt` + the logos - the *About Imagery Business Systems* window (`docs/design/Free Modules Design.md`).
- `src/WebToolkit/` — Web Toolkit for FutureBasic (working name, MIT): web apps in FB behind nginx (FastCGI). The core
  (`Web Server/Session/Widgets/Render/Events.incl`) knows no data model; `Web Binding.incl` (optional) binds forms and
  tables through LogicBank for FutureBasic; `Resources/web.js` (AJAX, the page lifecycle) and `web.css` (themes);
  `Template/` (the app template: the developer writes `Pages.incl`). `src/WebToolkitExample/` (Orders) is built from it.
  `Web Layout.incl`: pages laid out in XIB files (`.webxib`), rules in `tools/web_layout_reference.py`, its Objective-C
  compiled here with GNUstep (`tools/check_web_layout.py`); `Layout Tool/Layout Tool.html` lays them out (`tools/check_layout_tool.py`).
  Copies are identical (`run_tests.sh`); `tools/web_toolkit_reference.py` tests web.js (`docs/features/WEB_TOOLKIT_FEATURE.md`).
- `src/RecordFilesExample/` — Record Files for FutureBasic (working name, MIT): `Record File.incl` (fixed-size records in
  random-access files, FB's `open "R"`), `Record Index.incl` (B-tree index files; C between the markers "record index
  core", tested by `tools/check_record_index.py`), Customer / Order / Item timed against SQLite. Formats and the App
  Builder option: `docs/design/Record Files Design.md`; `tools/record_files_reference.py` reads both formats.
- `src/MacTests/` — single-file FB programs that answer a question on a Mac before a feature is built on it (`MapKit Points Test.fb`: how FB serves MapKit's point views); see `docs/TESTING.md`.
- `src/Professional/` — the Professional edition, in this repository for now (author, 2026-11-25; a private
  repository when it is sold): `DataObject_JSONAPI.incl` (the SQL Generator's JSON:API side: the same
  statement dictionaries -> ALS requests, on the model `src/AppBuilder/ALS Model.incl` reads). The contract: `docs/design/ALS Contract.md`;
  references and tests: `tools/als_contract.py`, `tools/jsonapi_reference.py`, `tools/models_py_reference.py`.
- `src/Runtime/` — our FB code copied into every generated app. Not bundled into the Studio
  (author, 2026-11-24): `Studio Library.incl` copies `src/Runtime` and `src/Templates` into the
  workspace (`workspace/Runtime`, `workspace/Templates`) the first time they are needed, and on
  *Generate > Update Runtime and Templates*, and on every Generate App while the Studio runs from its
  repository (so apps never get a stale runtime); generation copies from there. The list is `AppRuntimeFiles`:
  - data runtime — `Data SQLite.incl` (our SQLite declarations, transactions), the author's
    DataObject query builder (`DataObject.glbl`, `DataObject_Super.incl`, `DataObject.incl`,
    kept identical to Test_Xib_View's), `Data Model.incl` (Model.json entities),
    `Data Records.incl` (fetch / parent / children / insert / update / delete). The rules
    engine builds on it.
  - LogicBank for FutureBasic (clean-room) — `Logic Rules.incl` (declare, activate, order),
    `Logic Row.incl` (what a rule reads), `Logic Engine.incl` (LogicInsert / LogicUpdate /
    LogicDelete). Rules are FB functions registered with `@fn` and called through a C cast.
  - `App Data Lite.incl` — the app's data interface (list / save / remove / login, answers in `AppDataDone`), Lite edition: SQLite + the rules engine.
  - `App Shell.incl` — the generated app's frame: nav bar, header, footer, pages, theme menu (`features/APP_SHELL_FEATURE.md`); its buttons are pills (`Pill Buttons.incl`, `gThemePillButtons`).
  - `Binding Support.incl`; `Auto Complete.incl` (a foreign key as a text field that finds the parent record as you type: the list under or over the field, the key kept behind the scenes; its settings in App Builder's row under the Control popup); `Record Popover.incl` (a lookup Dropdown's info button: the chosen parent's details in a popover); `Record Tiles.incl` (a List's records as tiles, three or four across: the name as a subheading, other fields smaller; a Grid / Tiles switch in the List card's title row). `ALS Client.incl`, `ALS Binding.incl`, `ALS App.incl` are no longer copied into apps: the start of the Professional runtime, to move to its private repository.
- `src/Templates/` — starting files for generated apps, copied only when missing
  (from `workspace/Templates`, see above): `ERD/Model ERD.html` (the model diagram page), `Project/Settings2.plist`, `App/EventHandlers.incl`,
  `App/Menus.incl`, `App/Theme.incl` (the colours), `App/Rules.incl` (the app's business rules). `Windows.incl` is generated from the model the same way (only when missing).
- `docs/research/` — domain research behind the samples (flight planning, customs clearance), with sources.
- `docs/design/` — `Web Toolkit Design.md` (feasibility: a standalone web server and UI in FB, replacing Wt; proof: `src/MacTests/Web Server Test.fb`), `Free Modules Design.md` (the SQL Generator and LogicBank for FutureBasic: free, each with a sample app and the About Imagery window; App Builder licensed), `Derived Attributes Design.md` (a rule's attribute stored in the database or computed in memory), `Page Designer Design.md` (pages composed from entities, a List or a Detail each, linked by the model's relationships), `Editions Design.md` (Lite and Professional: one app, two data layers, which rules belong to which edition), `Licensing Design.md` (one app, signed licences from the Imagery License Server, the Licence menu and upgrade), `AI Assistant Design.md` (rules as sentences in the model's names, translated by AI into LogicBank for FutureBasic and ALS's declare_logic.py; controls suggested), `Flight Service Filing Design.md` (Professional: the simulated FAA filing interface in ALS), `App Shell Design.md` (the generated app), `Generator App Design.md` (the generator: workspace, settings, git), `Logic Engine Design.md` (LogicBank rewritten for FB: rules as FB code, the runtime engine, Imagery Logic Studio in the generator).
- `docs/reference/` — `FB Coding Rules.md`, `FB Documentation Map.md`, `FB Reference Index.md`, `XIB Reference.md` (what a XIB is, FB's nib statements, how we write and check them).
- `docs/design/architecture.svg` — the end-to-end diagram, drawn by `tools/make_architecture_svg.py` (edit the script, not the SVG).
- `docs/controls/` — `Controls Catalog.md` (native controls, FB toolboxes, readiness).
- `docs/DOC_ONE_PAGER.md` — the one-page introduction (keep it true with the user guide).
- `docs/USER_GUIDE.md` — the user guide (keep it true when what a user sees or can do changes).
- `docs/TEST_SCENARIOS.md` → `docs/TEST_SCENARIOS.pdf` (`tools/make_test_guide.py`) — the test scenario guide for testers: every feature, step by step, Pass / Fail (keep it true with the features).
- `docs/features/` — one `<NAME>_FEATURE.md` per feature (how it works, where, decisions, verification).
- `docs/archive/` — kept for the record, not maintained (the first LinkedIn post, a dated summary report).
- `docs/ROADMAP.md` (phases), `docs/BACKLOG.md` (open items), `docs/DEVELOPMENT_LOG.md`
  (what was done and learned, newest first, with commits).
- `tools/` — `fblint.py` (checks FB sources and generated projects against the coding rules),
  `sqlite_model.py` (reference implementation of the SQLite model reader),
  `logic_reference.py` (reference logic engine + acceptance scenarios: `--test <db.sqlite>`),
  `make_logic_test.py` (builds the FB test project for the same scenarios, to run on a Mac),
  `rules_bridge.py` (declare_logic.py import / export, Rules.json check, FB rule generation),
  `check_erd_page.py` (test: the model diagram page in headless Chromium),
  `check_app_pages.py` (test: the generated App Pages.incl lints with the runtime),
  `make_site.py` (Imagery's FutureBasic site, fb.imagery-business-systems.com, built from the repository into `site/`), `licence_reference.py` (licences: issue, verify, the Mac test program), `logicbank_example_reference.py` (the LogicBank example's model, rules and story on the reference engine), `make_logicbank_svg.py` (its Help diagram),
  `make_sql_generator_svg.py` (draws `docs/design/SQL Generator Object Model.svg`), `svg_to_png.js` (an SVG as a 2x PNG, light colours: the example's Help diagram),
  `als_contract.py` (test: the API Logic Server contract, against a running server),
  `jsonapi_reference.py` (the SQL Generator's JSON:API side; test: same rows as SQL, against a server),
  `models_py_reference.py` (an ALS project's `database/models.py` read as text; test: against SQLAlchemy),
  `als_project_reference.py` (the Open ALS Project screen: folders, files, GitHub, the Studio model),
  `run_tests.sh` (every check that runs without a Mac). How to run each test: `docs/TESTING.md`.
- `samples/Northwind/metadata.json` — sample ALS `/metadata` response.
- `samples/<Name>/` — the sample applications (author, 2026-11-26), one use case each: `Telecom` (a mobile carrier's travel
  plans priced from roaming agreements, 39 rules), `Customs` (Bermuda customs clearance, automated: FOB duty, manifest, risk
  lanes, release, bond, the port gate, 93 rules), `FlightPlanner` (VFR flights in New England: wind triangle, weight and balance, runways, weather, currency, go / no-go, 104 rules). Each: `schema.sql`; `lookup.sql` (reference data that stays) and `sample.sql` (the demo scenario) apart,
  as on the C++ side, with `purge_sample.sql`; `build_db.py` (every row through the rules, `--lookup-only`); the rules
  (`<name>_rules.py`, tested by `test_rules.py` and `--prove`) and the same rules in FB (`Rules.incl`).
  `samples/sample_loader.py` replays the SQL files through the rules.

One concern per file, aptly named — in `src/` and in what the generator emits.

Generated apps go to `~/Library/Application Support/App Builder for FutureBasic/workspace/<project>/FBapp/`; the project's settings (`Project.json`, `Design.json`) to `<project>/`; settings will live in `~/Library/Application Support/App Builder for FutureBasic/`, secrets in the Keychain (see `docs/design/Generator App Design.md`). The app bundle is never written to. macOS only.

## Related repositories
- **thomasgpeters/FutureBasic_Documentation** (private) — the FB reference. See References.
- **thomasgpeters/Test_Xib_View** — the author's SQLite + XIB app ("Modern CRM"):
  the record/view pattern generated apps should follow, and the test bed for
  FB 7.1.x fixes. Its `Database/` folder builds `contacts.sqlite` from
  `schema.sql`/`seed.sql` or from an ALS model (`build_db.py --als`).
- **thomasgpeters/Domain-Driven-Design-Book** (private, read-only here) — the
  author's book on AI-assisted, domain-driven development. Its principles
  govern the generator: the model is the source of truth and generated code is
  disposable (§20.4), ubiquitous language (§2.2), the layer dependency rule
  (§5.3), Lite tier first then an infrastructure rewrite (§5.1, §10.1).
  See `docs/design/App Shell Design.md` → Principles.
- `futurebasic-apis` — outdated (pre-7.0.35); don't rely on it.

## Tools are FutureBasic; no Python in anything FB builds
The Studio's features and tools are written in FB (author, 2026-11-24). **No Python artifact goes
into the Studio's bundle or into a generated app** — no `.py` resource, no call to `python3`.
Python in `tools/` is only for references and tests that run here, where FB cannot
(`logic_reference.py`, `sqlite_model.py`, `rules_bridge.py`, `check_*.py`, `fblint.py`);
`rules_bridge.py` is the reference for its FB port (backlog).

## FB code rules (summary — full list with sources in `docs/reference/FB Coding Rules.md`)
These apply to hand-written code **and to everything the generator emits**.
- A fn that returns a value declares its type (`local fn X(...) as Type`); FB 7.1.4+
  treats untyped fns as `void` and rejects `end fn = value` in them.
- Comments are `//`, `/* */`, `///` or `rem`. Never `'` comments, never `'~'1`
  divider lines — the current translator rejects both.
- No `#build` in projects (single-file `.fb` programs only); compiler options
  such as `-lsqlite3` go in Build Settings.
- Verify every toolbox name/signature in FutureBasic_Documentation's headers, and check the header's date: a `Tlbx` header
  dated 2026 may be newer than the author's FB (declare the calls ourselves, as the top of `Licence.incl` does).
- `View…` functions take a view tag, never a window tag — use `_windowContentViewTag`.
- Cast CF types passed to `ObjectRef` parameters: `fn ObjectClassName( (ObjectRef)dta )`.
- `alert` button titles are an array; don't quit a Cocoa app with `end`.
- Avoid deprecated syntax (`globals "file"`, `proc`, `def*` letter ranges, `index$`, `TextLabelWithTag`).
- FB source files use classic-Mac **CR** line endings (convert to LF to edit,
  back to CR before committing). XIB, JSON, SQL and Python use LF.
- **A global does not keep its value alive** (FB's CF types are plain pointers): use a local when one function is enough;
  otherwise keep the value with the module's Kept fn (`LicenceKept`, `DataKept`, `WebKept`). `fblint` reports an object global set from a fn and not kept.
- Logging is gated: every `NSLog` - errors too - is `if ( isLoggingOn ) then NSLog( ... )`. `isLoggingOn` is NO by default,
  declared in the app's own globals (generated apps: `App Globals.glbl`, a template; the Studio: `My Globals.glbl`;
  the examples: their `.glbl`). `fblint` reports an ungated `NSLog` (single-file `.fb` tests, whose output is their log, are exempt).

## Data rules (SQLite and ALS)
- `sqlite3_open` silently **creates an empty file** when the database is
  missing: create the schema first (or check for the tables), or every query
  fails to prepare ("statement is NULL").
- Queries must match the schema exactly; keep the schema in one place
  (`schema.sql`) and add columns to existing databases with
  `ALTER TABLE … ADD COLUMN` (harmless when it already exists).
- When a prepare fails, log `fn SQL3ErrorMsg( db )` and the SQL text, not just "NULL".
- Numeric columns (SQLite REAL/INTEGER, ALS numbers) arrive as NSNumber and
  JSON nulls as NSNull: show them with `ControlSetObjectValue`, not `ControlSetStringValue`.
- ALS: JSON:API under `/api/<Resource>`; login tries `/api/auth/login`, then
  `/api/authentication-User/login`; `/metadata` carries no primary-key information.

## Licensing
- Never copy FB toolbox files into generated projects or other public repos —
  they are FB-team code with no redistribution license; generated apps use the
  user's FB install. Generated projects contain only our own code.

## Workflow
- **Nothing can be compiled here.** The author builds in FutureBasic on a Mac
  and pastes the Build Log or run-time alerts; treat those as the test results.
  Before handing over FB changes, run `tools/run_tests.sh` (lint, logic scenarios, every rule
  proven, the FB test project) — `docs/TESTING.md` lists every test, also the Mac-only ones.
- Work on branch `claude/dazzling-darwin-awec2o` in each repo; the author merges
  via pull requests. After a merge, bring the branch up to date by merging
  `origin/main` into it (force-pushing is not allowed), then push.
- If a report repeats errors already fixed, compare its line numbers with the
  repo: the author's checkout is probably stale. The FB editor rewrites files
  on open (e.g. converting old comments), so local edits can block `git pull` —
  suggest `git stash`, then `git fetch origin && git merge --ff-only origin/<branch>`,
  and give such commands in separate code blocks.
- Fix root causes in the shared pattern too: a bug found in Test_Xib_View
  usually exists in `src/AppBuilder/` or `src/Runtime/` (and vice versa).
- Keep the docs current with each change: add or update the feature's
  `docs/features/<NAME>_FEATURE.md`, add a `docs/DEVELOPMENT_LOG.md` entry (newest
  first, with commit hashes and discoveries), tick or add `docs/BACKLOG.md` items,
  and move `docs/ROADMAP.md` status.

## References
- **Primary: https://github.com/thomasgpeters/FutureBasic_Documentation**
  (private, ~54 MB): the current FB reference manual (`FBHelp/`), all toolbox
  headers (`Toolboxes/Headers/`) and 578 examples (`FBExamples/`). Clone it
  beside this repo and read it in chunks; `docs/reference/FB Documentation Map.md` says
  where things are.
- `docs/reference/FB Reference Index.md` maps keywords to reference pages (same page names
  locally). The online manual is the fallback:
  https://www.brilorsoftware.com/fb/documentation/FBHelp/FBHelp.htm (bot
  protection; fetch single pages only; needs the `Api_Logic_Client` environment).
- FB release notes (breaking changes):
  https://www.brilorsoftware.com/fb/pdfs/releasenotes.pdf.
