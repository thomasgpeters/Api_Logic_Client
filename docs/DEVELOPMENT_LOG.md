# Development Log

What was done and what was learned, newest first. Commits are on
`claude/dazzling-darwin-awec2o` (Api_Logic_Client unless marked *TXV* = Test_Xib_View).
For the plan see `ROADMAP.md`; for open items `BACKLOG.md`.

---

## 2026-11-16 — First generator build: 100+ translator errors

- **Runtime files compiled into the generator.** `resources "../Runtime/x.incl"`
  is translated as source; `ALS Client.incl`'s `end globals` then ended the implicit
  global scope, so every global in `My Globals.glbl` (`isLoggingOn`, `projectName`,
  `gXibNextID`, …) became "unknown". Fix: `resources "../Runtime"` — a folder resource
  is copied, not compiled (as `Api_Logic_Client.xcodeproj` already was);
  `BundleURLForResource( …, @"incl", @"Runtime" )`.
- **FB keywords as names:** `record`, `text`, `resources` → `aRecord`,
  `textValue`, `resourceDict` (also in generated binding code).
- **`for x in`** needs an array variable, not `fn …` or `@[ … ]`.
- **Overloads:** `#if 0 // ERROR_PARAM` blocks hold planned `@err` signatures; the
  active `FileManagerRemoveItemAtURL( url )` / `FileManagerCopyItemAtURL( src, dst )`
  have none.
- fblint learned all four (keyword list, active-declaration argument counts, `for … in`,
  source files as resources); it reproduces the build's error classes on the old code.

---

## 2026-11-16 — Workspace in Application Support

- Projects now live in `~/Library/Application Support/Api_Logic_Client/workspace/<project>/`
  (was `~/ApiLogicClient/<project>/`; the earlier plan of a user-chosen folder under
  `~/Documents` is dropped). Settings will share the same Application Support folder.
- `~/Library` is hidden in Finder, so *Model → Show Workspace in Finder* reveals the
  current project (or the workspace) with `WorkspaceActivateFileViewerSelectingURLs`.
- Application Support is found with `FileManagerURLForDirectory( NSApplicationSupportDirectory, NSUserDomainMask )`.

## 2026-11-16 — Repository layout and documentation

- `1802bb0` Repository restructured: `src/Generator` (FB project), `src/Runtime`,
  `docs/{design,reference,controls,features}`, `tools/`, `samples/`. Generator and
  Runtime moved together so `data.fbproj`'s `../Runtime/…` paths still work.
- `.fbeproj` is a bundle but just a folder: its build order is the plain-text
  `data.fbproj`, edited and versioned like any source file.
- Controls research (`docs/controls/Controls Catalog.md`): toast, popover, pill box
  (`NSTokenField`), rounded corners (`BoxSetCornerRadius`, `CALayerSetCornerRadius`),
  image viewers (`NSImageView`, `IKImageView`), `PDFView`, `PDFThumbnailView`,
  Quick Look thumbnails, carousel (`NSCollectionView` — no FB example yet).
- Styling: AppKit has no CSS. FB reaches system colors, appearances
  (`AppearanceNamed`, `App/Window/ViewSetAppearance`), asset-catalog colors
  (`ColorNamed`), dynamic colors (`ColorWithName`), fonts — enough for a CSS-like
  theme file.

## 2026-11-16 — Designer view, List parts, binding code

- `0776b0e` Entity definitions with recommendations (Title, FB type, size, key role,
  control, widths) and designer adjustments in `Design.json`; `<Entity>List.xib`;
  `<Entity> Binding.incl`; separate Generate XIBs / XIB / Binding Code / App.
- **Title** is the term for an attribute's field label *and* column heading.
- `StringCapitalizedString` lowercases the rest of each word: CamelCase names became
  `Companyname`. Titles now split CamelCase; constants keep case.
- FB's table data source matches row keys by **column identifier**; the generator's
  attribute table had automatic identifiers, so its rows likely never displayed as intended.
- The current `tableview` statement takes a `columnWidths` argument the outdated
  toolbox copy lacked; runtime calls fixed.
