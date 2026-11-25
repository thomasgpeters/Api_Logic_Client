# Draft post for the FutureBasic list

**Subject:** SQL Generator: use SQLite from FB without writing SQL (MIT, with an example app)

Hi all,

After years of reading this list and borrowing from what you all share, here is something back.

The **SQL Generator** is a small FutureBasic module that writes SQL for you. You describe a
statement with dictionaries and arrays (its tables, columns, joins and filters) and it gives you
the SQL and the values to bind:

```
query = fn InitQueryDictionary
fn AddTableToQuery( query, @"person", @"p" )
fn AddColumnToQuery( query, @"p.surName", @"Surname" )
fn AddFilterToQuery( query, @"p", @"balance", fn NumberWithDouble( 100.0 ), _realType, 0, _isGreaterThan, 0 )
sql = fn GenerateSelectSQL( query )
// SELECT "p"."surName" AS "Surname" FROM "person" AS "p" WHERE "p"."balance" > ?
```

- SELECT with joins and filters (=, <, >, LIKE, IS NULL, AND / OR), INSERT, UPDATE, DELETE
- an INSERT of a whole array of dictionaries (what a SELECT gives back) in one statement
- every value bound to a `?` placeholder, never pasted into the SQL
- names quoted, so tables called Order or Group just work
- an UPDATE or DELETE without a filter is refused, so a whole table is never wiped by accident

It comes as a complete example project: ten examples on a small CRM database, each showing the
FB, the SQL it produced, the values and the result as a SQL command line prints it, plus a user
guide in the Help menu. Open the project, build, run.

MIT licence: use it in anything, change it, pass it on.

[link]

Comments, fixes and ideas are very welcome.

[your name]
