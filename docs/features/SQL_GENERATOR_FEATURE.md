# SQL Generator (module and example project)

The author's query builder (`DataObject.glbl`, `DataObject_Super.incl`, `DataObject.incl`): a
statement is described in dictionaries and arrays, the generator writes parameterized SQL and
lists the values for its placeholders. It is the data runtime's SQL in every generated app, the
SQL of Test_Xib_View, and since 2026-11-25 a module shared on its own (MIT).

## Where

| | |
|---|---|
| `src/Runtime/DataObject*.{glbl,incl}` | the copy generated apps get |
| `src/SQLGeneratorExample/` | the example project (FB project from `src/CleanApp`) with the module, `SQL Generator SQLite.incl` (a runner), ten examples on a CRM database, the Help window, About box, `README.md`, `LICENSE` (MIT), `ANNOUNCEMENT.md` (draft for the FB list) |
| Test_Xib_View `DataObject*` | the author's app |
| `docs/design/SQL Generator Object Model.svg` | the object model, drawn by `tools/make_sql_generator_svg.py` |

The three copies stay identical: `tools/run_tests.sh` checks it.

## The model

`InitQueryDictionary` -> `selecttables`, `selectcols`, `associations`, `filter` (arrays of
dictionaries; `metadata`, `results` unused). INSERT: `insertintotable` + `columnvalues`. Rows:
`insertintotable` + `rows` (array of column -> value) + `columnnames` (the rows' keys, sorted, or
`SetInsertColumns`). UPDATE: `updatetable` + `columnvalues` + `filter`. DELETE:
`deletefromtable` + `filter`. `QueryParameterValues`: column values, then rows, then filters
(IS NULL / IS NOT NULL take none).

## Decisions and fixes (2026-11-25)

- `associations` was created as a dictionary but used as an array: the first join would have
  crashed (`-[__NSDictionaryM addObject:]`). Nothing used joins yet; fixed in every copy.
- New: `InitInsertRowsDictionary`, `AddRowsToInsert`, `SetInsertColumns`, `GenerateInsertRowsSQL`
  (author: an INSERT from an array of dictionaries, the opposite of a SELECT's result).
- Leftovers removed for the public release (`_noNaxCharacters`, `_taskCol`, `_priorityCol`, a
  commented-out block); MIT headers; comments name the module, not one project.
- Known limits, documented: no ORDER BY in the builder (appended by hand); `IN ( ? )` takes one
  value; no schema statements.

## The example app

A window (Run All, Clear, Reset Database, ?) and one scrolling rich-text output with every example run at launch (author, 2026-11-25: no example popup): the FB
(purple), the SQL with a `sqlite>` prompt (blue), the values (teal), results as a SQL command line
prints them (Menlo, `+---+` borders, numbers right-aligned, "n rows in set", "Query OK, 1 row
affected"); also to NSLog (Examples > Also Log to NSLog). Help opens `User Guide.txt` in its own window (author, 2026-11-25): a heading and opening
paragraph, the object model diagram (`SQL Generator Diagram.png`, made from the SVG by
`tools/svg_to_png.js`, light colours, 2x; `![name]` in the markup), how it fits together, then
every function one by one, the runner's too. **Open in Preview** writes it as a paginated PDF
(a print job saved to a file, in the light appearance) and opens it in Preview; **Export…** saves
PDF or Rich Text with the diagram (RTFD); **View Diagram** shows the diagram full size in its own
window (zoom, full screen). Also in the Help menu.
window, styled from simple markup by `Rich Text.incl` with system colours (light and dark). The
About box is `Credits.rtf`. The database: `~/Library/Application Support/SQL Generator Example/crm.sqlite`,
five made-up people, made through the INSERT builder.

## Verify on a Mac

- [ ] The example project builds (FB 7.0.38) and runs; Run All shows all ten examples
- [ ] Joins (examples 2, 4) work - the first real use of `AddAssociationToQuery`
- [ ] Example 10 inserts three rows in one statement; example 1 then lists them
- [ ] Help window: headings, bold, coloured code blocks, the diagram, in light and dark mode; Open in Preview (black on white even in dark mode); Export as PDF and as Rich Text (opens in TextEdit with the diagram); View Diagram (zoom, full screen)
- [ ] About box shows the tag-line and what the module does
