# Editions and Licensing

The Studio generates a business app in one of two editions. **Lite ships first**; Professional is
on the roadmap (author, 2026-11-24: "I want to get the free, SQLite edition out the door first,
then we can roadmap the paid edition for future").

| | Lite | Professional |
|---|---|---|
| Price | free | paid |
| Source | open source (this repository, public) | private repository, paid build only |
| Tiers | two: the app and its SQLite database | three: the app, an API Logic Server, the database |
| Data | `App Data Lite.incl`: the app opens the database itself (`Data Records.incl`) | `App Data Professional.incl`: JSON:API calls to the server (`ALS Client.incl`) |
| Business rules | in the app: LogicBank for FutureBasic, `Studio Rules.incl` + `Rules.incl` | on the server: LogicBank in ALS, `declare_logic.py` exported by the Studio |
| Sign-in | none (the database is on this Mac) | the header's Log In: the server's JWT login |
| Status | building now | roadmap |

API Logic Server is open source and the same for everyone, in either edition (author). What
Professional sells is the Studio's three-tier generation and its client runtime, not the server.

## One app, two data layers

Everything a user sees is the same in both editions: the shell, the pages, the XIBs, the
bindings, the model diagram. Only the data layer differs, behind one interface (the
application layer of `App Shell Design.md`, book §5.3: the infrastructure is replaced, the UI
survives):

```
App Pages.incl  ──  AppDataList / AppDataSave / AppDataRemove / AppDataLogin / AppDataKeyValues
                         │                                   answers in AppDataDone( op, entity, result, message )
          ┌──────────────┴───────────────┐
  App Data Lite.incl              App Data Professional.incl  (private)
  Data Records + Logic Engine      ALS Client (URLSession, asynchronous)
  SQLite on this Mac               API Logic Server → database
```

The interface answers through a handler rather than a return value because the server's replies
come back later (URLSession). Lite answers at once, through the same handler, so the pages need
no edition test.

## How the code is split

| Where | What |
|---|---|
| This repository (public) | the Studio; `src/AppBuilder/Edition.incl`, the **Lite-only** edition hook; the runtime for Lite (`App Data Lite.incl`, the data runtime, the rules engine, the shell) |
| Private repository (to create) | its own `Edition.incl` (offers Professional when the licence allows, adds its runtime files and start-up), `App Data Professional.incl`, its sign-in window, the `declare_logic.py` export step, and the paid build's project file |

The paid build is the same Studio with one file replaced: its project lists the private
`Edition.incl` in place of this one. The hook's functions:

| Function | Lite (this repository) |
|---|---|
| `EditionProfessionalAvailable` | `NO` |
| `EditionOfProject( projectDict )` | `Project.json` `"edition"`, Lite unless Professional is available |
| `EditionDescription( edition )` | the words the README and main program use |
| `EditionDataRuntimeFiles( edition )` | the data runtime, the rules engine, `App Data Lite.incl` |
| `EditionMainStart( edition, host, user )` | `DataOpen`, `DeclareStudioRules`, `DeclareRules`, `LogicActivate` |
| `EditionRulesInApp( edition )` | `YES` |
| `EditionRefusal( edition, hasDatabase )` | refuses an app for a model read from an API Logic Server: that app is Professional. Open the server's SQLite database instead for a Lite app |

The existing `ALS Client.incl`, `ALS Binding.incl` and `ALS App.incl` in `src/Runtime/` are no
longer copied into generated apps. They are the starting point of the Professional runtime and move
to the private repository when it exists. They are already public in this repository's history,
which is acceptable: they are a thin JSON:API client for an open-source server.

## Rules: where the line is (author, 2026-11-26)

The split is not by rule kind: it is by **where the rules run and who shares them**.
- **Lite** covers everything about defining, testing and running rules for one person, on one Mac, against one
  SQLite database.
- **Professional** covers everything about rules that many people share through a server: enforced there,
  exchanged with API Logic Server, connected to other systems, secured and governed.

LogicBank for FutureBasic is an open module, so holding rule kinds back from Lite would only cripple the free
product.

| Feature | Edition | Why |
|---|---|---|
| The engine, LogicBank for FutureBasic: every rule kind (formula, constraint, sum, count, copy, parent check, delete actions, events) | Lite | the open module; without it a Lite app has no behaviour |
| Rules page, `Rules.json`, the rules check, `Rules.incl` generated | Lite | authoring is the point of App Builder |
| Rules as sentences in the model's names, with model-name suggestions while typing | Lite | how users write rules (`AI Assistant Design.md`) |
| Explain and the logic log | Lite | needed to trust the rules |
| Rules on the model diagram | Lite | documentation for the one user |
| Scenarios, `--prove`, test data that can be purged | Lite | testing is part of writing rules |
| In-app actions on rule results (e.g. *Release all releasable*) | Lite | local, started by the user |
| AI Assistant: Translate, Suggest Rules, Suggest Controls, with the user's own key | Lite | a bare schema becomes a working app; the user pays the AI provider |
| Import and export of `declare_logic.py` | Professional | only meaningful with an ALS project, the Professional catalyst |
| Enforcement on the server (ALS is the authority) | Professional | three tiers |
| Equivalence of the FB and ALS rules (the same scenarios against both) | Professional | only when both exist |
| Multi-user correctness: concurrent saves, one transaction across clients | Professional | needs a server |
| Integration events: web services, mail, messaging (e.g. Flight Service filing) | Professional | they run on the server, with its secrets; Lite keeps local row and commit events |
| Scheduled and background rules (release when a ship docks, overdue alerts) | Professional | something must run when no app is open |
| Authorization rules: row-level security, grants by role | Professional | ALS security; meaningless for one user |
| Rule governance: versions, sign-off, an audit trail, roles | Professional | a team's concern (Imagery LogicBank Studio's ground) |
| AI through ALS's `genai-logic`, plus shared prompts and settings for a team | Professional | AI on the server, for an organisation |

