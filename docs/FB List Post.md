# Draft post for the FutureBasic list - the free modules, in one post

One post for all the free modules (author, 2026-11-28: "a single post for all the mods so as to not tire the men").
It replaces the separate drafts (`src/SQLGeneratorExample/ANNOUNCEMENT.md`, `src/WebToolkit/ANNOUNCEMENT.md`), which
stay as the longer text for each module's own page. Plain text, no attachments: the downloads are on the page the post
links to (the list's storage fills up). The author's style: short, direct, the point first.

Before sending: replace `[link]` with where the downloads are (see "Where the link points" below), and `[your name]`.

---

**Subject:** Three free modules for FB: SQL, business rules, web apps

Hi all,

Sorry I've been quiet. I've been building some things for FB 7, and I'd like to share three of them.
All free, MIT licence, each with a small example app.

**1. SQL Generator.** You describe the query, it writes the SQL:

```
query = fn InitQueryDictionary
fn AddTableToQuery( query, @"person", @"p" )
fn AddColumnToQuery( query, @"p.surName", @"Surname" )
fn AddFilterToQuery( query, @"p", @"balance", fn NumberWithDouble( 100.0 ), _realType, 0, _isGreaterThan, 0 )
sql = fn GenerateSelectSQL( query )
```

gives `SELECT "p"."surName" AS "Surname" FROM "person" AS "p" WHERE "p"."balance" > ?`.
Start with the one-file demo (about 40 lines).

**2. LogicBank for FutureBasic.** Business rules, declared once and kept on every save: an order's total
is the sum of its items, a customer's balance never goes over the credit limit. A save that would break
a rule is refused and rolled back, with a message to show. Your rules are FB functions. The example walks
through an order step by step.

**3. Web Toolkit for FutureBasic** (a working name). Web apps written in FB: the page is built in FB, and
every click is answered by your FB code on the server, in the background, without reloading the page.
nginx (free) sits in front and talks to the browsers. A page is a few lines:

```
fn WebField( session, @"page", @"visitorName", @"Your name", @"text", @"" )
fn WebButton( session, @"page", @"greet", @"Greet", @"primary" )
fn WebOn( session, @"greet", @"clicked", @fn GreetClicked )
```

The example is customers, orders and items, running the business rules from no. 2 on every save.
This one is early; I'd like to hear what you would build with it.

Everything is here, no attachments: [link]

Questions welcome.

[your name]

---

## Where the link points

The plan is Imagery's FutureBasic site (`tools/make_site.py` builds it into `site/`: a page per module, the downloads,
each module's help). Until it can be hosted, any of these works for the link, and the site can move later:

- **GitHub Pages:** the built `site/` folder pushed to a public repository; GitHub serves it at
  `https://<account>.github.io/<repository>/`, with no firewall or server of your own. The custom name
  (fb.imagery-business-systems.com) can point at it later with one DNS record.
- **A public GitHub repository of the three modules** (their folders and READMEs): the link goes to its page, and
  each download is GitHub's "Download ZIP".
- **The zips on a file-sharing service** (iCloud Drive, Dropbox): quickest, but no pages to read before downloading.
