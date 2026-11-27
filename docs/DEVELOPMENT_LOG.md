# Development Log

What was done and what was learned, newest first. Commits are on
`claude/dazzling-darwin-awec2o` (Api_Logic_Client unless marked *TXV* = Test_Xib_View).
For the plan see `ROADMAP.md`; for open items `BACKLOG.md`.

---

## 2026-11-27 — The page designer: links between pages

- **Author:** drag and drop a relationship between pages; the first thing shown is the relationship between the two
  pages, from the relationships of their entities.
- `tools/pages_reference.py`: `page_associations( model, a, b )` (from each part of a to b's driver: children,
  parent, the same record; the proposed one first), `resolve_link` (b's driver records for a's current record), a
  page's `links` in `Pages.json` and in the check. 13 more checks (49 in all): Customers -> Orders, Orders ->
  Customers, the invoice page to Customers and to Products, pages with nothing in common, the check's three new
  reports. The design (`design/Page Designer Design.md`, "Links between pages"): the sheet in the designer; Go to in
  the part's card, the crumb trail and Back in the generated app.

## 2026-11-27 — The page designer, phase 1: Pages.json and the links

- **Author:** the proposals accepted (Detail / List / List with detail; the toolbar on the part with the focus; the same
  entity twice later; the Web Toolkit later); the page designer is **Professional only** (Lite keeps one page per
  entity and ignores `Pages.json`).
- `tools/pages_reference.py`: the `Pages.json` format (pages, parts with a display and what they follow), the links
  proposed on a drop (`children` / `parent` from the model's `toone` / `tomany`, `same` for a Detail of a List's
  row; parts in page order, the driver first), the default pages, the check, a page resolved from a driver record.
  `tools/fixtures/northwind.sql`: the classic Northwind schema with its foreign keys (13 tables, `Order Details` with
  its space, `Orders.ShipVia` -> `Shippers`) and a few rows. 36 checks: the invoice page built from drops and
  resolved for 10248 (its customer, three lines, the first line's product, Buchanan, Federal Shipping) and 10249 (a
  line whose product is missing shows none); every relationship of Northwind and the samples (12, 34, 21, 18) offered
  both ways. In `run_tests.sh`.
- Next: phase 2, the Pages view in the Studio.

## 2026-11-27 — The page designer, designed

- **Author:** pages composed by dropping entities from a palette, each asked for its display (a list or a "scalar",
  one record), linked to what is already on the page through the relationship, as an invoice page holds several
  object types. This is the "new layout manager" asked for earlier (the backlog item now says so).
- `design/Page Designer Design.md`: pages and parts (Detail, List, List with detail), links proposed from the
  model's `toone` / `tomany` relationships, the driver and the parts that follow it, the invoice example, what the
  generated app needs (above all: a part generated per page with its own tag base, the binding taking the base), five
  phases, four open decisions. Nothing built yet.

## 2026-11-27 — The search dialog; a separator in the toolbar; a scrolling navigation bar (6b9fa7d)

- **Author:** a scrolling navigation bar (the full Northwind, about twenty tables); a separator keeping Search apart
  from the record actions; Search opening a dialog: *Search by* a field from a dropdown, and the value in a text box,
  a date picker (a little calendar) for a date field, and, for a field with distinct values such as a type, a
  second dropdown of those values - dynamic, for every field type, built into the generated app.
- **Search dialog** (App Toolbar.incl, Cocoa popover): the field popup (Any Field + the page's fields), then a
  search field, a value popup or a graphical date picker (`NSDatePickerStyleClockAndCalendar`, year-month-day).
  Distinct values come from the page's records: at most 15, each used more than once on average; keys and parents
  get a text box (their values are numbers). Queries `{ field, mode, text }`; `RecordSearchQuery` (Record
  Search.incl): text (every word, in that field or any), value (exact), date (that day: the value starts with
  yyyy-mm-dd). Generated: `AppPageSearchFields` per page (`AppSearchFieldsLiteral`: kind date / key / text from the
  control kind, the SQL type, the key and the lookup), `gAppPageQuery`.
- **Separator:** a toolbar item whose view is a vertical `NSBoxSeparator` box (`ToolbarItemSetView`).
- **Navigation bar:** `ShellNavScroll` moves the entity buttons and the highlight into an NSScrollView with a
  flipped document view (Cocoa, `ShellNavScrollViews`) the first time a page is shown; `ShellNavItemY` measures
  from the list's top then; the page's button is scrolled into view. Test scenarios G-01a, G-02b. Waits for a Mac
  build.

## 2026-11-27 — The navigator in the tiles; the list and toolbar checked against FB's reference

- **Author:** check the list view's selection (-1 when nothing is selected, else from 0), the callbacks available
  for the list view and the toolbar; make the navigator work in the tiles view, with a ring round the selected tile.
- **Checked** (FutureBasic_Documentation): `TableViewSelectedRow` wraps Cocoa's `selectedRow` (-1 with none,
  rows from 0); `TableViewClickedRow` the same for a right-click or double-click. The table events FB's reference
  documents for apps are `_tableViewSelectionDidChange` (we use it: a row clicked or the arrow keys) and
  `_tableViewDoubleAction`; the header lists more delegate events (`_tableViewShouldSelectRow`,
  `_tableViewSelectionShouldChange`, ...) with no documented way to answer them. The toolbar has
  `_toolbarItemClick` (we use it) and `_toolbarItemValidate` (no documented answer either, so the items'
  autovalidation is off and `AppToolbarSetEnabled` sets them).
- **Tiles:** `RecordTilesSelect( page, index )` (Record Tiles.incl): the ring (3 pt, the accent colour) moves to the
  tile and the tiles scroll to show it. `AppPageGoTo` calls it, so the navigator, a tile click, a row click, the
  search and a list arriving all move it; New clears it. `TilesMark` now through Cocoa. Test scenario G-05.

## 2026-11-27 — Save in the toolbar; the toolbar knows the context

- **Author:** Save in the toolbar too; the toolbar's buttons context-aware: Save only when there is a change (the
  dirty bit), Delete only when a record is in focus. The navigator stays in the footer, below the list.
- Save moved to the toolbar (the footer now holds the navigator and the status line). `AppToolbarSetEnabled` (App
  Toolbar.incl) with the items' autovalidation off. The dirty bit is a comparison, not a flag: `gAppPageClean` is the
  Form read just after a record is shown (and again after its lookups fill in); `AppPageHasChange` reads the Form
  now and compares, so undoing an edit dims Save again. `AppPagesDoDialog` now wraps the handler
  (`AppPagesHandleDialog`) and updates the toolbar after every event; `AppToolbarWatchEdits` (Cocoa,
  NSControlTextDidChangeNotification) at every keystroke. Waits for a Mac build.

## 2026-11-27 — Studio: Generate App's progress sheet

- **Author:** Generate App needs a confirmation, a progress dialog with the steps enumerated, the bar moving forward
  as each part is generated; "Generated" at the end and a Done button; no closing it while it generates.
- **`Generate Progress.incl`** (new, before the generators in the build order): a Cocoa sheet on the Studio's window
  with nine steps (screens, binding code, runtime and templates, model and About, main program and project file,
  starting files, App Pages, runtime files, business rules), each marked waiting / under way / done / failed, a
  determinate bar, the message and Done (dimmed until the end; Return closes it). Generation runs on the main
  thread, so the sheet is redrawn after each step and held 0.18 s (the run loop in the modal-panel mode: no events
  are handled meanwhile). `AppGenerate` calls `GenerateProgressStep( n )`; it does nothing for the other Generate
  commands, which show no sheet. Waits for a Mac build.

## 2026-11-27 — Studio: the Welcome list without its box

- **Author:** "I don't like the square box at all": the Recent Projects list should be transparent, with super-light
  grid lines, on a card shaded a little lighter than the window in dark mode and a super-light grey in light mode.
