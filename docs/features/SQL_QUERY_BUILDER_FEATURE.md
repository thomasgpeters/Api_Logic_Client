# SQL Query Builder

Parameterized SQL from statement dictionaries — the data layer the lite edition
will package as runtime files. Lives in **Test_Xib_View** today
(`DataObject_Super.incl`, `DataObject.incl`, `SQLite Interface.incl`).

| Statement | Describe | Generate | Run |
|---|---|---|---|
| SELECT | `InitQueryDictionary`, `AddTableToQuery`, `AddColumnToQuery`, `AddFilterToQuery`, `AddAssociationToQuery` (joins) | `GenerateSelectSQL` | `BuildPreparedStatement_Select` + `ExecutePreparedStatement` |
| INSERT | `InitInsertIntoDictionary`, `AddTableToInsert`, `AddColumnToInsert` | `GenerateInsertIntoSQL` | `ExecuteInsert` → new id |
| UPDATE | `InitUpdateDictionary`, `AddTableToUpdate`, `AddColumnToUpdate`, `AddFilterToQuery` (alias `@""`) | `GenerateUpdateSQL` | `ExecuteUpdate` → rows changed |
| DELETE | `InitDeleteFromDictionary`, `AddTableToDelete`, `AddFilterToQuery` | `GenerateDeleteFromSQL` | `ExecuteDelete` → rows deleted |

- One binder, `SQLBindValues`, binds values in placeholder order; values may be
  strings or numbers; text binds with length -1 (UTF-8 safe); `IS NULL` filters
  have no placeholder.
- UPDATE and DELETE without a filter are refused.
- Filters after the first default to AND; `IN ( ? )`; joins put AND between conditions.
- Example: `InsertPersonRecord`, `UpdatePersonRecord`, `DeletePersonRecord`
  (deletes the person's contacts and addresses first — SQLite enforces foreign keys
  only when the connection turns them on).
- Planned: UPSERT (`INSERT … ON CONFLICT ( key ) DO UPDATE SET … = excluded.…`, SQLite 3.24+).

Verified by porting the generators and binder to Python and running the statements
against `contacts.sqlite`.