- FB has no CLI translator: FBtoC merged into the editor in FB 7.0 ("Farewell FBtoC").
  Compiling can be scripted from logged UNIX commands or *Make Xcode Project* +
  `xcodebuild`; translation needs the editor. The workflow stays: author builds,
  pastes the Build Log.

## 2026-11-16 — Model from SQLite

- `375346c` *Model → Open SQLite Database…*: tables, keys, `keyKind`, relationships
  from `sqlite_master` / `pragma_table_info` / `pragma_foreign_key_list`; our own
  SQLite declarations (no FB-team toolbox file needed); `tools/sqlite_model.py` reference.
- Northwind (ALS project in FutureBasic_Documentation `nw/`): 12 identity keys (7
  AUTOINCREMENT, tracked in `sqlite_sequence`), 5 assigned keys incl. composite
  `Location(country, city)`; no triggers; one view. `admin.yaml` is ALS's UI model —
  `tab_groups` (relationships), `user_key` (record display name).
- SQLite has no GUID type or `uuid()`; Cocoa's `UUIDString( UUIDInit )` is the choice.
- Decisions recorded: lite edition talks to SQLite directly; ALS later behind the same
  data interface; macOS only; immutable bundle; workspace folder; settings in
  Application Support, secrets in the Keychain; git via NSTask, GitHub via REST.
- `edd0d6f` Principles from the author's DDD book: model as source of truth,
  ubiquitous language, layer dependency rule by include order, lite tier first.

## 2026-11-16 — SQL query builder (*TXV*)

- `67ef667` INSERT / UPDATE / DELETE completed in the SELECT pattern; one binder;
  unfiltered UPDATE/DELETE refused. SELECT fixes: missing AND between filters,
  `IN ( ? )`, joins' AND placement, integer filters given as strings, decimals,
  UTF-8 text length, `IS NULL` bind positions.
- `f33a190` Obsolete demo code removed after a call-graph check (whole
  `SQLite3_Super.incl`, contacts-table functions). Still unreferenced: `BuildMenu`
  (never called — File menu not built), `OpenSQLite`/`CloseSQLite`, `GetCustomers`.
- `local mode` before a `local fn`: following `dim`s are local, globals hidden,
  executable statements in between never run.
- A CF dictionary cannot hold NULL.

## 2026-11-16 — Test_Xib_View runs (*TXV*)

- `448914a`, `f951485` 67 build errors: FB 7.1.4 made returning a value from an
  untyped fn an error; `Tlbx SQLite3.incl` relied on it. Then `'` comments and
  `'~'1` dividers (dropped in 7.0.24/7.0.25) and `#build` (single-file programs
  only). The FB editor converts old comments on open, so only freshly pulled files failed.
- `94dd77b` "Invalid tag. Control 1 does not exist in window 1
  (ViewSetAutoresizesSubviews)": `View…` functions need a view tag — `_windowContentViewTag`.
- `850ea29`, `a72fcc4` `sqlite3_open` silently creates an empty file; the app now
  builds the schema when the `person` table is missing.
- `5962f8f` "no such table / no such column: balance": schema and queries out of
  step; `ALTER TABLE … ADD COLUMN` upgrades existing files; REAL values arrive as
  NSNumber → `ControlSetObjectValue`.
- `a3dab6c` `Database/`: `schema.sql`, `seed.sql`, ready-made `contacts.sqlite`,
  `build_db.py` (also from an ALS model).

## 2026-11-15/16 — Foundations

- `fadfda5` First XIB generator (one view per resource, type → control mapping).
- `8bf5442` Generated ALS app: client, binding, master-detail runtime; FB project moved
  into `Generator/`.
- `f361679` `docs/reference/FB Coding Rules.md` and `tools/fblint.py`.
- `d6c95a1` FutureBasic_Documentation adopted as the primary FB reference
  (`futurebasic-apis` is pre-7.0.35).
- `dc09bb6` CF types passed to `ObjectRef` parameters need a cast.
- Licensing: FB toolbox headers carry no redistribution license; generated projects
  never include them.