**An Professional client also runs the rules locally, as a preview.** The app shows "this would be refused" as you
type, using LogicBank for FutureBasic, while the server makes the final decision.

**Upgrading carries the rules over.** The same sentences work in both editions: moving a project from Lite to
Professional exports its rules to `declare_logic.py` unchanged.

## Licensing (decided, author, 2026-11-26)

Design: `Licensing Design.md`. In short:

- **One app.** The same App Builder for Lite and Professional; Professional features are switched on by the licence.
  `Edition.incl` is no longer swapped by a separate build: `Licence.incl` answers `LicenceAllows( feature )`.
- **Everyone registers.** Lite licences are free, issued by the Imagery License Server when the user registers;
  only then is the download offered. *Upgrade to Professional…* in the app's Licence menu leads to the License
  Server's order form.
- **Signed licences** (the earlier option B), ECDSA P-256:
  - verified offline with `SecKeyVerifySignature`;
  - bound to the registered account, not to a Mac.

  The License Server is needed to register and to upgrade, never to run App Builder (the 2026-11-24 offline
  decision stands).
- **The source:** App Builder's source becomes private; LogicBank for FutureBasic and the SQL Generator stay
  public modules (MIT).
- **Generated apps never check a licence.**

## Roadmap (Professional)

1. Choose the licence option (A, B or C above) — author.
2. Create the private repository; move the ALS runtime there.
3. `App Data Professional.incl`: list / save / remove / login over JSON:API, one request context
   per call (URLSession `userData`), answers on the main thread (`dispatchmain`).
4. Sign-in window; token kept for the session; the Keychain for a remembered password.
5. Generate App (Professional): export the project's rules to `declare_logic.py` for the server.
6. License Server: the FB Studio product and the chosen licence format.
7. The paid build: project file, release, distribution from the License Server.
