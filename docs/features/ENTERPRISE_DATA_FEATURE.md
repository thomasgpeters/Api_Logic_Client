# Enterprise data: the SQL Generator's JSON:API side

The author's design (2026-11-25): the Enterprise edition uses the SQL Generator's own dictionaries
and arrays, and writes JSON:API requests for API Logic Server instead of SQL, from the ALS model.
So the pages, bindings and examples do not know which edition they run on.

## Where

| | |
|---|---|
| `src/Enterprise/ALS Model.incl` | the model from `app_model.yaml` (ALS 17.3 and earlier) or `admin.yaml`: attributes, primary keys, relationships (name, direction, resource, fks), the display column (`favorite` / `user_key`). Line by line by indentation, the design of the C++ Studio's `Model::fromAppModelYaml` |
| `src/Enterprise/DataObject_JSONAPI.incl` | `GenerateJSONAPISelect / Insert / InsertRows / Update / Delete`, `JSONAPIPagePath`, `JSONAPIRowsFromAnswer`, `JSONAPILastError` |
| `src/Runtime/ALS Client.incl` | sends the requests (Bearer token, paging, errors) |
| `tools/jsonapi_reference.py` | the reference and its test: 19 checks against a running server |

## The mapping

| Statement dictionary | SQL | JSON:API |
|---|---|---|
| first table | `FROM` | `/api/<resource>` |
| columns with aliases | `col AS alias` | rows renamed to the aliases; plus `id`, `S_CheckSum` |
| filters | `WHERE ... ?` | `filter=[{"name","op","val"}]` (eq ne lt le gt ge like notilike in notin; null for IS NULL) |
| OR on one column | `OR` | `in` |
| ORDER BY | `ORDER BY` | `sort=a,-b` |
| join to a parent | `WHERE child.fk = parent.key` (inner) | `include=<relationship from the model>`; rows without the parent dropped |
| INSERT / rows | `INSERT ... VALUES` | `POST` (one per row) |
| UPDATE / DELETE with one `=` key filter | `UPDATE ... WHERE` / `DELETE ... WHERE` | `PATCH` / `DELETE /api/<resource>/<id>` |

Refused (NULL, `JSONAPILastError`): OR across columns, a filter or sort on a joined parent, a join
the model has no relationship for, an UPDATE or DELETE without one `=` filter. Names are resource
names (Northwind: `Category` is table `CategoryTableNameTest`).

## Decisions

- **The model is API Logic Server's, never FutureBasic's** (author, 2026-11-25). The Studio points
  at the ALS project the app is built from (its folder or repository) and reads the model ALS
  generated there: `ui/app/app_model.yaml` (ALS 17.3 and earlier), else `database/models.py`
  (current ALS: types, primary keys, foreign keys, relationship names), with `ui/admin/admin.yaml`
  for labels and the display column. Read as text (as the C++ Studio does), never run.
- The two editions mirror each other (author): Lite points at the **SQLite file** and reads the
  model from the database itself (`SQLite Model.incl`); Enterprise points at the **ALS project** and
  reads the model ALS generated. Enterprise cannot read the server's database instead: the app speaks
  to ALS in ALS's names - resources (Category, stored in CategoryTableNameTest) and relationships
  (WorksForDepartment) - which only ALS's model has.

- The model file: `app_model.yaml` (author), read with the same reader as `admin.yaml` (same shape);
  current ALS (17.04+) writes only `admin.yaml` - and `database/models.py`, which the author's
  onboarding guide ranks first (a reader for it: backlog). `/metadata` has no relationships.
- Relationship names are never guessed (Employee has two to Department).
- Inner-join rows on the JSON:API side, so both sides return the same rows.

## Verify

- [x] `jsonapi_reference.py`: 19 checks against ALS 17.05 Northwind (same rows both ways; writes read back)
- [ ] The FB code on a Mac: lint passes; first use comes with App Data Enterprise
