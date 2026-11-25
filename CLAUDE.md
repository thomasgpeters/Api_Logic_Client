# Api Logic Client — Imagery LogicBank Studio for FutureBasic

The product's name is **Imagery LogicBank Studio for FutureBasic** (shown in the app; `Branding.incl`).
The Studio's Application Support folder is `Imagery LogicBank Studio for FutureBasic` (author,
2026-11-24; an old `Api_Logic_Client` folder is moved over on first launch). The repository and the
FB project file keep the name Api_Logic_Client until the author renames them (backlog).

A **FutureBasic** (FBE, macOS/Cocoa) generator. It reads an API Logic Server
(ALS) project's model (`/metadata?include=attributes`) and generates a complete
FutureBasic app for it: XIB screens, an ALS JSON:API client, and logic binding
the API to the UI. Northwind is only the test model; any ALS project is the target.

The author's general preferences mention C++/Wt and Bootstrap — they do **not**
apply here. What carries over: keep code modular, and keep appearance
theme-able (generated XIBs use macOS system/catalog colors, so light and dark
mode work without extra code).

## Repo layout
- `src/Generator/` — the FB project (`Api Logic Client.fbeproj`): open it in the FB
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
  - `Edition.incl` — which edition the Studio generates (this repo: Lite only; the paid build replaces this file). `docs/design/Editions and Licensing.md`.
  - `App Generator.incl` — `AppGenerate`: Generate XIBs / XIB / Binding Code / App.
  - `Project Workspace.incl` — workspace folders (`<project>/`, `<project>/FBapp/`) and `Project.json` (project settings).
  - `New Project.incl` — the New Project view (`NewProjectView.xib`): name + SQLite database → a project (the lite edition's catalyst); the ALS form is one button away.
  - `Project Settings.incl` — the Project Settings view (`ProjectSettingsView.xib`): the About text (≤ 250 chars, the app's `Credits.rtf`) and branding (logo, tag-line, copyright for the app shell).
  - `Rules Bridge.incl` — Import / Export Rules (declare_logic.py) and `Studio Rules.incl` on Generate App; until its port to FB it says "coming" and writes an empty `Studio Rules.incl`.
  - `ERD Generator.incl` — Model > Show Model Diagram: `<project>/Model ERD.html` from the `Templates/ERD` page, the model and `Rules.json`.
  - `Recent Projects.incl` — the Recent Projects list (`Recent Projects.json` in Application Support), shown on the Welcome view.
  - `ALS Model.incl` — an ALS project's model, parsed as text (never run): `database/models.py`, else `app_model.yaml` / `admin.yaml` (attributes, keys, relationships, display column).
  - `ALS Project.incl` — where that model is: an ALS project folder, a model file, or a public GitHub repository (raw.githubusercontent.com); the copy in `<project>/ALS Model/`; the ALS model -> the Studio's.
  - `Open ALS Project.incl` — the API Logic Server Project view (`ALSProjectView.xib`): point at the ALS project (type, Folder…, Model File…, or drop on a subclassed view) → a project (the Enterprise catalyst).
  - `Project Actions.incl` — Open Project, model loading, entity definitions, design load/save, generate commands.
- `src/CleanApp/` — a project the FB editor created (author, 2026-11-24): the reference for project
  settings (`Settings2.plist`: SDK, architecture, minimum macOS) and the starting point of new example
  projects (its Hello button and menu were removed at the author's request, 2026-11-25). Keep the
  Studio's, the template's and Test_Xib_View's settings in step with it.
- `src/SQLGeneratorExample/` — the SQL Generator shared on its own (MIT): the module, a SQLite runner,
  ten examples on a CRM database, a Help window and About box; README, LICENSE, a draft post for the FB
  list (`docs/features/SQL_GENERATOR_FEATURE.md`). Its module files stay identical to `src/Runtime`'s
  and Test_Xib_View's (`run_tests.sh` checks).
- `src/Enterprise/` — the Enterprise edition, in this repository for now (author, 2026-11-25; a private
  repository when it is sold): `DataObject_JSONAPI.incl` (the SQL Generator's JSON:API side: the same
  statement dictionaries -> ALS requests, on the model `src/Generator/ALS Model.incl` reads). The contract: `docs/design/ALS Contract.md`;
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
  - `Binding Support.incl`. `ALS Client.incl`, `ALS Binding.incl`, `ALS App.incl` are no longer copied into apps: the start of the Enterprise runtime, to move to its private repository.
- `src/Templates/` — starting files for generated apps, copied only when missing
  (from `workspace/Templates`, see above): `ERD/Model ERD.html` (the model diagram page), `Project/Settings2.plist`, `App/EventHandlers.incl`,
  `App/Menus.incl`, `App/Theme.incl` (the colours), `App/Rules.incl` (the app's business rules). `Windows.incl` is generated from the model the same way (only when missing).
- `docs/design/` — `App Shell Design.md` (the generated app), `Generator App Design.md` (the generator: workspace, settings, git), `Logic Engine Design.md` (LogicBank rewritten for FB: rules as FB code, the runtime engine, Imagery Logic Studio in the generator).
- `docs/reference/` — `FB Coding Rules.md`, `FB Documentation Map.md`, `FB Reference Index.md`, `XIB Reference.md` (what a XIB is, FB's nib statements, how we write and check them).
- `docs/design/architecture.svg` — the end-to-end diagram, drawn by `tools/make_architecture_svg.py` (edit the script, not the SVG).
- `docs/controls/` — `Controls Catalog.md` (native controls, FB toolboxes, readiness).
- `docs/DOC_ONE_PAGER.md` — the one-page introduction (keep it true with the user guide).
- `docs/USER_GUIDE.md` — the user guide (keep it true when what a user sees or can do changes).
- `docs/features/` — one `<NAME>_FEATURE.md` per feature (how it works, where, decisions, verification).
- `docs/ROADMAP.md` (phases), `docs/BACKLOG.md` (open items), `docs/DEVELOPMENT_LOG.md`
  (what was done and learned, newest first, with commits).
- `tools/` — `fblint.py` (checks FB sources and generated projects against the coding rules),
  `sqlite_model.py` (reference implementation of the SQLite model reader),
  `logic_reference.py` (reference logic engine + acceptance scenarios: `--test <db.sqlite>`),
  `make_logic_test.py` (builds the FB test project for the same scenarios, to run on a Mac),
  `rules_bridge.py` (declare_logic.py import / export, Rules.json check, FB rule generation),
  `check_erd_page.py` (test: the model diagram page in headless Chromium),
  `check_app_pages.py` (test: the generated App Pages.incl lints with the runtime),
  `make_sql_generator_svg.py` (draws `docs/design/SQL Generator Object Model.svg`),
  `als_contract.py` (test: the API Logic Server contract, against a running server),
  `jsonapi_reference.py` (the SQL Generator's JSON:API side; test: same rows as SQL, against a server),
  `models_py_reference.py` (an ALS project's `database/models.py` read as text; test: against SQLAlchemy),
  `als_project_reference.py` (the Open ALS Project screen: folders, files, GitHub, the Studio model),
  `run_tests.sh` (every check that runs without a Mac). How to run each test: `docs/TESTING.md`.
- `samples/Northwind/metadata.json` — sample ALS `/metadata` response.

One concern per file, aptly named — in `src/` and in what the generator emits.

Generated apps go to `~/Library/Application Support/Imagery LogicBank Studio for FutureBasic/workspace/<project>/FBapp/`; the project's settings (`Project.json`, `Design.json`) to `<project>/`; settings will live in `~/Library/Application Support/Imagery LogicBank Studio for FutureBasic/`, secrets in the Keychain (see `docs/design/Generator App Design.md`). The app bundle is never written to. macOS only.

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
- Verify every toolbox name/signature in FutureBasic_Documentation's headers.
- `View…` functions take a view tag, never a window tag — use `_windowContentViewTag`.
- Cast CF types passed to `ObjectRef` parameters: `fn ObjectClassName( (ObjectRef)dta )`.
- `alert` button titles are an array; don't quit a Cocoa app with `end`.
- Avoid deprecated syntax (`globals "file"`, `proc`, `def*` letter ranges, `index$`, `TextLabelWithTag`).
- FB source files use classic-Mac **CR** line endings (convert to LF to edit,
  back to CR before committing). XIB, JSON, SQL and Python use LF.
- Logging is gated on `isLoggingOn`.

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
  usually exists in `src/Generator/` or `src/Runtime/` (and vice versa).
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
