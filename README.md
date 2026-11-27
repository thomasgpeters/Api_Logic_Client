# App Builder for FutureBasic

App Builder turns your data model into a complete FutureBasic app for the Mac. Point it at a SQLite database (or, in
the Professional edition, an [API Logic Server](https://apilogicserver.github.io/Docs/) project), review what it
proposes, and it writes the windows, forms, lists, data binding and business rules. You open the result in the
FutureBasic editor, build it, and keep it as your own.

The app is called **Studio for FB**. This repository (still named Api_Logic_Client) also holds the free FutureBasic
modules App Builder is made of, which you can use on their own.

![From your data model to a FutureBasic app: the model, App Builder, the project workspace, the generated app, with business rules all the way through](docs/design/architecture.svg)

## Getting started

1. Open `src/AppBuilder/Studio for FB.fbeproj` in FutureBasic and build it.
2. On the Welcome page, **Create Project** and choose a SQLite database.
3. Click an entity to see what App Builder proposes for each field: its title, control, type and widths. Change
   what you like; your changes are kept.
4. **Generate App** (Command-G), then open the generated project in FutureBasic and build it.

The [user guide](docs/USER_GUIDE.md) covers each step in full, along with project settings, the model diagram,
business rules and the shortcuts.

## What you get

A generated app has a navigation bar with a page per entity, a list (as a grid or as tiles) above a form, lookups for
related records, and New, Save, Delete and Refresh. Every save goes through your business rules: totals, balances,
limits and the rest are kept right for you. Light and dark mode work out of the box.

The generated code is plain FutureBasic. The files you are meant to change (event handlers, menus, windows, theme,
rules) are created once and never overwritten; the rest is regenerated from the model whenever it changes.

## Editions

| | Lite | Professional |
|---|---|---|
| Licence | free, with registration | paid |
| Start from | a SQLite database | a SQLite database, or an API Logic Server project |
| The app | runs on the Mac, with its rules | talks to API Logic Server: many users, rules on the server |

Licences are signed and checked offline. See [Licensing](docs/features/LICENSING_FEATURE.md).

## The free modules

Each comes with an example app, a user guide and the MIT licence. They are also on
[fb.imagery-business-systems.com](https://fb.imagery-business-systems.com/), built from this repository by
`tools/make_site.py`.

| Module | What it does | Folder |
|---|---|---|
| SQL Generator | Describe a query with dictionaries; it writes safe, parameterized SQL for SQLite. | [`src/SQLGeneratorExample`](src/SQLGeneratorExample/README.md) |
| LogicBank for FutureBasic | Business rules declared once and enforced on every save. | [`src/LogicBankExample`](src/LogicBankExample/README.md) |
| Web Toolkit for FutureBasic | Web apps written in FutureBasic, served behind nginx. | [`src/WebToolkit`](src/WebToolkit/README.md) |
| Record Files for FutureBasic | Fixed-size records with B-tree indexes, timed against SQLite (an experiment). | [`src/RecordFilesExample`](src/RecordFilesExample/README.md) |

## The repository

```
src/
  AppBuilder/            Studio for FB, the app itself
  Runtime/               the FutureBasic code every generated app gets
  Templates/             starting files for generated apps (yours once copied)
  SQLGeneratorExample/   LogicBankExample/   WebToolkit/   WebToolkitExample/   RecordFilesExample/
  Shared/                the About Imagery window the examples share
  Professional/          the Professional edition's data side
  MacTests/              small programs that answer a question on a Mac
samples/                 sample applications: Telecom, Customs, FlightPlanner (each a database, rules and tests)
tools/                   checks, references and builders (Python, run here; nothing FB builds uses them)
docs/                    the documentation (below)
```

App Builder never writes into its own app bundle. Projects live in
`~/Library/Application Support/App Builder for FutureBasic/workspace/`, one folder each, and passwords and keys stay
in the Keychain. The [user guide](docs/USER_GUIDE.md#5-the-workspace-and-your-projects-files) shows what is in a
project folder.

## Documentation

| Read this | For |
|---|---|
| [User guide](docs/USER_GUIDE.md) | Using App Builder, from the first project to business rules |
| [Test scenario guide](docs/TEST_SCENARIOS.pdf) | Checking every feature on a Mac, step by step (source: [TEST_SCENARIOS.md](docs/TEST_SCENARIOS.md)) |
| [Testing](docs/TESTING.md) | The automated checks, and how to run them |
| [Features](docs/features/) | How each feature works, one file each |
| [Design](docs/design/) | The larger designs: the generated app, the rules engine, licensing, the Web Toolkit, record files |
| [FB coding rules](docs/reference/FB%20Coding%20Rules.md) | The rules all our FutureBasic follows, hand-written or generated |
| [Roadmap](docs/ROADMAP.md), [backlog](docs/BACKLOG.md), [development log](docs/DEVELOPMENT_LOG.md) | Where it is going, what is open, what was done |

## Building and checking

You need a Mac with FutureBasic 7. Build Studio for FB as above. The examples build the same way, each from its own
`.fbeproj`.

FutureBasic does not run outside the Mac, so the repository carries checks that do: a linter for our coding rules,
the rules engine's scenarios, the B-tree and web tests, and more. Run them all with:

```bash
tools/run_tests.sh
```

[Testing](docs/TESTING.md) describes each check and the tests that need a Mac.

## Related repositories

- **FutureBasic_Documentation** (private): the FutureBasic reference, toolbox headers and examples we check against.
- **Test_Xib_View**: the SQLite and XIB app whose record and view pattern generated apps follow.

MIT licence for the free modules (see each folder's LICENSE). The Imagery name and logos are not licensed for reuse.
