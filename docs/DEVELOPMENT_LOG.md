# Development Log

What was done and what was learned, newest first. Commits are on
`claude/dazzling-darwin-awec2o` (Api_Logic_Client unless marked *TXV* = Test_Xib_View).
For the plan see `ROADMAP.md`; for open items `BACKLOG.md`.

---

## 2026-11-24 — One-pager

- `docs/DOC_ONE_PAGER.md`: what the Studio is, for the FB community — how it works, what a
  generated app has, rules declared once (with what one save does), what stays yours, needs and
  status. Also published as a designed page (claude.ai artifact) with the same text.

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
