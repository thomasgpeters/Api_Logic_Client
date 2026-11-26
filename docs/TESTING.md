# Testing

Every test, how to run it, and what passing looks like. Two kinds: **checks that run
anywhere** (Python, no FutureBasic needed) and **checks on a Mac** (FutureBasic builds and runs).

All of them need the [FutureBasic_Documentation](https://github.com/thomasgpeters/FutureBasic_Documentation)
clone beside this repository: its toolbox headers (for the linter) and its Northwind database
(`nw/database/db.sqlite`; the tests only ever work on copies of it).

## 1. Everything that runs without a Mac — one command

```bash
tools/run_tests.sh
```

(or `tools/run_tests.sh <path to FutureBasic_Documentation>` when it is somewhere else;
`--help` explains the options. Every tool in `tools/` takes `--help`.)

| Check | What it proves | Passing |
|---|---|---|
| `fblint` on `src/` (and Test_Xib_View beside this repo) | every FB file follows `reference/FB Coding Rules.md`: typed fns, comments, CR endings, toolbox names and argument counts, keywords as names, `for … in`, block balance, build order | `0 problems` |
| `logic_reference.py --test` | the logic engine's behaviour, scenario by scenario, on a copy of Northwind (the Python reference follows the FB code function by function) | `70 scenarios, 0 failed` |
| `logic_reference.py --prove` | every rule is really tested: each rule left out in turn makes a scenario fail | `20 rules, 0 not proven` |
| `rules_bridge.py --test` | `declare_logic.py` → `Rules.json` (lambdas translated to FB, the rest switched off with its Python kept), `check`, FB generation lints with the runtime, export and the round trip back | `23 checks, 0 failed` |
| `make_logic_test.py` + `fblint` | the FB test project assembles from the real runtime files and lints clean, build order included | `0 problems` |
| `run_tests.sh` (SQL Generator) | the module's three copies (runtime, `src/SQLGeneratorExample`, Test_Xib_View) are identical | `the copies are identical` |
| `check_app_pages.py` | the `App Pages.incl` the generator writes (its `AppPagesSource` played for two entities) lints with the real runtime, templates and stand-in bindings | `0 failed` |
| `samples/<Name>/test_rules.py` (and `--prove`), for Telecom and Customs | each sample's rules on its database, built through the rules from `lookup.sql` and `sample.sql`: the scenarios, the purge (`purge_sample.sql` empties the sample tables and leaves the lookup data exactly as a lookup-only build makes it), every rule left out must fail a scenario; its FB `Rules.incl` lints with the runtime | Telecom `32 scenarios`, `39 rules, 0 not proven`; Customs `41 scenarios`, `35 rules, 0 not proven` |
| `check_erd_page.py` | the model diagram page, filled as `ERD Generator.incl` fills it, draws every entity, relationship and rule symbol, opens / closes, drags and selects with no script errors (headless Chromium; skipped without node + Playwright) | `0 failed` |
| `als_project_reference.py --test` (projects from `ALS_PROJECTS`; `--github` with `ALS_GITHUB=1`) | the Open ALS Project screen's logic, as `ALS Project.incl` does it: GitHub addresses; a project's folder, `database/` and `models.py` find the same model; the Studio model (keys, relationships, lookups and their display columns); public repositories over raw.githubusercontent.com | `25 checks, 0 failed` |
| `models_py_reference.py` (Enterprise; when `ALS_PROJECTS` and `ALS_PYTHON` are set) | an ALS project's `database/models.py`, read as text the way `ALSModelFromModelsPy` reads it, equals SQLAlchemy's own model of the same file: classes, tables, attributes, primary keys, relationships with their key columns. Make projects with `ApiLogicServer create --project_name=nw --db_url=nw-` and `--db_url=sqlite:///<file>` | `0 failed` per project |

Run any one of them alone:

```bash
python3 tools/fblint.py --headers ../FutureBasic_Documentation/Toolboxes/Headers src
```

```bash
python3 tools/logic_reference.py --test ../FutureBasic_Documentation/nw/database/db.sqlite
```

```bash
python3 tools/logic_reference.py --prove ../FutureBasic_Documentation/nw/database/db.sqlite
```

## 2. On a Mac — the logic engine in FutureBasic

```bash
python3 tools/make_logic_test.py ../FutureBasic_Documentation/nw/database/db.sqlite ~/Desktop/LogicTest
```

Open `~/Desktop/LogicTest/Logic Test.fbeproj` in FutureBasic, build and run. The NSLog window
lists one `PASS` / `FAIL` line per scenario — the same scenarios as `logic_reference.py --test` —
and ends with `logic test: 70 scenarios, 0 failed`. It works on `~/Desktop/LogicTest/test.sqlite`,
a copy; run `make_logic_test.py` again for a fresh one. Paste the Build Log or the NSLog lines
into a session when something fails.

### Web Toolkit: the template and the Orders example (`docs/features/WEB_TOOLKIT_FEATURE.md`)

Here: `tools/web_toolkit_reference.py --test` (in `run_tests.sh`) drives `web.js` in headless Chromium against a Python
reference of the protocol (30 checks); `--serve 8099` shows its page. On a Mac:
1. Build `src/WebToolkitExample/WebToolkitExample.fbeproj` and run it.
2. In that folder, `nginx -c "$PWD/nginx.conf" -p "$PWD"`, then open http://127.0.0.1:8088/.
3. Report:
   - a customer's credit limit lowered below the balance: refused, with the message;
   - an item added: the total and the balance follow;
   - Ship Today;
   - a second browser sees the changes after switching back;
   - an item typed, then the tab switched: it is saved;
   - the theme menu.
4. Also build `src/WebToolkit/Template` once.

### FastCGI Test (the pattern: nginx in front of a FutureBasic program)

`tools/check_fastcgi_core.py` (in `run_tests.sh`) compiles the program's FastCGI core here and runs it behind nginx. On a
Mac: `brew install nginx`, copy `src/MacTests/FastCGI Test nginx.conf` to `/opt/homebrew/etc/nginx/servers/`,
`brew services restart nginx`, run `src/MacTests/FastCGI Test.fb`, open http://127.0.0.1:8088/ - the same reports as
the Web Server Test below.

### Web Server Test (feasibility: a web app in FutureBasic, `docs/design/Web Toolkit Design.md`)

Open `src/MacTests/Web Server Test.fb` in FB and run it; click Open in Browser (http://127.0.0.1:8080/). Report:
- does the page appear;
- does Add One count up without reloading;
- does Greet show `<b>Bob</b>` as typed (not bold);
- two tabs, many fast clicks: does it keep up (the window counts the requests);
- anything the window or the NSLog window says.

## 2b. On a Mac — MapKit points (before the Map view is built)

Open `src/MacTests/MapKit Points Test.fb` in FB and run it. Five points (three customers in blue,
two suppliers in orange); the popup answers the map's `_mapViewViewForAnnotation` event four ways.
Report which modes show coloured markers with a person / shipping-box icon, and a bubble with two
lines of details and an (i) button; paste the `MapTest:` lines from the log
(`design/Map View Design.md`).

## 3. On a Mac — the generator and generated apps (by hand)

| Check | How | Passing |
|---|---|---|
| Generator builds and runs | open `src/AppBuilder/Studio for FB.fbeproj`, build | builds; window opens |
| New Project | Create Project → Choose… a database → Create | tables summary; entity list and definitions |
| Workspace | Help → Show Workspace in Finder | `<project>/Project.json`, `Database/<db>`, `Design.json` after an edit |
| Designer adjustments | edit a Title or a width in the attribute table | `Design.json` written; kept after reopening |
| Project Settings | ⌘; → About text | counter, 250 limit, saved in `Project.json` |
| Recent Projects | quit, relaunch | the project is listed; double-click opens it |
| Resizing | drag the window | minimum 1000 × 620; list and pages stretch |
| Generate App | ⌘G, open `FBapp/<project>.fbeproj`, build | builds; NSLog shows `Data: opened …` and `Logic: rules active` |
| About box | run the generated app, About | the About text under name and version |
| Model diagram | Model → Show Model Diagram (⇧⌘D) | the ERD opens in the browser; `features/MODEL_DIAGRAM_FEATURE.md` → Verify |
| Test_Xib_View | build and run | persons list, add, save, delete (the shared query builder) |

The feature pages (`features/*_FEATURE.md`) each end with their own "Verify on a Mac" list;
`BACKLOG.md` → "Verify on a Mac" tracks what is still unchecked.

## Adding tests

- A new rule type or engine behaviour: add scenarios to `tools/logic_reference.py` **and** the
  same ones in FB to `tools/make_logic_test.py`, then run `tools/run_tests.sh` — `--prove` must stay
  at 0 unproven (a new rule nobody tests is reported).
- A new FB coding pitfall found in a Build Log: teach `fblint.py`, reproduce the error on the old
  code, check that it reports nothing else.
