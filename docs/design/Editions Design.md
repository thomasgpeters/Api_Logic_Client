# Editions Design

App Builder makes a business app in one of two editions. Both come from the same App Builder: the licence decides
which one a project can use (`Licence.incl`, `LicenceAllows`). How licences work, and what they cost, is in
[Licensing Design](Licensing%20Design.md).

| | Lite | Professional |
|---|---|---|
| Licence | free, with registration | paid |
| Tiers | two: the app and its SQLite database | three: the app, an API Logic Server, the database |
| Data | `App Data Lite.incl`: the app opens the database itself (`Data Records.incl`) | `App Data Professional.incl`: JSON:API calls to the server (`ALS Client.incl`) |
| Business rules | in the app: LogicBank for FutureBasic, `Studio Rules.incl` and `Rules.incl` | on the server: LogicBank in ALS, `declare_logic.py` exported by App Builder |
| Sign-in | none (the database is on this Mac) | the header's Log In: the server's sign-in |
| Status | built | the data side started (`features/PROFESSIONAL_DATA_FEATURE.md`) |

API Logic Server is open source and the same for everyone. What Professional sells is App Builder's three-tier
generation and its client runtime, not the server.

## One app, two data layers

What a user sees is the same in both editions: the shell, the pages, the XIBs, the bindings, the model diagram. Only
the data layer differs, behind one interface (the application layer of `App Shell Design.md`: the infrastructure is
replaced, the screens stay):

```
App Pages.incl  --  AppDataList / AppDataSave / AppDataRemove / AppDataLogin / AppDataKeyValues
                         |                                   answers in AppDataDone( op, entity, result, message )
          +--------------+---------------+
  App Data Lite.incl              App Data Professional.incl
  Data Records + Logic Engine      ALS Client (URLSession, asynchronous)
  SQLite on this Mac               API Logic Server -> database
```

The interface answers through a handler rather than a return value because a server's replies come back later. Lite
answers at once, through the same handler, so the pages never need to ask which edition they are in.

## The edition hook (`src/AppBuilder/Edition.incl`)

| Function | What it answers |
|---|---|
| `EditionProfessionalAvailable` | whether the licence includes the Professional runtime |
| `EditionOfProject( projectDict )` | `Project.json`'s `"edition"`; Lite unless Professional is available |
| `EditionDescription( edition )` | the edition in a few words, for the README and the main program |
| `EditionDataRuntimeFiles( edition )` | the data runtime, the rules engine, the edition's `App Data` file |
| `EditionMainStart( edition, host, user )` | the start-up: open the data, declare the rules, activate them |
| `EditionRulesInApp( edition )` | whether the rules run in the app |
| `EditionRefusal( edition, hasDatabase )` | why an app cannot be made, e.g. a Lite app from a model read from API Logic Server |

`ALS Client.incl`, `ALS Binding.incl` and `ALS App.incl` in `src/Runtime/` are no longer copied into generated apps:
they are the start of the Professional runtime.

## Rules: where the line is (author, 2026-11-26)

The split is not by kind of rule. It is by **where the rules run and who shares them**:

- **Lite** covers defining, testing and running rules for one person, on one Mac, against one SQLite database.
- **Professional** covers rules that many people share through a server: enforced there, exchanged with API Logic
  Server, connected to other systems, secured and governed.

LogicBank for FutureBasic is an open module, so holding rule kinds back from Lite would only weaken the free product.

| Feature | Edition | Why |
|---|---|---|
| The engine, every rule kind (formula, constraint, sum, count, copy, parent check, delete actions, events) | Lite | the open module; without it a Lite app has no behaviour |
| The Rules page, `Rules.json`, the rules check, `Rules.incl` generated | Lite | writing rules is the point of App Builder |
| Rules as sentences in the model's names, with suggestions while typing | Lite | how users write rules (`AI Assistant Design.md`) |
| Explain and the logic log | Lite | needed to trust the rules |
| Rules on the model diagram | Lite | documentation for the one user |
| Scenarios, `--prove`, test data that can be purged | Lite | testing is part of writing rules |
| In-app actions on rule results (e.g. *Release all releasable*) | Lite | local, started by the user |
| AI Assistant: Translate, Suggest Rules, Suggest Controls, with the user's own key | Lite | a bare schema becomes a working app; the user pays the AI provider |
| Import and export of `declare_logic.py` | Professional | only meaningful with an ALS project |
| Enforcement on the server (ALS is the authority) | Professional | three tiers |
| The FB and ALS rules proven equal (the same scenarios against both) | Professional | only when both exist |
| Multi-user correctness: concurrent saves, one transaction across clients | Professional | needs a server |
| Integration events: web services, mail, messaging (e.g. Flight Service filing) | Professional | they run on the server, with its secrets |
| Scheduled and background rules | Professional | something must run when no app is open |
| Authorization: row-level security, grants by role | Professional | ALS security; meaningless for one user |
| Rule governance: versions, sign-off, an audit trail, roles | Professional | a team's concern |
| AI through ALS's `genai-logic`, with shared prompts and settings for a team | Professional | AI on the server, for an organisation |

**A Professional client also runs the rules locally, as a preview.** The app shows "this would be refused" as you type,
while the server makes the final decision.

**Upgrading carries the rules over.** The same sentences work in both editions: moving a project from Lite to
Professional exports its rules to `declare_logic.py` unchanged.

What is next for Professional is in the [roadmap](../ROADMAP.md) (phase 4).
