# AI Assistant Design: rules in natural language, and a designer's second opinion

Status: design (author, 2026-11-26). Nothing is built yet; see BACKLOG.

## The problem

A database schema has structure but no behaviour. When someone imports `customs.sqlite`, App Builder can
generate every screen, but none of the 93 rules that make it a customs system: duty, risk lanes, release,
the bond. Today rules come from only two places:

- **Written by hand**, as in the samples: `samples/*/<name>_rules.py` and their `Rules.incl`.
- **Imported from an ALS project's `declare_logic.py`** (Enterprise, through the rules bridge).

A user who starts from a bare schema, which is what the Lite edition invites, has neither. The AI Assistant
is the third source. It also helps with the second job a new project faces: choosing the right control for
each attribute.

## Principles

1. **A rule is a sentence in the model's own language** (author, 2026-11-26: "rules as natural language,
   using the entity, model and attributes provided by the structure"). The sentence names real entities,
   attributes and relationships: tables and columns in Lite, resources and attributes from ALS in
   Enterprise. This is the ubiquitous language of the DDD book (§2.2), applied to behaviour.
2. **The sentence is the source of truth.** It is what the user writes, reads, approves and keeps. Every
   translation of it is derived and can be regenerated.
3. **The AI proposes; a person approves.** Nothing the AI says takes effect until someone accepts it, sentence
   by sentence.
4. **Generation stays reproducible.** Generating the app never calls the AI. Only the *Suggest…* and
   *Translate* commands do, and their results are saved as project files kept in git.
5. **One rule, two engines.** The same sentence becomes a LogicBank for FutureBasic rule in the app (Lite), and
   a LogicBank rule in ALS's `declare_logic.py` (Enterprise). The rules mean the same on both sides.
6. **No Python in anything FB builds.** The connector is FB: an HTTPS request with JSON, through FB's
   URLSession toolbox. The API key is kept in the Keychain.

## LogicBank for FutureBasic is a module of its own

LogicBank for FutureBasic is our clean-room rewrite of LogicBank for FB, and it should stand on its own:

- **As LogicBank is to ALS on the Python side:** a package ALS uses, not a part of ALS.
- **Its files:** `Logic Rules.incl`, `Logic Row.incl`, `Logic Engine.incl`, and the data runtime they read
  through (`Data Records.incl`, `Data Model.incl`, `Data SQLite.incl`, the DataObject builder).
- **Who uses it:** the generated apps copy it today; it should be usable by any FB program, with or without
  App Builder.
