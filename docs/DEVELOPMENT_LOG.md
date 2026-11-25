# Development Log

What was done and what was learned, newest first. Commits are on
`claude/dazzling-darwin-awec2o` (Api_Logic_Client unless marked *TXV* = Test_Xib_View).
For the plan see `ROADMAP.md`; for open items `BACKLOG.md`.

---

## 2026-11-25 — Map view made generic: a result set with latitude / longitude

- The author: more generic - choose the Map view and show a result set whose rows carry a
  geographic location in latitude and longitude columns; start with an entity's records (Customer,
  Supplier). The design changed: the map takes rows and the names of their location and title
  columns (`App Map.incl`), so any entity, several at once (layers) or a query's rows can be shown.
  Geocoding becomes how a table's location columns are filled (written into the rows), not a cache
  beside them. Northwind has no location columns: adding them (Lite: ALTER TABLE in the project's
  copy; Enterprise: on the server, then an ALS rebuild) is step 4. `design/Map View Design.md`.

## 2026-11-25 — Map view designed (records on a map, addresses geocoded)

- The author: a look with a map - an entity's records (Customers) on a map, addresses translated
  into locations. Found in FutureBasic: `mkmapview`, `MKPointAnnotationWithTitle`,
  `MKMapViewShowAnnotations`, the pin-selected event `_mapViewDidSelectAnnotationView`, and Apple's
  geocoder `CLGeocoderGeocodeAddressString` (no key, no location permission; FBExamples *Coordinates
  from address*); macOS 26 adds `MKGeocodingRequest`. Northwind's places: Customer, Employee,
  Supplier (Address, City, Region, PostalCode, Country) and Order (Ship…). Design with open
  questions: `design/Map View Design.md`; steps in `BACKLOG.md` (Modern look).

## 2026-11-25 — Docs brought up to date; the backlog reviewed and prioritized

- The author: bring the user guide, the development log and especially the backlog up to date, then
  prioritize. `BACKLOG.md` rewritten in full: a proposed order at the top (a green Mac build, the
  Form layout bug, the Modern look controls, the Lite release, Enterprise data, rules in FB), what
  waits on the author, one "Verify on a Mac" list for everything built since the last build, and
  every area's open items. Fixed on the way: ORDER BY was still open (done: `AddOrderToQuery`);
  the old "ALS edition" section merged into Enterprise (relationships now come from models.py);
  the diagram's "relationships from /metadata" (it has none) dropped; Open Project is ⌘O; the
  bundled-runtime check dropped (the runtime is in the workspace now). `IN` with one `?` per value
  is still open.
- `ROADMAP.md`: Phase 2 is the Modern look; Phase 4 (Enterprise) started, licensing still parked.
  `USER_GUIDE.md`: the pill buttons (§12), what is not built yet (§18). `DOC_ONE_PAGER.md`: an ALS
  project is opened from its folder, file or repository. Commit hashes added to the last entries.

## 2026-11-25 — Pill buttons; the Modern look backlog (`c36220b`)

- The author: a modern Mac look with pill-shaped buttons, and a backlog for the UI transformation
  (toggle switch, combo box, date / time display, calendar picker, colour picker for generated
  apps) - `BACKLOG.md`, Modern look.
