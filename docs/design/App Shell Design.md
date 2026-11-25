# Generated App Shell — Design

The generator turns any ALS model into a **generic base app**: one shell, many
entities, built from embeddable XIB parts. The author then edits and extends
the generated app, so the output must be readable, modular, and safe to regenerate.

## Principles

From *Building Production Software with AI — A Domain-Driven Approach*
(the author's book; repository `Domain-Driven-Design-Book`, read-only here):

- **The model is the source of truth; generated code is disposable.** The
  generator re-expresses one model (SQLite schema, later ALS `admin.yaml`)
  as FB code. Review the generator and the model, not every generated file;
  trust the output unless a check fails (fblint, generated-SQL checks,
  the author's build). (Book §20.4, §2.7)
- **Ubiquitous language.** Entity and attribute names come from the model
  unchanged: table `Customer` is `Customer` in function names, tags
  (`_customerCompanyName`), XIB files, labels and SQL. No synonyms, no
  renaming in generated code. Relationship names follow the model
  (`OrderList`). (Book §2.2)
- **Dependency rule, by include order.** FB has no imports, so the layers
  live in separate files and `data.fbproj`/include order enforces direction:
  domain → application → infrastructure → ui. (Book §5.3)

  | Layer | Generated / runtime files | Knows about |
  |---|---|---|
  | domain | `Model.json`, `Model Tags.incl`, `<Entity> Hooks.incl` (rules, validation) | nothing below |
  | application | `App Data.incl` — list / get / related / insert / update / upsert / delete per entity | domain |
  | infrastructure | `SQLite Data.incl` (lite) — later `ALS Client.incl` | implements the application's data interface |
  | ui | XIB parts, `App Shell.incl` (navigator, crumbs, tabs), `ALS Binding.incl` | application, domain |

- **Lite first, then rewrite the infrastructure.** The lite edition (SQLite
  direct) mirrors the book's Lite tier; adding ALS replaces only the
  infrastructure file, behind the same data interface. The UI and the hooks
  survive. (Book §5.1, §10.1)
- **Hand-written code lives in hook files** that regeneration never touches,
  so the author's edits and invariants are never lost.

## Screen

```
+---------------------------------------------------------------------------+
| Customers › ALFKI › Orders › 10643                         (crumb trail)  |
+---------------+-----------------------------------------------------------+
| ENTITIES      |  List part: rows of the selected entity                   |
|  Category     |                                                           |
|  Customer   ◀ |-----------------------------------------------------------|
|  Employee     |  Scalar part: the selected row (form)                     |
|  Order        |                                                           |
|  Product      |-----------------------------------------------------------|
|  …            |  [ Orders | Demographics ]   ← one tab per relationship   |
|               |  small related list (child rows of the selected record)   |
+---------------+-----------------------------------------------------------+
| [New] [Save] [Delete] [Refresh]                               status      |
+---------------------------------------------------------------------------+
```

- **Entity navigator** (left): every resource in the model. Selecting one makes it
  the page: its rows in the List part, nothing selected in the Scalar part.
- **List part**: the entity's rows. Selecting a row shows it in the Scalar part.
- **Scalar part**: the selected record's fields (today's `<Resource>View.xib`).
- **Related tabs**: when the entity has relationships, a tab view under the form
  shows one small list per relationship (e.g. Customer → Orders), filtered to the
  selected record (master-detail).
- **Drill-in**: opening a row in a related list **replaces the page** with that
  entity, positioned on that record, and pushes a crumb. (A modal-dialog variant
  can be added later as an option.)
- **Crumb trail** (top, `pathcontrol`): the navigation stack, e.g.
  `Customers › ALFKI › Orders › 10643`. Clicking a crumb returns to that page and
  record; choosing an entity in the navigator starts a new trail.

## Window layouts (author, 2026-11-24)

A project setting chooses how the generated app shows its entities. The pages are the same in
every layout: each entity's List part, Form part and bindings (`<Entity>List.xib`,
`<Entity>Form.xib`, `<Entity> Binding.incl`); only where they are placed differs, so the layout is
the shell's business (App Shell.incl), not the pages'.

