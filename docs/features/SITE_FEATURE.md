# Imagery's FutureBasic site: https://thomasgpeters.github.io/imagery-fb-site/

Status: **live** (2026-11-28) on GitHub Pages, from `thomasgpeters/imagery-fb-site` (its `main`); later at
`fb.imagery-business-systems.com`, when that name points there. Generator: `tools/make_site.py` (how to republish: its header).

## What it is

A static site, generated from this repository, for the author's own server (author, 2026-11-26: published from his
network, at `fb.imagery-business-systems.com`; the apps use the domain name, never an address, so the host can change
without redeploying them).

| Page | From |
|---|---|
| `/` | the author's introduction (in his words, 2026-11-28), the free modules, App Builder, the samples |
| `/sql-generator/`, `/logicbank/`, `/web-toolkit/` | each module's README, its download, its user guide (the Web Toolkit: the module and the Orders example, two downloads) |
| `/help/sql-generator/`, `/help/logicbank/`, `/help/web-toolkit/` | each example's (the Web Toolkit: the module's) `User Guide.txt` (the markup the apps' Help uses), with its diagram |
| `/samples/`, `/samples/<name>/` | each sample's README and download |
| `/app-builder/` | Lite and Professional. While `APP_BUILDER_RELEASED` is False (author, 2026-11-28: not released until it can be paid for) its buttons are disabled and say *Coming Soon*, the landing card's tag too, and nothing links to registration; set it True to show the registration buttons (the Imagery License Server: `LICENCE_SERVER` + `LICENCE_PAGE`, read from `Licence.incl`) |
| `/downloads/*.zip` | each module's example folder and each sample folder, named `<what>-<purpose>-<release date>.zip` |

- **No packages needed:** it uses the standard library only (a small Markdown converter for the READMEs: headings,
  lists nested by indent, fenced code, tables, links). The output is plain HTML and CSS, light and dark, and it fits
  a phone.
- **Not kept in git:** `site/` is listed in `.gitignore`; build it, then upload it.
- **Licences:** the footer says the modules are MIT, and that the Imagery name and logos are not licensed for reuse.
- **The apps:** the *About Imagery Business Systems* window's website button is `ABOUT_IMAGERY_SITE` (`src/Shared`, and
  its copies): the GitHub Pages address until the custom name is set up; its text says App Builder is not released yet.
- **Say only what is true today** (author, 2026-11-28: "I was hoping you would catch some shortcomings"): what is
  planned is said in the future tense or marked *coming*, as the editions page's statuses are.

## Publishing

```
python3 tools/make_site.py            # -> site/
rsync -a --delete site/ <server>:/var/www/fb.imagery-business-systems.com/
```

## Next

- The examples' Help windows load `/help/<module>/` in a web view, and keep the bundled guide when offline
  (author's idea, 2026-11-26).
- The About Imagery window from the site the same way.