- `Pill Buttons.incl` (the Studio and the runtime, identical): AppKit's capsule border shape on
  macOS 26 (`ButtonSetBorderShape`, found in FB's headers as macOS 26.0+); on macOS 15, the
  project's minimum, the property does not exist, so the layer draws the same shape. Works on XIB
  buttons as on code-made ones (found by tag). The Studio's push buttons; the generated app's
  footer and Log In (`gThemePillButtons` in Theme.incl). `features/PILL_BUTTONS_FEATURE.md`.

## 2026-11-25 — Open ALS Project: a project from the model API Logic Server generated (`e909058`)

- *Project > New Project from API Logic Server…* (⇧⌘N) and **API Logic Server Project…** on New
  Project open `ALSProjectView.xib`: an ALS project's folder, its model file or a public GitHub
  repository - typed, chosen (Folder…, Model File…) or dropped. Create keeps a copy in
  `<project>/ALS Model/` and opens the project from it; `Project.json` gets `alsSource` and
  `edition: enterprise`. `features/ALS_PROJECT_FEATURE.md`.
- The drop zone: the author pointed out FB's translator writes the subclass code, so only its own
  classes exist - made in code with `subclass view` over the XIB's box, not a class name in the XIB.
- `ALS Model.incl` moved to `src/Generator/` (the Studio reads ALS models); `ALS Project.incl`
  (finding, GitHub, the copy, the ALS model -> the Studio's with lookups); `LoadALSModel`;
  App Generator treats `.py` / `.yaml` sources as no database (Generate App: Enterprise).
- Learned from the public repositories: `ApiLogicServer/demo`'s models.py writes
  `class X(SAFRSBaseX, Base):` and trailing `# comments`; the reader (FB and reference) takes both.
  Its admin.yaml lists 11 relationships, models.py 26 including all 11: models.py first.
  `ApiLogicServer/basic_demo` and `demo` read over raw.githubusercontent.com from here.
- `tools/als_project_reference.py` (25 checks) in `run_tests.sh`; String(15) now VARCHAR(15).

## 2026-11-25 — The ALS model from database/models.py, parsed as text (`dedb93b`)

- In the sandbox: `ApiLogicServer create` (17.05.44) on Northwind and on the CRM's contacts.sqlite.
  Both projects have the model only in `database/models.py` (no `app_model.yaml`): the same file in
  the same place whatever the database.
- The author: the Studio parses models.py; no Python interpreter inside FutureBasic.
  `tools/models_py_reference.py` reads it line by line, as the FB port does, and its test imports
  the same file with SQLAlchemy and compares every class, table, attribute, key and relationship:
  Northwind (17 classes) and CRM (3) equal. Learned on the way: `back_populates` names are not
  unique (Customer, Employee and Location each have an `OrderList`), so a to-many's key columns come
  from the child's to-one that points back by name *and* class; composite keys only in
  `ForeignKeyConstraint` (Order -> Location by Country, City); `Table(...)` blocks are views.
- `src/Enterprise/ALS Model.incl`: `ALSModelFromModelsPy` (the port), `ALSModelFromText` (models.py
  or YAML, by contents, so a dropped file works whatever its name); `ALSModelFromURL` uses it. The
  model is keyed by resource, like admin.yaml's. fblint clean; FB-type names avoided (`single`).
- `run_tests.sh`: the reader vs SQLAlchemy when `ALS_PROJECTS` and `ALS_PYTHON` are set.

## 2026-11-25 — The JSON:API side in FB; the ALS model from app_model.yaml

- The author: `app_model.yaml` is the model source (not admin.yaml). Found: ALS 17.04+ (17.05 here)
  no longer writes it (`app-create` is gone); the C++ Studio reads it with a line-by-line reader
  and its notes say the same; its onboarding guide ranks `models.py` first. So one reader for both
  layouts (`entities/columns/primary_key/favorite` and `resources/attributes/user_key`), preferring
  `app_model.yaml`; checked against PyYAML on the live server's admin.yaml and on the C++ Studio's
  app_model.yaml sample (primary keys, display column).
- `src/Enterprise/ALS Model.incl` and `src/Enterprise/DataObject_JSONAPI.incl`: the FB port of the
  reference (19 checks). FB has no `continue`: the reader handles one line per call, state in
  globals. fblint caught `record` (an FB keyword).
- `run_tests.sh`: the side-by-side test when `ALS_DB` names the server's db.sqlite.

## 2026-11-25 — The SQL Generator's JSON:API side (reference), ORDER BY, the ALS model's relationships

- `AddOrderToQuery` (ORDER BY) in the shared SQL Generator - all three copies (runtime, example,
  *TXV*); the example's first query uses it instead of SQL added by hand.
- `tools/jsonapi_reference.py`: the same statement dictionaries -> SQL or a JSON:API request
  (filters as the JSON list, OR on one column as `in`, sort, a join to a parent as `include=` with
  inner-join rows, POST / PATCH with `S_CheckSum` / DELETE by the record's id). 17 checks: every
  query run both ways (SQL on the server's db.sqlite, JSON:API on the server) gives the same rows;
  writes through JSON:API read back through SQL; OR across columns, filters on a parent and an
  UPDATE without a key are refused.
- The author: "ALS does give relationships" - right: `/metadata` leaves them out on purpose, but
  `/ui/admin/admin.yaml` (no auth) has them (`tab_groups`: direction, name, resource, fks; role
  names; composite keys) and `user_key` (a lookup's display column). The reference reads it with a
  YAML-subset reader checked against PyYAML; relationship names are never guessed.
- Resource names are not table names (Northwind: Category -> CategoryTableNameTest).

## 2026-11-25 — ALS filters measured; the JSON:API side of the SQL Generator (design)

- The author: the Enterprise edition should use the SQL Generator's own dictionaries and arrays and
  write JSON:API requests instead of SQL, from the ALS model the Studio already reads.
- Filters measured (`als_contract.py`, now 25 checks; `design/ALS Contract.md` -> Filters): only the
  JSON list `filter=[{"name","op","val"}]` is reliable; ops eq ne lt le gt ge like ilike notilike in
  notin; null with eq / ne is IS NULL / IS NOT NULL; filters AND together (ALS's SAFRSBaseX); no OR
  (`{"or":...}` refused, OR on one column is `in`); `filter[attr][op]=val` is SILENTLY IGNORED (0 rows).
- The C++/Wt Studio's ApiClient (imagery-logicbank-studio, read-only here) agrees: it uses `include=`
  for parents and notes that `filter[x]=null` matches the text "null".

## 2026-11-25 — Enterprise: the API Logic Server contract, measured

The author: start on API Logic Server now (multi-user, three tiers); Enterprise code in this
repository for now; a real ALS in the cloud session for tests.
- API Logic Server 17.05.44 installed in a scratch venv; the Northwind sample with SQL security
  and credit-limit rules, run with `SECURITY_ENABLED=true`.
- `tools/als_contract.py` (18 checks) and `docs/design/ALS Contract.md`. Found:
  - `links.next` comes one page short (830 rows, pages of 200: offset 600 has no next) - page by
    offset until `meta.total`;
  - an update's answer carries the OLD `S_CheckSum` - read the record again before the next save,
    or it is refused as "row altered by another user";
  - a rule's message is `errors[0].title`; `detail` is a dictionary;
  - a wrong password is a bare JSON string (needs fragments allowed); a non-token is 422.
- `ALS Client.incl` fixed for all four: `ALSErrorMessage` (title first, msg, bare strings),
  `ALSNeedsSignIn` (401 / 422), `ALSListPage` + `ALSResponseTotal`, `ALSGet`, fragments allowed.
- `run_tests.sh` runs the contract when a server answers on localhost:5656.
- Backlog: the Enterprise steps; Kafka (through ALS first - the author already does this - then a
  plain-HTTP module for Kafka's REST Proxy and Redis).

## 2026-11-25 — The SQL Generator as a shared module: an example project for the FB list

The author wants to share the SQL Generator (the DataObject query builder) on the FutureBasic
list, open source (MIT), as an example app built from `src/CleanApp`.
- `src/SQLGeneratorExample/`: the module; `SQL Generator SQLite.incl` (a runner, our own SQLite
  declarations, `SQLGen` prefix); `CRM Database.incl` (person / address / contact, five made-up
  people inserted through the builder); ten examples (`CRM Examples.incl`, the FB each shows in
  `Example Code.txt`); output in colour with results as a SQL command line prints them (`sqlite>`
  prompt, Menlo, `+---+` tables, "n rows in set", "Query OK"); a Help window with the user guide
  (`User Guide.txt` in simple markup -> `Rich Text.incl`, system colours for light and dark);
  About box (`Credits.rtf`); README, LICENSE (MIT), ANNOUNCEMENT (draft post).
- Module changes, in all three copies (runtime, example, *TXV* 2293f73): joins fixed (the
  `associations` entry was a dictionary used as an array: the first join would have crashed,
  `-[__NSDictionaryM addObject:]`; nothing had used joins yet); INSERT of an array of dictionaries
  (author): `InitInsertRowsDictionary`, `AddRowsToInsert`, `SetInsertColumns`,
  `GenerateInsertRowsSQL`, rows in `QueryParameterValues`; MIT headers; unused leftovers removed.
- `tools/make_sql_generator_svg.py` -> `docs/design/SQL Generator Object Model.svg` (the
  dictionaries and arrays a statement is described with; author's idea), in the user guide (17)
  and the example's README. `run_tests.sh` checks the three copies are identical.
- `src/CleanApp`: the Hello function, button, label and menu removed (author).
- fblint caught `line` (an FB keyword), `for ... in` over a function call, and
  `FileManagerURLForDirectory` called with five arguments (it takes two).

## 2026-11-25 — One-pager: "app builder" (author)

- The Studio is introduced as "An app builder that runs on your Mac" instead of "A generator"
  (author: say app builder where it says generator). The SQL Generator keeps its name (it builds
  SQL, not apps); its paragraph says "It writes the SQL". PDF reprinted, page republished.

## 2026-11-24 — One-pager: the SQL Generator (author)

- `docs/DOC_ONE_PAGER.md` / `.html` / `.pdf`: a section on the SQL Generator (the DataObject
  query builder): FB code describing a two-table query with a join and a filter, the exact SQL
  `GenerateSelectSQL` writes for it (quoted names, `?` placeholders, the values apart), and what it
  guarantees: SELECT / INSERT / UPDATE / DELETE, parameterized, names quoted, no UPDATE or DELETE
  without a filter. "Data, done properly" names it. PDF reprinted (still two pages); the published
  page republished (new link: https://claude.ai/artifact/4h8NeeASNMggnnztHuicky).

## 2026-11-24 — Crumb trail rebuilt from buttons

- The `NSPathControl` trail highlighted when clicked but did nothing (author): the item handed
  back by `PathControlClickedPathItem` is most likely not the object we stored, so the action was
  never found. Replaced with up to four borderless buttons (symbol and title, sized to fit,
  `_crumbButtonBase` 611-614) and chevron image views between them (621-623), made once in
  `BuildSubViews` and titled, placed and shown by `StudioUpdateCrumbs`; the last crumb is bold.
  Clicks are `_btnClick` -> `StudioCrumbClicked` (EventHandlers.incl, logged). The square-icon
  workaround (`StudioCrumbImage`) went with the path control: a button keeps a symbol's proportions.

## 2026-11-24 — Crumb icons kept square; the entity line's placeholder

- The path control draws each item's image in a square, so SF Symbols were squeezed (author's
  screenshot). `StudioCrumbImage` draws the symbol centred in a 16-point square, proportions kept
  (`ImageWithSize`, `ImageLockFocus`, `ImageDrawInRect`), as a template image.
- With a project open and no entity chosen, the summary line showed the XIB's placeholder
  "an object"; it now says "Choose an entity in the Objects list" (`StudioUpdateCommands`).

## 2026-11-24 — The Studio's crumb trail (author: "a way to navigate back to the Project screen")

- `Menus.incl`: `StudioUpdateCrumbs` builds an `NSPathControl` trail from the visible view and the
  state (Projects › project › entity or Settings; › New Project; › API Logic Server), keeping an
  action beside each item (`gStudioCrumbActions`); `StudioCrumbAction` reads the clicked one
  (`PathControlClickedPathItem`, `_btnClick`). Projects -> the Projects screen, the project -> its
  entity definitions.
- `Windows.incl`: the trail at the top of the page area, the heading moved down under it
  (`_crumbTrailHeight`; `_pageHeadingHeight` 60 -> 86 so the pages start below both).
- A "< Projects" button beside the heading was written first and replaced by the trail before
  committing (the author's suggestion).

## 2026-11-24 — Keyboard shortcuts for the Studio's commands (author)

- `Menus.incl`: ⌘1 Recent Projects, ⌘2 Entity Definitions (a new Project menu item, the
  toolbar's Entities), ⌥⌘R Show Project in Finder, ⌥⌘I / ⌥⌘E Import / Export Rules, ⌥⌘G Show
  Generated App, ⌥⌘U Update Runtime and Templates, ⇧⌘K Show Workspace; the option-command ones
  through the `menu` statement's modifier mask. Delete Project has none on purpose. Toolbar
  tooltips name the shortcut (in words: no new non-ASCII string literals).

## 2026-11-24 — Studio review step 1: menus, toolbar, commands enabled by state

- `Menus.incl` (moved before the other includes so every file can call it): Project / Edit /
  Model / Generate / Window / Help; `StudioUpdateCommands` enables each menu item, toolbar item
  and design popup from the state - a project, an entity selected (the Generate XIB item names
  it), an attribute selected, a project selected in Recent Projects (Delete). Called at launch,
  after every menu command, toolbar click and button, on table selection, when a model loads,
  on Close and Delete.
- `Toolbar.xib`: Projects, Entities, Diagram, Generate, Settings (tags 600-604, handled in
  `_toolbarItemClick`); the old items were never implemented (author: they came from
  Test_Xib_View) and shared tags with view controls.
- New commands: New Project (⌘N), Close Project (⇧⌘W, `ProjectClose`, sharing
  `ProjectResetToEmpty` with Delete), Show Project / Generated App / Workspace in Finder, Help
  (the user guide from the repository, else GitHub). The ALS form's Cancel works.
- Open One Xib is behind `STUDIO_DEBUG_MENU` (off). Docs follow the new menus.

## 2026-11-24 — Studio review: inventory and proposal

- `docs/STUDIO_REVIEW.md`: every toolbar item, menu item and view control, with its status.
  Found: the toolbar is dead (no `_toolbarItemClick` handler) and its tags collide with view
  controls (205 = the ALS form's Cancel, 303 = the tag-line field); Preferences and Help are
  empty; the ALS form's Cancel and the Objects list's + / − do nothing; nothing is ever disabled.
- Proposal: Project / Model / Generate / Window / Help menus, a state table for enabling,
  a five-item toolbar with its own tag range, context menus on the Objects list, the attribute
  table and Recent Projects. Waiting for the author's answers before changing anything.
- FB facts for the work: `_toolbarItemClick` (Toolbar.incl), `ToolbarItemSetEnabled`,
  `MenuSetAutoenablesItems` / `MenuItemSetEnabled`, a context menu is a `menu` not in the menu bar
  attached with `ResponderSetMenu` / `ViewSetMenu` (FBExamples, View Contextual Menu).
- Users and roles for generated apps (author) added to the backlog.

## 2026-11-24 — Form designer 3: Dropdowns, radio buttons, value lists; the Form layout popup

- `SQLite Model.incl` (and `tools/sqlite_model.py`): a single-column foreign key gets
  `lookup` { entity, key, display }; `SQLiteModelDisplayAttribute` picks the column to show.
  contacts.sqlite: `address.personID` and `contact.personID` look up `person` showing `givenName`.
- `Type Mapping.incl`: `_xibKindRadio`, `_xibKindDropdown`; a lookup recommends Dropdown;
  `TypeMapAttributeValues` (the Values column), fallbacks when a choice has nothing to offer;
  the Values column shows a lookup as `→ person.givenName`.
- `XIB Generator.incl`: an empty `popUpButton`; radio groups in their own view (side by side or
  stacked); heights per attribute (`XibFormFieldHeight`); Model.json fields carry `values` / `lookup`.
- `Binding Generator.incl`: Choice and Radio show / take; `<Entity>FormSetUp`, `<Entity>Lookups`,
  `<Entity>FillLookup`.
- Runtime: `Binding Support.incl` choices (keys per tag, the wanted value kept for late rows,
  radio tags and exclusivity); `App Data Lite.incl` `AppDataLookup` -> `_appDataLookup`.
- App Pages: lookups requested when a page is shown, filled on the answer; value lists set up
  when the page is built; radio clicks handled first in AppPagesDoDialog.
- The Studio: the Values column in the attribute table (ProjectDetailView.xib).
- Form layout popup (author: "pops back to automatic and never sets"): cause not found by
  reading; the choice now logs the item and the entity, and the popup is redrawn from what was
  stored - the log will show where it is lost.
- fblint caught `text` (an FB keyword) as a variable name.

## 2026-11-24 — App and entity icons; a larger app name centred on the icon

The author asked for the app's name in larger type, centred up and down beside the icon, and
for the developer to choose icons for the app and for each entity.
- App Shell: the name is 24-point bold, centred on the 52-point icon (with a tag-line, the two
  lines together); a picture icon also becomes the Dock / About box icon (`AppSetIconImage`);
  `ShellSetAppSymbol` puts the chosen SF Symbol in the header when there is no picture.
- Type Mapping: `TypeMapIconChoices` (33 SF Symbols), `TypeMapRecommendedIcon` (moved from App
  Generator's `AppNavSymbol`), `TypeMapEntityIcon` (designer's choice first). Model.json carries
  each entity's `icon`; App Pages.incl uses it for the navigation button and defines `APP_SYMBOL`.
- The Studio: the entity view has a design row under its summary - Control, Form layout, Icon
  (with a preview); Project Settings' well is now the *app icon*, with a symbol popup and preview
  for apps without a picture (`appSymbol` in Project.json).
- fblint again caught functions used before their definition (Project Workspace builds before
  Project Settings); moved.

## 2026-11-24 — Form designer 2: time and date-and-time pickers, the Control popup; nav heading

- `Type Mapping.incl`: `_xibKindTime`, `_xibKindDateTime` ("Time picker", "Date and time picker");
  DATETIME / TIMESTAMP recommend the date and time picker, TIME the time picker;
  `TypeMapRecommendedKind` (before the designer's choice), `TypeMapControlKinds` (the popup's order).
- `XIB Generator.incl`: one date-picker writer for the three, with their `datePickerElements`.
- `Binding Support.incl` (runtime): `BindingShowTime` / `BindingTakeTime`, `BindingShowDateTime` /
  `BindingTakeDateTime`; formatters are en_US_POSIX so a user's region never changes stored digits.
- The Studio: the **Control** popup in the entity view (`_controlPopup`): its items are rebuilt
  for the selected attribute, the first naming the recommendation; `DesignSetAttributeValue` is
  shared with cell editing and keeps the row selected.
- App shell: a **Business Objects** heading above the entity buttons (author), coloured by
  `gThemeNavHeadingText` (Theme.incl template; NULL falls back to the buttons' colour).
- fblint caught `DisplayAttributeControl` called before its definition; moved up.

## 2026-11-24 — Navigation items at the top of the bar (second fix)

- The flipped scroll-view document (78be389) still left the navigation buttons at the bottom on
  the author's Mac. Replaced: no scroll view, no flipped view. The buttons and the highlight are
  placed in the window, measured from the navigation bar's top edge (`ShellNavItemY`), with a fixed
  top margin (`NSViewMinYMargin`), the plain Cocoa way. A model with more entities than the bar's
  height holds needs scrolling again later (BACKLOG).

## 2026-11-24 — Generated app builds without warnings

- clang warned about five unused variables in `DataObject.incl` (`selectfilterArrayRef`,
  `filterDictionaryRef`, `sqlFilterCount`, `columnLogic`, `aLogic`): names in the `local mode` dims
  before `GenerateSelectSQL` that it never uses (the filter code has its own locals). Removed from
  both copies, which stay identical: here and *TXV* 32cfa32.

## 2026-11-24 — Form designer 1: layout columns, Hidden, read-only keys

The author asked for a richer Form designer: 1 / 2 / 3-column forms, hidden fields, read-only
keys, and widgets (time, date-and-time, checkbox, radio buttons, dropdowns from lookup tables or
value lists). Split into three features (BACKLOG, *Form designer*); this is the first.
- `Type Mapping.incl`: kinds `_xibKindReadOnly`, `_xibKindHidden` ("Read-only text", "Hidden" in
  the Form Control column); a key the database generates is read-only by default;
  `TypeMapFormColumns` (designer's choice or automatic), `TypeMapShownAttributes`.
- `SQLite Model.incl` (and `tools/sqlite_model.py`): `"generated"` on the key column of an
  identity / autoincrement table.
- `XIB Generator.incl`: the Form lays out in 1-3 columns, labels as wide as the longest title,
  Hidden attributes left out (tags keep model order), read-only fields without a bezel; the List
  has no column for a Hidden attribute.
- `Binding Generator.incl`: no code for Hidden fields; read-only fields are shown, not read back.
- The Studio: a *Form layout* popup in the entity view (`Windows.incl`, `DesignFormColumnsChosen`),
  saved under `"@entity"` in `Design.json` (`DesignSave` / `DesignLoad`).
- An assigned key (typed by the user, e.g. a customer code) stays editable: a new record needs it.

## 2026-11-24 — First generated app runs: navigation, fields, list

The author's Northwind app built and ran (Address page). Three cosmetic faults, fixed:
- **Navigation buttons at the bottom, on top of each other** (`App Shell.incl`). The flipped
  navigation document was shorter than its scroll view, so it sat at the bottom; and FB's
  buttons keep a flexible top margin, so each time the document grew for a new button the
  earlier ones moved down onto it. Now the document is at least the scroll view's height and
  grows with it, and buttons and the highlight have a fixed top margin (`NSViewMaxYMargin` in a
  flipped view).
- **Every text field a 90-point text area** (`Type Mapping.incl`): SQLite declares every string
  `TEXT`, which mapped to a text area. `TEXT` is now a one-line field (280 wide); CLOB / MEDIUMTEXT /
  LONGTEXT stay text areas, and the designer can still choose Text area per attribute.
- **The list's first row under its header** (generated `<Entity> Binding.incl`): the list view is
  resized when the page is laid out and kept its old scroll position; `<Entity>RecordsToList` now
  scrolls to the first row after reloading.
- Answered: the pages are XIBs (`<Entity>Form.xib`, `<Entity>List.xib`, loaded with `nibview`);
  the frame around them (navigation, header, footer) is built in code by `App Shell.incl`.

## 2026-11-24 — Generated apps always get the Studio's own runtime

- The generated app crashed again in `DataExecute` ("index 0 beyond bounds for empty array"):
  the fix (23ced18) was in the repository, but not in the app. *Update Runtime and Templates*
  copied from the **remembered** folder (`Studio Library.json`), which after the bisect pointed at
  an older clone; Generate App copied only when the workspace had no runtime at all.
- Now (`Studio Library.incl`): when the Studio runs from the repository it was built in,
  `StudioLibraryReady` copies `src/Runtime` and `src/Templates` from there on every Generate App
  (and at launch); *Update Runtime and Templates* also tries that repository first. The
  remembered folder and the folder panel are only for a Studio that is not inside a repository.
- Learned: a cache of our own code must never be preferred over the source the Studio was built
  from; during development the two drift as soon as the author switches clones.

## 2026-11-24 — Delete Project

- *Model > Delete Project…* (`ProjectDelete`, Project Actions.incl): the open project, or the one
  selected in Recent Projects, after a confirmation, to the Trash (`FileManagerTrashItemAtURL`);
  its Recent Projects entries removed; the Studio back to an empty Welcome page.

---

## 2026-11-24 — The first generated app builds and runs: an unsigned loop bound

- The author generated an app (from Test_Xib_View's contacts database), opened it in FB, built it:
  it compiled. At launch it stopped in `DataExecute` (`index 0 beyond bounds for empty array`):
  `for i = 0 to fn ArrayCount( params ) - 1` with no parameters - `ArrayCount` is unsigned, so
  `0 - 1` wraps and the loop runs. Eight such loops (runtime, Studio, logic engine) now cast to
  `long`; `fblint` reports the uncast form; `FB Coding Rules.md` records it.

---

## 2026-11-24 — The Studio's folder takes the product's name

- The Studio builds and launches again (the author's screenshot: the first-launch prompt for the
  runtime and templates). The author: the location is `~/Library/Application Support/Imagery
  LogicBank Studio for FutureBasic`. `APP_SUPPORT_FOLDER_NAME` changed; on first launch an existing
  `Api_Logic_Client` folder is moved over, and the paths in `Recent Projects.json` and each
  `Project.json` are rewritten (plain and JSON-escaped). Generated apps take the new path on their
  next Generate App.
- FB: `Redefined variable … projectFolderURL` — a local named like a global (FB forbids it).
  Renamed; `fblint` now reports a local that redeclares a global of the same project.
- The Studio builds and launches; the open panel was read as asking for a place in `~/Library`
  (hidden). It asked for the repository. Now the Studio finds the repository itself from its own
  app's location (FB builds it in `src/Generator`) and copies without asking; the panel remains a
  fallback, with clearer words. The Application Support folders are created as needed.
- Welcome view: the logo and the heading drifted apart in a wide window (both floated with
  flexible margins). The logo is anchored left; the heading and subtitle start beside it and stretch.

---

## 2026-11-24 — The crash is gone; FutureBasic 7.0.38's own errors fixed

- With the folder resources off the build list (the Xcode project last), FutureBasic translates the
  Studio again: no crash. Its errors: `width` used as a variable (an FB keyword); the newer type
  names `URLRef`, `StringRef`, `DataRef`, `DictionaryRef`, `ArrayRef` unknown in FB 7.0.38; a `…` in
  a string literal.
- Fixed: `colWidth` in XIB Generator; every FB source (Studio, runtime, templates, generated code,
  the FB logic test, Test_Xib_View) back to the CF names; the alert's `Locate...`. `fblint` now
  reports the newer names and `width`. Learned: FutureBasic_Documentation's headers are newer than
  the author's FB — a name the linter accepts can still be unknown to the translator.

---

## 2026-11-24 — Runtime and templates in the workspace, not the Studio's bundle

- The headers change (below) did not stop the crash. What every crashing version shares: the
  project listed two real folders outside the project as resources (`../Runtime`, `../Templates`,
  added 16 Nov), something FB's project model (pseudo-folder groups, file items) does not have.
- The author: they live in the workspace, not the bundle. `Studio Library.incl`: `workspace/Runtime`
  and `workspace/Templates`, copied from the repository folder (chosen once, remembered in
  `Studio Library.json`) the first time they are needed; *Model > Update Runtime and Templates*.
  Generation and the ERD read from there. The Studio's project lists neither folder.
- Still listed: `Api_Logic_Client.xcodeproj` (the author's, a folder too) — the next suspect if FB
  still crashes.
- It still crashed; `Api_Logic_Client.xcodeproj` (listed since the first commit, used by nothing in
  the Studio) is taken off the build list, so the project lists only files, like a fresh FB project.

---

## 2026-11-24 — The FB crash (not the cause): FB headers listed as project items

- Bisecting in a fresh clone (the author's builds): every commit crashed, the 16 Nov one included;
  so not a code change — the clone lacks something. The Studio's `data.fbproj` listed FB's own
  headers (`Tlbx XML.incl`, `NSLog.incl`) as project items; FB looks for them beside the project,
  finds nothing, and its translator scans a null text (the crash report's instruction bytes: a byte
  read at 0 followed by character comparisons). FB's examples include them from source instead.
- Fixed: the Studio's Headers group is empty and `My Globals.glbl` includes both headers; generated
  apps and the FB logic test get an `App Headers.incl` that includes `NSLog.incl`. `fblint` reports
  any project item that is not beside the project. `FB Coding Rules.md` rule 9.
- The earlier SDK and tools changes stay (they match a fresh FB project and the no-Python rule).

---

## 2026-11-24 — FutureBasic crashed building the Studio: the SDK in the build settings

- The author's build of the Studio crashed FutureBasic 7.0.38 itself (a null read after a path,
  `NSPathStore2`). A fresh project from the FB editor (`src/CleanApp`, added by the author) builds;
  comparing the two: our `Settings2.plist` asked for `BaseSDK` 13.1 (and Intel, macOS 10.13, a
  precompiled header, an old `-m64 -DDECARBONATE` option); the clean one has 26.2, Apple Silicon,
  macOS 15.0. The 13.1 SDK is no longer in current Xcode — the likely cause, and why the same
  project built on 2026-11-16.
- Fixed in the Studio's project, the generated apps' template (`src/Templates/Project/`, also used
  by the FB logic test) and Test_Xib_View (*TXV* `6fa70e2`); our `-lsqlite3` options kept.
- `.gitignore`: every project's `build_temp_*/` and `*.app/`.
- Learned: keep project settings like a fresh FB project (`FB Coding Rules.md` rule 8).
- The SDK fix did not stop the crash (same place in FutureBasic). Next: the `tools` folder
  resource (new since the last good build: `.py`, `.sh`, a local `__pycache__`). The author: no
  Python in anything FB builds. Rules Bridge.incl no longer runs `python3`; Import / Export say
  "coming" and Generate App writes an empty `Studio Rules.incl` until the FB port. Commits
  `d6df05e` (tools by name) and the follow-up removing them.

---

## 2026-11-24 — Editions: the Lite data interface; Enterprise on the roadmap

- Two editions (author): **Lite**, free and open source, SQLite in the app; **Enterprise**, paid,
  three-tier over API Logic Server (open source, the same in both). Lite ships first; Enterprise is
  roadmap (`design/Editions and Licensing.md`). Commits `b9c6565` and the docs follow-up.
- Runtime: `App Data Lite.incl`, the app's data interface (`AppDataList`, `AppDataSave`,
  `AppDataRemove`, `AppDataLogin`, `AppDataKeyValues`), answering through one handler so an
  asynchronous server can sit behind the same calls. `App Shell.incl`: footer status line and page
  actions (New, Save, Delete, Refresh), Records menu numbers, `ShellDoAppEvent`, `ShellShowLogin`.
- Generator: `Edition.incl` (Lite-only hook the paid build replaces); `App Pages.incl` now drives
  the actions through App Data (saves through the rules; a refused save shows the rule's message);
  templates no longer call the old ALS runtime, which is no longer copied into apps; an ALS-sourced
  project is refused for Generate App with the way to a Lite app.
- `tools/check_app_pages.py` (test only): plays `AppPagesSource` for two entities and lints the
  output with the runtime and templates; in `run_tests.sh`.
- Licensing: decided offline and Studio-only; the check itself is open. Found in the License
  Server: keys use C++ `std::hash` (not the same on a Mac) and a published salt, so the FB Studio
  cannot verify them as they are. Options written up: portable checksum, signed licence file,
  online activation.
- `docs/LINKEDIN_POST.md`: the post, kept with the one-pager.

---

## 2026-11-24 — One-pager

- `docs/DOC_ONE_PAGER.md`: what the Studio is, for the FB community — how it works, what a
  generated app has, rules declared once (with what one save does), what stays yours, needs and
  status. Also published as a designed page (claude.ai artifact) with the same text.
- The big picture added (data model → Studio → FutureBasic project → Mac app, and the loop back
  to the database through the rules); the page widened to fill the screen and made responsive.
- `docs/DOC_ONE_PAGER.html` (the page, standalone) and `docs/DOC_ONE_PAGER.pdf` (two Letter pages,
  printed from it with headless Chromium) for sharing.

---

## 2026-11-24 — Model diagram: an interactive ERD with the rules on it

- *Model → Show Model Diagram* (⇧⌘D): `ERD Generator.incl` (FB) fills
  `Templates/ERD/Model ERD.html` with the model as the generator holds it and the project's
  `Rules.json`, writes `<project>/Model ERD.html` and opens it.
- The page: crow's-foot ERD with PK / FK markers, optional relationships dashed, self
  relationships looped; rule symbols (ƒ Σ # ⇣ ! ✓ ⚡ ⊘), faded when switched off; drag, open /
  close, select (relationships highlighted, side panel with rules, parents, children,
  attributes), find, zoom and pan, Arrange, five themes, Export SVG; state kept per project.
- `tools/check_erd_page.py` (test only) fills the page the same way and drives it in headless
  Chromium; added to `run_tests.sh`.
- Decision (author): the Studio's tools are FutureBasic, not Python. A first Python generator for
  the diagram was dropped before commit; `rules_bridge.py` is now a backlog item to port.
- Northwind has no foreign key from Product to Supplier, so Supplier stands alone in the diagram —
  the diagram shows the database as it is.

---

## 2026-11-24 — App shell: a common look for generated apps; branding in the Studio

- `src/Runtime/App Shell.incl`: the frame of every generated (SQLite) app, built in code from
  FB's per-control functions — a dark blue navigation bar of white, bold, icon buttons; a header
  with the logo, app name, tag-line, theme menu (System / Light / Dark) and Log In; a footer with
  the copyright; pages in a content view. `ShellDoDialog` handles navigation and the theme menu.
- Templates: `Theme.incl` (yours: `ApplyTheme`, the colours); `EventHandlers.incl` rewritten with
  developer notes, routing `ShellDoDialog` → `AppPagesDoDialog` → `DoLogin` → `ALSDoDialog`.
- Generator: `App Pages.incl` (a page per entity: `nibview` List and Form into `_shellContent`,
  `ShellAddNavItem` with an SF Symbol picked from the entity's name, `AppPageShown` fills the List
  with `DataFetch`, a row fills the Form); `Windows.incl` for SQLite projects builds the shell;
  `README.md` in `FBapp/` tours the project; the project file gains Pages, `Theme.incl`, `AppLogo.png`.
- Studio: Project Settings has a logo well (paste / drag → `<project>/Branding/logo.png`), a
  tag-line (≤ 80) and a copyright, saved in `Project.json`. An Edit menu (`editmenu`) so Paste
  works; Generate XIBs moved from ⌘X to ⇧⌘X.
- `fblint`: a template may declare fns the generator writes beside it (`// generated: Name`).
- Learned: generated code is read by FB developers who never saw the generator — each file now
  says what it is, whether it is regenerated, and where your own code goes.

---

## 2026-11-24 — User guide: FutureBasic's nib keywords

- New §9 "Screens: FutureBasic's nib keywords": `nibwindow`, `nibview` (with `identifier`,
  `origin`, `superviewTag`), `nibtoolbar`, `nibmenu`, `nibpopover`, each linked to FutureBasic's
  reference page; the generated `Windows.incl` and the generator's own calls as examples; what
  to know (tags, names, embedding with `superviewTag`, bottom-left origins, load once).
  Later sections renumbered.

---