| Layout | What the user sees | Status |
|---|---|---|
| **Single window** | one window: the navigation bar on the left, one entity's page at a time in the content area (the shell as built) | built |
| **Multiple windows** | the main window keeps the header and the navigation bar; choosing an entity opens (or brings forward) **its own window** with its List and Form and its own New / Save / Delete / Refresh. A **Window** menu lists the open entity windows and arranges them: **Stack** (cascade, each offset down and right from the last) and **Tile** (side by side in a grid that fills the screen's visible frame) | next |
| **Tabs** | one window, one tab per entity (or the open ones), the navigation bar optional | future |

Decisions for *Multiple windows*:
- One window per entity, opened once: choosing it again brings it to the front.
- Window tags: a range of their own (e.g. 63000 + page index), clear of the model's tags.
- Each entity window is a standard titled, closable, resizable window titled with the entity's
  Title; closing it does not quit the app (the main window does).
- App Data stays the same: answers go to the window of the entity they name (today they go to
  the page on screen), so `AppDataDone` routes by entity, not by "the current page".
- Stack: windows in navigation order, each 24 points down and right of the previous one,
  starting at the top left of the visible screen. Tile: n windows in ceil(sqrt(n)) columns, rows
  to match, each the same size, filling the visible frame (menu bar and Dock excluded).
- Window menu items: Stack Windows, Tile Windows, then one item per open entity window.

## Designer workflow (generator)

1. **Open** a model — *Model → Open SQLite Database…* (or ALS metadata JSON).
2. **Review the entity definitions.** Selecting an entity shows its summary (key,
   key kind, relationships ↑ toone / ↓ tomany) and one row per attribute: Name,
   **Title** (field label *and* column heading), Data Type, FB Type, Size, Key
   (PK / FK → parent), Required, Default, Form Control, Form Width, List Width,
   Adjusted.
3. **Adjust.** Title, FB Type, Form Control, Form Width and List Width are
   editable; an edit is kept as the designer's adjustment (empty = back to the
   recommendation) in `<project>/Design.json` and re-applied whenever the model is
   opened. The *Adjusted* column shows what was changed.
4. **Generate**, each on its own:

   | Command | Writes |
   |---|---|
   | Generate XIBs | every entity's `<Entity>Form.xib` and `<Entity>List.xib` |
   | Generate XIB for Selected Entity | the selected entity's two parts |
   | Generate Binding Code | `<Entity> Binding.incl` for every entity |
   | Generate App | all of it, plus `Model.json`, `Model Tags.incl`, `<project>.fb`, runtime |

All rules and adjustments live in `src/Generator/Type Mapping.incl`; the XIB and
binding generators read attributes only through it, so what the designer sees is
what gets generated.

## Code organisation

- **One concern per file, aptly named** — in the generator (`SQLite Access`,
  `SQLite Model`, `Type Mapping`, `XIB Generator`, `Binding Generator`,
  `App Generator`) and in generated apps (`<Entity> Binding.incl`,
  `<Entity> Hooks.incl`, runtime files).
- **FB's event model, procedurally.** One `on dialog` / `on menu` handler routes
  events by tag range to per-entity procedures (selection, `_tableViewDoubleAction`
  for drill-in, cell edits, buttons). No imitation of objects; entity behaviour is
  a set of named procedures next to its binding code and hooks.

## Styling and themes

XIBs and AppKit do not understand CSS. What macOS offers — all reachable from FB:

- **System (catalog) colors** in generated XIBs (`labelColor`,
  `controlBackgroundColor`, …) already follow light/dark mode and the accent color.
- **Appearances**: `AppearanceNamed` with `AppSetAppearance`, `WindowSetAppearance`,
  `ViewSetAppearance` force light, dark or vibrant per app, window or view.
- **Named colors** from an asset catalog (`ColorNamed`; FB builds `Assets.xcassets`)
  with light/dark variants.
- **Dynamic colors** computed at run time (`ColorWithName` with a provider callback).
- **Fonts and text colors** per control (`FontWithName`, `ControlSetFont`,
  `TextFieldSetTextColor`).

A CSS-like layer is therefore possible: a **theme file** (JSON) of named styles —
colors with light/dark values, fonts, sizes — and selectors by control kind, entity,
or tag range, applied when a part is loaded. Themes (light, dark, colorful, base)
become files the user switches; the XIBs stay plain. Not built yet (backlog).

