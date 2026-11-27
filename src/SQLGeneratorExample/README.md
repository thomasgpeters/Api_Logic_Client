# SQL Generator for FutureBasic

Use a SQL database from FutureBasic without writing the SQL yourself. You describe each statement with
dictionaries and arrays (its tables, columns, joins and filters), and the SQL Generator writes the SQL, with
every value kept apart from it.

It's free and MIT licensed: use it in free or commercial apps, change it, share it.

## Start small

The quickest way in is the one-file demo. Download `SQL-Generator-Module.zip` (the module's four files and
the demo), or take the same files from this folder:

1. Keep the files together in one folder.
2. Open `SQL Generator - Smallest Program.fb` in FutureBasic and run it.
3. Watch the NSLog window: the SQL it wrote, and the rows it read back.

The demo is about 40 lines of code. It makes a small table, adds three people with one INSERT, and reads
back the two with a balance over 100.

## The example app

When you want more, this folder is also a complete project. Open `SQLGeneratorExample.fbeproj` in
FutureBasic, build and run. Ten examples run on a three-table CRM database, and for each one you see the
FutureBasic that describes the statement, the SQL it produced, the values for its `?` placeholders, and the
result, printed the way a SQL command line prints it:

```
sqlite> SELECT "p"."givenName" AS "Given Name", "p"."surName" AS "Surname", "a"."street" AS "Street",
        "a"."apartment" AS "Apartment", "a"."city" AS "City" FROM "person" AS "p", "address" AS "a"
        WHERE "a"."personID" = "p"."id" AND "p"."surName" = ?;
   -> values for ?: 'Fischer'
+------------+---------+--------------+-----------+---------+
| Given Name | Surname | Street       | Apartment | City    |
+------------+---------+--------------+-----------+---------+
| Lena       | Fischer | 5 Mill Ln.   | NULL      | Madison |
| Lena       | Fischer | 300 Lake Dr. | Apt. 12   | Madison |
+------------+---------+--------------+-----------+---------+
2 rows in set
```

| | Shows |
|---|---|
| 1 | everyone, by surname: a SELECT with ORDER BY (`AddOrderToQuery`) |
| 2 | a person and their addresses: a join and a filter |
| 3 | addresses without an apartment: IS NULL |
| 4 | email addresses at test.com: LIKE, AND |
| 5 | one surname, or a balance over 1000: OR |
| 6 | add a person and their email: INSERT, and the new id |
| 7 | change a balance: UPDATE |
| 8 | remove a phone number: DELETE |
| 9 | change every balance with no filter: refused, no SQL |
| 10 | add three people at once: an INSERT of an array of dictionaries |

All ten run when the window opens; Run All runs them again. The database is made the first time you launch
the app, with five made-up people, at `~/Library/Application Support/SQL Generator Example/crm.sqlite`, and
Reset Database makes it again.

Help (the ? button, or Command-?) is the user guide. It starts with the object model diagram and explains
every function: joins, each filter operator, INSERT (one row or an array of dictionaries), UPDATE, DELETE and
the SQLite runner. You can open it in Preview, export it as PDF or Rich Text, and view the diagram full size.

## Use it in your own app

All you need is the FutureBasic editor. The module is four files:

| File | What it holds |
|---|---|
| `DataObject.glbl` | the constants: operators, AND / OR, value types |
| `DataObject_Super.incl` | the builders that describe a statement |
| `DataObject.incl` | the SQL: `GenerateSelectSQL` and the others, `QueryParameterValues` |
| `SQL Generator SQLite.incl` | optional: runs the SQL on SQLite |

1. Copy the four files into your project's folder.
2. Drag them into your project's window, above your own files and in the order above. FutureBasic builds
   from the top of the list down, and a function must be defined before it's used.
   `SQLGeneratorExample.fbeproj` shows the order.
3. Link SQLite: in Build Settings, add `-lsqlite3 -Wno-unused-command-line-argument` to Compiler options.
4. Open the database and create its tables with plain SQL (`CREATE TABLE IF NOT EXISTS ...`). A new
   database file starts out empty, and the generator writes queries, not schemas.
5. Describe, generate and run:

```
query = fn InitQueryDictionary
fn AddTableToQuery( query, @"person", @"p" )
fn AddColumnToQuery( query, @"p.surName", @"Surname" )
fn AddFilterToQuery( query, @"p", @"balance", fn NumberWithDouble( 100.0 ), _realType, 0, _isGreaterThan, 0 )
sql = fn GenerateSelectSQL( query )
// SELECT "p"."surName" AS "Surname" FROM "person" AS "p" WHERE "p"."balance" > ?

rows = fn MutableArrayNew
fn SQLGenExecute( db, sql, fn QueryParameterValues( query ), rows )   // rows: dictionaries, "Surname" -> value
```

In a single-file program, include the four files at the top instead, and link SQLite with
`#build CompilerOptions @"-lsqlite3 -Wno-unused-command-line-argument"`, as the one-file demo does.

## How a statement is described

![The SQL Generator's object model: a query is a dictionary of arrays of dictionaries](SQL%20Generator%20Object%20Model.svg)

A query is a dictionary. `AddTableToQuery`, `AddColumnToQuery`, `AddAssociationToQuery` and
`AddFilterToQuery` each add a small dictionary to one of its arrays; INSERT, UPDATE and DELETE each have a
dictionary of their own. The Generate functions read them and write the SQL, and `QueryParameterValues`
lists the values for its placeholders, in order.

## What it takes care of

- Values are bound to `?` placeholders, never pasted into the SQL: no SQL injection, and no quoting
  trouble with names like O'Brien.
- Table and column names are quoted, so `Order`, `Group` or names with spaces just work.
- An UPDATE or DELETE without a filter gets NULL instead of SQL, so you can't change a whole table by
  accident.
- An array of dictionaries (what a SELECT gives you) goes back in with one INSERT.

Two things to know: IN writes a single `?`, so use OR filters for a few values; and you create your tables
yourself, with plain SQL.

## Files in this folder

| | |
|---|---|
| `DataObject.glbl`, `DataObject_Super.incl`, `DataObject.incl`, `SQL Generator SQLite.incl` | the module |
| `SQL Generator - Smallest Program.fb` | the one-file demo |
| `CRM Database.incl` | the example database: tables and sample people |
| `CRM Examples.incl`, `Example Code.txt` | the ten examples, and the FB each one shows |
| `Example Output.incl`, `Rich Text.incl` | the coloured output and the SQL-command-line tables |
| `Help.incl`, `User Guide.txt`, `SQL Generator Diagram.png` | the Help window and its text |
| `Windows.incl`, `Menus.incl`, `EventHandlers.incl`, `SQLGeneratorExample.main`, `SQLGeneratorExample.glbl` | the app |
| `About Imagery.incl`, `About Imagery.txt`, `Credits.rtf`, `Info.plist` | the About boxes and the app's name |

It needs FutureBasic 7 on a Mac (built with 7.0.38 on Apple Silicon, for macOS 15 or later).

---

MIT License. Copyright (c) 2026 Imagery Business Systems, LLC. The SQL Generator also reads and writes the
database of every app that App Builder for FutureBasic generates.
