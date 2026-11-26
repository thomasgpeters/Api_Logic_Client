# Editions and Licensing

The Studio generates a business app in one of two editions. **Lite ships first**; Enterprise is
on the roadmap (author, 2026-11-24: "I want to get the free, SQLite edition out the door first,
then we can roadmap the paid edition for future").

| | Lite | Enterprise |
|---|---|---|
| Price | free | paid |
| Source | open source (this repository, public) | private repository, paid build only |
| Tiers | two: the app and its SQLite database | three: the app, an API Logic Server, the database |
| Data | `App Data Lite.incl`: the app opens the database itself (`Data Records.incl`) | `App Data Enterprise.incl`: JSON:API calls to the server (`ALS Client.incl`) |
| Business rules | in the app: LogicBank for FutureBasic, `Studio Rules.incl` + `Rules.incl` | on the server: LogicBank in ALS, `declare_logic.py` exported by the Studio |
| Sign-in | none (the database is on this Mac) | the header's Log In: the server's JWT login |
| Status | building now | roadmap |

API Logic Server is open source and the same for everyone, in either edition (author). What
Enterprise sells is the Studio's three-tier generation and its client runtime, not the server.

## One app, two data layers

Everything a user sees is the same in both editions: the shell, the pages, the XIBs, the
bindings, the model diagram. Only the data layer differs, behind one interface (the
application layer of `App Shell Design.md`, book §5.3: the infrastructure is replaced, the UI
survives):

```
App Pages.incl  ──  AppDataList / AppDataSave / AppDataRemove / AppDataLogin / AppDataKeyValues
                         │                                   answers in AppDataDone( op, entity, result, message )
          ┌──────────────┴───────────────┐
  App Data Lite.incl              App Data Enterprise.incl  (private)
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
| Private repository (to create) | its own `Edition.incl` (offers Enterprise when the licence allows, adds its runtime files and start-up), `App Data Enterprise.incl`, its sign-in window, the `declare_logic.py` export step, and the paid build's project file |

The paid build is the same Studio with one file replaced: its project lists the private
`Edition.incl` in place of this one. The hook's functions:

| Function | Lite (this repository) |
|---|---|
| `EditionEnterpriseAvailable` | `NO` |
| `EditionOfProject( projectDict )` | `Project.json` `"edition"`, Lite unless Enterprise is available |
| `EditionDescription( edition )` | the words the README and main program use |
| `EditionDataRuntimeFiles( edition )` | the data runtime, the rules engine, `App Data Lite.incl` |
| `EditionMainStart( edition, host, user )` | `DataOpen`, `DeclareStudioRules`, `DeclareRules`, `LogicActivate` |
| `EditionRulesInApp( edition )` | `YES` |
| `EditionRefusal( edition, hasDatabase )` | refuses an app for a model read from an API Logic Server: that app is Enterprise. Open the server's SQLite database instead for a Lite app |

The existing `ALS Client.incl`, `ALS Binding.incl` and `ALS App.incl` in `src/Runtime/` are no
longer copied into generated apps. They are the starting point of the Enterprise runtime and move
to the private repository when it exists. They are already public in this repository's history,
which is acceptable: they are a thin JSON:API client for an open-source server.

## Rules: where the line is (author, 2026-11-26)

The split is not by rule kind: it is by **where the rules run and who shares them**.
- **Lite** covers everything about defining, testing and running rules for one person, on one Mac, against one
  SQLite database.
- **Enterprise** covers everything about rules that many people share through a server: enforced there,
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
| Import and export of `declare_logic.py` | Enterprise | only meaningful with an ALS project, the Enterprise catalyst |
| Enforcement on the server (ALS is the authority) | Enterprise | three tiers |
| Equivalence of the FB and ALS rules (the same scenarios against both) | Enterprise | only when both exist |
| Multi-user correctness: concurrent saves, one transaction across clients | Enterprise | needs a server |
| Integration events: web services, mail, messaging (e.g. Flight Service filing) | Enterprise | they run on the server, with its secrets; Lite keeps local row and commit events |
| Scheduled and background rules (release when a ship docks, overdue alerts) | Enterprise | something must run when no app is open |
| Authorization rules: row-level security, grants by role | Enterprise | ALS security; meaningless for one user |
| Rule governance: versions, sign-off, an audit trail, roles | Enterprise | a team's concern (Imagery LogicBank Studio's ground) |
| AI through ALS's `genai-logic`, plus shared prompts and settings for a team | Enterprise | AI on the server, for an organisation |

**An Enterprise client also runs the rules locally, as a preview.** The app shows "this would be refused" as you
type, using LogicBank for FutureBasic, while the server makes the final decision.

**Upgrading carries the rules over.** The same sentences work in both editions: moving a project from Lite to
Enterprise exports its rules to `declare_logic.py` unchanged.

## Licensing (decision for later)

Decided (author, 2026-11-24): the Studio checks the licence **offline** (it never calls the
License Server, consistent with "no Imagery application is a dependency"), and the licence gates
**the Studio only**: apps already generated never stop working.

Still open: **how** the Studio knows a licence is real. What the License Server issues today
(`Imagery-License-Server` README, `TokenGenerator`):

- a key `XXXX-XXXX-MMMM-XXXX-XXXX`: site, product, module bitmask, random part, checksum;
- the checksum is C++ `std::hash` of the other parts plus a salt that is published in the README.

Two things stop the Studio from using it as it is. First, `std::hash` is not the same on Linux
and on a Mac (libstdc++ and libc++ differ), so FutureBasic cannot recompute it. Second, anyone
who reads the salt can make a valid key. There is also no product entry for the FB Studio yet;
the existing `imagery_logicbank_studio` product "is free and never checks a licence".

The choices, in plain terms:

| Option | How it works | Trade-off |
|---|---|---|
| **A. The key as it is, with a portable checksum** | The License Server computes the checksum with SHA-256 (the same on every machine) instead of `std::hash`. The Studio recomputes it. | A small change on the License Server. Anyone who reads the Studio's code or the README can still make a key: it keeps honest people honest. |
| **B. A signed licence file** | Besides the key, the License Server issues a small file (who, which product, Enterprise, expiry) and *signs* it with a private key that never leaves the server. The Studio holds only the matching public key: it can check a signature but cannot make one, so nobody can forge a licence without the server's private key. macOS checks such signatures natively (`SecKeyVerifySignature`, in FB's Security headers). | A new feature on the License Server (key pair, signing, a file to download). The strongest offline option. |
| **C. Online activation** | The Studio sends the key to the License Server, which says yes or no. | Simple to reason about; makes the License Server a run-time dependency, which the no-dependency rule forbids. |

A signature works like a notary's seal: anyone can check it, only the notary can make it.
Option A is enough for a first paid release if forgery is not a worry; B can follow without
changing what users do (they still enter the key; the file comes with it).

Whichever is chosen, the License Server needs a product for the FB Studio (proposal:
`imagery_logicbank_studio_fb`, bit 0 `enterprise`) and the Studio needs a "Licence…" entry in
Project Settings or Preferences. Both belong to the Enterprise work.

## Roadmap (Enterprise)

1. Choose the licence option (A, B or C above) — author.
2. Create the private repository; move the ALS runtime there.
3. `App Data Enterprise.incl`: list / save / remove / login over JSON:API, one request context
   per call (URLSession `userData`), answers on the main thread (`dispatchmain`).
4. Sign-in window; token kept for the session; the Keychain for a remembered password.
5. Generate App (Enterprise): export the project's rules to `declare_logic.py` for the server.
6. License Server: the FB Studio product and the chosen licence format.
7. The paid build: project file, release, distribution from the License Server.