## Generated parts (per entity)

| Part | File | Contents |
|---|---|---|
| List | `<Entity>List.xib` | scroll view + view-based table, one column per attribute (identifier = attribute name, heading = Title); tags 20000 + index·10 (+1 scroll, +2 table) |
| Scalar | `<Entity>Form.xib` | Title + control per attribute |
| Related list | built from the child entity's list columns | one per relationship, inside the tab view |

Each part is a self-contained custom view with its own tag range, so parts can be
embedded in any window, and the same entity can appear as a page and as a related
list without tag clashes.

## Model additions

`Model.json` gains, per resource:

```json
"relationships": [
  { "name": "OrderList", "target": "Order", "kind": "toMany",
    "foreignKey": ["customer_id"], "parentKey": ["customer_id"] }
]
```

**Source of relationships** — lite edition: SQLite foreign keys (see below).
ALS edition, still open: `/metadata?include=attributes`
(see `samples/Northwind/metadata.json`) carries no relationships. Candidates:
the ALS model's own relationship info if `/metadata` can include it, the
JSON:API `relationships` member of a fetched record (names + related-resource
links, but not the target type or keys), or ALS's Swagger/OpenAPI document.

## Lite edition (first) — SQLite direct

The first generated apps talk **directly to the SQLite database**; the ALS
middleware (JSON:API) is added later behind the same data interface.

Reference project: `nw/` in FutureBasic_Documentation (ALS Northwind:
`database/db.sqlite`, `database/models.py`, `ui/admin/admin.yaml`).

**Model source**
- **SQLite introspection (authoritative)** — the generator opens the `.sqlite`
  file and reads `sqlite_master`, `PRAGMA table_info` (columns, declared types,
  primary keys, incl. composite) and `PRAGMA foreign_key_list` (relationships,
  incl. composite keys such as `Order(Country, City) → Location`).
  A foreign key gives both directions: `toone` on the child, `tomany` on the parent.
- **`admin.yaml` hints (optional, later)** — ALS's UI model: attribute order and
  labels, `user_key` (the field shown for a record, e.g. Customer → `CompanyName`,
  used in lists and the crumb trail), relationship names (`OrderList`), search/sort.
- **Naming without hints** — follow ALS conventions: tomany = `<Child>List`,
  toone = parent entity name; `user_key` = first text column that is not a key.
- **Entity names** — the table name (ALS class names can differ:
  `CategoryTableNameTest` is class `Category`; `admin.yaml` provides the mapping).

**Data layer** — the DataObject query builder proven in Test_Xib_View
(Select / Insert / Update / Delete dictionaries, parameterized SQL, `SQLBindValues`),
packaged as runtime files. The shell calls a small data interface (list rows,
get row, related rows, insert, update, delete) so the ALS JSON:API client can
replace SQLite later without touching the UI code.

**Identifiers** — SQLite tables and columns can be reserved words (`Order`,
`Union`) or mixed case: generated SQL quotes every identifier (`"Order"`).

## Data access

- Page list: `GET /api/<Entity>?page[limit]=…`
- Related list: `GET /api/<Parent>/<id>/<RelationshipName>` (JSON:API related
  endpoint), or `GET /api/<Child>?filter[<fk>]=<id>`.
- Same ALS client, binding layer and `Model.json` field maps as today.

## Generated code layout (editable, regeneration-safe)

| File | Regenerated? | Purpose |
|---|---|---|
| `<project>.fb` | yes | includes, settings, starts the shell |
| `Model.json`, `Model Tags.incl`, `*.xib` | yes | model and parts |
| `ALS Client/Binding.incl`, `App Shell.incl` | yes | runtime |
| `<Entity> Hooks.incl` | **only if missing** | per-entity customization points (validation, formatting, actions) |
| `App Hooks.incl` | **only if missing** | app-wide customization |

Hand edits go in the hook files; regeneration never overwrites them.

## Build order

0. Model from SQLite introspection (generator) → `Model.json` with keys and relationships.
1. List XIB parts per entity (generator).
2. Shell: navigator + List part + Scalar part, wired to ALS (replaces today's master-detail).
3. Crumb trail and page stack.
4. Relationships in the model, related tabs, drill-in.
5. Hook files for hand edits.
