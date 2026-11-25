# SQL Generator for FutureBasic

**Use a SQL database from FutureBasic without writing SQL.** You describe each statement with
Cocoa dictionaries and arrays: its tables, columns, joins and filters. The SQL Generator writes
the SQL, with every value kept apart from it.

This folder is a complete FutureBasic project: the SQL Generator module, a small runner for
SQLite, and an example app that runs ten examples on a three-table CRM database and shows each
step. Open `SQLGeneratorExample.fbeproj` in FutureBasic, build and run.

MIT licence: use it in free or commercial apps, change it, share it.

## What you see

The window opens with all ten examples run, in one scrolling output (Run All runs them again). For
each one it shows the FutureBasic that builds the statement's dictionaries, then - after a blank
line - the SQL it produced, the values for its `?` placeholders, and the result as a SQL command line
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

Help (the ? button, or Command-?) opens the user guide in a window of its own: the object model diagram, then every function explained one by one. It opens in Preview as a PDF, exports as PDF or Rich Text, and shows the diagram full size. The About box says
what the app and the module do.

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

The database is `~/Library/Application Support/SQL Generator Example/crm.sqlite`, made on first
launch with five made-up people. Reset Database makes it again.

## Use it in your own app

Copy four files into your project folder and add them in this order (FutureBasic needs a function
defined before it is used):

| File | What it holds |
|---|---|
| `DataObject.glbl` | the constants: operators, AND / OR, value types |
| `DataObject_Super.incl` | the builders: describe the statement |
| `DataObject.incl` | the SQL: `GenerateSelectSQL` and the others, `QueryParameterValues` |
| `SQL Generator SQLite.incl` | optional: runs the SQL on SQLite (add `-lsqlite3` in Build Settings) |

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

The user guide inside the app covers every function: joins, every filter operator, INSERT
(one row or an array of dictionaries), UPDATE and DELETE.

## How a statement is described

![The SQL Generator's object model: a query is a dictionary of arrays of dictionaries](SQL%20Generator%20Object%20Model.svg)

A query is a dictionary. `AddTableToQuery`, `AddColumnToQuery`, `AddAssociationToQuery` and
`AddFilterToQuery` each add a small dictionary to one of its arrays. INSERT, UPDATE and DELETE
each have a dictionary of their own. The Generate functions read them and write the SQL;
`QueryParameterValues` lists the values for its placeholders, in order.

## What it does for you

- **Parameterized.** Values are bound to `?` placeholders, never pasted into the SQL: no SQL
  injection, no quoting bugs with names like O'Brien.
- **Names quoted.** Tables and columns called `Order`, `Group` or with spaces just work.
- **Safe by default.** An UPDATE or DELETE without a filter gets NULL instead of SQL, so a whole
  table is never changed by accident.
- **Many rows at once.** An array of dictionaries (what a SELECT returns) goes back in with one
  INSERT.

Good to know: IN writes a single `?`, so use OR
filters for a few values; the generator writes queries, not schemas (create tables with plain SQL).

## Files in this folder

| | |
|---|---|
| `DataObject.glbl`, `DataObject_Super.incl`, `DataObject.incl`, `SQL Generator SQLite.incl` | the module |
| `CRM Database.incl` | the example database: tables and sample people |
| `CRM Examples.incl`, `Example Code.txt` | the ten examples, and the FB each one shows |
| `Example Output.incl`, `Rich Text.incl` | the coloured output and the SQL-command-line tables |
| `Help.incl`, `User Guide.txt`, `SQL Generator Diagram.png` | the Help window and its text (simple markup: `#` headings, `**bold**`, code blocks, `![picture]`); Open in Preview, Export (PDF, Rich Text), View Diagram |
| `Windows.incl`, `Menus.incl`, `EventHandlers.incl`, `SQLGeneratorExample.main`, `SQLGeneratorExample.glbl` | the app |
| `Credits.rtf`, `Info.plist` | the About box and the app's name |

Needs FutureBasic 7 on a Mac (built with 7.0.38, Apple Silicon, macOS 15 or later).

---

MIT License. Copyright (c) 2026 Imagery Business Systems, LLC. The SQL Generator comes from
Imagery LogicBank Studio for FutureBasic, where it reads and writes the database of every
generated app.
