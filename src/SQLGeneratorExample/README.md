# SQL Generator for FutureBasic

If you'd like to use a SQL database from FutureBasic without writing the SQL yourself, this module is for you.
You describe each statement with Cocoa dictionaries and arrays (its tables, columns, joins and filters), and
the SQL Generator writes the SQL, keeping every value apart from it.

This folder is a complete FutureBasic project. It holds the SQL Generator module, a small runner for SQLite,
and an example app that runs ten examples on a three-table CRM database and shows you each step. Open
`SQLGeneratorExample.fbeproj` in FutureBasic, build and run.

It's MIT licensed, so you're welcome to use it in free or commercial apps, change it and share it.

## What you see

When the window opens, all ten examples have already run, in one scrolling output (Run All runs them again).
For each one you'll see the FutureBasic that builds the statement's dictionaries. After a blank line come the
SQL it produced, the values for its `?` placeholders, and the result, printed the way a SQL command line
prints it:

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

Help (the ? button, or Command-?) opens the user guide in its own window. It starts with the object model
diagram and then explains every function in turn. You can open it in Preview as a PDF, export it as PDF or
Rich Text, and view the diagram full size. The About box tells you what the app and the module do.

## The examples

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

The database lives at `~/Library/Application Support/SQL Generator Example/crm.sqlite`. It's made the first
time you launch the app, with five made-up people, and Reset Database makes it again.

## Use it in your own app

You only need the FutureBasic editor and the Finder. The Help window (and `User Guide.txt`) walks through
every step; here's the short version.

1. Copy these four files into your project's folder:

   | File | What it holds |
   |---|---|
   | `DataObject.glbl` | the constants: operators, AND / OR, value types |
   | `DataObject_Super.incl` | the builders: describe the statement |
   | `DataObject.incl` | the SQL: `GenerateSelectSQL` and the others, `QueryParameterValues` |
   | `SQL Generator SQLite.incl` | optional: runs the SQL on SQLite |

2. Drag them into your project's window in the FutureBasic editor, above your own files and in the order
   above. FutureBasic builds from the top of the list down, and a function has to be defined before it's
   used. `SQLGeneratorExample.fbeproj` shows the order.
3. Link SQLite: in Build Settings, add `-lsqlite3 -Wno-unused-command-line-argument` to Compiler options.
4. Open the database and create its tables with plain SQL (`CREATE TABLE IF NOT EXISTS ...`), because a new
   database file starts out empty.
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

If you're writing a single-file program rather than a project, include the four files at the top and link
SQLite with `#build CompilerOptions @"-lsqlite3 -Wno-unused-command-line-argument"`.
`SQL Generator - Smallest Program.fb` is a complete one in about 60 lines; open it in FutureBasic and run it.

The Help window explains every function: joins, each filter operator, INSERT (one row or an array of
dictionaries), UPDATE and DELETE, and the SQLite runner.

## How a statement is described

![The SQL Generator's object model: a query is a dictionary of arrays of dictionaries](SQL%20Generator%20Object%20Model.svg)

A query is a dictionary. `AddTableToQuery`, `AddColumnToQuery`, `AddAssociationToQuery` and
`AddFilterToQuery` each add a small dictionary to one of its arrays, and INSERT, UPDATE and DELETE each have
a dictionary of their own. The Generate functions read them and write the SQL, while `QueryParameterValues`
lists the values for its placeholders, in order.

## What it takes care of

Values are bound to `?` placeholders and never pasted into the SQL, so there's no SQL injection and no
quoting trouble with names like O'Brien. Table and column names are quoted too, which means `Order`,
`Group` or names with spaces just work.

An UPDATE or DELETE without a filter gets NULL instead of SQL, so you can't change a whole table by
accident. And an array of dictionaries (what a SELECT gives you) goes back in with one INSERT.

A couple of things to know: IN writes a single `?`, so use OR filters when you have a few values. The
generator writes queries and leaves schemas to you; create your tables with plain SQL.

## Files in this folder

| | |
|---|---|
| `DataObject.glbl`, `DataObject_Super.incl`, `DataObject.incl`, `SQL Generator SQLite.incl` | the module |
| `SQL Generator - Smallest Program.fb` | the module in the fewest lines: a single-file program to open and run |
| `CRM Database.incl` | the example database: tables and sample people |
| `CRM Examples.incl`, `Example Code.txt` | the ten examples, and the FB each one shows |
| `Example Output.incl`, `Rich Text.incl` | the coloured output and the SQL-command-line tables |
| `Help.incl`, `User Guide.txt`, `SQL Generator Diagram.png` | the Help window and its text (simple markup: `#` headings, `**bold**`, code blocks, `![picture]`); Open in Preview, Export (PDF, Rich Text), View Diagram |
| `Windows.incl`, `Menus.incl`, `EventHandlers.incl`, `SQLGeneratorExample.main`, `SQLGeneratorExample.glbl` | the app |
| `Credits.rtf`, `Info.plist` | the About box and the app's name |

You'll need FutureBasic 7 on a Mac (it's built with 7.0.38, on Apple Silicon, for macOS 15 or later).

---

MIT License. Copyright (c) 2026 Imagery Business Systems, LLC. The SQL Generator comes from App Builder for
FutureBasic, where it reads and writes the database of every app App Builder generates.
