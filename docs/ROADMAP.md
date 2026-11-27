# Roadmap

Where App Builder for FutureBasic is going, phase by phase. The details of each item are in the
[backlog](BACKLOG.md), what was done is in the [development log](DEVELOPMENT_LOG.md), and the larger designs are in
[design/](design/).

Status words: **done** (built and tried on a Mac), **built** (written and checked here, waiting for a Mac build),
**next**, **designed**, **open** (a decision is needed).

## Phase 1: the Lite edition, a SQLite app (current)

| Step | Status |
|---|---|
| The model from a SQLite database: tables, keys, relationships | done |
| Entity definitions: recommendations and your adjustments (`Design.json`) | done |
| Form and List XIB parts per entity; the binding code; the generated FB project with its starting files | done |
| The app's frame: navigation bar, header, footer, pages; New, Save, Delete, Refresh through the rules | done |
| Cards, light and dark mode, the project's branding | built |
| Records as tiles beside the grid (`Record Tiles.incl`) | built |
| Crumb trail and page stack in the generated app | next |
| Related lists in tabs (master and detail), drill-in | next |
| The page designer: pages from entities, linked by relationships (`design/Page Designer Design.md`) | designed |
| Hook files for hand-written code (created only if missing) | |
| `admin.yaml` hints: titles (the display column is done) | |

## Phase 2: the look and feel

| Step | Status |
|---|---|
| Pill buttons in App Builder and generated apps | done |
| The Studio's pages as cards; the Welcome page as its own heading | built |
| More form controls: toggle switch, combo box, calendar picker, colour picker | next |
| Map view: records with a latitude and longitude on a map (`design/Map View Design.md`) | designed |
| Image and PDF viewers, thumbnails, token fields | |
| Theme files: named styles (light, dark, colourful, base) | |

## Phase 3: App Builder itself

| Step | Status |
|---|---|
| The workspace in Application Support; Recent Projects; the model diagram | done |
| A Settings window (Application Support and the Keychain) | |
| Git: commit on generation, status, push and pull; GitHub | |
| Settings for API Logic Server, AI providers, mail | |

## Phase 4: the Professional edition

Design: [Editions Design](design/Editions%20Design.md) and [Licensing Design](design/Licensing%20Design.md).

| Step | Status |
|---|---|
| The data interface (`App Data`) with the Lite implementation; the edition hook | done |
| Licences: signed, checked offline, kept in the Keychain; the Licence menu and window | done |
| The ALS contract, measured (`design/ALS Contract.md`); the SQL Generator's JSON:API side | built |
| The ALS model from `database/models.py`; the API Logic Server Project page | built |
| `App Data Professional.incl`: connection and sign-in | next |
| Seats: copies on the local network, Macs activated online | designed |
| The License Server: registration, the order form, licences issued | open (its own repository) |
| The private repository and the paid build | |

## Phase 5: business rules

Design: [Logic Engine Design](design/Logic%20Engine%20Design.md).

| Step | Status |
|---|---|
| The data runtime the engine stands on (SQLite records, transactions) | done |
| LogicBank for FutureBasic: formulas, constraints, sums, counts, copies, parent checks, delete actions, events (70 scenarios, every rule proven) | done |
| `declare_logic.py` import and export (the Python reference, `tools/rules_bridge.py`) | built; the FB port is next |
| The Rules page in App Builder: `Rules.json`, the check, Explain | next |
| Rules from plain sentences, with AI (`design/AI Assistant Design.md`) | designed |

## Phase 6: the free modules and the site

| Step | Status |
|---|---|
| The SQL Generator: the module, the example app, the one-file demo | done; shared on the FB list next |
| LogicBank for FutureBasic: the module and its example story | built (the example's crash fix waits for a Mac run) |
| Web Toolkit for FutureBasic: the module, the Orders example, the Layout Tool | built |
| Record Files for FutureBasic: record files with B-tree indexes (an experiment) | built |
| The site, fb.imagery-business-systems.com, built from this repository | built; to upload |
| The test scenario guide (`TEST_SCENARIOS.pdf`) | done |