- **How it ships:** as its own module, like the SQL Generator (`src/SQLGeneratorExample`): its own folder, an
  example, a README, a licence, its own tests (the reference engine `tools/logic_reference.py`, and the
  samples' `--prove`).
- **What App Builder adds:** App Builder uses the module; the AI Assistant writes rules for it. Neither is
  part of the module.

In this repository, "LogicBank" means LogicBank for FutureBasic unless ALS is named. On the ALS side,
LogicBank is the Python original, and the same rules are written as `declare_logic.py`.

## The rule pipeline

```
 the user's sentence            "A Declaration's TotalDuty is the sum of its DeclarationLine Duty."
        │   grounded: every name checked against the model while typing
        ▼
 the AI translates  ──────────▶ a question, when the sentence is ambiguous
        │                       ("all lines, or only lines without relief?")
        ▼
 the rule (Rules.json)          kind: sum   entity: Declaration   attribute: TotalDuty
        │                       list: DeclarationLineList   childAttribute: Duty
        │   checked by App Builder: names, kinds, types, cycles (the rules bridge's check, in FB)
        ▼
 approved by the user  ───────▶ the sentence and its rule are shown side by side
        │
        ├──▶ LogicBank for FutureBasic:  Studio Rules.incl  (generated, Lite and Enterprise clients)
        └──▶ LogicBank in ALS:           logic/declare_logic.py  (generated, Enterprise)
```

### 1. Writing: grounded sentences

- A **Rules** page per entity. The user types a sentence; App Builder suggests entity, attribute and
  relationship names as they type (the model is known: `SQLite Model.incl` or `ALS Model.incl`), the way
  Imagery LogicBank Studio does.
- **An unknown name is flagged at once.** A sentence never reaches the AI naming something the model lacks.
- **Values from a code list are offered by their meaning:** "when its Lane is Red" (R), "once it is Released" (R).

### 2. Translating: the AI turns a sentence into a rule

- **What the AI receives:**
  - the sentence;
  - the model: entities, attributes and types, keys, relationships and their role names, code lists;
  - the rules already approved;
  - the prompt (below).
- **What it returns:** JSON, either one rule of a known kind or a question. The kinds are the engine's:
  formula, constraint, sum, count, copy, parent check, delete action, row event, commit event.
- **Several rules or none:** a sentence can need several rules ("Released goods still owing count against
  the importer's bond" is a sum plus a constraint). Some sentences describe what the engine cannot do: a
  maximum or minimum aggregate, a value from a grandparent. The AI then says so, and suggests the
  workaround the samples use: a copy, a reference date, a column read from the row that needs it.

### 3. Expressions: one neutral language, two targets

- **The problem with FB bodies:** sums, counts, copies, parent checks and delete actions are fully
  declarative: names only. Formulas, constraints and `where` conditions need an expression. Today
  `Rules.json` keeps those as FB, and the rules bridge translates FB to Python and back (imperfectly).
- **Proposal:** a small, neutral expression language in `Rules.json`. The AI writes it; App Builder
  generates both FB and Python from it, deterministically:
  - attributes and parent attributes (`Value`, `Arrival.ArrivedDate`);
  - numbers, text, dates;
  - `+ - * /`, comparisons, `and` / `or` / `not`;
  - `if … then … else`, `round( x, n )`, `days( from, to )`, `is empty`;
  - code-list values by name.
- **What goes beyond it:** anything the language cannot say (the samples' great-circle distance, the wind
  triangle) is a named function the user or the sample supplies in FB and in Python. The rule refers to the
  function by name, so the sentence and the rule still say what is computed.
- **The order of work:** this replaces the FB bodies in `Rules.json` step by step. Existing FB bodies keep
  working until then.

### 4. Checking and approving

- **App Builder's check, in FB:** names exist; the kind fits (a sum over a text column is refused);
  dependencies are found; no formula cycles; and the engine limits the samples ran into:
  - a child formula reading a parent aggregate it changes;
  - a cycle back into the row being saved.

  This is the rules bridge's `check`, ported to FB (already in the backlog).
- **The user then sees:**
  - the sentence;
  - the rule in plain terms ("sum of DeclarationLine.Duty into Declaration.TotalDuty");
  - for an expression, the formula;
  - and approves, edits the sentence (it is translated again), or rejects.

### 5. The two engines

- **Lite:** *Generate App* writes `Studio Rules.incl`, which the generated app runs with LogicBank for
  FutureBasic, as today.
- **Enterprise:**
  - The same rules export to the ALS project's `logic/declare_logic.py`: `Rule.sum`, `Rule.count`,
    `Rule.formula`, `Rule.constraint`, `Rule.copy`, `Rule.parent_check`, events. Each rule carries its
    sentence as a comment, so the ALS project stays readable on its own.
  - The rules bridge's export does this today from FB bodies; with the neutral expressions it becomes
    exact.
  - *Import Rules* reads an existing `declare_logic.py` back into rules. Each imported rule is given a
    sentence (the AI writes one from the rule; the user approves the wording), so every project ends up
    with sentences.
- **Equivalence is tested, not assumed.** The samples' scenarios (`test_rules.py`) are the yardstick. The
  same scenarios run against the FB rules (reference engine) and, for Enterprise, against ALS
  (`tools/als_contract.py`).

### 6. Suggesting: rules the user did not write

- *Model > Suggest Rules…* asks the AI what a schema like this one usually needs. It answers in the
  same form: sentences in the model's names, each with a short reason:
  - "Statement.Total looks like the sum of its Declarations' AmountDue."
  - "Leg.FromAirportId and ToAirportId should differ."
  - "A Declaration with Payments probably should not be deletable."
- **They wait for approval:** suggestions sit in a list; accepting one adds its sentence, which is translated
  and checked like any other.
- **What it can see:** column names, types, keys, relationships, code lists; and, only if the user allows it,
  a few sample rows.

## The designer's second opinion: controls

`Type Mapping.incl` already chooses a control for every attribute, deterministically, and `Design.json`
keeps the designer's adjustments. The AI does not replace that. It gives a second opinion:

- *Design > Suggest Controls…* sends the model (names, types, keys, code lists, relationships; sample values
  only if allowed).
- **The answer is JSON, one entry per attribute:** a control from the Controls Catalog
  (`docs/controls/Controls Catalog.md`), and a one-line reason. For example:
  - `Pilot.MedicalExam`: a date picker;
  - `Declaration.Lane`: a code list Green / Yellow / Red / Blue;
  - `Airport.Latitude` / `Longitude`: a map view;
  - `Declaration.Remarks`: a text view.
- **Only controls App Builder can generate are accepted.** Others come back as "not supported yet".
- **Accepted suggestions are written into `Design.json`**, marked as AI-suggested, where the designer can
  change them like any other adjustment.
- **The same for the page:** which attributes the list shows, the form's order and grouping, which
  relationships appear as related lists (Page Layouts, when it exists).

## The connector

- **One FB module in App Builder** (`AI Connector.incl`): a provider, a model and the key; one request
  (prompt + JSON in) and one answer (JSON out); time-outs and errors reported plainly.
- **The provider:** Claude to begin with (the latest model), behind an interface narrow enough to add
  others later.
- **The key** lives in the Keychain (`docs/design/Generator App Design.md`), is entered once in Settings, is
  never shown again (the last four characters only), and is never logged.
- **The prompts** are files in the workspace's Templates (`Templates/AI/Rules Prompt.md`,
  `Templates/AI/Controls Prompt.md`): editable by the user (the author's "special custom prompt") and
  versioned like the rest of the project.
- **What leaves the Mac is shown before it is sent:**
  - the schema by default;
  - sample rows only when allowed for that request;
  - never the database file;
  - never credentials.
- **Every answer is saved** with its prompt and date in `<project>/AI/` (git), so a rule or a control can say
  where it came from.
- **Offline:** without a key or a network the Studio works exactly as today; the *Suggest* and *Translate*
  commands say why they are unavailable.

## What the samples give us: an evaluation set

Telecom (39 rules), Customs (93) and Flight Planner (104) have hand-written rules, each proven by a
scenario. That makes them a test of the Assistant:

1. Write each sample's rules as sentences (the README "rules" sections are most of the way there).
2. Translate them with the Assistant, from the bare schema, and compare with the hand-written rules: the
   scenarios and `--prove` decide, not a reading.
3. Run *Suggest Rules* on each bare schema. Count how many of the real rules it finds, and how many wrong
   ones it adds.

The prompts are tuned against these numbers before the feature ships, and kept in `run_tests.sh` with a
recorded answer (no network in the test).

## Open decisions (for the author)

- **Edition:**
  - all editions with the user's own key;
  - or Enterprise only;
  - or a paid feature in either.
- **Provider:** Claude only to begin, or a pluggable connector from the start.
- **Imagery LogicBank Studio** (C++/Wt) never calls a language model itself; it asks ALS's `genai-logic`.
  - For Enterprise, App Builder could do the same: send the sentence to the ALS project's `genai-logic`.
    The ALS side then writes `declare_logic.py`, and App Builder imports it.
  - Lite has no server, so it needs the direct connector.
  - Should the two products agree here?
- **The expression language:** adopt it (and retire FB bodies in `Rules.json`), or keep FB bodies and
  translate them.
- **LogicBank for FutureBasic as a module:** its name, its folder, and whether it is published on its own like
  the SQL Generator.

## Plan

1. Package LogicBank for FutureBasic as its own module (folder, README, example, tests).
2. The neutral expression language: its grammar, the FB and Python generators, and `Rules.json` with
   sentences (the reference in Python first, then FB).
3. The rules check in FB (port of `rules_bridge.py check`).
4. The connector (FB, Keychain, prompts as templates, answers saved).
5. Rules page: grounded sentences, Translate, approve.
6. Suggest Rules; the evaluation on the three samples.
7. Suggest Controls into `Design.json`.
8. Enterprise: `declare_logic.py` from the same rules, sentences as comments; scenarios against ALS.
