# Imagery's FutureBasic site: https://fb.imagery-business-systems.com/

Status: built (2026-11-26); not yet published. Generator: `tools/make_site.py`.

## What it is

A static site, generated from this repository, for the author's own server (author, 2026-11-26: published from his
network, at `fb.imagery-business-systems.com`; the apps use the domain name, never an address, so the host can change
without redeploying them).

| Page | From |
|---|---|
| `/` | the free modules, App Builder, the samples |
| `/sql-generator/`, `/logicbank/`, `/web-toolkit/` | each module's README, its download, its user guide (the Web Toolkit: the module and the Orders example, two downloads) |
| `/help/sql-generator/`, `/help/logicbank/`, `/help/web-toolkit/` | each example's (the Web Toolkit: the module's) `User Guide.txt` (the markup the apps' Help uses), with its diagram |
| `/samples/`, `/samples/<name>/` | each sample's README and download |
| `/app-builder/` | Lite and Enterprise; registration on the Imagery License Server (`LICENCE_SERVER` + `LICENCE_PAGE`, read from `Licence.incl`) |
| `/downloads/*.zip` | each module's example folder and each sample folder |

- **No packages needed:** it uses the standard library only (a small Markdown converter for the READMEs: headings,
  lists nested by indent, fenced code, tables, links). The output is plain HTML and CSS, light and dark, and it fits
  a phone.
- **Not kept in git:** `site/` is listed in `.gitignore`; build it, then upload it.
- **Licences:** the footer says the modules are MIT, and that the Imagery name and logos are not licensed for reuse.
- **The apps:** the *About Imagery Business Systems* window's website button is `ABOUT_IMAGERY_SITE` (`src/Shared`).

## Publishing

```
python3 tools/make_site.py            # -> site/
rsync -a --delete site/ <server>:/var/www/fb.imagery-business-systems.com/
```

## Next

- The examples' Help windows load `/help/<module>/` in a web view, and keep the bundled guide when offline
  (author's idea, 2026-11-26).
- The About Imagery window from the site the same way.
