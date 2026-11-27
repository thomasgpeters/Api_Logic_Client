# Draft post for the FutureBasic list

Plain text, no attachments: everything is on the web page the post links to (the list's storage fills up).
Written in the author's own style: short, direct, the point first.

---

**Subject:** SQL Generator is back

Hi all,

Sorry I've been quiet for a while. I've brought back my SQL Generator, updated for FB 7.

You describe the query, it writes the SQL:

```
query = fn InitQueryDictionary
fn AddTableToQuery( query, @"person", @"p" )
fn AddColumnToQuery( query, @"p.surName", @"Surname" )
fn AddFilterToQuery( query, @"p", @"balance", fn NumberWithDouble( 100.0 ), _realType, 0, _isGreaterThan, 0 )
sql = fn GenerateSelectSQL( query )
```

which gives:

```
SELECT "p"."surName" AS "Surname" FROM "person" AS "p" WHERE "p"."balance" > ?
```

To try it, start with the one-file demo (about 40 lines). There's also a sample app with ten
examples if you want more.

Everything is here, no attachments: [link]

Free, MIT licence. Questions welcome.

[your name]
