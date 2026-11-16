# Api Logic Client

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
  - `API Interface.incl` — ALS connectivity for the generator itself (metadata fetch).
  - `SQLite Access.incl` — our own minimal SQLite declarations (open read-only, prepare, step, columns).
  - `SQLite Model.incl` — the model from a SQLite file: columns, keys (`keyKind`), relationships.
  - `Type Mapping.incl` — the rules: control kind, FB type, size, Title, widths, plus the designer's adjustments (`design` per attribute, saved in `Design.json`).
  - `XIB Generator.incl` — Form and List parts per entity; `Model Tags.incl`; model entries.
  - `Binding Generator.incl` — `<Entity> Binding.incl` (record ↔ Form, records → List).
  - `App Generator.incl` — `AppGenerate`: Generate XIBs / XIB / Binding Code / App.
  - `Project Actions.incl` — model loading, entity definitions, design load/save, generate commands.
- `src/Runtime/` — our FB code copied into every generated app (bundled as resources
  of the generator via `../Runtime/…`): `ALS Client.incl`, `ALS Binding.incl`,
  `ALS App.incl`, `Binding Support.incl`.
- `src/Templates/` — starting files for generated apps, copied only when missing
  (bundled as the `../Templates` folder): `Project/Settings2.plist`, `App/EventHandlers.incl`,
  `App/Menus.incl`. `Windows.incl` is generated from the model the same way (only when missing).
- `docs/design/` — `App Shell Design.md` (the generated app), `Generator App Design.md` (the generator: workspace, settings, git).
- `docs/reference/` — `FB Coding Rules.md`, `FB Documentation Map.md`, `FB Reference Index.md`.
- `docs/controls/` — `Controls Catalog.md` (native controls, FB toolboxes, readiness).
- `docs/features/` — one `<NAME>_FEATURE.md` per feature (how it works, where, decisions, verification).
- `docs/ROADMAP.md` (phases), `docs/BACKLOG.md` (open items), `docs/DEVELOPMENT_LOG.md`
  (what was done and learned, newest first, with commits).
- `tools/` — `fblint.py` (checks FB sources and generated projects against the coding rules),
  `sqlite_model.py` (reference implementation of the SQLite model reader).
- `samples/Northwind/metadata.json` — sample ALS `/metadata` response.

One concern per file, aptly named — in `src/` and in what the generator emits.

Generated output goes to the workspace, `~/Library/Application Support/Api_Logic_Client/workspace/<project>/`; settings will live in `~/Library/Application Support/Api_Logic_Client/`, secrets in the Keychain (see `docs/design/Generator App Design.md`). The app bundle is never written to. macOS only.

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
  Before handing over FB changes, run:
  `python3 tools/fblint.py --headers <FutureBasic_Documentation>/Toolboxes/Headers src`
  (and on any other FB repo touched, e.g. Test_Xib_View).
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
