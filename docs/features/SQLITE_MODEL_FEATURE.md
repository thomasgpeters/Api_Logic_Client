# SQLite Model

Reads a data model straight from a SQLite database's own structure: the lite
edition needs no server and no metadata file.

**Where:** `src/Generator/SQLite Model.incl` (model), `src/Generator/SQLite Access.incl`
(our own SQLite declarations), *Model → Open SQLite Database…* (⌘D) in
`Project Actions.incl`. Reference implementation: `tools/sqlite_model.py`.

## What it reads

| Source | Gives |
|---|---|
| `sqlite_master` | tables and views, and each table's SQL (for `AUTOINCREMENT`, `WITHOUT ROWID`) |
| `pragma_table_info(t)` | columns in order: name, declared type, NOT NULL, default, primary-key position |
| `pragma_foreign_key_list(t)` | foreign keys, grouped by id — composite keys stay one relationship |

## Model per entity

- `attributes` `[{name, type, notnull, default, pk}]`, `keys` (in key order)
- `keyKind`:

  | keyKind | Detected by | On insert |
  |---|---|---|
  | `identity` | single `INTEGER PRIMARY KEY` (rowid alias) | omit the key; read `last_insert_rowid()` |
  | `autoincrement` | the same + `AUTOINCREMENT` (ids never reused; tracked in `sqlite_sequence`) | same |
  | `assigned` | any other key (text, composite) | user enters it on New |
  | `none` | no primary key (e.g. views) | — |

  A `guid` kind is planned: keys generated with Cocoa `fn UUIDString( fn UUIDInit )`
  (store lower-case `TEXT`). SQLite has no `uuid()`; a `randomblob()` default works but
  hides the new key from `last_insert_rowid()`.
- `relationships` — every foreign key in both directions:
  `toone` on the child, `tomany` on the parent, with `fks` and `parentKeys`
  (an empty target column means the parent's primary key).

## Naming (API Logic Server conventions)

`toone` = parent table name; `tomany` = `<Child>List`. When a child has several
keys to one parent (Employee → Department), names come from the key column without
`Id`: `OnLoanDepartment` / `OnLoanEmployeeList`, `WorksForDepartment` /
`WorksForEmployeeList`. On Northwind this matches ALS's `admin.yaml` everywhere
except `OnLoanEmployeeList` (ALS: `EmployeeList`), a deliberate disambiguation.

## Northwind findings

17 tables + 1 view; 12 identity keys (7 `AUTOINCREMENT`), 5 assigned (text `Id`s and
the composite `Location(country, city)`); 14 relationships incl. the composite
`Order(Country, City) → Location`; no triggers; column defaults (`OrderCount 0`,
`Quantity 1`). Computed-looking columns (`Customer.Balance`, `OrderCount`) are plain
stored values — ALS would maintain them with LogicBank rules (see ROADMAP: LogicBank
for FutureBasic).

## Verified

`tools/sqlite_model.py` against Northwind's `db.sqlite`; the FB reader's own SQL
strings executed against the same file; fblint clean.
