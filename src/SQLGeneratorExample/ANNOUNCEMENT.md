# Draft post for the FutureBasic list

Plain text, no attachments: everything is on the web page the post links to (the list's storage fills up).
The link is the SQL Generator's page on Imagery's FutureBasic site (`tools/make_site.py` builds it), or the
GitHub page if that goes up first.

---

**Subject:** Back again, with an old friend: the SQL Generator

Hi all,

I owe the list an apology. I have been quiet for a long while, reading now and then but not
joining in. Life and work took over. I am sorry for that, and glad to be back.

I come bearing a small gift. Some of you may remember the SQL Generator, my little module for
building SQL from dictionaries. I have dusted it off and brought it up to date for FB 7.

The idea is simple. You describe what you want, and it writes the SQL for you:

```
query = fn InitQueryDictionary
fn AddTableToQuery( query, @"person", @"p" )
fn AddColumnToQuery( query, @"p.surName", @"Surname" )
fn AddFilterToQuery( query, @"p", @"balance", fn NumberWithDouble( 100.0 ), _realType, 0, _isGreaterThan, 0 )
sql = fn GenerateSelectSQL( query )
```

That gives you:

```
SELECT "p"."surName" AS "Surname" FROM "person" AS "p" WHERE "p"."balance" > ?
```

The values go in separately, so no quotes to fuss over.

If you want to try it, start small. There is a single-file program, about forty lines of code, that makes
a little table, adds three people and reads two of them back. Put it in a folder with the module's
four files, open it, run it, and watch the NSLog window.

When you want more, there is also an example app with ten examples, each showing the FB code,
the SQL it wrote, and the result. You do not need it to use the module.

Everything is on one page, so nothing clogs the list:

[link to the SQL Generator page]

It is free (MIT licence). Questions and suggestions are welcome, here or by email.

Good to be back,

[your name]
