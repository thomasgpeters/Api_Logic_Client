# Data Runtime (SQLite records)

**Where:** `src/Runtime/` — copied into every generated app, first in its Runtime group:

| File | Layer | Does |
|---|---|---|
| `Data SQLite.incl` | SQLite | our own declarations against SQLite's public C API: open read-write (never creates a file), prepare, bind, step, column values, `DataExecute`, `DataBegin` / `DataEnd` |
| `DataObject.glbl`, `DataObject_Super.incl`, `DataObject.incl` | SQL | the author's DataObject query builder (shared with Test_Xib_View): describe a statement, generate parameterized SQL |
| `Data Model.incl` | model | entities from `Model.json`: columns, keys, keyKind, relationships, `database` |
| `Data Records.incl` | records | `DataOpen`, `DataFetch`, `DataFetchOne`, `DataParent`, `DataChildren`, `DataInsert`, `DataUpdate`, `DataDelete`, `DataKeyValues` |

The layer the app shell and the **rules engine** (`design/Logic Engine Design.md`) sit on:
the engine needs exactly these calls — read a row by key, its parent along a role, its
children along a list, write rows, and one transaction around a save and everything it
chains to.

## How it works

- **Records** are mutable dictionaries, column name → `NSNumber` / `NSString` / `NSData` /
  `NSNull` (`fn DataNull`; CF collections cannot hold NULL). Values bind by their class:
  NSNumber holding a float → REAL, other NSNumber → INTEGER, NSData → BLOB, NSNull →
  NULL, anything else → TEXT. Columns come back the same way.
- **The database** is the project's own copy: Generate App writes its path to `Model.json`
  (`"database"`), and the generated `.main` calls `fn DataOpen( NULL )`. ALS projects
  (metadata JSON) get no database and no `DataOpen`.
- **Transactions nest.** `DataBegin` / `DataEnd( keep )`: only the outermost pair sends
  `BEGIN IMMEDIATE` / `COMMIT`. Any part that ends with `keep = NO` makes the outermost
  `DataEnd` roll back — how a failed rule will undo a save and everything it chained to.
- **Relationships** use the model's names: `DataParent( @"Order", anOrder, @"Customer" )`,
  `DataChildren( @"Customer", aCustomer, @"OrderList" )` (`fks` / `parentKeys` from the
  SQLite model).
- **Inserts** leave out an empty identity / autoincrement key and set it in the record from
  `last_insert_rowid()` afterwards. Updates take the *old* key values, so a key can change.
  Views are read-only.
- **Errors** always log (prepare/step message, SQL, values); trace logging is gated on
  `isLoggingOn`, which the generated `.main` sets.

## Changes to the query builder (both repositories)

- Every table, column and alias name is quoted (`QuoteSQLName`): `Order` → `"Order"`,
  `a.id` → `"a"."id"`; names already quoted (`'Given Name'`) are kept.
- `GenerateSelectSQL` released `myOperator`, a value it only read from a dictionary
  (`CFDictionaryGetValue` does not transfer ownership) — an over-release that could crash
  a SELECT with joins. Removed.
- CF calls replaced by FB's Cocoa wrappers (`DictionaryObjectForKey`,
  `MutableDictionarySetObjectForKey`, `MutableArrayNew`, `MutableArrayAddObject`,
  `MutableStringAppendString`, `ArrayCount`, `ArrayObjectAtIndex`, `NumberWithInteger`);
  CF type names replaced by FB's current ones (`StringRef`, `DictionaryRef`, `ArrayRef`, …).
  `CFNumberCreate` results were never released (leak) — gone with it.
- `AddFilterToQuery`'s value is a `CFTypeRef` (strings, numbers or NSNull).
- New `QueryParameterValues( statement )`: the values in `?` order (SET/VALUES, then
  filters; `IS NULL` takes none).
- The local `sqlAssociationCount` is reset before use.

## Verified here

The SQL the layer generates — quoting, `IS NULL`, `ORDER BY`, parent/children through
`fks`/`parentKeys`, INSERT/UPDATE/DELETE on `"Order"` inside a rolled-back transaction —
ran against the Northwind SQLite copy with the model from `tools/sqlite_model.py`
(ALFKI: 6 orders; 23 unshipped). fblint: 0 problems on the runtime and on a generated-project
layout (build order checked).

## Verify on a Mac
- [ ] Generate App; the project builds with the Data files first in the Runtime group
- [ ] NSLog shows "Data: opened …/Database/db.sqlite" at launch
- [ ] Test_Xib_View still lists, inserts, updates and deletes persons (builder changes)
