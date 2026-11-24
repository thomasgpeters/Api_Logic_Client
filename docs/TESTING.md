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

## 3. On a Mac — the generator and generated apps (by hand)

| Check | How | Passing |
|---|---|---|
| Generator builds and runs | open `src/Generator/Api Logic Client.fbeproj`, build | builds; window opens |
| New Project | Create Project → Choose… a database → Create | tables summary; entity list and definitions |
| Workspace | Model → Show Workspace in Finder | `<project>/Project.json`, `Database/<db>`, `Design.json` after an edit |
| Designer adjustments | edit a Title or a width in the attribute table | `Design.json` written; kept after reopening |
| Project Settings | ⌘; → About text | counter, 250 limit, saved in `Project.json` |
| Recent Projects | quit, relaunch | the project is listed; double-click opens it |
| Resizing | drag the window | minimum 1000 × 620; list and pages stretch |
| Generate App | ⌘G, open `FBapp/<project>.fbeproj`, build | builds; NSLog shows `Data: opened …` and `Logic: rules active` |
| About box | run the generated app, About | the About text under name and version |
| Test_Xib_View | build and run | persons list, add, save, delete (the shared query builder) |

The feature pages (`features/*_FEATURE.md`) each end with their own "Verify on a Mac" list;
`BACKLOG.md` → "Verify on a Mac" tracks what is still unchecked.

## Adding tests

- A new rule type or engine behaviour: add scenarios to `tools/logic_reference.py` **and** the
  same ones in FB to `tools/make_logic_test.py`, then run `tools/run_tests.sh` — `--prove` must stay
  at 0 unproven (a new rule nobody tests is reported).
- A new FB coding pitfall found in a Build Log: teach `fblint.py`, reproduce the error on the old
  code, check that it reports nothing else.
