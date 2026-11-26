# Model Diagram — the project's ERD

*Model → Show Model Diagram* (⇧⌘D) writes `<project>/Model ERD.html` and opens it in the browser:
an entity-relationship diagram of the whole model, with the business rules drawn on it.

## What you can do on the page

| | |
|---|---|
| Move an entity | drag it by its header |
| Open / close an entity | the triangle in its header (attributes shown / hidden); **Expand All**, **Collapse All** |
| See one entity's world | click it: its relationships turn orange, the rest fade; the side panel lists its rules, parents, children and attributes |
| Move around | drag the background; scroll (or pinch) to zoom; **Fit** |
| Find | type in *Find entity or attribute* — matches stay, the rest fade |
| Start over | **Arrange** — parents left of their children, entities with no relationships in rows below |
| Theme | System, Light, Dark, Colorful, Base |
| Keep it | **Export SVG** saves the diagram as you see it (for documents, git, slides) |
| Details | hover anything: an attribute's type and key, a relationship's role and list, a rule's text |

Positions, open / closed entities, the zoom and the theme are remembered in the browser, per project.

## How it is drawn

- **Entities:** a box per table (views have a grey header); `PK` and `FK` beside the key and
  foreign-key attributes; the type at the right.
- **Relationships:** from the child's foreign key to the parent's key. A crow's foot at the child
  (many), a bar at the parent (one); **dashed with a small circle when optional** (a foreign key
  that may be empty), solid when required. A self relationship loops on the box's right.
- **Rules** (from the project's `Rules.json`):

| Symbol | Rule | Where |
|---|---|---|
| ƒ | formula | on the attribute it derives |
| Σ | sum | on the attribute it derives |
| # | count | on the attribute it derives |
| ⇣ | copy from parent | on the attribute it copies into |
| ! | parent required (parent check) | on the foreign key |
| ✓ | constraint | in the entity's header |
| ⚡ | row event / commit event | in the entity's header |
| ⊘ | delete action (prevent / cascade / nullify) | on the relationship, by the parent |

  A switched-off rule is drawn faded; hover for its text (the imported Python when there is one).

## Where

| Part | File |
|---|---|
| The command | `src/AppBuilder/ERD Generator.incl` (FutureBasic): `ErdShow` → `ErdWritePage` fills the template's `/*__ERD_DATA__*/null` with `{ title, resources, rules }` — the model as the generator holds it (`gProjectDictionary`) and `Rules.json` — and opens the page with `WorkspaceOpenURL` |
| The page | `src/Templates/ERD/Model ERD.html` (bundled with the generator's Templates): sections THEMES, MODEL, LAYOUT, DRAW, INTERACTION, EXPORT; one file, no network, no libraries |
| Menu | `Menus.incl` `_iShowModelDiagram`; `EventHandlers.incl` |
| Test | `tools/check_erd_page.py` (test only): fills the page as `ErdWritePage` does and drives it in headless Chromium |

## Decisions

- **The generator is FutureBasic** (author, 2026-11-24: "We need to be writing these tools in FB
  code, not python"). The FB side collects the model and the rules and writes the page; the page,
  like a generated XIB, is output. A first Python version of the generator side was dropped.
- **One layout implementation**, in the page: the FB code passes the model unchanged, so a
  change to the model needs no change here.
- **HTML + SVG, not a native view:** drag, zoom, hover and export come with the browser; any
  Mac opens it; it can be shared. A native window (WKWebView inside the Studio) can host the
  same page later.
- Crow's-foot notation (Martin / Information Engineering): the common ERD notation.

## Verify on a Mac

- [ ] Model → Show Model Diagram opens `Model ERD.html` in the browser with every entity.
- [ ] Rules imported from `declare_logic.py` show their symbols; switched-off ones faded.
- [ ] Drag, open / close, select, search, themes; reload — positions kept; Export SVG opens in Safari.
- [ ] An ALS project (metadata) draws its entities (relationships when the metadata has them).
