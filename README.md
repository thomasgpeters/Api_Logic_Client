# Api Logic Client

A macOS FutureBasic app that turns a data model — a SQLite database today, an
[API Logic Server](https://apilogicserver.github.io/Docs/) project next — into a
native macOS FutureBasic app the developer keeps editing. One shell, many
entities: an entity navigator, a List part and a Form part per entity, related
lists in tabs, drill-in with a crumb trail.

## How it works

1. **Open a model** — *Model → Open SQLite Database…* (⌘D) reads tables, columns,
   keys and relationships straight from the database. A saved ALS
   `/metadata?include=attributes` response (e.g. `samples/Northwind/metadata.json`)
   also works.
2. **Review the entity definitions.** Each attribute shows its recommended
   **Title** (field label and column heading), FB type, size, key role, form
   control and widths. Adjust what you like; adjustments are kept in
   `Design.json` and survive regeneration.
3. **Generate** — each step on its own, or all at once:
   *Generate XIBs* · *Generate XIB for Selected Entity* · *Generate Binding Code* ·
   *Generate App*. Output goes to `~/Library/Application Support/Api_Logic_Client/workspace/<project>/FBapp/`;
   the project's own settings (`Project.json`, `Design.json`) stay in `<project>/`.
4. **Open `FBapp/<project>.fbeproj` in FutureBasic**, build, and keep editing: generated code is
   plain, readable FB; `EventHandlers.incl`, `Menus.incl` and `Windows.incl` start from
   templates and are yours — regeneration never touches them.

## Repository layout

```
Api_Logic_Client/
├── README.md · CLAUDE.md · .gitignore
├── src/
│   ├── Generator/    ← open "Api Logic Client.fbeproj" here in the FB editor
│   ├── Runtime/      ← FB code copied into generated apps (regenerated)
│   └── Templates/    ← starting files for generated apps (copied only when missing)
├── docs/
│   ├── design/       ← App Shell Design, Generator App Design
│   ├── reference/    ← FB Coding Rules, FB Documentation Map, FB Reference Index
│   ├── controls/     ← Controls Catalog
│   ├── features/     ← one <NAME>_FEATURE.md per feature
│   ├── ROADMAP.md · BACKLOG.md · DEVELOPMENT_LOG.md
├── tools/            ← fblint.py, sqlite_model.py
└── samples/          ← Northwind metadata
```

## Where the app keeps its files

The app bundle is never written to. Everything the generator creates lives in
its Application Support folder (*Model → Show Workspace in Finder* opens it;
`~/Library` is hidden in Finder):

```
~/Library/Application Support/Api_Logic_Client/
├── Settings.plist                 (planned) settings: git, GitHub, ALS/APIs, AI/LLMs, SMTP
└── workspace/
    └── <project>/                 one folder per project: the generator's settings for it
        ├── Project.json           name, model source, base URL, user name (no passwords)
        ├── Design.json            the designer's adjustments (kept)
        ├── Database/              (planned) the SQLite file and schema
        └── FBapp/                 the generated FutureBasic app - open <project>.fbeproj
            ├── <project>.fbeproj      the FB project: data.fbproj (regenerated), Settings2.plist (kept)
            ├── <project>.main         main program: connection, handler registration, start (regenerated)
            ├── EventHandlers.incl     DoAppEvent / DoMenu / DoDialog (starting template, kept)
            ├── Menus.incl             BuildMenus (starting template, kept)
            ├── Windows.incl           BuildWindows + nibview per Form part (starting template, kept)
            ├── <Entity>Form.xib       generated Form part per entity (regenerated)
            ├── <Entity>List.xib       generated List part per entity (regenerated)
            ├── <Entity> Binding.incl  generated binding code per entity (regenerated)
            ├── Model.json             the model the app reads at run time (regenerated)
            ├── Model Tags.incl        tag constants for your own code (regenerated)
            ├── *.incl                 runtime files copied from src/Runtime (regenerated)
            └── <Entity> Hooks.incl    (planned) your hand-written code, never overwritten
```

Secrets (tokens, API keys, passwords) go in the macOS Keychain, never in a file.

## Documentation

| Document | What it answers |
|---|---|
| [`docs/ROADMAP.md`](docs/ROADMAP.md) | Where the project is going, phase by phase |
| [`docs/BACKLOG.md`](docs/BACKLOG.md) | Open items and ideas |
| [`docs/DEVELOPMENT_LOG.md`](docs/DEVELOPMENT_LOG.md) | What was done, what was learned, with commits |
| [`docs/features/`](docs/features/) | How each feature works |
| [`docs/design/`](docs/design/) | The generated app's shell; the generator app (workspace, settings, git) |
| [`docs/reference/FB Coding Rules.md`](docs/reference/FB%20Coding%20Rules.md) | Rules every FB file follows — hand-written and generated |
| [`docs/controls/Controls Catalog.md`](docs/controls/Controls%20Catalog.md) | Native controls available to generated apps |

## Building

FutureBasic 7.1.x on macOS. Open `src/Generator/Api Logic Client.fbeproj` in the
FB editor and build (the project links `-lsqlite3`). Before handing over FB
changes, check them:

```bash
python3 tools/fblint.py --headers <FutureBasic_Documentation>/Toolboxes/Headers src
```

## Related repositories

- **FutureBasic_Documentation** (private) — the current FB reference manual,
  toolbox headers and examples; the Northwind ALS project used for testing.
- **Test_Xib_View** — the SQLite + XIB "Modern CRM" app: the record/view pattern
  generated apps follow, and the SQL query builder.
- **Domain-Driven-Design-Book** (private) — the principles the generator follows.
