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

## Generated parts (per entity)

| Part | File | Contents |
|---|---|---|
| List | `<Entity>List.xib` | scroll view + table, one column per attribute (identifier = attribute name) |
| Scalar | `<Entity>Form.xib` | label + control per attribute (existing generator) |
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
(see `Samples/Northwind/metadata.json`) carries no relationships. Candidates:
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
