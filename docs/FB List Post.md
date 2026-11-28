# Draft post for the FutureBasic list - the free modules, in one post

One post for all the free modules (author, 2026-11-28: "a single post for all the mods so as to not tire the men").
It replaces the separate drafts (`src/SQLGeneratorExample/ANNOUNCEMENT.md`, `src/WebToolkit/ANNOUNCEMENT.md`), which
stay as the longer text for each module's own page. Plain text, no attachments: the downloads are on the page the post
links to (the list's storage fills up). The author's style: short, direct, the point first.

Before sending: replace `[your name]`. The links are live (author, 2026-11-28). Rewritten on the author's theme
(2026-11-28): back on the list after a long silence, three open source contributions, each with a short description and its
page.

---

**Subject:** Three open source modules for FB: SQL Generator, LogicBank, Web Toolkit

Hi all,

Although I have remained silent on the list for a long time, I still follow what's going on, and I realize that my
participation has been lacking and my contributions few. I'd like to turn that around, so I've packaged up some
of what I've been working on and made it available as my open source contribution.

Three items are available now, each with a sample app that shows what it does:

1. SQL Generator for SQLite
   Describe a query as a dictionary (its tables, columns, filters and joins) and it writes the SQL for you:
   SELECT, INSERT, UPDATE and DELETE, with names quoted and every value bound rather than pasted in. Start with
   the one-file demo, about 40 lines; the sample app has ten more examples.
   https://thomasgpeters.github.io/imagery-fb-site/sql-generator/

2. LogicBank for FutureBasic
   Business rules, declared once and kept on every save: an order's total is the sum of its items, a customer's
   balance never goes over the credit limit. A save that would break a rule is refused and rolled back, with a
   message you can show. Your rules are FB functions. The sample walks through an order step by step.
   https://thomasgpeters.github.io/imagery-fb-site/logicbank/

3. Web Toolkit for FutureBasic
   Web apps written in FB. The page is built in FB, and every click is answered by your FB code on the server,
   in the background, without reloading the page. nginx (free) sits in front and talks to the browsers. The
   sample is customers, orders and items, running LogicBank's rules on every save. This one is early, and I'd
   like to hear what you would build with it.
   https://thomasgpeters.github.io/imagery-fb-site/web-toolkit/

All three are free, MIT licence, and need no registration. Everything is on the site, no attachments:
https://thomasgpeters.github.io/imagery-fb-site/

Questions and suggestions welcome.

[your name]

---

## Where the link points

**Chosen (author, 2026-11-28): GitHub Pages,** from the repository `thomasgpeters/imagery-fb-site` (built by
`tools/make_site.py`; how to republish: its header). The other options below are kept for the record.

The plan is Imagery's FutureBasic site (`tools/make_site.py` builds it into `site/`: a page per module, the downloads,
each module's help). Until it can be hosted, any of these works for the link, and the site can move later:

- **GitHub Pages:** the built `site/` folder pushed to a public repository; GitHub serves it at
  `https://<account>.github.io/<repository>/`, with no firewall or server of your own. The custom name
  (fb.imagery-business-systems.com) can point at it later with one DNS record.
- **A public GitHub repository of the three modules** (their folders and READMEs): the link goes to its page, and
  each download is GitHub's "Download ZIP".
- **The zips on a file-sharing service** (iCloud Drive, Dropbox): quickest, but no pages to read before downloading.
