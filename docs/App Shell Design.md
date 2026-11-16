# Generated App Shell — Design

The generator turns any ALS model into a **generic base app**: one shell, many
entities, built from embeddable XIB parts. The author then edits and extends
the generated app, so the output must be readable, modular, and safe to regenerate.

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

**Source of relationships — open question.** `/metadata?include=attributes`
(see `Samples/Northwind/metadata.json`) carries no relationships. Candidates:
the ALS model's own relationship info if `/metadata` can include it, the
JSON:API `relationships` member of a fetched record (names + related-resource
links, but not the target type or keys), or ALS's Swagger/OpenAPI document.

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

1. List XIB parts per entity (generator).
2. Shell: navigator + List part + Scalar part, wired to ALS (replaces today's master-detail).
3. Crumb trail and page stack.
4. Relationships in the model, related tabs, drill-in.
5. Hook files for hand edits.
