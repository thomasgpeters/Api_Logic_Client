# Backlog

Open items and ideas, grouped by area, with a proposed order at the top. The phase plan is in
`ROADMAP.md`; what was done and learned is in `DEVELOPMENT_LOG.md`; each feature's page is in
`features/`. Reviewed in full on 2026-11-25.

## Priorities (proposal, 2026-11-25 - the author decides)

1. **Generate an app and build it** (the author built Studio for FB and the SQL Generator example on 2026-11-25:
   the build bugs were fixed together and both came up). Still to do on the Mac: generate an app with Studio for FB
   - Telecom or Customs, which bring their business rules - build it and run it; and build again to take in what
   landed after that build (the rename to `src/AppBuilder/Studio for FB.fbeproj`, value lists with codes, the record
   popover, the example's Help window).
2. **The open bug:** the Form layout popup "pops back to automatic" (needs the log lines below).
3. **Modern look controls** for generated Forms (the author's current interest): toggle switch,
   combo box, date / time display, calendar picker, colour picker. Each follows the Form
   designer's pattern (Control popup -> XIB part -> binding), so they are small and independent.
   Then the **Map view** (any result set with latitude / longitude on a map, an entity first; a bigger piece: a generic map part, then filling the columns by geocoding).
4. **Lite release:** a generated app builds and runs on a Mac; tag it. Then post the SQL Generator
   to the FB list.
5. **Professional data:** `App Data Professional.incl` and the connection / sign-in, so an ALS project
   generates a working three-tier app.
6. **Rules in FB:** the port of `rules_bridge.py` (Rules.json check, Studio Rules.incl), then the
   Rules page.
7. Then the Studio review (context menus), the generated app's toolbar, window layouts, users and
   roles.

## Web Toolkit for FutureBasic (`docs/features/WEB_TOOLKIT_FEATURE.md`)

- [x] The module: FastCGI server, sessions, widgets, rendering, events (AJAX), the page lifecycle, optional binding
      through LogicBank for FutureBasic, `web.js`, themes; the app template; the Orders example (2026-11-26).
- [ ] **On a Mac:** build the template and the example; run them behind nginx; send the Build Log.
- [x] **XIB files as page templates** (2026-11-26): `WebLoadLayout` (`Web Layout.incl`), the rules in
      `tools/web_layout_reference.py`, the Objective-C tested with GNUstep; the Orders example laid out in three `.webxib`.
- [x] **The layout tool** (2026-11-26): `src/WebToolkit/Layout Tool/Layout Tool.html` - design, web preview, FB code,
      saving `.xib` and `.webxib`; tested in Chromium.
- [ ] **On a Mac:** FB copies `.webxib` resources unchanged; a XIB saved by the layout tool opens in Interface Builder.
- [ ] App Builder opens the layout tool on an entity's Form (a web view; saving into the project); the web target
      writes `.webxib` from the generated Form XIBs.
- [ ] Layouts: tab views, split views, a stack view as a row or column; a "fill" rule for full-width fields.
- [ ] **App Builder's target:** Desktop app or Web app; the web target generates `Pages.incl` (forms and tables per
      entity), `Web App.glbl`, the toolkit and `nginx.conf` from the model.
- [ ] Data through the SQL Generator (SQLite) in a web app, as in generated desktop apps (`Data Records.incl`).
- [ ] Server push (a long poll or WebSocket) for changes another visitor makes; for now: refresh on visible / shown.
- [ ] HTTPS without nginx (Apple's Network framework); sessions in SQLite for several app copies behind nginx.
- [ ] Widgets: tabs, a dialog, a date picker beyond the browser's, charts, a map; file upload and download.
- [x] Free (MIT), the third free module (author, 2026-11-26): its user guide, its page and downloads on the site, the
      About Imagery window in its example.
- [ ] The name ("Web Toolkit for FutureBasic" is a working name); its own public repository.
- [x] **Pricing decided** (author, 2026-11-26): Lite free; Professional on the company-wide tiers as developer seats
      (`docs/design/Licensing Design.md` -> Pricing); the web target is in Professional.
- [ ] The Licence window shows the licence's tier and seats; the License Server issues them (its L36).
- [ ] **Seats on the local network (Bonjour)** (author, 2026-11-26; `Licensing Design.md` -> Seats): copies with
      the same licence find each other. The newest copy past the seat count is read-only until resolved. Lite: one
      copy at a time.
- [ ] **Online activation per Mac:** the License Server refuses more Macs than seats, then App Builder works offline;
      "Release this Mac" frees a seat. Needs the License Server's endpoints (its L38).

## The generated app's look (author's first run, 2026-11-27)

- [ ] Records as tiles (`Record Tiles.incl`): the switch in each List card, three or four across, the name and details, a click shows the record in the Form; light and dark

- [x] Nav bar darker in dark mode; the working area apart from the Forms and Lists (cards on a backdrop); Forms and
      Lists across the full width with margins, the List's columns sharing it (`APP_SHELL_FEATURE.md`).
- [ ] **On the Mac:** generate again and build. `Theme.incl` is yours and is not overwritten, so to get the new
      colours, delete it before generating, or copy the new lines from `src/Templates/App/Theme.incl`.

## Waiting on the author

- [ ] **The page designer** (author, 2026-11-27, the "new layout manager"): pages composed from entities dropped from a
      palette, each shown as a List, a Detail or both, linked through the model's relationships (an Order with its
      customer and its lines on one page). Professional only. Design: `design/Page Designer Design.md`; phase 1 done (`tools/pages_reference.py`); next: the
      Pages view in the Studio (drag and drop, the sheet on drop).

- [ ] **Bug:** Form layout popup - choosing "3 columns" pops back to "automatic". Diagnostics are in
  (`DesignFormColumnsChosen`): the NSLog lines "Form layout popup: item …" and "Form layout of …"
- [ ] A crash seen in the Studio (2026-11-24): the author is trying to reproduce it
- [ ] Studio review: agree the generated app's toolbar (`STUDIO_REVIEW.md` 2.6)
- [ ] The Modern look: more controls and looks to add to the list
- [ ] Map view (backlogged; MapKit decided): run `src/MacTests/MapKit Points Test.fb`; location columns for Northwind's test data and their names; layer colours; the bubble's details and menu actions (`design/Map View Design.md`)
- [ ] Professional licensing option (A / B / C, see Parked)
- [ ] Proposal to Val Huber: percentage offer + the name "LogicBank for FutureBasic"

## Verify on a Mac - everything built since the last Mac build

The Studio
- [x] Generator builds and runs (2026-11-16); runs again after the 2026-11-24 fixes
- [ ] After the globals sweep (2026-11-27): the Studio, a generated app (Northwind), LogicBankExample (Story to the end), the Web Toolkit example and the SQL Generator example build and run without a crash
- [ ] Menus regrouped, commands enabled by project / entity / attribute, keyboard shortcuts (`USER_GUIDE.md` §16)
- [ ] Toolbar: Projects, Entities, Diagram, Generate, Settings; the crumb trail's buttons go back
- [ ] New Project: Choose… shows the tables; Create opens the definitions
- [ ] API Logic Server Project (⇧⌘N): drop an ALS project folder; paste `https://github.com/ApiLogicServer/basic_demo` + Read; Create; Employee's two Department keys are Dropdowns; reopen from Recent Projects (`features/ALS_PROJECT_FEATURE.md` → Verify)
- [ ] Pill buttons on every page, light and dark, Return presses Create; on macOS 15 too if possible (`features/PILL_BUTTONS_FEATURE.md`)
- [ ] Definitions: editing Title / widths writes `Design.json` and it is re-applied; the regex Title split
- [ ] Form designer: the Form layout popup; a 3-column Form; a Hidden field; the read-only key on New / Save
- [ ] Form designer: the Control popup follows the selected attribute; TIME and DATETIME round-trip through Save
- [ ] Form designer: a foreign key's Dropdown lists the parent's rows and stores the key; a value-list Dropdown; Radio buttons
- [ ] A value list with codes: `R = Retail, W = Wholesale` on a type field - the Dropdown shows Retail, Save stores R, reopening selects Retail
- [ ] Record popover: ⓘ beside Order's Customer shows the Customer; "No … chosen" when empty; no button on a value list (`features/RECORD_POPOVER_FEATURE.md`)
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
- [ ] **Map view** (author, 2026-11-25; design: `design/Map View Design.md`): any result set whose rows carry
  latitude and longitude columns, on a map - generic, starting with an entity's records (Customer, Supplier).
  Backlogged for later decisions (author, 2026-11-25)
  - [x] 0. Decided: Apple's MapKit (author, 2026-11-25), not an HTML / JavaScript map
  - [ ] 0b. Run `src/MacTests/MapKit Points Test.fb` on a Mac: which mode answers `_mapViewViewForAnnotation`
    (coloured markers with icons, bubbles with details and a button); paste its "MapTest:" log lines
  - [ ] 1. One entity's result set: the location columns found by name and type (or chosen); a generic
    `App Map.incl` (rows + latitude / longitude / title keys -> pins); List | Map; a pin click opens the row's Form
  - [ ] 2. Several result sets on one map (Customers and Suppliers): layers, a colour each, show / hide
  - [ ] 3. Any result set: a query's rows (SQL Generator / JSON:API) on the map
  - [ ] 4. Filling the columns: *Add Location Columns* in the Studio (Lite: ALTER TABLE in the project's copy;
    Professional: the columns to add on the server, then an ALS rebuild); *Locate* in the app - address -> location
    with Apple's geocoder (`CLGeocoder`; `MKGeocodingRequest` on macOS 26), one at a time, written into the row
  - [ ] 5. The points (author; details later): each row an icon (the entity's SF Symbol in the layer's colour,
    `MKMarkerAnnotationViewSetGlyphImage`), a bubble that expands to more of the row's details
    (`DetailCalloutAccessoryView`), and an interactive menu of actions on the row (a callout button); first a small
    Mac test of `_mapViewViewForAnnotation` (no FBExample uses it)
  - [ ] 6. Later: clustering many pins; directions between rows; a small map on the Form
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

- [x] Record popover (author, 2026-11-25; `features/RECORD_POPOVER_FEATURE.md`): an info button beside every lookup
  Dropdown shows the chosen parent record's details in a popover (Order → Customer, Employee → Department, …)
- [x] Value lists as code = label pairs (author, 2026-11-25): `R = Retail, W = Wholesale` in Values - a Dropdown
  or Radio buttons store the code and show the label, like a lookup; written into the generated code
- [ ] Choose the lookup's display column (or several: "givenName surname"); show the display value in the List instead of the key
- [ ] Generated app toolbar (author): New, Save, Delete, Refresh, Search, Theme, Log In - proposal in `STUDIO_REVIEW.md` 2.6
- [ ] Window layouts, a project setting (`design/App Shell Design.md`): Single window (built); Multiple windows - a window per entity, Window menu with Stack and Tile; Tabs - one per entity (future)
- [ ] Users and roles (author, 2026-11-24): sign-in, users, roles (Admin, Editor, Viewer) deciding who may see, edit or delete each entity; Lite: users in the app's SQLite database; Professional: the server's. Then an audit trail (who changed which record, when)
- [ ] Finder icon: the icon picture as `AppIcon.icns` plus `#plist CFBundleIconFile @"AppIcon"` (FB help, Build System)
- [ ] Navigation bar: scroll when there are more entities than fit (the flipped scroll view left the items at the bottom; removed for now)
- [ ] Form fields stretch and List tables fill when the window grows (the same masks as the Studio)
- [ ] Crumb trail and page stack (drill-in replaces the page; back via crumbs)
- [ ] Related-list tabs (master-detail) and drill-in; optionally a modal dialog instead of replacing the page
- [ ] Per-entity event handlers routed from one `on dialog` handler by tag range; per-entity hook files, created only if missing
- [ ] Assigned keys: editable on New, read-only after (identity keys are read-only already)
- [ ] `guid` key kind: generated with `UUIDString( UUIDInit )`, stored lower-case `TEXT`
- [ ] Lite release: the first Mac build of a generated app; fix what the Build Log shows; tag a release

## Professional edition - started 2026-11-25 (author: "we must not fall behind" on multi-user, three tiers)

Code in this repository for now (`src/Professional`, behind `Edition.incl`), moved to a private
repository when sold (author). The model is API Logic Server's: Lite points at the SQLite file,
Professional at the ALS project.

- [x] The ALS contract measured against a running server: `design/ALS Contract.md`, `tools/als_contract.py` (25 checks); `ALS Client.incl` follows it
- [x] The SQL Generator's JSON:API side (`src/Professional/DataObject_JSONAPI.incl`, `features/PROFESSIONAL_DATA_FEATURE.md`); `AddOrderToQuery` on both sides
- [x] The ALS model from `database/models.py`, parsed as text (never run): `ALSModelFromModelsPy` (`src/AppBuilder/ALS Model.incl`), tested against SQLAlchemy on Northwind and CRM; older `class X(SAFRSBaseX, Base)` too
- [x] API Logic Server Project page (`features/ALS_PROJECT_FEATURE.md`): folder, model file or public GitHub repository; typed, chosen or dropped; a copy in `<project>/ALS Model/`; lookups from the relationships, display columns from `admin.yaml`
- [ ] **Next:** `App Data Professional.incl`: the App Data interface over ALS (list with paging, lookups, save with `S_CheckSum` + re-read, remove, login), answers on the main thread; records keep the JSON:API id
- [ ] Connection: the server's address (the page's API Server, `baseURL`), login paths; a sign-in window for the header's Log In; the token for the session, a remembered password in the Keychain
- [ ] Multi-user: a stale checksum explained to the user (reload the record, re-apply the change); Refresh reads the server
- [ ] *Model > Refresh Model from API Logic Server*: read `alsSource` again, replace the copy, keep the design
- [ ] Private GitHub repositories: a token in the Keychain; GitHub read without blocking the window (URLSession)
- [ ] `admin.yaml` titles as the attributes' Titles (its `user_key` is used already)
- [ ] Generate App (Professional): `declare_logic.py` from the project's rules (the rules bridge in FB)
- [ ] `Edition.incl` offers Professional (licensing parked)
- [ ] The Studio's own ALS fetch (the running-server form) uses the form's base URL and credentials (still a hard-coded host and `admin` / `p`), and waits for login before fetching
- [ ] Kafka (author, 2026-11-25; already used behind ALS in the author's other applications): first through ALS's own Kafka integration (the app keeps talking JSON:API); then a plain-HTTP messaging module in FB for Kafka's REST Proxy, and Redis through an HTTP gateway (Webdis, Upstash) - publish / poll, set / get over URLSession

## AI Assistant - rules in natural language, controls suggested (author, 2026-11-26; `design/AI Assistant Design.md`)

A rule is a sentence in the model's own names; the sentence is the source of truth, and the AI translates it into
LogicBank rules - LogicBank for FutureBasic in the app, `declare_logic.py` in ALS (Professional).
- [x] LogicBank for FutureBasic as a module of its own (as LogicBank is to ALS): `src/LogicBankExample` - the module,
  `Data Memory.incl`, the example on Customer / Order / Item in memory, Help with the user guide, README, MIT licence
  (author, 2026-11-26; `features/LOGICBANK_MODULE_FEATURE.md`)
- [ ] Verify on a Mac: the LogicBank example builds and its story matches `tools/logicbank_example_reference.py`;
  Help, Diagram, Preview, Export; About Imagery (in both examples)
- [x] About Imagery Business Systems window (`src/Shared`), in the SQL Generator example's application menu
- [x] `ABOUT_IMAGERY_SITE` = https://fb.imagery-business-systems.com/ (the author's own server, not GitHub Pages)
- [x] The site, generated: `tools/make_site.py` (`features/SITE_FEATURE.md`) - [ ] published on the author's server
- [ ] Web Help: the examples' Help windows load `/help/<module>/` in a web view, the bundled guide when offline; the
  About Imagery window from the site too (author, 2026-11-26)
- [ ] The neutral expression language for formulas / constraints / where (FB and Python generated from it);
  `Rules.json` keeps each rule's sentence
- [ ] The rules check in FB (port of `rules_bridge.py check`), with the engine's limits the samples found
- [ ] The AI connector (FB, URLSession, key in the Keychain, prompts as Templates, answers saved in `<project>/AI/`):
  Claude first, behind a narrow interface; every edition, the user's own key
- [ ] Rules page: grounded sentences (type-ahead from the model), Translate, approve
- [ ] Suggest Rules; the evaluation on Telecom, Customs and Flight Planner (sentences from their READMEs)
- [ ] Suggest Controls into `Design.json`
- [ ] Professional: `declare_logic.py` from the same rules, sentences as comments; the scenarios run against ALS;
  translation through the ALS project's `genai-logic` when it has it, else the Studio's connector
- [ ] Professional: the client previews the rules locally (LogicBank for FutureBasic) while the server decides
- [x] Decisions (author, 2026-11-26): every edition with the user's own key; Claude first; Professional both routes;
  the neutral expression language; the module published. The rules split: `design/Editions Design.md`

## Rules - Logic for FutureBasic (`design/Logic Engine Design.md`, ROADMAP Phase 5)

- [ ] Derived attributes stored or in memory (author, 2026-11-27; `design/Derived Attributes Design.md`): the two open
  questions first; then the Python reference's scenarios, the FB engine and Data Records, App Builder's Add Derived
  Attribute, the generated Form and List

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
- [x] Names (author, 2026-11-26): the product is **App Builder for FutureBasic** (no "Imagery": the FB community knows the tool, not the company); the built app is **Studio for FB** (`Studio for FB.fbeproj` / `.main`); `src/Generator` is `src/AppBuilder`; the Application Support folder follows the product name (earlier folders moved over)
- [ ] Still to rename, when wanted: the repository (`Api_Logic_Client`) and the bundle id

## Installing the Studio

- [ ] Installer for a release: the Studio app plus the runtime and templates, put into
  `~/Library/Application Support/App Builder for FutureBasic/workspace/` (a `.pkg` with a
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

## Licensing - one app, licensed through the Imagery License Server (author, 2026-11-26; `design/Licensing Design.md`)

1. [x] The Python reference: sign and verify test licences (ES256), tampered / expired / other product / bad signature
       (`tools/licence_reference.py`, TEST keys in `tools/licence_test_keys`)
2. [x] `Licence.incl`: verify with `SecKeyCreateWithData` + `SecKeyVerifySignature`, keep in the Keychain,
       `LicenceAllows( feature )`; `Edition.incl` follows the licence; `src/MacTests/Licence Verify Test.fb`
       (`features/LICENSING_FEATURE.md`) - [ ] verify on a Mac
3. [x] The Licence window and menu (Licence…, Enter Licence…, Upgrade to Professional…, Manage Licence Online…,
       Remove Licence…), the upgrade offer - [ ] the edition in the About box
4. [x] The gate on every Professional command ("(Professional)" in the menu title, not hidden); no generation without a licence
4a. [ ] Before release: the production public key in `LICENCE_PUBLIC_KEY`; confirm `LICENCE_SERVER` and its pages
5. [ ] The `appbuilderfb://` URL scheme and the `.fblicence` document type
6. [ ] License Server (its own repository): product `app_builder_fb` and its feature bits (Lite `0x0003`,
       Professional `0x01FF`), signed licences (ES256), the `/appbuilder` landing page, registration to download,
       the upgrade with payment, the licence delivered back to the app
7. [ ] The author: make this repository private; public repositories for LogicBank for FutureBasic and the SQL Generator
8. [ ] The release: the signed, notarized app, downloaded from the License Server

## Sample applications - the whole lifecycle, use case by use case (author, 2026-11-26)

Each use case is a SQLite database first, made right for it; App Builder then generates its business
application; it is built and run on a Mac; it is published as a sample on the GitHub Pages site and
announced on the FutureBasic list. Many use cases and user stories, through the whole lifecycle.

Every sample has the same parts (`samples/<Name>/`, as `samples/Telecom`): `README.md` (the use case, its
**user stories**, the model, the rules), `schema.sql`, `lookup.sql` (reference data that stays) and `sample.sql` (the
demo scenario) apart (author: as on the C++ side), `purge_sample.sql`, `build_db.py` (every row through the rules),
`<name>.sqlite`, the rules for the reference engine with `test_rules.py` (scenarios, `--prove`), and `Rules.incl`
(the same rules in FutureBasic). Its steps: [database] -> [generated and built on a Mac] -> [screenshots, page on
the site, download] -> [post to the list].

| Sample | Database | App on a Mac | On the site | Posted |
|---|---|---|---|---|
| Telecom - Northstar Mobile: travel plans priced from roaming agreements | done (39 rules) | | | |
| Flight planner for amateur pilots - VFR in New England: wind triangle, weight and balance, runways, weather, currency, go / no-go | done (104 rules) | | | |
| Asset management for oil and gas | | | | |
| National customs clearance - set in Bermuda: FOB value and duty, manifest, risk lanes, automated release, bond, the port gate | done (93 rules) | | | |

- [ ] The GitHub Pages site (repository name from the author): a page per sample - what it is, its user stories,
  screenshots, the download
- [ ] Telecom: build it on a Mac: New Project from `telecom.sqlite`, Generate App, copy `Rules.incl` over
  `FBapp/Rules.incl`, build; buy a quote, try one over the credit limit, add a country with no service (Kenya)
- [ ] Telecom: its Page Layouts once they exist (a Travel Planner page); its Map view (countries carry latitude and longitude)
- [x] Flight planner: the database (pilots, aircraft and their performance, airports, flight plans and legs,
  position reports with other traffic); 44 rules - great-circle distance and course, wind, time, fuel and the
  reserve, VFR altitudes, runways, medical, night currency, the annual, go / no-go, the logbook (2026-11-26)
- [x] Flight planner, elaborated from the domain research (author, 2026-11-26): wind triangle, weight and balance,
  runways (takeoff / landing distance at density altitude, crosswind), weather minimums, NOTAMs, medical / BasicMed,
  flight review, currency from the logbook, student endorsements, inspections, the plan's life cycle - 104 rules
- [ ] Professional: Flight Service filing, simulated in the ALS project (author, 2026-11-26) - file, amend, cancel,
  activate, close, extend; the ICAO message from a FlightPlan; overdue -> QALQ -> INREQ -> ALNOT on read.
  Design: `docs/design/Flight Service Filing Design.md`
- [x] Customs, elaborated from the domain research (author, 2026-11-26: automated clearance, auto-release) - duty
  on the price paid (FOB) at the week's rate, specific / compound / stepped rates, wharfage, relief, personal
  allowances; master and house bills; agency permits, holds, prohibited goods; risk score and lanes (green,
  yellow, red, blue, random); release reasons; statements within the bond - 93 rules
- [ ] Automatic release in the generated app (and in ALS for Professional): release every Releasable declaration
  when something changes (a ship docks, a permit is approved, a payment lands) - the rules say which
- [ ] Flight planner: build it on a Mac; its Map view (legs between airports, the track replayed, other traffic)
- [ ] Oil and gas assets: the database (sites, assets, responsible organisations, operating hours, maintenance
  schedules and work orders, sensors, readings, controllers, alarms); rules for maintenance due, alarms, lock-outs;
  simulated devices first, Raspberry Pi / Arduino later
- [ ] Customs: build it on a Mac (New Project from `customs.sqlite`, Generate App, its `Rules.incl`); release the red-lane
  entry after an inspection, let the stopped truck out after correcting the seal
- [ ] Purge sample data from a generated app or the Studio: a command that runs the sample's `purge_sample.sql` (and
  an app built lookup-only from the start) - so a sample becomes a real system

## Web Toolkit for FutureBasic - feasibility (author, 2026-11-26; `design/Web Toolkit Design.md`)

- [x] Run `src/MacTests/Web Server Test.fb` on a Mac: can FB serve a page and take its clicks? Yes (author, 2026-11-28:
  the page, Add One without reloading, `<b>Bob</b>` shown as typed, two tabs and fast clicks kept up)
- [x] Run `src/MacTests/FastCGI Test.fb` behind nginx on a Mac: passed (author, 2026-11-28; nginx run from `src/MacTests`, FastCGI on 9010)
- [ ] Run the Orders example (`src/WebToolkitExample`) behind nginx on a Mac - mostly passed (author, 2026-11-28): the
  page, a customer chosen, a credit limit refused, totals and balance following an item, Ship Today, the theme menu.
  A save after a refused one crashed (`WebTableRefresh`, fixed in bd55a86). Still to try: two browsers side by side;
  an item typed, then the tab switched (saved)

## Web Toolkit - hosting: a first public app (author, 2026-11-28; `design/Web Toolkit Design.md` -> Hosting)

- [ ] The host Mac: a Mac mini (port forwarding or Cloudflare Tunnel) or a rented Mac; a setup checklist (FileVault,
  firewall, no automatic login, updates)
- [ ] HTTPS: a commented HTTPS server block in the template's `nginx.conf`; `certbot` and its renewal; HTTP to HTTPS;
  HSTS (the cookie's `Secure` is in place: set when nginx passes `HTTPS=on`)
- [ ] Unattended: a LaunchDaemon plist beside the LaunchAgent; the app runs with no window; logs to files, rotated;
  a `/health` URL
- [ ] Sign-in: users with salted PBKDF2 hashes (CommonCrypto), a sign-in page, sign-out, a new session id at sign-in;
  `limit_req` on sign-in; roles later, checked on the server
- [ ] Hardening: CSP, `X-Content-Type-Options`, `Referrer-Policy`, `frame-ancestors` from nginx; `limit_req` /
  `limit_conn` per address; fuzz the FastCGI parser here
- [ ] A security review of the toolkit for public use, before the first public app
- [ ] Data: SQLite behind the rules in a web app (`Data Records.incl`); scheduled backups and a tried restore
- [ ] Deploying a new version: a short script (copy, `launchctl kickstart -k`) and its notes
- [ ] The first public app: chosen by the author, built on all of the above

## Record Files for FutureBasic (author, 2026-11-27; `design/Record Files Design.md`)

- [x] The module: record files (FB, `open "R"`) and B-tree indexes (C, tested here); the example on Customer / Order / Item, timed against SQLite
- [ ] Build and run `src/RecordFilesExample` on the Mac: the table of times at 10,000 and 100,000 customers; `tools/record_files_reference.py --records / --index` on the files it made
- [ ] A stop in the middle: quit with Force Quit during a Run, open again - the counts recovered, the indexes rebuilt, Check sound
- [ ] Record checksums (a half-written slot is found), before it is offered in App Builder
- [ ] App Builder: "Record files with B-tree indexes" as a data choice beside SQLite - records and indexes generated from the model, `App Data Records.incl` behind the same app data interface

## Documentation

- [ ] `DOC_ONE_PAGER.html` / `.pdf`: bring them in step with `DOC_ONE_PAGER.md` (editions, grid or tiles, App Builder naming), or build them from the Markdown with a tool

## Ideas

- **An Imagery menu bar launcher** (author, 2026-11-27, from a screenshot of a "Qwik" launcher: one status-bar icon
  whose menu lists a family of small apps, each with its icon): one Imagery icon in the menu bar listing the Imagery
  FutureBasic apps installed (Studio for FB, the free modules' sample apps, generated apps), launching or bringing
  each forward. Questions for the author: a separate small app or a part of the Studio; which apps it lists
  (found in /Applications by bundle id prefix, or a list the Studio keeps); could generated apps offer the same
  status item as an App Shell option
- **National customs clearance** (author, 2026-11-26; a separate application, from the author's earlier work in
  the customs clearance industry): for any country's customs service - the US, Bermuda or another with its own
  tariffs. Shipments crossing the border; pre-clearance: trucks with transponders, pre-cleared drivers, the declared
  contents of containers, container seals, routes registered in advance with the country's customs. Tariffs and the
  clearance checks are a natural fit for the rules engine; routes and crossings for the map
- **Asset management for oil and gas** (author, 2026-11-26; a separate application): pumps, wells and equipment
  spread over many locations, on a map; the organisation responsible for each asset's maintenance; operating hours;
  an IoT interface between the assets' sensors and controllers, with control screens that pop up. The first version
  simulates the IoT side; later, real devices built on the author's Raspberry Pi and Arduino boards, with logic of
  their own. Shares the Map view's groundwork, and the rules engine (maintenance due by operating hours, alarms)
- **Flight planner for amateur pilots** (author, 2026-11-26; a separate application, begun earlier by the author
  with Rahul): aircraft on a MapKit map with their position, heading (vector) and altitude, moving across the
  screen; airports and locations; zoom along the flight path; other aircraft nearby. A fun exercise for MapKit
  in FutureBasic - it shares the Map view's groundwork (`design/Map View Design.md`, `src/MacTests/MapKit Points Test.fb`)

- LogicBank for FutureBasic: offer it back to Val Huber's project (above, waiting on the author).
- The ALS model's relationships make a Lite app possible from an ALS project too: its
  `database/db.sqlite` (SQLite projects) with the ALS model's names.