- `StudioQuietTable` (Branding.incl): the table's and scroll view's backgrounds cleared, no border, horizontal grid
  lines at 6% of the label colour. `StudioCardColor` is now worked out from the window's own background (3.5% darker
  in light mode, 7% lighter in dark), so it always stands apart from it. Waits for a Mac build.

## 2026-11-27 — The generated app's toolbar and search

- **Author:** a toolbar at the top of the window, customisable as Mac toolbars are; its first item Search, linked to
  the object in focus ("Search Customers", "Search Products"); then, on the author's direction, FB's own toolbar items
  (tags, click events) with icons, a magnifying glass for Search, and New and Delete moved from the footer into it.
- **`App Toolbar.incl`** (runtime): `toolbar` / `toolbaritem` with SF Symbols (Search, flexible space, New, Delete,
  Refresh), customisation and autosave on. FB has no search toolbar item, so Search opens a Cocoa popover with an
  NSSearchField under the item (`showRelativeToToolbarItem:`, macOS 14+; the apps need 15). Its label follows the
  page (`AppToolbarShowPage`, with a plural: Category -> Categories).
- **`Record Search.incl`** (runtime): `RecordSearchFilter`: every word of the search in some value of the record,
  Finder-style (`StringLocalizedStandardContainsString`).
- **App Pages** (generated): `gAppPageSearch`, `gAppPageShown` (the List's records: those that match);
  `AppPageSearchChanged` as you type (the List, the navigator, "5 of 91 match"); the toolbar's clicks; a new page
  clears the search. Rows, tiles and the navigator all work on the records shown.
- **Footer:** Save only, under the Form (New, Delete, Refresh are in the toolbar; all four in the Records menu).
- Test scenario G-02b. Waits for a Mac build. A first version built the whole toolbar in Cocoa (an
  NSSearchToolbarItem); replaced, before commit, by FB's toolbar items at the author's direction.

## 2026-11-27 — The record navigator

- **Author:** the generated app should behave like a record navigator: the first item of a List selected (as the
  Studio's entity list is), the List focused and that row loaded; buttons at the bottom to move one record at a time,
  Previous dimmed at the start, Next at the end; the footer naming the entity and the record count.
- **The footer** (App Shell.incl): First, Previous, *"Customer 3 of 91"*, Next, Last at its left (SF Symbols,
  borderless), then the status line, then New / Save / Delete / Refresh. The copyright moved to the foot of the
  navigation bar. `ShellSetNavigator` (the label and which buttons apply), `ShellSelectRow` (select, scroll, focus),
  `ShellSetEnabled`, all through Cocoa.
- **The pages** (App Pages.incl, generated): `AppPageGoTo( row )` selects, shows and updates the navigator;
  `AppPageChooseRow` runs when a list arrives: the record that was showing (after Save or Refresh), the new one
  (after adding: the one not in the list before), the one in the deleted record's place, else the first. A row
  clicked, the arrow keys or a tile clicked move the navigator too. The "91 records" status message is gone (the
  navigator shows the count).
- Test scenario G-02a. Waits for a Mac build.

## 2026-11-27 — The info button is off until a parent is chosen

- **Author:** "If no related record is chosen disable the info button so that you never see the dialogue. Intuitive."
  `RecordPopoverRefresh` (Record Popover.incl) turns each lookup's info button on only while its field has a parent
  chosen; App Pages calls it after a record is shown (`AppPageShowRecord`: also New and after a delete), after a
  lookup's rows arrive (`AppPageFillLookup`) and after any click (a Dropdown's choice). An auto-complete updates its own
  button as a match is chosen, the text is cleared, or a record is shown (`updateInfoButton`). The "No Customer chosen"
  popover is gone.
- The click path no longer uses any FB tag function: the chosen record, its title, the button's look all through
  Cocoa (`ShellFindView`), so "View does not exist" cannot come from it.

## 2026-11-27 — Right-click menus; a Project menu that follows the page

- **Author:** "the Project menu needs to better understand context. Also, right-click on a project should display a menu
  to delete the project, or open the project ... people expect these type of thing when using a mac app."
- **Right-click menus** (FB's `ResponderSetMenu` on the list, as FB's *View Contextual Menu* example; menus 101 and 102,
  not in the menu bar): a project in Recent Projects (Open, Show in Finder, Remove from Recent Projects, Delete
  Project...) and an entity in the Objects list (Generate XIB, Show Model Diagram). The row right-clicked is selected
  first (`ContextRow`, `TableViewClickedRow`), so the page and the menu bar agree with it.
- **The Project menu names its target:** on the Welcome page the project selected in Recent Projects, elsewhere the
  open one (`StudioRecentTargetRow`); Delete, Show in Finder and Close carry its name; a tick on the page showing;
  Clear Recent Projects is dimmed when the list is empty. Before, Delete on the Welcome page deleted the open project
  even with another selected. `ProjectDelete` split into `ProjectDeleteFolder` (the one place a folder goes to the Trash).
- Test scenario B-08. Waits for a Mac build.

## 2026-11-27 — The info button's popover: a tag-range clash

- **Still no popover** (author). Not a scope problem: every page's Form and List are already loaded when the app opens
  (`AppPagesBuild`, two `nibview`s per entity) and hidden until their page is shown. The click was taken earlier in
  `AppPagesDoDialog`: `BindingRadioClicked` claimed every tag from 30000 to 59999 as a radio button, and the lookups'
  info buttons are 40000 + the field's tag, so it answered "mine" and `RecordPopoverClicked` never ran. Radio buttons
  now start at 100000 (`_xibRadioTagBase`, `_bindingRadioTagBase`) and their range ends at 199999, clear of everything
  else. Regenerate the app (Generate App rewrites the XIBs with the new tags).

## 2026-11-27 — "Call to undeclared function 'StudioFindView'"

- **The build error** (author): FB compiles a project in several chunks; a C function written only in `BeginCFunction`
  is seen in its own chunk, not in `Project Actions.incl`'s. Every C function FB calls now has its prototype in a
  `BeginCDeclaration` block (FB's reference pattern, as `Web Server.incl` already did): `StudioFindView`,
  `ShellFindView`, the auto-complete's, the Record Files example's (53 in all; the generated apps and the example would
  have failed the same way). fblint reports a `toolbox` C function with no declaration; rule in FB Coding Rules.

## 2026-11-27 — Auto-complete on local values

- **Asked** (author): auto-completes on other fields too, "based on in-memory values (called local values), not just
  lookups of related tables"; the designer chooses a Dropdown or an Auto-complete.
- **Built:** an attribute's Values list feeds the auto-complete (`AutoCompleteSetValues`; labels shown, codes stored);
  **Allow other values** keeps typed text (default on for a plain list, off for codes; `acOthers` in Design.json); the
  settings row shows "From the Values list" and the check box. Test scenario G-07. Waiting on the Mac.
- **New values remembered** (author: they "would revert back to the original list when the app is recycled, unless
  stored in a plist"): a value typed under Allow other values joins the suggestions and is kept in the app's preferences
  (`NSUserDefaults`, `Auto-complete <Entity.attribute>`), merged in at the next launch.

## 2026-11-27 — Auto-complete for related records; "View does not exist" found for good

- **"Cannot find a view with tag: 40100"** (author, the info button again): the tag is the info button itself. FB's
  `ViewWithTag` looks only in its current output window, which is not the app's window when the click arrives. Views are
  now found with Cocoa's `viewWithTag:` across the app's windows: `ShellFindView` (runtime) and `StudioFindView` (App
  Builder), used by the popover, the tiles, the auto-complete, the cards and the entity list. Rule in FB Coding Rules.
- **Auto-complete** (author): a foreign key as a text field that finds the parent record as you type; the matches in a
  list under the field (above it near the bottom of the window), the name shown, the key stored. `Auto Complete.incl`
  (runtime, Cocoa), the generator (`_xibKindAutoComplete`), and in App Builder a settings row under the Control popup:
  the field shown, the letters before results, the most results (`features/AUTO_COMPLETE_FEATURE.md`). Test scenario
  G-06. Waiting on the Mac: its AppKit code could not be compiled here (no AppKit headers).

## 2026-11-27 — The lookup's info button: "View does not exist", the popover never opened

- **The report** (author, a generated app): clicking the info button beside a lookup (Person) showed "View does not
  exist" and no popover. The popover was an FB `popover` with tagged labels inside it, filled through those tags; one of
  those look-ups failed. `RecordPopoverShow` (`Record Popover.incl`) now builds the popover in Cocoa: a heading and a
  grid of titles and values, anchored to the info button itself, with no tags inside it. Waiting on the Mac.

## 2026-11-27 — The Studio's cards: "View does not exist ... tag: 110"

- **The alert** (author, at launch): the cards were set up by the tags 110 and 111 given to their boxes in the XIBs;
  an NSBox is not a control, so the tags never reach it. Now `StudioCardAround` finds each box from a control inside
  it (the Recent Projects table, the form's Project Name field) and styles it. Rule added to FB Coding Rules.
- **The entity list only with a project open** (author: "not needed until the user actually opens a project ... the
  welcome screen should fill the whole working area"): `StudioLayoutForProject` (Menus.incl, run with the crumb trail)
  hides the list and its + / - without a project, and moves the pages, the crumb trail and the heading to the left.
- **Derived attributes, stored or in memory** (author): designed (`design/Derived Attributes Design.md`), two
  questions open; not built.
- **A project opens on its first entity** (author): `ProjectModelLoaded` selects it, highlights it (the list has
  the focus) and shows its definitions.

## 2026-11-27 — Documentation cleanup (author: "remove redundancies and fix wording to be professional but warm and readable")

- **README** rewritten (bd477b6): what App Builder is, a four-step start, editions, the free modules, the repository,
  a documentation map. The details live in the user guide; the README links to them.
- **USER_GUIDE.md**: shorter sentences, "you", "App Builder" throughout; licences and editions in section 2; the
  Welcome page's new layout, the project icon, grid or tiles; repeats merged. Stale facts fixed: the example
  `Windows.incl` (it showed functions the generator no longer writes), Open Project is Command-O, Delete Project is in
  the Project menu, FutureBasic 7 (not 7.1.x), every Generate command needs a licence.
- **DOC_ONE_PAGER.md**: App Builder throughout, the editions, grid or tiles. Its .html and .pdf are hand-made and now
  lag the Markdown (backlog).
- **ROADMAP**: current statuses; phase 6, the free modules and the site.
- **Editions Design.md** (was Editions and Licensing.md): the editions, the two data layers, the rules split;
  licensing is in Licensing Design only.
- **The modules' READMEs**: the gentle start first; the Templates README corrected (it described bundled templates,
  listed three of seven, and showed an old start-up).
- **docs/archive/**: the LinkedIn post and the dated summary report.

## 2026-11-27 — The test scenario guide (PDF)

- **Asked** (author): "a test scenario guide to enable people to test and validate all the various features.
  Professional style pdf document".
- **Built:** `docs/TEST_SCENARIOS.md` (the source: 32 scenarios, 94 steps, in nine areas - the Studio's launch and
  licence, projects, entity definitions, settings, the model diagram, generating, the generated app with its tiles,
  the free modules, the checks without a Mac) and `tools/make_test_guide.py`, which builds `docs/TEST_SCENARIOS.pdf`:
  a cover with the tester's record, a results summary, and each scenario's steps in a table with Pass / Fail boxes.
- **On the site** (`tools/make_site.py`): `/downloads/Test-Scenario-Guide.pdf`, a card on the home page and a "Test it
  yourself" section on the App Builder page.

## 2026-11-27 — Generated apps: records as tiles beside the grid

- **Asked** (author): a "grid-bag" of tiles beside the grid for multi-record results: popping style, the name as a
  subheading, other details smaller, three or four across.
- **Built:** `src/Runtime/Record Tiles.incl` (copied into every app), a Grid / Tiles switch in each List card's
  title row; the generator picks each entity's name field and four details from the model (`AppTilesCall`).
  `docs/features/APP_SHELL_FEATURE.md`, "Records as tiles". `tools/check_app_pages.py` lints the generated calls
  with the new runtime file. Waiting on the Mac.

## 2026-11-27 — The SQL Generator for the FB list: a short post, a small download

- **The post** (`src/SQLGeneratorExample/ANNOUNCEMENT.md`), in the author's style (author: "the apology is too much ...
  they will stop there"): one line of apology, then the code; the one-file demo first, the example app second; a link,
  no attachments (the list's storage fills up).
- **The small download** (author: most on the list share a single-file app; the example app may overwhelm):
  `SQL-Generator-Module.zip` on the site (`tools/make_site.py`), about 50 KB - the module's four files, the one-file
  demo, the licence and a README.txt of three steps. It is the first button on the SQL Generator page and the home
  page's Download link; the example app is the second button.

## 2026-11-27 — Record Files for FutureBasic: record files and B-tree indexes, timed against SQLite

- **The idea** (author): FB's `begin record` types in random-access files as legacy FB did, with index files beside
  them, as Btrieve; "I would love to see how it performs"; if stable, a developer choice in App Builder to generate
  record databases with B-tree indexes instead of SQLite. Answered first: nothing has to be loaded into memory -
  record n is at n x the slot length, and a B-tree finds a key in three or four pages.
- **Built** (`src/RecordFilesExample/`): `Record File.incl` in FutureBasic (`open "R"`, `record`, `read file`,
  `write file`; a header slot, a free list, recovery after a stop); `Record Index.incl`, the B-tree in C inside the
  .incl (key segments, equal keys kept apart by the record number, seven seeks, next / previous along chained leaves,
  `RICheck`); `Orders Records.incl` (Customer, Order, Item with six indexes: what the generator would write);
  `Benchmark.incl` against `SQLite Comparison.incl` on the same data (`Sample Data.incl`).
- **Tested here:** `tools/check_record_index.py` compiles the B-tree exactly as written and runs six random runs
  (keys of 8 to 220 bytes, many equal keys, deletes, every seek, next / previous) against a sorted list; every file is
  read back by `tools/record_files_reference.py`, which checks the tree with its own walk. 300,000 keys: inserted in
  0.43 s, 300,000 lookups 0.29 s, scanned in 0.02 s (Linux, this machine). `tools/check_record_files_example.py`:
  the SQLite side and the sample data. The FB parts lint clean; they are built on the Mac first.
- **Learned:** fblint caught `width` (an FB keyword) and a `for ... in fn ...` in the new code before the Mac did.

## 2026-11-27 — The LogicBank example's opening page; the Studio's heading with no project open

- **LogicBank example, opening page** (author: "needs paragraph breaks... we need to see the rules as natural
  language, so the user gets a sense of what they're about to see"): short paragraphs, then **The rules, in plain
  words** - each rule in `Rules.incl` as one sentence, grouped item / order / customer - then **What you will see**
  (the thirteen steps, and the buttons). `StoryIntro`, `StoryRule` in `Story.incl`.
- **The Studio's Welcome page** (author, a screenshot: "the heading is redundant on the welcome page, and the Imagery
  logo should not be inside the box ... heading, then working part of the app"): the logo, the product's name and the
  tag-line ("Business rules and native Mac apps from your data model", no longer repeating "for FutureBasic") are the
  page's own heading, above the box; the box holds Create Project, Open Project and Recent Projects. The window's
  heading hides while the Welcome page shows (`StudioUpdateCrumbs`), and the page takes its place (`FitWelcomeView`).
  The running API Logic Server form has the same treatment (author: "yes, same treatment for the server form"): the
  logo, the name and "A project from a running API Logic Server" above its box (`FitOwnHeadingView`).
  Build error on the Mac: `CGRect r = gStudioHeadingFrame` became `= &gStudioHeadingFrame` (FB passes a global record
  by address); the heading keeps only its left edge (`gStudioHeadingLeft`) and reads its frame from the view. fblint
  now reports a record declared with a global record as its value.
  More room around that heading (author: "still too squished"): 24 points above the logo and 24 below it, before the
  box, on both pages.
  The working area as a card (author): rounded corners (12), no outline, a background a shade apart from the window -
  white on the light one, a lighter grey on the dark one (`StudioCardColor`, `StudioCard`, Branding.incl). Its buttons
  float right, the main action rightmost (Open Project..., then Create Project; Cancel, then Create on the server form),
  and on the Welcome page they sit below the project list (author: "the action buttons should be below the project list").
  Project pages: the project's icon and name, no Imagery logo (author: "each project should have an ICON"): its
  picture from Project Settings, else its SF Symbol (`ProjectIconImage`, `ProjectShowHeading`), updated when
  Project Settings is closed.
- **The generated app's header** (author: the suggested icon does not show; the title should be centred on the icon):
  the app name is centred up and down on the icon, tag-line or not; the tag-line sits under it, smaller (11 pt); the
  symbol is drawn at 34 points (`ImageWithSymbolConfiguration`), not stretched from its text size. Waiting on the Mac.
- **Back to Projects with a project open** (author: the heading stayed): the heading follows the page now -
  `ProjectShowHeading` (`Project Workspace.incl`): the product's name on the Projects page, the project's on its entities.
- **Studio for FB, no project open:** the heading said "Untitled Project"; it now shows the product's name
  (`APP_DISPLAY_NAME`), in `MainWindow.xib` and when a project is closed (`ProjectResetToEmpty`).

## 2026-11-27 — Three Mac reports: StringRef, the Web Toolkit's Objective-C, LogicBankExample's crash; globals swept

- **Generated app (Northwind): "Unknown variable type StringRef"** in `App Shell.incl`'s colour provider, written from
  the example in FB's `Color.incl`; that header now defines `StringRef` (2026-09-30), the author's FB 7.0.38 does not.
  Fixed: `CFStringRef`. fblint had the check, but it ran after the fn-definition check, which ends a line's checks, so
  parameters were never looked at; it runs first now.
- **Web Toolkit example: clang "incompatible operand types (CFStringRef and NSString *)"** in `Web Render.incl`: the
  `?: @""` stood outside the bridge cast. Now inside: `(__bridge CFStringRef)([... description] ?: @"")`. The
  "discards qualifiers" warnings on `gWebSessions` / `gWebStylesheets`: the kept value is cast back to its mutable type.
- **LogicBankExample crashed in `DataMemoryCopyAll`** (Story, Next): `Data Memory.incl`'s in-memory database, made with
  `fn MutableDictionaryNew` and held in a global, was freed when the launch event ended. Kept with `DataKept` now, and
  its snapshot too.
- **Every global swept**, with a new fblint rule (an object global set from a fn and not kept). It found, besides the above:
  - generated apps: `gLogicRules` (the rules, registered at launch), `gAppPageKeys` (the record Save and Delete act on),
    the page lists, the lookups (`Binding Support.incl`, `Record Popover.incl`), the shell's pages and colour pairs,
    the theme's colours (kept by `ShellKeepTheme` when the window is built, so `Theme.incl` stays plain);
  - the Studio: the project dictionary, the project name, the crumb trail's actions, the ALS project's model text,
    the selected entity (`objectName`); its scratch globals used inside one function are locals now (author: "if it's
    only one call, why not a local variable?") and gone from `My Globals.glbl`;
  - the SQL Generator example's code samples; the Professional JSON:API model and last error; *TXV*: `gDatabaseURL`.
- **Learned:** the question to ask first is whether a value needs to be global at all.

## 2026-11-27 — Crash fix: globals keep their values (retain, release)

- **The crash:** Studio for FB crashed on Generate App, in `LicenceFeaturesOf` (`objc_msgSend` on a freed object).
  - **Why:** the licence's payload comes from `JSONSerializationJSONObjectWithData`, autoreleased, and was stored in the
    global `gLicence`. FB's CF types are plain pointers, so the global did not retain it. The event that loaded the
    licence ended, the payload was freed, and the next check read freed memory.
- **The fix:** `LicenceKept` retains the new value and releases the old one, for `gLicence` and `gLicenceProblem`.
- **The same in the other modules:**
  - `DataKept` in the shared data module: `gDataEntities`, `gDataDatabasePath`, `gLogicMessage`. The copies in the
    LogicBank and Web Toolkit examples are identical.
  - `WebKept` in the Web Toolkit: the page builder, the hooks, the script and style text, the sessions.
  - The Studio's `gAuthDictionary`.
- **FB Coding Rules:** a global does not keep its value alive.

## 2026-11-27 — Build fixes: NSLog.incl where it was missing; fblint checks opt-in headers

- **The author's build of the Web Toolkit example** stopped at 47 errors:
  - 44 were "Unknown statement 'NSLog'". The SQL Generator's files include `NSLog.incl` themselves, but the Web Toolkit
    example, its template and the LogicBank example have no SQL Generator. Each now includes `NSLog.incl` in its globals,
    as does the generated app's `App Globals.glbl` template.
  - 3 came from `CFDateFormatterRef`, which is in `Tlbx CFDateFormatter.incl`; FB's own `DateFormatterRef` is now used.
- **`MapKit Points Test.fb`** had the same `NSLog` problem.
- **`fblint`: names from opt-in headers.** It now finds a name from an opt-in header that the project never includes.
  - The opt-in headers are `NSLog.incl` and the `Tlbx` headers FB's own examples include by hand, plus `Tlbx
    Security.incl` and `Tlbx CFDateFormatter.incl`.
  - It reads the includes of a file included from beside it, and skips comments and C blocks.
  - On the old files it reports exactly the author's errors.
- **The author: our files are never named `Tlbx ...`.** That prefix is for toolboxes that wrap C code (FB Coding Rules).

## 2026-11-27 — Build fix: our own Security declarations

- **The author's build after the rename** stopped at `include "Tlbx Security.incl"` ("Missing or invalid source
  file", error 1234), and every licence call failed with it.
- **Learned:** FutureBasic_Documentation's headers can be newer than the author's FutureBasic. `Tlbx Security.incl` is
  dated 2026-05-05.
- **The fix:** the top of `src/AppBuilder/Licence.incl` declares the calls the licence uses (first tried as a new file, `Licence Security.incl`: the editor, with the project open, never read it - the second build gave the same errors): `include library
  "Security"`, the C `#import`, the `system` constants and the `toolbox fn` declarations, written from Apple's
  headers.
  - `My Globals.glbl` no longer includes FB's header.
  - The Mac licence test carries the same declarations.
  - FB Coding Rules: check a header's date before including it.

## 2026-11-27 — The generated app's look: dark nav, cards on a backdrop, full width

- **The author's first look at a generated app:** "looks great at first glance". Three changes asked for: a darker nav
  bar in dark mode; a working area that stands apart from the forms; layouts and grids across the full width, with
  ample margins.
- **`App Shell.incl`:**
  - `ShellDynamicColor` gives light and dark pairs (FB's `ColorWithName` with a provider function).
  - New theme colours: the content backdrop, the card, and the card border.
  - `ShellCard` and `ShellPlacePart` put each part on a rounded card, with margins of 24 and 16 pt.
- **`App Generator.incl`:** pages place their Form and List on cards across the full width, and list the cards with
  the page's views.
- **`XIB Generator.incl`:** Form controls stretch in proportion; fixed-width ones move with their column. The List's
  columns are `uniform`.
- **`Theme.incl` (the template):** the new colours.
- Learned:
  - **A part's card must exist before the part:** the part's `nibview` lands on top, and `ViewAddSubview` moves the
    card into the content view.
  - **Proportional autoresizing** (`flexibleMinX` + `widthSizable` + `flexibleMaxX` on every control) spreads a
    multi-column form across any width without Auto Layout.

## 2026-11-26 — Enterprise is now Professional; seats on the network

- **The rename:** the author renamed App Builder's paid edition from Enterprise to Professional. It applies across
  the code, the tools, the docs and the licence payload (`"edition": "professional"`). `src/Enterprise` is now
  `src/Professional`, and `ENTERPRISE_DATA_FEATURE.md` is now `PROFESSIONAL_DATA_FEATURE.md`.
  - Projects and licences that say "enterprise" are still read as Professional (`Edition.incl`, `Licence.incl`).
  - The Mac licence test was regenerated.
  - Earlier entries of this log keep the old name, as written.
- **Seats:** designed in `Licensing Design.md` -> Seats, from the author's answers.
  - Bonjour finds copies with the same licence on the local network; past the seat count, the newest copy is
    read-only until resolved.
  - Each Mac is activated online once, then works offline.
  - Lite: one copy at a time.

## 2026-11-26 — The Web Toolkit is the third free module; pricing

- **The author:** the Web Toolkit is a free module, like the other two. Those who take it write their own pages;
  App Builder automates them, "that's why it's incentive to buy the subscription".
- **Pricing:** an annual subscription under $299, monthly 20% more. This is recorded in `Licensing Design.md` ->
  Pricing, with two questions for the author: is it the Enterprise subscription, and is the web target (feature
  bit 9, proposed) in it? It is kept out of the marketing repository until it is public.
- **The module:**
  - its user guide (`src/WebToolkit/User Guide.txt`);
  - its page on the site (`make_site.py`: the module, the Orders example and the guide, each downloadable);
  - the About Imagery window in the Orders example (checked identical by `run_tests.sh`).
- **The template:** gained `AppMenusBuild`, `AppMenu` and `AppDialog`, so an app's own menus and windows need no
  change to the shared `Server Window.incl`.
- Commit 573c365 (XIB layouts and the Layout Tool) preceded this.

## 2026-11-26 — Web Toolkit: XIB layouts and the layout tool

- The author: "go ahead with the XIB templates and layout tool". A XIB is now a web page's layout:
  - `WebLoadLayout` (`Web Layout.incl`) reads a `.webxib` and makes its widgets: controls, labels joined to their
    fields, rows in twelfths, boxes as cards or forms, an empty named label as a message band, Identifiers as
    widget ids.
  - The layout tool (`src/WebToolkit/Layout Tool/Layout Tool.html`) lays them out, previews them as the web shows
    them, writes the FB code, and saves `.xib` and `.webxib`.
  - The Orders example is laid out in three `.webxib` panels (a table beside a form, each).
- The rules have one reference (`tools/web_layout_reference.py`) and three implementations, each tested against it:
  - Python (the reference itself);
  - the Objective-C in `Web Layout.incl`, compiled here with GNUstep: `tools/check_web_layout.py`;
  - the tool's JavaScript, in Chromium: `tools/check_layout_tool.py`.

  The comparisons use the reference's test layout and the repository's 15 XIBs, which all lay out with unique ids.
- Commit 752eb47 (the widget library) preceded this.
- Learned:
  - **FB compiles a `.xib` resource into a nib,** so there is no XML at run time. Hence `.webxib`: the same file
    under another name, copied as it is (to confirm on a Mac).
  - **GNUstep's runtime has no object literals or subscripts,** so the Objective-C is written without them. It then
    compiles here and on a Mac alike.
  - **Python's `round()` rounds halves to even,** while C and JavaScript round them up. The reference uses
    `floor( x + 0.5 )` so that the three agree on spans.

## 2026-11-26 — Web Toolkit for FutureBasic: the widget library, the lifecycle, the app template

- The author: the widget library for all HTML controls, with event handlers back to FB and binding to the
  database - FB as the middleware, serving pages that behave as any normal page. Added during the work:
  - every widget AJAX;
  - a page lifecycle so data is saved back;
  - an FB app template for the events in and out of FastCGI;
  - the core tied to no data model, because App Builder will target a desktop or a web app;
  - XIB files as page templates, with a layout tool (designed, next).
- What was built:
  - `src/WebToolkit/`: Server (the tested FastCGI core, verbatim), Session, Widgets (16 kinds), Render (escaped HTML,
    Bootstrap class names), Events (routing, CGI answers, the lifecycle, `WebStart`), Binding (optional: forms and
    tables through LogicBank), `web.js`, `web.css` (four themes as tokens).
  - The template: `src/WebToolkit/Template/`.
  - The example: `src/WebToolkitExample/` (Orders on the LogicBank example's model and rules).
- Tests:
  - `tools/web_toolkit_reference.py`: the protocol in Python, and `web.js` in headless Chromium, 30 checks.
  - `run_tests.sh` also checks that the copies are identical.
- Learned:
  - **Define before use** shapes the module: the core cannot call the binding, so the binding registers two hooks
    (field edited, save dirty) when a form is first bound. That is also what keeps the core free of any data model.
  - **`data` is an FB keyword** (so are `line`, `text`, `record`, `select`, `button`): fblint caught `line`.
  - **Beacons:** `navigator.sendBeacon` with a JSON Blob carries the cookie, so "leaving" reaches the FB app without
    an answer awaited.

## 2026-11-26 — Feasibility: web applications in FutureBasic, replacing Wt

- The author's pattern: FastCGI, with nginx in front and a long-running FB app behind it answering requests with
  HTML from our own widgets; Foundation throughout (`design/Web Toolkit Design.md` -> The pattern).

- The author asked whether a standalone web server and web UI, with the business logic in FB, could replace Wt and
  its licence: a feasibility question for now.
- `docs/design/Web Toolkit Design.md` covers:
  - the purpose: replace Wt, clean-room, no Wt code or licence;
  - what FB offers;
  - an architecture in Wt's spirit: sessions, widget dictionaries, events through `@fn`, incremental updates, a
    small `web.js`, CSS themes;
  - security, HTTPS (a proxy at first, then Apple's Network framework), and the limits.
- `src/MacTests/Web Server Test.fb` is the proof: a C HTTP server (`BeginCFunction`, BSD sockets, GCD on the main
  queue) calls an FB handler through an `@fn` pointer. The page is a counter and a greeting, updated without reloading.
- Learned:
  - FB has no web-server example or HTTP library.
  - `BeginCDeclaration` / `BeginCFunction` ... `EndC` with `toolbox fn` brings in C the size of a small server.

## 2026-11-26 — Imagery's FutureBasic site, generated

- The author hosts the site on his own server at `fb.imagery-business-systems.com` (a domain name, so the host can
  change without redeploying the apps). `ABOUT_IMAGERY_SITE` points there.
- `tools/make_site.py` builds the static site from the repository:
  - the home page;
  - each module's page (README, download, user guide);
  - the examples' user guides as web pages (`User Guide.txt`'s markup), ready for web Help;
  - the samples' pages and zips;
  - App Builder's page, with registration on the License Server.

  Standard library only. Checked in Chromium: light and dark, phone width, tables and nested lists.

## 2026-11-26 — Licensing built in App Builder; logging gated everywhere

- Licensing (`docs/features/LICENSING_FEATURE.md`):
  - `Licence.incl`: ES256 licences verified offline with the Security framework, kept in the Keychain,
    `LicenceAllows`.
  - `Licence Window.incl`: the Licence menu and window, and `LicenceGate` on ALS projects, rules exchange and every
    Generate command. `Edition.incl` follows the licence.
  - `tools/licence_reference.py`: issue and verify; 10 cases; it writes the Mac test program, which carries
    `Licence.incl`'s verify part unchanged.
  - The keys here are TEST keys; the production pair is made on the License Server.
- Logging (author): every `NSLog` - errors too - is gated on `isLoggingOn`, NO by default, declared in the app's own
  globals.
  - Generated apps get a new template, `App Globals.glbl` (first in the build order); the generated main no longer
    sets `isLoggingOn = YES`.
  - The runtime's `Data SQLite.incl` and the LogicBank example's `Data Memory.incl` no longer declare it. The Studio's
    `My Globals.glbl` has it NO.
  - The examples' "Log to NSLog" menu items toggle `isLoggingOn`; their separate flag is gone.
  - Test_Xib_View likewise (279496a).
  - 62 calls gated here, 21 in Test_Xib_View. `fblint` now reports an ungated `NSLog` (FB Coding Rules 27).
- Learned:
  - macOS verifies ECDSA P-256 natively (`kSecKeyAlgorithmECDSASignatureMessageX962SHA256`, DER signatures - what
    OpenSSL and Python's `cryptography` produce). The Security framework is `include "Tlbx Security.incl"`.
  - Rather than an output parameter, a verify function reports why it refused in a global (`gLicenceVerifyProblem`).

## 2026-11-26 — LogicBank for FutureBasic as a free module, with its example app

- The author: LogicBank's sample is its own app, on three objects that never touch a database - Customer, Order,
  Item - with hand-written rules; App Builder is what adds the AI, the checks and the tests. Open-sourcing the module
  also keeps faith with LogicBank for Python, which is open source. And like the SQL Generator's, the example gets a
  Help window with the user guide and examples.
- `src/LogicBankExample`:
  - `Data Memory.incl`: the engine's data calls answered from memory - copies out, a snapshot rolled back on a
    refused save, generated keys.
  - The module's files are identical to the runtime's.
  - The example: `Rules.incl` (all rule kinds), a 13-step story with Next / Run All / Start Again and the engine
    log, Help with `User Guide.txt` and a rules diagram, About Imagery.
  - `tools/logicbank_example_reference.py` checks the story on the reference engine and writes `Model.json`.
- Learned:
  - The engine depends on its data only through about fifteen `Data…` calls, so a data layer is a file:
    memory today, ALS tomorrow (the Enterprise client's preview of the rules).
  - `%-8@` widths do nothing for objects in NSString formats: pad with `StringByPaddingToLength`; numbers keep
    `%8.2f`.

## 2026-11-26 — The free modules and the About Imagery window

- The author: the SQL Generator and LogicBank for FutureBasic are free modules, downloadable from the GitHub Pages
  site, each with a sample app. Both apps have *About Imagery Business Systems…*, describing Imagery's FutureBasic
  work. App Builder is the licensed app Imagery resells. Design: `docs/design/Free Modules Design.md`.
- `src/Shared/About Imagery.incl`:
  - one self-contained window: the logo following light and dark mode, the text from the resource
    `About Imagery.txt` (simple markup), *Visit the Website*, Close;
  - added to the SQL Generator example's application menu and build order;
  - `run_tests.sh` checks the copies are identical.
- Learned: FB's application menu takes items after its required separator (`menu _mApplication, item,, title`,
  FBExamples MainMenu). A window closes with the `window close` statement.

## 2026-11-26 — Licensing designed: one app, signed licences from the Imagery License Server

- The author: App Builder is one app for Lite and Enterprise, the Enterprise features gated by the licence. Lite is
  licensed too: users register on the Imagery License Server before they can download, and upgrade from a Licence
  menu in the app. Design: `docs/design/Licensing Design.md`.
- Decided:
  - App Builder's source goes private; LogicBank for FutureBasic and the SQL Generator stay public modules.
  - Licences are bound to the registered account, signed for both editions, and checked offline.
  - Generated apps never check a licence.
- Learned:
  - The License Server's current tokens can be forged (a published salt, a non-cryptographic hash) and use
    `std::hash`, which differs between Linux and macOS.
  - macOS verifies ECDSA P-256 natively (`SecKeyVerifySignature`, in FB's Security headers); Ed25519 would need
    a library. Licences are therefore ES256.
  - Fleet Dispatcher's editions-as-bit-bundles is the pattern App Builder follows (Lite `0x0003`, Enterprise
    `0x01FF`).

## 2026-11-26 — Rules: the line between Lite and Enterprise; the AI Assistant's decisions

- The author drew the line for rules by where they run and who shares them (`docs/design/Editions and Licensing.md`):
  - **Lite** defines, tests and runs rules on one Mac: the whole engine, authoring, sentences, Explain, scenarios,
    and the AI Assistant with the user's own key.
  - **Enterprise** covers rules shared through a server: enforcement, `declare_logic.py` import and export,
    equivalence tests, multi-user, integration and scheduled rules, authorization, governance, `genai-logic`.
  - An Enterprise client previews the rules locally.
- AI Assistant decisions:
  - Claude first, behind a narrow interface.
  - Enterprise uses both routes (ALS `genai-logic`, else the Studio's connector).
  - The neutral expression language.
  - LogicBank for FutureBasic is published as its own module.

## 2026-11-26 — AI Assistant designed: rules as sentences in the model's language

- The author: a schema brings no rules, so an AI connector in App Builder. Rules are natural language using the
  model's entities and attributes, and the same rules go to ALS as `declare_logic.py`. LogicBank for FutureBasic
  should be a module of its own, as LogicBank is to ALS. Design: `docs/design/AI Assistant Design.md`.
  - The sentence is the source of truth, grounded in the model as it is typed.
  - The AI translates it into the engine's rule kinds, or asks a question when the sentence is ambiguous.
  - App Builder checks and the user approves each translation.
  - A neutral expression language generates both FB and Python.
  - Suggest Rules and Suggest Controls (into `Design.json`).
  - The three samples are the evaluation set.
  - Generation never calls the AI.

## 2026-11-26 — Customs elaborated from the research: automated clearance

- `samples/Customs` rebuilt: 22 tables, 93 rules, 88 scenarios, `--prove` 93 of 93.
  - Value on the price paid (FOB, Bermuda's Public Notice 17) at the week's exchange rate, rounded first.
  - Ad valorem, specific, compound and stepped rates.
  - Wharfage 1.25 %; none on personal baggage.
  - Relief for approved importers; resident and visitor allowances.
  - Master and house bills with a manifest check; late security filing.
  - Agency permits, holds, prohibited goods.
  - Risk score and lanes: green, yellow, red, blue, plus a random draw.
  - `ReleaseReason` / `Releasable`: automatic release is the app releasing what the rules call releasable.
  - Monthly statements within the bond; required bond.
  - The port gate, kept.
- Learned:
  - A child's formula that reads its parent's aggregate sees it before the child is counted. Ten house bills
    reading their master bill's "manifest match" kept a stale value. Read the aggregate from the row that
    needs it, not through the child: the declaration copies `MasterBillId` and reads the master bill.
  - A cycle (an inspection lowers the importer's points, which raise the same entry's risk) leaves the
    entry's own score stale. Break it the way the domain does: score with the points as they were when the
    entry was lodged (a copy rule).
  - CIF (in the earlier sample) was wrong for Bermuda: duty is on the transaction value.

## 2026-11-26 — Flight Planner elaborated from the research; Flight Service filing designed

- The author asked for research on both samples' domains, then for everything it suggested. Research notes:
  `docs/research/Flight Planning Research.md`, `docs/research/Customs Clearance Research.md` (c52efcc).
- `samples/FlightPlanner` rebuilt: 14 tables, 104 rules, 104 scenarios, `--prove` 104 of 104.
  - Wind triangle per leg.
  - Weight and balance from loading stations, with a sloped forward CG limit.
  - Runways: takeoff and landing distance at the density altitude (x 1.5), crosswind with the gust.
  - Weather: flight category and the VFR minimums by airspace, tighter for students.
  - NOTAMs that close an airport.
  - Medical expiry from exam date and age, or BasicMed; flight review.
  - Landings and night landings in 90 days from the logbook. Night currency counts only with passengers
    (the research's correction).
  - Student solo, cross-country and Class B endorsements.
  - Annual, transponder, ELT and battery; the 100-hour inspection for hire.
  - Draft - Filed - Active - Closed (old-value constraint), ETA and the search-and-rescue time.
  - Each leg's `Problem`; the plan's `NoGoReason`.
- Learned:
  - Recency windows ("90 days") need a reference date the rules can see. Without max / min aggregates the
    "third-latest landing" cannot be found, so the logbook counts back from the pilot's `AsOf` date (today in
    the app), and a child formula reads it from the parent.
  - The data loader steps a status through its life cycle (`STEPS`) when a rule guards the transitions.
- The author: file the plan with the FAA, simulated, Enterprise only, inside ALS. Researched: Leidos Flight
  Service web services (REST / SOAP, vendor access only), the ICAO fields, the life cycle (expiry after 2 hours,
  overdue at ETA + 30, QALQ, INREQ, ALNOT). Designed: `docs/design/Flight Service Filing Design.md`. Built later.

## 2026-11-26 — Flight Planner sample (VFR in New England)

- `samples/FlightPlanner`: 7 tables, 44 rules, 45 scenarios, `--prove` 44 of 44; the same pattern as Telecom and
  Customs (schema, lookup, sample, purge; `build_db.py` through the rules; `Rules.incl` in FB, linted with the runtime).
  A leg's distance and true course by the great circle (haversine, initial bearing) from the airports'
  coordinates; magnetic course, ground speed, minutes and fuel; the VFR hemispheric altitude rule (14 CFR 91.159),
  runway length; the plan's totals, the reserve (30 / 45 minutes, 91.151) and the margin; `NoGoReason` - no legs,
  medical, night currency (61.57), annual, altitude, runway, fuel - and filing needs a GO; the logbook from closed
  plans; position reports for a flown track and other traffic (for the Map view).
- Learned: FB's `sin`, `cos` and `asin` are keywords (radians), `atan2( y, x )`, `sqrt`, `floor`, `fmod` and `M_PI`
  come from math.incl. Rounding is `floor( x + 0.5 )` in both the reference and FB, so the numbers agree.
- Next (author): research both domains (flight planning; customs clearance and automated release) and elaborate
  the two samples from it.

## 2026-11-26 — Customs sample (Bermuda); lookup data and sample data apart

- The author chose customs clearance next, set in Bermuda. No land border: goods arrive by sea and air, and
  pre-clearance is at the port gate - transponder read, seal matching the declared one, truck and driver
  cleared on the day, a registered and approved route. `samples/Customs`: 15 tables, 35 rules - duty from
  the tariff (copied rates), the declaration's totals and balance, the deferment bond, the green and red
  lanes, release (goods, lane or inspection, no failed inspection), and `Movement.Reason`: the first gate
  check that fails, recomputed when its source changes. 41 scenarios; `--prove` 35 of 35. Sample duty rates
  in Bermuda's style, not the official tariff; companies and people made up.
- Learned: constraints of a parent run in the same save (the importer's bond refused a release before the
  entry's own inspection rule) - scenarios must isolate the rule they test; delete actions run in declared
  order - refuse (payments) before cascading (lines), or the cascade changes the entry and another rule
  refuses it for the wrong reason.
- The author: as on the C++ side, the schema and the data are separate files, lookup data (stays) apart from
  sample data (the demo scenario), which can be purged. Both samples now have `lookup.sql`, `sample.sql`
  (plain INSERTs of the typed columns) and `purge_sample.sql`; `samples/sample_loader.py` replays them
  through the rules (forward references deferred, guarded statuses last); `--lookup-only`. The rebuilt
  databases are identical to the earlier ones, table by table; the purge leaves exactly the lookup-only build.

## 2026-11-26 — The sample applications: one lifecycle, use case by use case

- The author: a SQLite database for each use case (Telecom, the flight planner, oil and gas assets, customs
  clearance), made right first; App Builder generates each business application; each is added as a
  sample to the GitHub Pages site and posted on the FutureBasic list - the whole lifecycle, many use cases
  and user stories. `BACKLOG.md` -> Sample applications: the parts every sample has (as `samples/Telecom`),
  its steps, and a table of the four. The Telecom README gained its user stories.

## 2026-11-26 — Telecom sample: travel plans priced from roaming agreements, 39 rules

- The author: a second application from a database, to show the business rules on a real-world case
  unlike orders and products - a mobile carrier: customers, accounts, plans, phones (a phone is part of
  a plan); networks matter for roaming abroad; customers buy a travel plan for their countries and dates,
  priced from the carrier's agreements with partner networks. `samples/Telecom`.
- The pricing engine is rules over data: a country's cost per day at its preferred agreement's rates,
  the zone's markup and a rounding step; a trip's countries copy the day price (a quote keeps it), are
  free in the home zone; purchased trips add up phone -> plan -> account against the credit limit. LogicBank
  has no max/min aggregate, so the design uses formulas, copies, sums and constraints only.
- Every seed row goes in through the rules (`build_db.py`, the reference engine): the database's prices and
  totals are the rules' own. 30 scenarios, `--prove` 39 of 39; FB `Rules.incl` lints with the runtime. Days
  between ISO dates in FB with the Julian day formula and `fix` (FB's `int` rounds) - checked against
  Python's calendar over 20,000 days.
- Backlog: four more applications from the author - the flight planner, oil and gas asset management, national
  customs clearance (with the Telecom sample's Map and Page Layouts items).

## 2026-11-26 — SQL Generator example: how to put the module in your own app

- The author: the example needs further instructions for including the module's files in one's
  own application - in the plain FutureBasic editor, by drag and drop (open source users will not
  have the Studio). The Help (`User Guide.txt`) has a new part, "Using the SQL Generator in your own
  app": copy the four files; drag them into the project window above your own files, in build order
  (FB builds the list from the top; definition before use); Build Settings > Compiler options
  `-lsqlite3 -Wno-unused-command-line-argument` and why; the single-file way (`include` + `#build`,
  which FB allows in single files only); opening the database and creating its tables; describe,
  generate, run; the names the module uses, using your own SQLite code, updating, errors. The
  README's section follows it in short.
- `SQL Generator - Smallest Program.fb`: the module in the fewest lines - a single-file program
  (an in-memory database, a table, one INSERT of three rows, a SELECT with a filter and an order).

## 2026-11-26 — Names: App Builder for FutureBasic, built as Studio for FB

- The author: the product is **App Builder for FutureBasic** - without "Imagery", which the FB
  community does not know - and apart from Imagery LogicBank Studio (C++/Wt, a different product).
  The built app is **Studio for FB** ("Studio" alone is the other product). Done:
  - the name in the app (`APP_DISPLAY_NAME`: window, Welcome view, server form, About box, Help
    menu), the generated apps' templates and file headers ("Generated by App Builder for
    FutureBasic"), the docs, the architecture diagram (script redrawn), the one-pager and its PDF
    (remade with headless Chromium, Letter, scale 0.5: two pages as before);
  - the Application Support folder `App Builder for FutureBasic`; on first launch the folder of
    either earlier name (`Imagery LogicBank Studio for FutureBasic`, `Api_Logic_Client`) is moved
    over and the paths stored in its JSON files fixed (`StudioMoveOldSupportFolder( url, oldName )`);
  - `src/Generator` -> `src/AppBuilder` (32 files, and `check_app_pages.py`, which built the path
    in pieces); `Api Logic Client.fbeproj` / `.main` -> `Studio for FB.fbeproj` / `.main` (the
    built app takes the project's name; `data.fbproj` and FB's `Window.plist` updated).
  - Kept: "Imagery LogicBank Studio" where it means the C++ product (rules design notes); the
    repository's name; past entries of this log.
- Open the project from its new place: `src/AppBuilder/Studio for FB.fbeproj`. The old
  `src/Generator` build folder FB made can be deleted.

## 2026-11-25 — SQL Generator example: a Help window to read, preview and export

- The author: the Help window stays - a heading and opening paragraph, the architecture diagram, then
  each function explained one by one; it should print as PDF; then, instead of printing, Preview and
  Export (PDF or Rich Text). Done: `User Guide.txt` rewritten in that order (every public function of
  the module and the runner); the diagram as a PNG (`tools/svg_to_png.js`: the SVG in headless
  Chromium, light colours, 2x) placed by a new `![name]` markup line (`RichAppendImage`, a text
  attachment); **Open in Preview** (a print job saved to a temporary PDF, in the light appearance so
  it is black on white in dark mode, opened in /System/Applications/Preview.app), **Export…** (PDF, or
  RTFD with the diagram), **View Diagram** (full size, zoom, full screen); Help menu items too.
- FB has no wrapper for a print job to a file with a copied NSPrintInfo, for RTFD, or for opening
  with a given app: those are single `cln` lines. fblint caught `textView` (an FB keyword) and a
  function placed before one it calls.

## 2026-11-25 — SQL Generator example: one scrolling output with every result

- The author merged and pulled; the Studio and the example compile and run. For the example: no
  popup to choose an example - a scrolling text with all the results - and a blank line between the
  building of the dictionaries and the results. The window now opens with every example run
  (`ExampleRunAll` at launch, under a short introduction); Run All (Return, ⌘R) runs them again;
  the example popup and Run button are gone (the Examples menu still runs one). `ShowIntroText`
  moved to Example Output.incl: fblint caught it called before its file in the build order.
- The branch merged `origin/main` (merges only, no other changes there).

## 2026-11-25 — SQL Generator example: window title; Run All shows what it ran

- The author: the window title is now "SQL Generator Example by Imagery Business Systems, LLC";
  Run All "does not seem to work". Its wiring is right (button, menu ⌘R, `ExampleRunAll` runs
  1-10), but every example scrolls the output to its own end, so after Run All only the end of
  example 10 was in view - it looked like nothing, or one example, had run. Run All now starts
  with a heading, logs each example (when the output is logged), ends with a note and scrolls
  back to the top (`TextScrollRangeToVisible`). If it still does nothing on the Mac, the cause is
  elsewhere: the author's report decides.

## 2026-11-25 — Value lists with codes: "R = Retail" stores R, shows Retail

- The author: a type field should be able to be a Dropdown whose values the developer types,
  written into the FB code, not a lookup but behaving like one. Most of it existed (Control:
  Dropdown, the Values column, `BindingFillChoices` with the list in the generated binding); what
  a lookup did and a value list did not was storing a key while showing a name. Values now take
  `code = label` pairs: `TypeMapValuePart` / `TypeMapValueParts` / `TypeMapValuesArePairs` (Type
  Mapping); a Dropdown's binding calls `BindingSetChoices( tag, titles, codes )`, Radio buttons
  get the labels as titles (XIB) and the codes in their show / take. A plain list is generated as
  before.

## 2026-11-25 — SQL Generator example builds and runs; its warnings fixed

- The author's build of `SQLGeneratorExample` compiled, linked and ran, with two warnings:
  - `-lsqlite3: 'linker' input unused`, once per file: FB passes Build Settings' "Compiler options"
    to every compile, and that is where its reference says a library goes. The example lacked
    `-Wno-unused-command-line-argument`, which the Studio, the app template and Test_Xib_View
    already have; added.
  - `selectfilterArrayRef is used uninitialized` (`GetSelectFilterArray`, DataObject_Super.incl):
    a query without a filter returned an unset variable; it starts at NULL now - in the runtime,
    the example and *TXV* `e045def` (the copies stay identical).

## 2026-11-25 — Build fix: SQL Generator example, a text-view function newer than the author's FB

- The author's build of `SQLGeneratorExample`: "Unknown … Toolbox name … TextViewAppendAttributedString"
  (Rich Text.incl, lines 85 and 122). It is in FutureBasic_Documentation's `TextView.incl`
  (its "Convenience" block) but not in the FB that builds. `RichAppendAttributed` now appends to
  the text view's text storage (`TextViewTextStorage`, a mutable attributed string) with
  `MutableAttributedStringAppendAttributedString`, which the same file already used without trouble.
- fblint: `NEWER_THAN_FB`, names the headers have but the author's FB lacks, each with its way
  round; on the old file it reports both lines. Coding rule 26.

## 2026-11-25 — Build fix: a parameter named like a global

- The author's build: "Redefined parameter in line 359 of ALS Project.incl: projectName" -
  `ALSProjectKeepCopy( projectName … )`, and `projectName` is a Studio global (`My Globals.glbl`).
  Renamed `nameOfProject`. fblint already caught locals that reuse a global's name but skipped
  `local fn` lines: it now checks parameters too (and not a function's own name, which FB
  accepts); run on the old file it reports exactly line 359. Every other parameter and local in
  the Studio checked: none other. Coding rule 25.

## 2026-11-25 — Map view: Apple's MapKit decided; a Mac test for its points

- The author: use Apple's MapKit (not an HTML / JavaScript map). `src/MacTests/MapKit Points Test.fb`
  (new folder: single-file programs that answer a question on a Mac first) shows five points and
  answers `_mapViewViewForAnnotation` four ways, logging what FB passes. Found in FB's headers: the
  event's getters / setters are generic (`DialogEventObject`, `DialogEventSetObject`,
  `DialogEventSetView`), and `MKMarkerAnnotationView` has setters but no constructor - the test
  makes one with a `cln` line (`cln return (__bridge_retained CFTypeRef)…`).

## 2026-11-25 — Record popover: a related record's details beside its Dropdown

- The author (Lite): an Order's Customer Dropdown needs a small icon that shows that Customer's
  details in a popup - for every relationship. Built generic: the XIB generator puts an info
  button beside every lookup Dropdown (tag 40000 + the field's); the binding registers the
  parent's shown fields and titles; Binding Support keeps the lookup's rows so the chosen parent is
  at hand; `src/Runtime/Record Popover.incl` shows it in an FB popover (FBExamples' pattern:
  `popover`, labels made into it, `PopoverShow` beside the button). No new query: the same in
  both editions. `features/RECORD_POPOVER_FEATURE.md`.
- From FB's reference: `textlabel tag, text, rect, wndTag` alters a label in another window
  (the popover) without making it the output window.

## 2026-11-25 — Map view backlogged: native MapKit or an HTML map, to decide later

- The author asked whether the map is an HTML view with a JavaScript map or a native Cocoa view,
  then backlogged the Map view with everything gathered so the decisions can be made later. Cocoa
  has MKMapView (FB: `mkmapview`, three FBExamples); the comparison (look, key and cost, events,
  icons and bubbles, geocoding, code) and the one native risk (`_mapViewViewForAnnotation`
  untried in FB) are in `design/Map View Design.md`; step 0 of the Map view in `BACKLOG.md`.

## 2026-11-25 — Map points: icon, expandable bubble, menu (noted for later)

- The author: the map's points are the result set's rows, each shown as an icon with a bubble that
  expands to more details and an interactive menu - details to be worked out later. FB's MapKit
  header has the parts (marker glyph image and tint, callout, detail accessory view, callout
  buttons, clustering); the per-point view comes through `_mapViewViewForAnnotation`, which no
  FBExample uses, so a small Mac test comes first. `design/Map View Design.md`, step 5.

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
