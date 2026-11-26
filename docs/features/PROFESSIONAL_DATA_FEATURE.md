# Professional data: the SQL Generator's JSON:API side

The author's design (2026-11-25): the Professional edition uses the SQL Generator's own dictionaries
and arrays, and writes JSON:API requests for API Logic Server instead of SQL, from the ALS model.
So the pages, bindings and examples do not know which edition they run on.

## Where

| | |
|---|---|
| `src/AppBuilder/ALS Model.incl` (the Studio reads it too: `features/ALS_PROJECT_FEATURE.md`) | the model from `database/models.py` (every ALS project; the only model file from 17.04 on: `ALSModelFromModelsPy`, read as text, never run), or from `app_model.yaml` (ALS 17.3 and earlier) or `admin.yaml`; `ALSModelFromText` tells them apart by their contents: attributes, primary keys, relationships (name, direction, resource, fks), the display column (`favorite` / `user_key`). Line by line by indentation, the design of the C++ Studio's `Model::fromAppModelYaml` |
| `src/Professional/DataObject_JSONAPI.incl` | `GenerateJSONAPISelect / Insert / InsertRows / Update / Delete`, `JSONAPIPagePath`, `JSONAPIRowsFromAnswer`, `JSONAPILastError` |
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
  generated there: `database/models.py` (every project: types, primary keys, foreign keys,
  relationship names), else `ui/app/app_model.yaml` (ALS 17.3 and earlier), with `ui/admin/admin.yaml`
  for the display column. Built: Open ALS Project (`features/ALS_PROJECT_FEATURE.md`). Read as text (as the C++ Studio does), never run.
- **From a public GitHub repository** (author, 2026-11-25): the repository's address (and a branch,
  `main` by default) is enough. The Studio reads the model file over plain HTTPS, no sign-in:
  `https://raw.githubusercontent.com/<owner>/<repo>/<branch>/<path>`, trying `database/models.py`,
  then `ui/app/app_model.yaml`, then `ui/admin/admin.yaml` (a path can be given), and `master` when
  `main` is not there. Checked from the cloud session: a raw file answers 200; GitHub's API
  (`api.github.com`) is not needed (it refused here, 403, and is rate-limited without a token).
  The copy is kept in `<project>/ALS Model/` with its address and date in `Project.json`; *Refresh
  Model* fetches it again. Raw files can lag a push by a few minutes (GitHub's cache). A private
  repository needs a token (the Keychain) - later.
- **No repository access? Drop the model file** (author, 2026-11-25; Professional): the Professional
  New Project screen takes the ALS project three ways - choose its folder (a clone of its
  repository), **drag and drop** the model file onto a drop zone (`app_model.yaml`, `models.py` or
  `admin.yaml`, or the whole project folder), or Choose... the file in an open panel (the fallback
  that always works). The Studio keeps a copy of the dropped file in the project (`<project>/ALS
  Model/`), so the model is there next time without the original. FB: a view registered for
  `NSPasteboardTypeFileURL` drags, `_viewDraggingEntered` / `_viewPerformDragOperation` (FBExamples,
  TableView Drag Drop).
- The two editions mirror each other (author): Lite points at the **SQLite file** and reads the
  model from the database itself (`SQLite Model.incl`); Professional points at the **ALS project** and
  reads the model ALS generated. Professional cannot read the server's database instead: the app speaks
  to ALS in ALS's names - resources (Category, stored in CategoryTableNameTest) and relationships
  (WorksForDepartment) - which only ALS's model has.

- The model file: `database/models.py` - in the same place for any database (checked: `ApiLogicServer
  create` on Northwind and on the CRM's contacts.sqlite, ALS 17.05.44; neither has `app_model.yaml`).
  **Parsed as text, never run** (author, 2026-11-25: no Python interpreter inside FutureBasic). The
  lines read: `class X(Base)`, `__tablename__`, `_s_collection_name`, `Column(...)` (type, primary key,
  `ForeignKey('table.col')`, `nullable=False`), `Mapped["X"]` / `Mapped[List["X"]]` relationships with
  `foreign_keys` and `back_populates`, `ForeignKeyConstraint` (composite keys); `Table(...)` views
  skipped. A to-many's key columns are its child's to-one that points back: by name *and* class
  (Customer, Employee and Location each have an `OrderList`). The model is keyed by resource, as
  `admin.yaml` keys it. No display column in models.py: `admin.yaml`'s `user_key` when there.
  `app_model.yaml` / `admin.yaml` (older projects) keep their reader. `/metadata` has no relationships.
- Relationship names are never guessed (Employee has two to Department).
- Inner-join rows on the JSON:API side, so both sides return the same rows.

## Verify

- `tools/models_py_reference.py <ALS project> <ALS venv python>`: models.py read as text against
  SQLAlchemy's own mappers on the same file - every class, table, attribute, primary key and
  relationship (name, direction, resource, key columns). Passes on Northwind (17 classes: role names,
  self and composite relationships) and the CRM (3). In `run_tests.sh` when `ALS_PROJECTS` and
  `ALS_PYTHON` are set. The FB port follows the reference line for line (fblint clean); it runs on a Mac.

- [x] `jsonapi_reference.py`: 19 checks against ALS 17.05 Northwind (same rows both ways; writes read back)
- [ ] The FB code on a Mac: lint passes; first use comes with App Data Professional
