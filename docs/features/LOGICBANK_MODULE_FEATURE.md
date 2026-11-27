# LogicBank for FutureBasic: the module and its example app

Status: built (2026-11-26); not yet built on a Mac. Folder: `src/LogicBankExample`. Design:
`docs/design/Free Modules Design.md`.

## What it is

The rules engine that generated apps carry (`src/Runtime/Logic *.incl`), packaged as a free, open-source module
(MIT) with an example app, a user guide and a README.
- **Why open source** (author, 2026-11-26): LogicBank for Python, which inspired it, is open source; publishing
  ours in the same spirit also keeps faith with its author.
- **Why the example is its own app** (author's choice): it runs on three objects in memory, not the SQL
  Generator's database.
- **What App Builder adds:** with the module alone, rules are written by hand; App Builder adds the AI assistant,
  the checks, the tests and the generated app.

## How it works

- **The engine** talks to its data through about fifteen `Data…` calls (begin / end, fetch, parent, children,
  insert / update / delete, the model). Two layers answer them:
  - `Data Memory.incl` (new): objects in memory, copies handed out, a snapshot at the outermost `DataBegin` put
    back when a save is refused. Generated keys are the highest so far + 1.
  - `Data Records.incl`: SQLite, built on the SQL Generator (the runtime's).
- **The model** is `Data Model.incl` + `Model.json`, as in generated apps. The example's `Model.json` is written
  from the reference's schema (`tools/logicbank_example_reference.py --model`).
- **The example's rules** (`Rules.incl`) cover formula (with a parent's value), sum and count (with a where),
  constraint, copy, parent check, and delete actions prevent and cascade.
- **The story** (`Story.incl`) is thirteen saves, step by step (Next Step / Run the Whole Story / Start Again).
  After each: the FB call, Saved or Refused (with `LogicMessage`), and the objects. *Log to NSLog*
  turns on `isLoggingOn` (NO by default; every NSLog is gated on it).
- **The Help window** (`Help.incl`, `Rich Text.incl`, from the SQL Generator example):
  - the user guide (`User Guide.txt`): every rule kind with examples, what a rule reads, activation,
    Model.json, using the module in your own app;
  - the rules diagram (`tools/make_logicbank_svg.py`, then `tools/svg_to_png.js`);
  - Open in Preview, and Export as PDF or Rich Text.
- **About Imagery Business Systems** in the application menu (`src/Shared`).

## Verification

- `tools/logicbank_example_reference.py` runs the same model, rules and story on the reference engine and checks
  every value the story shows (13 steps).
- `run_tests.sh` checks:
  - the module files are identical to `src/Runtime`'s;
  - `Rich Text.incl` is identical to the SQL Generator example's;
  - the About Imagery files are identical to `src/Shared`'s;
  - the project lints clean.
- **On a Mac (to do):** build, run the story, and compare it with the reference's output; Start Again; the
  engine log; Help (Preview, Export, Diagram); About Imagery.
