# Development Log

What was done and what was learned, newest first. Commits are on
`claude/dazzling-darwin-awec2o` (Api_Logic_Client unless marked *TXV* = Test_Xib_View).
For the plan see `ROADMAP.md`; for open items `BACKLOG.md`.

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
